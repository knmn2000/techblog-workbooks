// ======================================================================================
// Assignment 13: Intersect a line and a quadratic curve
// Problem: problems/13-line-curve-intersection.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 13, as
//   `build/solutions/assignment_13.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 13`, or Run and Submit in the book.
//
// Your job:
//   Read each line as the curve's three points p1, p2 and p3 (start, control point, end),
//   then the word `line` and the line's two points l1 and l2. Call your line-curve
//   function from `utils/Geometry.h` and write the points it returns on one line (`x1 y1`
//   or `x1 y1 x2 y2`), or `none` when there are none.
//
// The other files of this assignment:
//   It adds to src/utils/Geometry.h, which you started earlier: Add a function that takes
//   a quadratic curve (start, control point, end) and two points on an infinite line, and
//   returns the points where they meet: none, one or two, in increasing t. A dot product
//   helper and a helper that solves a t^2 + b t + c = 0, the linear case a = 0 included,
//   belong here too. The Boilerplate's `Geometry.h` from assignment 10 already declares
//   the function as `segmentQuadBezierIntersect`.
//   Include them by their path under src/, e.g. #include "utils/Geometry.h".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
