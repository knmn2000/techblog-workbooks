// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Loading happens once, when the font opens: the character map, the glyph locations and
//   the advance widths. After that each character of a line goes through glyph lookup,
//   fill and pen advance.
//
// Your job:
//   Build the class from your earlier work: when you open the font, load the cmap
//   (assignment 03), the glyph locations (04) and the advance widths (05) once. To draw,
//   decode the text, then for each code point find its glyph (glyph 0 if the font has
//   none), fill each of its outlines from your `font/CompoundGlyph` with your non-zero
//   fill, and move the pen by the advance times the scale.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
