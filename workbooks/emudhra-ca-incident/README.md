# Elliptic-Curve Keys, Certificates and Chains of Trust

*Learn how to not f*ck up like eMudhra.*

LeetCode-style assignments built around
[eMudhra's statement on a certificate security incident](https://emudhra.com/en/post/certificate-security-incident).
Eight of eMudhra's intermediate certificate authority keys turned out to be weak (one had the
private key value 4), and anyone could have recovered them in under a second. You build the maths
that makes a key pair work, parse and validate certificates by hand, recover a weak key yourself,
sign with it, and then build the checks that would have caught it: correct key generation, a key
linter, a ceremony checker and SPKI blocklisting. Each assignment adds modules to a Python project
of your own. After the last one, `solutions/` holds `pkiaudit`, a working PKI auditor you can put
on GitHub as it is.

The problems are in `problems/` and, nicer to read, in the web problem book
(`book/problem-book.html`: open it in a browser). The book has a problem list with your progress,
and for each assignment the statement, what it adds to your project, hints that open in order, an
Editorial with a solution proven to pass every test, an editor with the assignment's files, and
the example test cases.

| # | Assignment | # | Assignment |
|---|---|---|---|
| 01 | Modular arithmetic | 09 | Validate a certificate chain |
| 02 | Add points on a toy curve | 10 | Find a weak private key |
| 03 | Multiply a point by a number | 11 | Sign a certificate with a recovered key |
| 04 | Verify an ECDSA signature | 12 | Generate a key correctly |
| 05 | Read DER | 13 | Lint a public key |
| 06 | Read a certificate | 14 | Check a key ceremony |
| 07 | Hash the public key (SPKI) | 15 | Block and distrust |
| 08 | Check a certificate's signature | 16 | Audit a PKI |

## Start here

Ask Claude to "set up my workbook": it checks the tools, asks which language you'd like (this
workbook's project is Python), creates the project and opens the book. Or double-click
`study.cmd` (or run `.\study` in PowerShell, `./study.sh` on macOS or Linux): the book opens with
Run and Submit working, and offers to create the project if there isn't one yet. Leave its window
open while you work, or use the book's **Exit** button when you're done.

## Your project

```
solutions/
  pyproject.toml, README.md, .gitignore
  src/pkiaudit/ecc/     modmath (01), curve and curves (02, 03), ecdsa (04, 11), keys (12)
  src/pkiaudit/asn1/    der (05)
  src/pkiaudit/x509/    certificate (06), spki (07), signature (08)
  src/pkiaudit/pki/     chain (09), lint (13), ceremony (14), trust (15), audit (16)
  src/pkiaudit/attack/  weak_key (10)
  src/pkiaudit/__main__.py   the pkiaudit command (16)
  examples/sample.pki   a small PKI to audit
  assignments/          assignment_01_modular_arithmetic.py ... assignment_16_audit_pki.py: one
                        program per assignment, which the checker runs; you write these too
```

Do the assignments in order. Opening an assignment (in the book, or with `.\check NN`) creates
its files, each with a comment saying why the file exists and what your job in it is. It doesn't
overwrite anything you've written. You write an assignment's real work in `src/pkiaudit/`, and
later assignments import it: ECDSA uses your curve arithmetic, the chain validator uses your
certificate reader, and the audit uses most of the package. The assignment's program in
`assignments/` reads a test input, calls your code and writes the answer.

Each test input carries what earlier assignments would produce, so an assignment's tests depend
only on the earlier modules it imports. **Re-check solved** in the book runs every solved
assignment again, so you see at once when a change breaks an earlier one (the book marks it with a
red `!`).

The **Files** panel in the book's editor shows the project as it grows, with each file's
assignment. Run the finished program:

```
py -P tools/run_py.py solutions -m pkiaudit audit solutions/examples/sample.pki
```

On its own (for example after you've pushed it to GitHub), `pip install -e .` in `solutions/`
installs the `pkiaudit` command.

## Doing an assignment

1. Read the problem (book or `problems/NN-*.md`). In the book, its **Start here** card lists the
   files to write, your job in each, the earlier modules you can use, and the two ways to start.
2. Write the files. Each one starts as the Boilerplate, which gives you the input/output code, the
   constants and the function signatures, and you fill in the bodies marked `TODO`. To write all
   of it yourself, choose **From scratch** on the Start here card: each file then starts empty
   apart from its comment.
3. Check it from this folder in PowerShell (`./check.sh` on macOS or Linux), or with Run and
   Submit in the book:

```
.\check 06                         run every test
.\check 06 -Case <test-id>         one test in full: input, expected output, your output
.\check 06 -Fresh                  a newly generated set of tests (new random seed)
.\check 06 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is `Accepted`, `Wrong Answer`, `Compile Error` (a syntax error anywhere in your
project), `Runtime Error`, `Time Limit Exceeded` or `Not implemented yet` (a function still raises
`NotImplementedError`). The checker compares text output word by word, so line endings and extra
spaces don't matter, except inside quoted strings. For each failure it shows its best guess at the
requirement behind it, where the expected value came from, and the command that reproduces it.

## If you think a test is wrong

Run `.\check 06 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on;
the verdict reads `Accepted (1 disputed)`. Then ask Claude to "review my disputes". Claude
rechecks the expected value against its independent source and either fixes the test or shows
you why it's right. The checker keeps disputes in `disputes.json`.

## Another language

The checker reads only your program's output, so you can write the project in any language. This
workbook's project, its starters and its reference are Python.

To work in another language, ask Claude. It shows which languages you have installed
(`py -P tools/langs.py` lists them) and how to install the others, keeps your Python project in a
folder of its own, and sets up a project in the new language with the same layout in that
language's style. It creates nothing for languages you don't choose.

To check a one-off program without changing anything, run
`.\check 06 -Run "path/to/program {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements (`tools/build_book.py` makes the book from these) |
| `solutions/` | Your project, created when you set the workbook up (see above) |
| `starters/project/` | What your project starts with: `pyproject.toml`, README, `.gitignore`, the package folders and the sample PKI |
| `starters/blank/`, `starters/boilerplate/` | Each assignment's files, blank and with the input/output and signatures done |
| `tests/NN/` | Test inputs and expected outputs |
| `study.cmd`, `study.command`, `study.ps1`, `study.sh` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server: only reachable from this computer; loads and saves your project's files and runs the checker |
| `tools/check.py` | The checker (`check.ps1`, `check.cmd` and `check.sh` call it) |
| `tools/run_py.py` | Runs an assignment's program with your package on the import path |
| `tools/project.py` | Sets up your project and starts assignments (`setup`, `start NN`, `status`) |
| `tools/blank_starters.py` | Writes the blank starters from `workbook.json` |
| `tools/gen_pNN.py` | Each assignment's test generator (used by `-Fresh`) |
| `tools/build_book.py` | Builds `book/problem-book.html` (the page design is `tools/book_template.html`) |
| `docs/authoring-guide.md` | How to write the assignments and their tests |
| `_spoilers/` | The reference project. Don't open it until you've passed. |

Needs: Python 3.11 or newer. For `-Fresh`, the test generators also need `openssl` on your PATH
and the `cryptography` package (`pip install cryptography`); your own project needs neither.
