# Keeping the workbook current

The tests are only as good as the React they were generated from. This workbook was last verified on 1 November 2026 against
React 19.3.1, react-dom 19.3.1, jsdom 30.1.3 and Node 26.13 (the LTS line, with Node 24 as the previous one). The versions are pinned
in `tools/oracle/package.json`, and `docs/react-today.md`, the README and the `site` block of `workbook.json` repeat them. When one of them
moves, go through this list.

1. Look up what is current: `npm view react version`, `npm view jsdom version engines`, and the release index at
   https://nodejs.org/dist/index.json for the newest LTS.
2. In `tools/oracle/`, change the exact versions in `package.json`, run `npm install`, and run
   `node selftest.mjs`. If the self-test fails, the harness or the oracle needs a fix before anything else.
3. Regenerate every test set: `py -P tools/gen_p01.py` ... `py -P tools/gen_p12.py`, then look at `git diff tests/`.
   A changed expected output means React behaves differently now (or the oracle drifted). Understand each one before accepting it, and update
   the page's requirement and `docs/react-today.md` if React really changed.
4. Run `.\check NN -Ref` for every assignment, and the fuzz cases with a few fresh seeds (`-Fresh`). Run the whole suite on the new Node too.
5. Rebuild the book (`py -P tools/build_book.py --all`) and the site.
6. Update the version statements: this file, `docs/react-today.md`, the README, `package.json` `engines` in the project skeleton,
   `site.requires` in `workbook.json` and the Node minimum in `tools/langs.py`.

Nothing here runs by itself. A scheduled workflow that opens an issue when `react` passes the pinned version would be a small addition
if someone wants one.
