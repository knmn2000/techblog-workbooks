// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The whole pipeline in one class: a font's tables loaded once, then each character of a
//   line of text mapped to its glyph, filled by the non-zero rule and followed by its
//   advance. The checker's program and `main.cpp` both draw through it.
//
// Your job:
//   Implement the class by calling your earlier work: load the cmap (assignment 03), the
//   glyph locations (04) and the advance widths (05) once, when the font is opened. To
//   draw, decode the text, then for each code point find its glyph (glyph 0 if the font
//   has none), fill each of its outlines from your `font/CompoundGlyph` with your non-zero
//   fill, and move the pen by its advance times the scale.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
