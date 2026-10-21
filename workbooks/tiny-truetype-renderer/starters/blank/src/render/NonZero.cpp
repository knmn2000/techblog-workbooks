// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Filling a glyph by the non-zero rule, the rule fonts are designed for, on top of
//   `render/Scanline`. This assignment handles straight edges, assignment 17 adds curves,
//   and the text renderer of assignment 18 fills every glyph with it. Later, assignment 17
//   adds to this file.
//
// Your job:
//   Implement it with your `render/Scanline`: on every row, walk the sorted crossings left
//   to right with a running winding count and fill each stretch where the count isn't
//   zero. Each crossing needs the direction of its edge; if your crossings from assignment
//   14 don't record it yet, add it to `render/Scanline` first.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
