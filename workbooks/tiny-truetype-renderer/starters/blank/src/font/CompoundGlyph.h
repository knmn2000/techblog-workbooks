#pragma once
// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Turning any glyph into the simple outlines it is drawn with: a compound glyph's
//   components are read, moved, scaled or rotated, and resolved however deeply they nest.
//   Assignment 18 draws every character of a line of text through it, so it never has to
//   tell simple glyphs from compound ones.
//
// Your job:
//   Declare a function that takes a glyph id, the font (through your `ByteReader`) and
//   where every glyph's record is (offset and length, like the locations from your
//   `Loca.h`), and returns a list of outlines in the form from `GlyphComponent.h`, one per
//   simple part.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
