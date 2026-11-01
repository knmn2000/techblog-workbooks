# didact

A small React: elements, a work loop over fibers, reconciliation by position and by key,
function components, `useState` and `useEffect`, and a todo app that runs on it. You write it
one assignment at a time in the workbook "Build React yourself", following Rodrigo Pombo's post
[Build your own React](https://pomb.us/build-your-own-react/) and Wim Jongeneel's post
[Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d).

## Run it

You need Node.js 26 or newer. There is nothing to install and nothing to build: the project is
plain ES modules.

The todo app from the last assignment runs in a browser. Browsers refuse ES modules from `file://`,
so serve this folder over HTTP from a terminal in it:

```
py -m http.server 8000      # python3 -m http.server 8000 on macOS and Linux
```

Then open http://localhost:8000/.

## How it's organised

| Where | What |
|---|---|
| `src/didact/` | The library: `createElement`, DOM nodes and props, the fiber work loop, commit, reconciliation, hooks |
| `src/app/` | The todo app, written against your library |
| `src/main.js` | Mounts the todo app in `index.html` |
| `harness/` | Given to you, not part of your code: a tiny DOM and the scenario runner the checker's tests use |
| `assignments/` | One small program per assignment, which the workbook's checker runs on that assignment's test cases |
