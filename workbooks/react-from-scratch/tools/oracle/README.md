# The React oracle

Runs a scenario file against **real React 19.3.1** (`react-dom` 19.3.1) on **jsdom 30.1.3** and prints the lines
the harness prints for the same commands. Test generators use it to get expected output; the workbook's
`useEffect` assignment pins its spec to what it observed (`_source/react-observed.md`).

Needs Node 26 (jsdom 30 needs Node 22.22 or newer). Install once, inside this folder (the versions are exact
and locked in `package-lock.json`; `node_modules/` is not committed):

```
cd tools/oracle
npm install
```

## Run it

```
node tools/oracle/run.mjs [--todo] <scenario-file>          prints the expected lines to stdout
node tools/oracle/selftest.mjs                              checks the harness and the oracle (about 2 seconds)
```

From Node code (a generator can call it directly):

```js
import { runOracle, closeOracle } from "./tools/oracle/run.mjs";
const lines = await runOracle(scenarioText, { todo: false, warnings: [] });
await closeOracle();                                         // lets the process end promptly
```

`runOracle` calls are serialised internally, so `Promise.all` is safe. `options.warnings` (an array) collects
React's `console.error` output instead of printing it; React warnings usually mean the scenario does something
a test should avoid (duplicate keys, a `value` prop without a handler, ...). Errors carry `err.scenarioLine`.

## What it does

- Reuses the harness: the scenario parser and command list, the markup, the catalog (with `lib = React`) and the
  dump labeler. Only the backend is different: `render` is `root.render(...)` inside `act`, `click`, `type`,
  `submit` and `poke` run inside `act`, the DOM is a jsdom `<div id="root">` in a fresh page for every run.
- `type` uses the native value setter and then dispatches a bubbling `input` event, as a user would.
- `<TodoApp/>` in a scenario (or `--todo`) registers `todoApp.mjs` as `components.TodoApp`: the todo application of
  assignment 12 written with real React. Its stored text is the trimmed draft.

## Placeholders and refusals

React cannot answer these, so the caller fills them in:

| Command | The oracle prints |
|---|---|
| `idle <k>` | `idle ?` |
| `ops ...` | `ops ?` |
| `call`, `props`, `show`, `create`, `update` | nothing: it throws "this runner does not support it" |

## Things to avoid in scenarios (React does something a library built from the posts will not)

See `_source/react-observed.md` for the list with evidence. The short version: do not click a disabled element
that has a handler; do not use `onChange` (React fires it on `input`); do not give an input a `value` and then
`type` into it; do not repeat a key.
