# Shared code

Put code you want to use in more than one checkpoint here. Your byte readers (01), table
parsers (02-05), glyph decoders (07, 09) and fill (16, 17) can then live in one place, and
checkpoint 18 calls them instead of copying them.

- Every `.cpp` file in this folder is compiled once and linked into each of your checkpoint
  programs (`p01` to `p18`, not the reference ones). Don't put a `main()` here.
- Include a header from a checkpoint file as `#include "common/your_header.h"`.
- A compile error here stops every checkpoint from building, and a function defined both here
  and in a checkpoint file won't link. Moving code here once it passes its checkpoint avoids
  both.
- The inputs still carry what earlier checkpoints would produce, so you can skip around. Going
  in order just means you can use your own code instead of the values you're given.
