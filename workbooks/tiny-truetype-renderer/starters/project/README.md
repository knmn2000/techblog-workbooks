# tiny_ttf

A tiny TrueType font renderer in C++, written from scratch. It reads a `.ttf` file, decodes the
glyph outlines, fills them and saves a line of text as a PNG:

```
tiny_ttf <font.ttf> "<text>" <out.png> [pixel-height]
```

Built step by step with the Tiny TrueType Workbook, following Yohei Yamasaki's post
[Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/).

## Build and run

Needs CMake 3.20 or newer and a C++20 compiler.

```
cmake -S . -B build
cmake --build build
./build/tiny_ttf path/to/font.ttf "Hello, TrueType!" hello.png
```

## How it's organised

| Where | What |
|---|---|
| `src/font/` | Reading the font: bytes, the table directory, the character map, glyph locations, metrics, glyph outlines and compound glyphs |
| `src/render/` | Drawing glyphs: outlines, and filling them by the even-odd and non-zero rules |
| `src/utils/` | Geometry (lerp, Bezier curves, intersections) and UTF-8 decoding |
| `src/FrameBufferCanvas.*` | The picture in memory, and PNG output |
| `src/Glyph.h`, `src/GlyphComponent.h` | The glyph types |
| `src/TextRenderer.*`, `src/main.cpp` | Putting it together: a line of text |
| `checkpoints/` | One small program per step, each checking that step against test cases |
| `third_party/` | [stb_image_write](https://github.com/nothings/stb) for writing PNG files (public domain) |
