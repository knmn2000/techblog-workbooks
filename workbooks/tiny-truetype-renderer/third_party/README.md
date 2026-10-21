# Third-party code

Bundled so the workbook builds without downloads. It isn't covered by the Apache-2.0 licence of
the rest of this repository.

| Folder | Library | Licence |
|---|---|---|
| `stb/` | [stb_image_write.h](https://github.com/nothings/stb) | Public domain or MIT, your choice (at the end of the header) |

Setting up your project copies `stb_image_write.h` into its own `third_party/`, so the project
builds on its own.
