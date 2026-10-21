#pragma once
// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Turning UTF-8 text into Unicode code points, the numbers a font's cmap is keyed by.
//   Your `TextRenderer` decodes every line of text with it.
//
// Your job:
//   Provide a function that decodes a string of UTF-8 bytes into a list of code points,
//   for characters of 1 to 4 bytes (the byte patterns are under Output, step 1). It is
//   small enough to live entirely in the header.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
