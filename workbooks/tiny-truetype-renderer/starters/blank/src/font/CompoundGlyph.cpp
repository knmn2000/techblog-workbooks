// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This code turns any glyph into the simple outlines you draw it with. It reads a
//   compound glyph's components, moves, scales or rotates each one, and resolves
//   components nested at any depth. In assignment 18 you draw every character of a line of
//   text through it, so your text renderer doesn't need to tell simple glyphs from
//   compound ones.
//
// Your job:
//   Implement the glyph resolver as "The compound glyph record" and "Placing a component"
//   describe. An empty glyph gives no parts, and a simple glyph gives itself, decoded by
//   your `GlyphParser` from assignment 07. For a compound glyph, read all of its component
//   records first, then resolve each component in record order: apply its own transform
//   first and the outer ones after.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
