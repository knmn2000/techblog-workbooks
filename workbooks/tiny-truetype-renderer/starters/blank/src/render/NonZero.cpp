// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It fills a glyph by the non-zero rule, the rule TrueType uses, on top of your
//   `render/Scanline`. This assignment handles straight edges, assignment 17 adds curves,
//   and the text renderer in assignment 18 fills every glyph with it.
//
// Your job:
//   Implement the non-zero fill with your `render/Scanline`: on every row, walk the sorted
//   crossings left to right with a running winding count and fill each stretch where the
//   count isn't zero. Each crossing needs the direction of its edge; if your crossings
//   from assignment 14 don't record it yet, add it to `render/Scanline` first.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
