// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Turning any glyph into the simple outlines it is drawn with: a compound glyph's
//   components are read, moved, scaled or rotated, and resolved however deeply they nest.
//   Assignment 18 draws every character of a line of text through it, so it never has to
//   tell simple glyphs from compound ones.
//
// Your job:
//   Implement it with "The compound glyph record" and "Placing a component": an empty
//   glyph gives no parts, and a simple glyph gives itself, decoded by your `GlyphParser`
//   from assignment 07. For a compound glyph, read all of its component records, then
//   resolve each component in record order, with its own transform applied first and the
//   outer ones after.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
