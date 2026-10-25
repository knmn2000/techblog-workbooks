// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Resolving a compound glyph means reading its components, transforming each one, and
//   following any component that is itself compound, to any depth. A simple glyph comes
//   back as itself and an empty one gives no parts.
//
// Your job:
//   Implement the resolver as "The compound glyph record" and "Placing a component"
//   describe. An empty glyph gives no parts, and a simple glyph gives itself, decoded by
//   your `GlyphParser`. For a compound glyph, read all the component records first, then
//   resolve each component in record order, applying its own transform before the outer
//   ones.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
