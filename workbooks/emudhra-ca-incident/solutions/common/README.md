# Shared code

Put code you want to use in more than one checkpoint here: modular arithmetic, point addition,
a DER reader, whatever later checkpoints build on. The last checkpoint can then call your
earlier work instead of copying it.

- Every checkpoint program is run with `solutions/` on its import path, so a module in this
  folder is imported as `import common.your_module` (or `from common.your_module import add`).
  Don't run code at import time: keep it to functions and constants.
- A syntax error or a failing import here stops every checkpoint that imports the module.
  Moving code here once it passes its checkpoint avoids that.
- The inputs still carry what earlier checkpoints would produce, so you can skip around. Going
  in order just means you can use your own code instead of the values you're given.
