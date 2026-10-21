// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This class holds the whole pipeline. It loads a font's tables once, then maps each
//   character of a line of text to its glyph, fills the glyph by the non-zero rule and
//   moves the pen on by its advance. The checker's program and `main.cpp` both draw
//   through it.
//
// Your job:
//   Implement the class by calling your earlier work: load the cmap (assignment 03), the
//   glyph locations (04) and the advance widths (05) once, when you open the font. To
//   draw, decode the text, then for each code point find its glyph (glyph 0 if the font
//   has none), fill each of its outlines from your `font/CompoundGlyph` with your non-zero
//   fill, and move the pen by its advance times the scale.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
