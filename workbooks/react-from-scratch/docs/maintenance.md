# Keeping the workbook current

The tests are only as good as the React they came from. Last verified on 1 November 2026 against React 19.3.1, react-dom 19.3.1, jsdom 30.1.3 and Node 26.13 (the LTS line; Node 24 is the previous one). `tools/oracle/package.json` pins the versions, and `docs/react-today.md`, the README and the `site` block of `workbook.json` repeat them. When one moves, follow this list.

1. Find out what is current: `npm view react version`, `npm view jsdom version engines`, and for the newest LTS the release index at https://nodejs.org/dist/index.json.
2. In `tools/oracle/`, set the exact versions in `package.json`, run `npm install`, then `node selftest.mjs`. A failing self-test means the harness or the oracle needs a fix before anything else.
3. Regenerate every test set with `py -P tools/gen_p01.py` ... `py -P tools/gen_p12.py` and then read `git diff tests/`. A changed expected output means React behaves differently now, or the oracle drifted. Understand each change before accepting it. If React did change, update the page's requirement and `docs/react-today.md`.
4. Run `.\check NN -Ref` for every assignment, plus the fuzz cases with a few fresh seeds (`-Fresh`). Run the whole suite on the new Node as well.
5. Rebuild the book (`py -P tools/build_book.py --all`) and the site.
6. Update the version statements in this file, `docs/react-today.md`, the README, `package.json` `engines` in the project skeleton, `site.requires` in `workbook.json` and the Node minimum in `tools/langs.py`.

Nothing here runs by itself. If someone wants it, a scheduled workflow that opens an issue when `react` passes the pinned version would be a small addition.
