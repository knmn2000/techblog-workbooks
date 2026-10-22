// ======================================================================================
// Assignment 13: Intersect a line and a quadratic curve
// Problem: problems/13-line-curve-intersection.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 13 as `build/solutions/assignment_13
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 13` (`./check.sh 13` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   Read each line as the curve's three points p1, p2 and p3 (start, control point, end),
//   then the word `line` and the line's two points l1 and l2. Call your line-curve
//   function from `utils/Geometry.h` and write the points it returns on one line (`x1 y1`
//   or `x1 y1 x2 y2`), or `none` if it returns no points.
//
// The other files of this assignment:
//   It adds to src/utils/Geometry.h, which you started earlier: Add a function that takes
//   a quadratic curve (start, control point, end) and two points on an infinite line, and
//   returns the points where they meet, in increasing t. There can be none, one or two.
//   Put a dot product helper here too, and a helper that solves a t^2 + b t + c = 0,
//   including the linear case a = 0. The Boilerplate's `Geometry.h` from assignment 10
//   already declares the function as `segmentQuadBezierIntersect`.
//   Include them by their path under src/, e.g. #include "utils/Geometry.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
