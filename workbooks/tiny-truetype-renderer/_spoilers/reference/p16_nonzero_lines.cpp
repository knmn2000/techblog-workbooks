// Reference solution - checkpoint 16 (fill a polygon, non-zero rule).
// SPOILERS: try the checkpoint yourself first. The work is in common/fill.h.

#define CANVAS_PNG_IMPLEMENTATION
#include "common/scene.h"

int main(int argc, char** argv) { return fill::run(argc, argv, fill::Rule::NonZero); }
