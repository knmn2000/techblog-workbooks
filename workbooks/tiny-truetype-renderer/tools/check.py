"""Builds your program for one checkpoint, runs it on every test case, and
compares what it writes with the expected output.

    .\\check 07                        check your solution
    .\\check 07 -Case <test-id>        run one case and show its full input and output
    .\\check 07 -Fresh [seed]          check against a newly generated set of cases
    .\\check 07 -Dispute <test-id> "why"   set aside a test you believe is wrong
    .\\check 07 -Ref                   check the reference solution (spoiler-free)
    .\\check 07 -Run "<command>"       check some other program; {input} and {output}
                                       are replaced with file paths
    .\\check 07 -Json                  print the result as JSON (used by .\\study)

Your program is started from the workbook folder as `<run> <input-file> <output-file>`.
How it is built and run is set in workbook.json, so any language or library works.
For checkpoints whose answer is a picture, the output file name ends in .png and your
program writes a PNG (or binary PPM) there.
"""

import contextlib
import io
import json
import re
import os
import random
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from imageio import ImageError, compare_images  # noqa: E402
import langs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOT_IMPLEMENTED_EXIT = 99
SHOWN_FAILURES = 3
DETAILED_FAILURES = 40  # failing cases described in full in -Json output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# What -Json prints: filled in as main() runs, next to the text it prints.
REPORT: dict = {}


def finish(code: int, **fields) -> int:
    REPORT.update(fields)
    return code


# ---- Test cases -----------------------------------------------------------------

@dataclass
class Case:
    id: str
    requirement: str
    title: str = ""
    source: str = ""
    input: list = field(default_factory=list)
    expected: list = field(default_factory=list)
    expected_file: str = ""  # for image cases: the expected picture


@dataclass
class CaseFile:
    header: dict
    requirements: list
    cases: list


def load_cases(path: Path) -> CaseFile:
    header, requirements, cases = {}, [], []
    current, block = None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        ends_block = line in ("expected", "end") or line.startswith("expected-file ")
        if current is not None and block in ("input", "expected") and not ends_block:
            getattr(current, block).append(line)
            continue
        if not line or line.startswith("#"):
            continue
        key, _, rest = line.partition(" ")
        if key == "case":
            case_id, _, req = rest.partition(" ")
            current, block = Case(case_id, req.strip()), None
        elif current is None:
            if key == "requirement":
                rid, _, text = rest.partition(" ")
                requirements.append((rid, text))
            else:
                header[key] = rest
        elif key in ("input", "expected"):
            block = key
        elif key == "end":
            cases.append(current)
            current, block = None, None
        elif key in ("title", "source"):
            setattr(current, key, rest)
        elif key == "expected-file":
            current.expected_file, block = rest, None
    for case in cases:
        case.source = case.source or header.get("source", "")
    return CaseFile(header, requirements, cases)


# ---- Comparing output -------------------------------------------------------------

@dataclass
class Comparison:
    """How a cases file wants output compared, from its `compare` header line:
    `records points=x,y,curve tolerance=0.001`  line by line, with named tuples
    `unordered tolerance=0`                      the same lines, in any order
    `image band=1 allow=0.0002`                 pictures, edges may move `band` pixels
    """
    mode: str = "records"
    fields: dict = field(default_factory=dict)
    tolerance: float = 0.0
    band: int = 1
    allow: float = 0.0


def parse_compare(spec: str) -> Comparison:
    words = spec.split()
    c = Comparison(mode=words[0] if words else "records")
    for part in words[1:]:
        key, _, value = part.partition("=")
        if key == "tolerance":
            c.tolerance = float(value)
        elif key == "band":
            c.band = int(value)
        elif key == "allow":
            c.allow = float(value)
        else:
            c.fields[key] = value.split(",")
    return c


def tokens(line: str) -> list:
    """Words of a line; a "quoted string" is one word with its spaces kept."""
    return re.findall(r'"[^"]*"|\S+', line)


def compare_unordered(expected: list, actual: list, fields: dict, tolerance: float):
    """The same lines in any order. Expected lines are matched in their own order; for one
    that's missing, the closest line written with the same keyword is shown."""
    exp = [tokens(l) for l in expected if l.strip()]
    act = [tokens(l) for l in actual if l.strip()]
    same = lambda a, b: len(a) == len(b) and all(same_token(x, y, tolerance) for x, y in zip(a, b))
    remaining = list(act)
    counts = f"({len(act)} lines written, {len(exp)} expected)"
    for e in exp:
        k = next((i for i, a in enumerate(remaining) if same(e, a)), None)
        if k is not None:
            remaining.pop(k)
            continue
        key = e[0]
        candidates = [a for a in remaining if a and a[0] == key]
        if not candidates:
            return f"missing line `{clip(' '.join(e))}` {counts}", [f"{key}:missing"]
        best = max(candidates, key=lambda a: sum(same_token(x, y, tolerance) for x, y in zip(e, a)) - abs(len(a) - len(e)))
        names = fields.get(key)
        spots = [f"{key}:missing"]
        detail = ""
        if names and len(best) == len(e) == len(names) + 1:
            differs = [names[i] for i in range(len(names)) if not same_token(e[i + 1], best[i + 1], tolerance)]
            spots = [f"{key}:{d}" for d in differs] + spots
            detail = f" - differs in {', '.join(differs)}"
        return (f"expected `{clip(' '.join(e))}`, closest line written: `{clip(' '.join(best))}`{detail} {counts}",
                spots)
    if remaining:
        return f"unexpected line `{clip(' '.join(remaining[0]))}` {counts}", [f"{remaining[0][0]}:extra"]
    return None, []


def same_token(a: str, b: str, tolerance: float) -> bool:
    if a == b:
        return True
    if tolerance <= 0:
        return False
    try:
        return abs(float(a) - float(b)) <= tolerance
    except ValueError:
        return False


def clip(text: str, width: int = 90) -> str:
    return text if len(text) <= width else text[: width - 3] + "..."


def compare(expected: list, actual: list, fields: dict, tolerance: float):
    """(None, []) if the output matches; otherwise a one-line explanation of the
    first difference, plus where it is (e.g. ["points:curve"]) for `explain`."""
    exp = [" ".join(tokens(l)) for l in expected if l.strip()]
    act = [" ".join(tokens(l)) for l in actual if l.strip()]
    # Output that starts with a keyword ("record 17 ...") is a list of records, and a difference
    # is reported with the record it's in. Purely numeric output has no records.
    record_key = exp[0].split()[0] if exp else None
    if record_key is not None and not record_key[:1].isalpha():
        record_key = None
    record = None
    for i, e in enumerate(exp):
        e_tokens = tokens(e)
        if e_tokens[0] == record_key:
            record = e
        where = f"  (in `{clip(record, 60)}`)" if record and record != e else ""
        if i >= len(act):
            return f"output ends early - expected line {i + 1}: `{clip(e)}`{where}", ["_lines"]
        a_tokens = tokens(act[i])
        if len(e_tokens) == len(a_tokens) and all(same_token(x, y, tolerance) for x, y in zip(e_tokens, a_tokens)):
            continue
        key = e_tokens[0]
        names = fields.get(key)
        if names and a_tokens and a_tokens[0] == key:
            n = len(names)
            e_vals, a_vals = e_tokens[1:], a_tokens[1:]
            for j in range(min(len(e_vals), len(a_vals)) // n):
                ev, av = e_vals[j * n:(j + 1) * n], a_vals[j * n:(j + 1) * n]
                if all(same_token(x, y, tolerance) for x, y in zip(ev, av)) and len(av) == n:
                    continue
                differs = [names[k] for k in range(n) if k >= len(av) or not same_token(ev[k], av[k], tolerance)]
                show = lambda vals: "(" + ", ".join(f"{names[k]}={vals[k]}" for k in range(len(vals))) + ")"
                return (f"{key}[{j}]: expected {show(ev)}, got {show(av)} - differs in {', '.join(differs)}{where}",
                        [f"{key}:{d}" for d in differs])
            return f"{key}: expected {len(e_vals) // n} entries, got {len(a_vals) / n:g}{where}", [f"{key}:count"]
        words = set(e_tokens) | set(a_tokens)
        return f"line {i + 1}: expected `{clip(e)}`, got `{clip(act[i])}`{where}", \
            [f"{key}~{w}" for w in sorted(words)] + [key]
    if len(act) > len(exp):
        return f"unexpected extra output at line {len(exp) + 1}: `{clip(act[len(exp)])}`", ["_lines"]
    return None, []


def likely_causes(where: list, explain: dict) -> list:
    """Map where the output differs to requirement ids, using the cases file's `explain` line."""
    by_word = [explain[s] for s in where if "~" in s and s in explain]
    if by_word:
        return list(dict.fromkeys(by_word))
    causes = []
    for spot in (s for s in where if "~" not in s):
        for candidate in (spot, spot.split(":")[0]):
            if candidate in explain:
                causes.append(explain[candidate])
                break
    return list(dict.fromkeys(causes))


# ---- Running programs -------------------------------------------------------------

def to_args(command: str) -> list:
    args = shlex.split(command, posix=(os.name != "nt"))
    args = [a[1:-1] if len(a) > 1 and a[0] == a[-1] == '"' else a for a in args]
    if args and ("/" in args[0] or "\\" in args[0]):
        args[0] = str((ROOT / args[0]).resolve())
    return args


def run_step(title: str, command: str) -> bool:
    proc = subprocess.run(to_args(command), cwd=ROOT, capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    run_step.output = output  # read by the caller to explain common build failures
    if proc.returncode != 0:
        print(f"{title} failed:\n{output}\n")
        return False
    warnings = [l for l in output.splitlines() if "warning:" in l]
    if warnings:
        print("Compiler warnings:\n  " + "\n  ".join(warnings[:10]) + "\n")
    return True


def describe_exit(code: int) -> str:
    known = {0xC0000005: "access violation (read or write through a bad pointer)",
             0xC00000FD: "stack overflow (infinite recursion?)",
             0xC0000094: "integer division by zero", 3: "abort() - often a failed bounds check",
             0xC0000409: "abort() - often a failed bounds check (index out of range)"}
    return known.get(code & 0xFFFFFFFF, f"exit code {code}")


@dataclass
class Result:
    case: Case
    status: str  # pass, fail, error, timeout, not-implemented, no-output
    message: str = ""
    actual: list = field(default_factory=list)
    reproduce: str = ""
    causes: list = field(default_factory=list)  # requirement ids the difference points to
    images: dict = field(default_factory=dict)  # picture cases: paths of the learner's image and the diff


def run_case(case: Case, run_template: str, work: Path, how: Comparison, explain, timeout) -> Result:
    in_path = work / f"{case.id}.in"
    out_path = work / (f"{case.id}.out.png" if how.mode == "image" else f"{case.id}.out")
    in_path.write_text("\n".join(case.input) + "\n", encoding="utf-8")
    out_path.unlink(missing_ok=True)
    rel_in = in_path.relative_to(ROOT).as_posix()
    rel_out = out_path.relative_to(ROOT).as_posix()
    command = run_template.format(input=rel_in, output=rel_out)
    try:
        proc = subprocess.run(to_args(command), cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Result(case, "timeout", f"Time Limit Exceeded (over {timeout} s)", reproduce=command)
    except FileNotFoundError:
        return Result(case, "error", f"could not start `{command}` - is it built?", reproduce=command)
    actual = []
    if how.mode != "image" and out_path.exists():
        actual = out_path.read_text(encoding="utf-8", errors="replace").splitlines()
    stderr = proc.stderr.strip().splitlines()
    if proc.returncode == NOT_IMPLEMENTED_EXIT:
        message = stderr[-1].removeprefix("not implemented: ") if stderr else "a function"
        return Result(case, "not-implemented", message, reproduce=command)
    if proc.returncode != 0:
        detail = stderr[-1] if stderr else ""
        return Result(case, "error", f"Runtime Error - {describe_exit(proc.returncode)}"
                      + (f": {clip(detail)}" if detail else ""), actual, command)
    if not out_path.exists():
        return Result(case, "no-output", f"no output file: your program finished without writing {rel_out} "
                      "(the second argument it was given)", reproduce=command)
    if how.mode == "image":
        diff_path = work / f"{case.id}.diff.png"
        diff_path.unlink(missing_ok=True)
        try:
            problem, where = compare_images(ROOT / case.expected_file, out_path, diff_path, band=how.band,
                                            allow=how.allow, label=diff_path.relative_to(ROOT).as_posix())
        except ImageError as e:
            problem, where = f"couldn't compare images: {e}", ["image:format"]
        actual = [f"(image written to {rel_out})"]
        images = {"actual": rel_out, "diff": diff_path.relative_to(ROOT).as_posix() if diff_path.exists() else None}
        if problem is None:
            return Result(case, "pass", actual=actual, reproduce=command, images=images)
        causes = likely_causes(where, explain) or ([case.requirement] if case.requirement != "E2E" else [])
        return Result(case, "fail", problem, actual, command, causes, images)
    elif how.mode == "unordered":
        problem, where = compare_unordered(case.expected, actual, how.fields, how.tolerance)
    else:
        problem, where = compare(case.expected, actual, how.fields, how.tolerance)
    if problem is None:
        return Result(case, "pass", actual=actual, reproduce=command)
    causes = likely_causes(where, explain)
    if not causes and case.requirement != "E2E":
        causes = [case.requirement]  # nothing more specific: the requirement this case targets
    return Result(case, "fail", problem, actual, command, causes)


# ---- Commands -------------------------------------------------------------------

def dots(text: str, width: int = 70) -> str:
    text = clip(text, width - 2)
    return text + " " + "." * (width - len(text) - 1)


def load_disputes() -> list:
    path = ROOT / "disputes.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def dispute(checkpoint: str, case_file: CaseFile, test_id: str, reason: str) -> int:
    if test_id not in {c.id for c in case_file.cases}:
        print(f"There is no test {test_id} in checkpoint {checkpoint}.")
        return 1
    disputes = load_disputes()
    disputes.append({"checkpoint": checkpoint, "test": test_id, "reason": reason,
                     "opened": date.today().isoformat(), "status": "open"})
    (ROOT / "disputes.json").write_text(json.dumps(disputes, indent=2) + "\n", encoding="utf-8")
    print(f"Set aside {test_id}: it won't count until the dispute is closed.\n"
          f"Ask Claude to \"review my disputes\" to have it checked and either fixed or explained.")
    return 0


VERIFIED = ROOT / "_spoilers" / "verified.json"
LOCAL_IMPORT = re.compile(r"""^\s*#\s*include\s+"([^"]+)"|require\(\s*['"](\.[^'"]+)['"]\s*\)|from\s+['"](\.[^'"]+)['"]""", re.M)


def reference_sources(meta: dict) -> list:
    """The reference solution's own source files: its main file, then every file under _spoilers/
    it includes (recursively). Headers from include/ or third_party/ are the workbook's, not listed."""
    main_file = ROOT / meta.get("referenceSource", f"_spoilers/reference/{Path(meta['solution']).name}")
    found, queue = [], [main_file]
    spoilers = (ROOT / "_spoilers").resolve()
    while queue:
        path = queue.pop(0).resolve()
        if path in found or not path.is_file() or spoilers not in path.parents:
            continue
        found.append(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in LOCAL_IMPORT.finditer(text):
            name = next(g for g in m.groups() if g)
            candidates = [path.parent / name] + ([path.parent / (name + ext) for ext in (".js", ".ts", ".py")]
                                                 if not Path(name).suffix else [])
            queue += [c for c in candidates if c.is_file()]
        if path.suffix == ".py":
            for m in re.finditer(r"^\s*(?:from|import)\s+([\w.]+)", text, re.M):
                queue.append(path.parent / (m.group(1).replace(".", "/") + ".py"))
    return found


def fingerprint(paths: list) -> dict:
    """sha256 of each file's text (line endings ignored), keyed by its path in the workbook."""
    import hashlib
    return {p.relative_to(ROOT).as_posix():
            hashlib.sha256(p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").encode()).hexdigest()
            for p in paths}


def record_verified(checkpoint: str, meta: dict, passed: int, total: int):
    """Remembers that the reference, exactly as it is now, passes every committed test.
    build_book.py shows the reference in the Editorial only with this proof attached."""
    sources = reference_sources(meta)
    if not sources:
        return
    data = json.loads(VERIFIED.read_text(encoding="utf-8")) if VERIFIED.exists() else {}
    data[checkpoint] = {"files": fingerprint(sources), "passed": passed, "total": total,
                        "date": date.today().isoformat()}
    VERIFIED.write_text(json.dumps(dict(sorted(data.items())), indent=2) + "\n", encoding="utf-8")


def still_blank(solution: str) -> bool:
    """True while the learner's file is unchanged from starters/blank/ (ignoring line endings)."""
    blank, mine = ROOT / "starters" / "blank" / Path(solution).name, ROOT / solution
    if not blank.exists() or not mine.exists():
        return False
    text = lambda p: [line.rstrip() for line in p.read_text(encoding="utf-8", errors="replace").splitlines()]
    return text(blank) == text(mine)


def main(argv: list) -> int:
    args = [a.lower() if a.startswith("-") else a for a in argv]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return finish(2, verdict="error", message="no checkpoint number given")
    checkpoint = f"{int(args[0]):02d}"
    config = json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))
    meta = config["checkpoints"].get(checkpoint)
    REPORT.update(checkpoint=checkpoint, title=meta["title"] if meta else "")
    if meta is None:
        print(f"Checkpoint {checkpoint} isn't in workbook.json yet.")
        return finish(2, verdict="error", message=f"checkpoint {checkpoint} isn't in workbook.json")

    def option(name, count=1):
        if name not in args:
            return None
        i = args.index(name)
        values = [argv[j] for j in range(i + 1, min(i + 1 + count, len(argv))) if not argv[j].startswith("-")]
        return values or [""]

    def build(step_config) -> bool:
        setup = config.get("setup")
        if setup and not (ROOT / setup["creates"]).exists() and not run_step("Setup", setup["command"]):
            return False
        command = step_config.get("build", "").format(id=checkpoint)
        if not command:
            return True
        proc = subprocess.run(to_args(command), cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0 and setup and "unknown target" in (proc.stdout + proc.stderr):
            run_step("Setup", setup["command"])  # a checkpoint was added since the last setup
        return run_step("Build", command)

    cases_path = ROOT / meta["cases"]
    if (other := option("-cases")) is not None:  # used when checking the checks
        cases_path = ROOT / other[0]
    fresh = option("-fresh")
    if fresh is not None:
        seed = int(fresh[0]) if fresh[0].isdigit() else random.randrange(1, 1_000_000)
        out = ROOT / "build" / "fresh" / checkpoint
        # Picture checkpoints draw their expected images with the reference program.
        if meta.get("generatorNeedsReference") and not build(config["reference"]):
            return finish(3, verdict="error", message="couldn't build the reference program to draw fresh pictures")
        command = meta["generator"].format(seed=seed, out=out.relative_to(ROOT).as_posix())
        if not run_step("Generating fresh cases", command):
            return finish(3, verdict="error", message="couldn't generate fresh cases")
        cases_path = out / "cases.txt"
        REPORT["fresh"] = seed
    case_file = load_cases(cases_path)

    if (d := option("-dispute", 2)) is not None:
        if len(d) < 2:
            print('Usage: .\\check 07 -Dispute <test-id> "why you think it is wrong"')
            return finish(2, verdict="error", message="-Dispute needs a test id and a reason")
        return finish(dispute(checkpoint, case_file, d[0], d[1]), verdict="dispute")

    use_ref = "-ref" in args
    custom = option("-run")
    steps = config["reference"] if use_ref else config
    run_template = custom[0] if custom else steps["run"]
    run_template = run_template.replace("{id}", checkpoint)

    # Another language than the workbook's own: built and run by tools/langs.py.
    chosen = option("-lang")
    lang = LANG_ALIASES.get((chosen[0] if chosen else "").lower(), (chosen[0] if chosen else "").lower()) or langs.native(config)
    if lang not in langs.LANGUAGES:
        print(f"Unknown language {lang!r}. Choose one of: {', '.join(langs.LANGUAGES)}")
        return finish(2, verdict="error", message=f"unknown language {lang}")
    REPORT["language"] = lang
    if lang != langs.native(config) and not use_ref and not custom:
        return check_other_language(checkpoint, meta, config, lang, case_file, cases_path, option)

    solution = ROOT / meta["solution"]
    if not use_ref and not custom and solution.exists() and not solution.read_text(encoding="utf-8", errors="replace").strip():
        print(f"Not started yet: {meta['solution']} is empty.\n"
              f"Write your program there (the problem is in {meta['problem']}), then run .\\check {checkpoint} again.\n"
              f"To start again from the blank starter, copy starters/blank/{solution.name} over it.")
        return finish(2, verdict="not-started", empty=True)

    if not use_ref and not custom and still_blank(meta["solution"]):
        boilerplate = f"starters/boilerplate/{Path(meta['solution']).name}"
        print(f"Not started yet: {meta['solution']} is still the blank starter.\n"
              f"Write your program there (the problem is in {meta['problem']}), then run .\\check {checkpoint} again.")
        if (ROOT / boilerplate).exists():
            print(f"To start from ready-made input/output code instead, copy {boilerplate} over it.")
        return finish(2, verdict="not-started", empty=False)

    if not custom and not build(steps):
        return compile_error(checkpoint, getattr(run_step, "output", ""))
    return run_and_report(checkpoint, meta, config, case_file, cases_path, option, run_template,
                          "reference solution" if use_ref else ("custom command" if custom else meta["solution"]),
                          use_ref and not custom)


LANG_ALIASES = {"c++": "cpp", "cxx": "cpp", "js": "javascript", "node": "javascript", "ts": "typescript",
                "py": "python", "python3": "python", "rs": "rust", "golang": "go"}
NO_MAIN = re.compile(r"undefined reference to `(WinMain|main)'|entry point must be defined|_main.*referenced from"
                     r"|function main is undeclared|`main` function not found")


def compile_error(checkpoint: str, output: str) -> int:
    no_main = bool(NO_MAIN.search(output))
    if no_main:
        print("Your program has no main() function. The checker runs it as a program, so it needs one.")
    print(f"Compile Error - fix the errors above and run .\\check {checkpoint} again.")
    return finish(3, verdict="compile-error", build=output, noMain=no_main, errors=compiler_errors(output))


def check_other_language(checkpoint, meta, config, lang, case_file, cases_path, option) -> int:
    """A checkpoint solved in a language other than the workbook's own (see tools/langs.py)."""
    spec = langs.LANGUAGES[lang]
    flag = f".\\check {checkpoint} -Lang {lang}"
    tool, problem = langs.find_tool(lang)
    if tool is None:
        print(langs.install_text(lang))
        return finish(2, verdict="missing-tool", install=langs.availability(lang))
    solution = langs.solution_path(meta, lang, config)
    rel = solution.relative_to(ROOT).as_posix()
    blank = langs.blank_starter(lang, checkpoint, meta, config)
    if not solution.exists():
        solution.write_text(blank, encoding="utf-8", newline="\n")
        print(f"Not started yet: created {rel} with a blank {spec['label']} starter.\n"
              f"Write your program there (the problem is in {meta['problem']}), then run {flag} again.")
        return finish(2, verdict="not-started", empty=False, created=rel)
    text = solution.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print(f"Not started yet: {rel} is empty.\nWrite your program there, then run {flag} again.")
        return finish(2, verdict="not-started", empty=True)
    if [l.rstrip() for l in text.splitlines()] == [l.rstrip() for l in blank.splitlines()]:
        print(f"Not started yet: {rel} is still the blank starter.\nWrite your program there, then run {flag} again.")
        return finish(2, verdict="not-started", empty=False)
    ok, output = langs.build(lang, checkpoint, meta, config)
    if not ok:
        print(f"Build failed:\n{output}\n")
        return compile_error(checkpoint, output)
    return run_and_report(checkpoint, meta, config, case_file, cases_path, option,
                          langs.run_command(lang, checkpoint, meta, config), f"{rel}, {spec['label']}", False)


def run_and_report(checkpoint, meta, config, case_file, cases_path, option, run_template, who, verify) -> int:
    """Runs every case and prints the verdict (text, and REPORT for -Json)."""
    fresh = option("-fresh")
    only = option("-case")
    cases = case_file.cases
    if only is not None:
        cases = [c for c in cases if c.id == only[0]]
        if not cases:
            print(f"There is no test {only[0]} in checkpoint {checkpoint}.")
            return finish(2, verdict="error", message=f"there is no test {only[0]} in checkpoint {checkpoint}")
    disputed = {d["test"] for d in load_disputes() if d["checkpoint"] == checkpoint and d["status"] == "open"}
    set_aside = [c.id for c in cases if c.id in disputed and only is None]
    cases = [c for c in cases if c.id not in set_aside]

    how = parse_compare(case_file.header.get("compare", "records"))
    REPORT["compare"] = {"mode": how.mode, "tolerance": how.tolerance}  # lets the book highlight real differences
    explain = dict(part.split("=", 1) for part in case_file.header.get("explain", "").split())
    work = ROOT / "build" / "cases" / checkpoint
    work.mkdir(parents=True, exist_ok=True)
    timeout = config.get("timeoutSeconds", 10)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        results = list(pool.map(lambda c: run_case(c, run_template, work, how, explain, timeout), cases))

    print(f"Checkpoint {checkpoint} - {meta['title']}")
    print(f"Program:  {run_template}   ({who})")
    print(f"Cases:    {cases_path.relative_to(ROOT).as_posix()} (seed {case_file.header.get('seed', '?')})\n")

    missing = next((r for r in results if r.status == "not-implemented"), None)
    if missing:
        print(f"Not implemented yet: {missing.message}\nWrite it in {meta['solution']}, "
              f"then run .\\check {checkpoint} again.")
        return finish(2, verdict="not-implemented", function=missing.message)

    order = [rid for rid, _ in case_file.requirements]
    texts = dict(case_file.requirements)

    if only is not None:
        r = results[0]
        REPORT.update(verdict="passed" if r.status == "pass" else "failed", passed=int(r.status == "pass"),
                      total=1, cases=[case_json(r, texts, full=True)])
        print(f"{r.case.id}  {r.case.title}\n\ninput:\n  " + "\n  ".join(r.case.input))
        if r.case.expected_file:
            print(f"\nexpected image:\n  {r.case.expected_file}")
        else:
            print("\nexpected output:\n  " + "\n  ".join(clip(l, 200) for l in r.case.expected))
        print("\nyour output:\n  " + ("\n  ".join(clip(l, 200) for l in r.actual) or "(nothing)"))
        print(f"\n{'Passed' if r.status == 'pass' else 'Failed: ' + r.message}")
        for rid in r.causes:
            print(f"likely cause: {rid} - {dict(case_file.requirements).get(rid, '')}")
        print(f"expected values from: {r.case.source}\nreproduce: {r.reproduce}")
        return 0 if r.status == "pass" else 1

    for r in results:
        if r.case.requirement not in texts:
            order.append(r.case.requirement)
            texts[r.case.requirement] = "(undeclared requirement)"
    passed = sum(r.status == "pass" for r in results)
    for rid in dict.fromkeys(order):
        group = [r for r in results if r.case.requirement == rid]
        if not group:
            continue
        ok = sum(r.status == "pass" for r in group)
        print(f"  {rid:<4}{dots(texts[rid])} {ok:>4} / {len(group):<4}{'' if ok == len(group) else 'FAILED'}")
        failed = [r for r in group if r.status != "pass"]
        for r in failed[:SHOWN_FAILURES]:
            causes = "".join(f"\n          likely cause: {c} - {texts.get(c, '')}" for c in r.causes)
            print(f"      x {r.case.id}  {clip(r.case.title, 80)}\n"
                  f"          {r.message}{causes}\n"
                  f"          expected values from: {r.case.source}\n"
                  f"          reproduce: {r.reproduce}")
        if len(failed) > SHOWN_FAILURES:
            print(f"      ... and {len(failed) - SHOWN_FAILURES} more")
    if set_aside:
        print(f"\n  Set aside (disputed): {', '.join(set_aside)}")

    failing = [r for r in results if r.status != "pass"]
    REPORT.update(passed=passed, total=len(results), disputed=set_aside,
                  requirements=[{"id": rid, "text": texts[rid],
                                 "passed": sum(r.status == "pass" for r in results if r.case.requirement == rid),
                                 "total": sum(r.case.requirement == rid for r in results)}
                                for rid in dict.fromkeys(order) if any(r.case.requirement == rid for r in results)],
                  cases=[case_json(r, texts, full=r in failing[:DETAILED_FAILURES]) for r in results])
    if passed == len(results):
        note = f" ({len(set_aside)} disputed)" if set_aside else ""
        print(f"\nAccepted: {passed} / {len(results)} tests passed{note}.")
        if verify and fresh is None and cases_path == ROOT / meta["cases"] and not set_aside:
            record_verified(checkpoint, meta, passed, len(results))
            print(f"Recorded in {VERIFIED.relative_to(ROOT).as_posix()}: the Editorial can show this solution.")
        return finish(0, verdict="accepted")
    tally = {}
    for r in results:
        for c in r.causes[:1]:
            tally[c] = tally.get(c, 0) + 1
    silent = all(r.status == "no-output" or (r.status == "fail" and not r.actual) for r in failing)
    if silent:
        # Nothing was written anywhere: that's the problem to fix, not any one requirement.
        example = run_template.replace("{input}", "<input-file>").replace("{output}", "<output-file>")
        print(f"\n  Your program wrote nothing in any failing test. It is run as\n      {example}\n"
              f"  and must write its answer to <output-file>, the second argument.")
    elif tally:
        top, count = max(tally.items(), key=lambda kv: kv[1])
        print(f"\n  Most failures ({count}) point to {top} - {texts.get(top, '')}")
        REPORT["mostLikely"] = {"id": top, "text": texts.get(top, ""), "count": count}
    print(f"\nWrong Answer: {passed} / {len(results)} tests passed.\n"
          f"  See one case in full:     .\\check {checkpoint} -Case <test-id>\n"
          f"  Think a test is wrong?    .\\check {checkpoint} -Dispute <test-id> \"why\"")
    return finish(1, verdict="wrong-answer", wroteNothing=silent)


# ---- JSON output (for .\study) ---------------------------------------------------

def trimmed(lines: list, count: int = 80, width: int = 400) -> list:
    out = [clip(line, width) for line in lines[:count]]
    return out + [f"... ({len(lines) - count} more lines)"] if len(lines) > count else out


def case_json(r: Result, texts: dict, full: bool) -> dict:
    d = {"id": r.case.id, "title": r.case.title, "requirement": r.case.requirement, "status": r.status}
    if full:
        d.update(message=r.message, source=r.case.source, reproduce=r.reproduce,
                 causes=[{"id": c, "text": texts.get(c, "")} for c in r.causes],
                 input=trimmed(r.case.input), expected=trimmed(r.case.expected), actual=trimmed(r.actual))
        if r.case.expected_file:
            d["images"] = {"expected": r.case.expected_file, **r.images}
    return d


def compiler_errors(output: str) -> list:
    """file, line and message of each error in the build output (any language), for marking the editor."""
    return langs.parse_errors(output)


def main_json(argv: list) -> int:
    """Runs main() with its text captured, then prints REPORT (plus that text) as one JSON object."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            code = main(argv)
        except Exception as e:  # the page can't read a traceback; report it instead
            code = finish(4, verdict="error", message=f"the checker itself failed: {e!r}")
    REPORT.update(exit=code, text=buffer.getvalue())
    sys.stdout.write(json.dumps(REPORT, ensure_ascii=False) + "\n")
    return code


if __name__ == "__main__":
    flags = [a.lower() for a in sys.argv[1:]]
    if "-json" in flags:
        sys.exit(main_json([a for a in sys.argv[1:] if a.lower() != "-json"]))
    sys.exit(main(sys.argv[1:]))
