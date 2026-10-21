#pragma once
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
//   Declare a class that loads a font from a path once and keeps what drawing needs: the
//   map from code point to glyph, where each glyph's record is, and the advance widths.
//   Give it a function that draws a UTF-8 string on a canvas from a pen x, baseline, scale
//   and colour and returns the pen x after the last character, plus, for `main.cpp`, a way
//   to measure a string's width and to read the font's ascent and descent.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
