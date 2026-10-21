#pragma once
// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The `hhea` and `hmtx` tables: the font's ascent and descent, and each glyph's advance
//   width and left side bearing. Later, assignment 18 moves the pen by each glyph's
//   advance width and sizes the text from the ascent and descent.
//
// Your job:
//   Declare the metrics of one glyph (advance width and left side bearing) and a function
//   that reads the font's ascent and descent and the metrics of every glyph id, given your
//   `ByteReader` and the table records from your `FontParser`.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
