// Reference solution - checkpoint 14 (fill a glyph, even-odd rule).
// SPOILERS: try the checkpoint yourself first. The work is in common/fill.h.

#define CANVAS_PNG_IMPLEMENTATION
#include "common/scene.h"

int main(int argc, char** argv) { return fill::run(argc, argv, fill::Rule::EvenOdd); }
