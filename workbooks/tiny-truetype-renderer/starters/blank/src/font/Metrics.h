#pragma once
// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Ascent and descent from `hhea`, and each glyph's advance width and left side bearing
//   from `hmtx`; this header is the reader for both. In assignment 18 the pen moves by
//   advance widths and the text is sized from the ascent and descent.
//
// Your job:
//   Declare the metrics of one glyph (advance width and left side bearing) and a function
//   that reads the font's ascent and descent and the metrics of every glyph id, taking
//   your `ByteReader` and the table records from your `FontParser`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
