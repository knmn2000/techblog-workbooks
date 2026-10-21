#pragma once
// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This code turns any glyph into the simple outlines you draw it with. It reads a
//   compound glyph's components, moves, scales or rotates each one, and resolves
//   components nested at any depth. In assignment 18 you draw every character of a line of
//   text through it, so your text renderer doesn't need to tell simple glyphs from
//   compound ones.
//
// Your job:
//   Declare a function that takes a glyph id, the font (through your `ByteReader`) and
//   where every glyph's record is (offset and length, like the locations from your
//   `Loca.h`), and returns a list of outlines in the form from `GlyphComponent.h`, one per
//   simple part.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
