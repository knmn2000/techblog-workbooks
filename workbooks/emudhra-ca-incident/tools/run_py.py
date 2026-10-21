"""Runs one checkpoint's Python program: run_py.py <solutions|reference> <id> <input> <output>

The checker's run command only knows the checkpoint id (`01`), while the program is called
`p01_<slug>.py`. This finds it, puts the shared-code folder on the import path, and runs it as
`__main__`. Whatever exit code the program ends with is the exit code of this script, so the
checker still sees 99 for "not implemented".

Shared code goes in `solutions/common/` and is imported as `import common.<module>`
(a reference solution uses `_spoilers/reference/common/` the same way).
"""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    kind, checkpoint, input_file, output_file = sys.argv[1:5]
    folder = ROOT / ("solutions" if kind == "solutions" else "_spoilers/reference")
    matches = sorted(folder.glob(f"p{checkpoint}_*.py"))
    if len(matches) != 1:
        sys.exit(f"expected exactly one {folder.name}/p{checkpoint}_*.py, found {len(matches)}")
    sys.path.insert(0, str(folder))
    sys.argv = [str(matches[0]), input_file, output_file]
    runpy.run_path(str(matches[0]), run_name="__main__")


if __name__ == "__main__":
    main()
