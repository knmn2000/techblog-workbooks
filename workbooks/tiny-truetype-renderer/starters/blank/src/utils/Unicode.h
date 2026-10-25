#pragma once
// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   UTF-8 in, Unicode code points out: those are the numbers a font's cmap maps to glyphs.
//   Your `TextRenderer` decodes each line of text with it.
//
// Your job:
//   Write a function that decodes a string of UTF-8 bytes into a list of code points, for
//   characters of 1 to 4 bytes (Output, step 1, lists the byte patterns). It is short
//   enough to write in the header itself.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
