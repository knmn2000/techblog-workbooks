#pragma once
// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `hhea` and `hmtx` tables: the font's ascent
//   and descent, and each glyph's advance width and left side bearing. Assignment 18 moves
//   the pen by each glyph's advance width and sizes the text from the ascent and descent.
//
// Your job:
//   Declare the metrics of one glyph (advance width and left side bearing) and a function
//   that reads the font's ascent and descent and the metrics of every glyph id, given your
//   `ByteReader` and the table records from your `FontParser`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
