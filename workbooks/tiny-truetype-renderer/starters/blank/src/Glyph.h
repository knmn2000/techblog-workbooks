#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A glyph as the glyf table stores it: whether it is empty, simple or compound, its
//   contour count, its bounding box and, for a simple glyph, its outline. Your
//   `GlyphParser` returns it, and assignment 09 uses its kind to tell simple glyphs from
//   compound ones.
//
// Your job:
//   Declare a glyph type that records which of the three kinds it is (empty, simple or
//   compound) and holds `numberOfContours`, the bounding box (`xMin`, `yMin`, `xMax`,
//   `yMax`) and, for a simple glyph, its outline in the form from `GlyphComponent.h`.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
