#pragma once
// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The `loca` table: where each glyph's record is in the file and how many bytes it
//   takes, by glyph id. Assignment 09 uses it to find the parts of a compound glyph, and
//   assignment 18 to find the glyph of every character.
//
// Your job:
//   Declare a glyph location (an offset from the start of the file and a length in bytes)
//   and a function that reads the location of every glyph, given your `ByteReader` and the
//   table records from your `FontParser`. Have its result also carry `numGlyphs` and
//   whether `loca` uses the short or long format, since the first output line needs both.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
