# Tools and the checker

Installs, terminal commands and how the checker behaves, with commands for Windows, macOS and Linux.

## Install and check Node.js 26
<!--
id: node-install
also: nodejs; node.js; npm; node version; winget; brew; fnm; nvm; LTS; node --version; command not found
-->
Node.js runs JavaScript outside a browser: your library, the harness, every test. This workbook needs version 26 or newer. The checker looks for `node` on your PATH, reads its version and, if that is too old, tells you how to get a newer one.

```
# Windows
winget install OpenJS.NodeJS.LTS

# macOS, with Homebrew
brew install node

# Linux: distribution packages such as apt's nodejs are often older than 26,
# so use fnm, the route nodejs.org itself suggests
curl -o- https://fnm.vercel.app/install | bash
fnm install 26
```

The download page also has plain installers and binaries if you'd rather use one. Open a new terminal afterwards: one that was already open doesn't see the changed PATH. Then check:

```
node --version
```

You want `v26.` and two more numbers, or a higher major version. Seeing an older number means another Node sits earlier on your PATH; `where node` on Windows or `which -a node` elsewhere lists them in order. npm comes with Node and matters once, when you run `npm install` inside `tools/oracle` before your first `-Fresh` check.

`.\check 01` already starts `node` on one of your files. Install it first.

Learn more:
- [Node.js: Download](https://nodejs.org/en/download)
- [fnm on GitHub](https://github.com/Schniz/fnm)
- [Homebrew: node](https://formulae.brew.sh/formula/node)

## `process.argv`, exit codes and `node --check`
<!--
id: node-process
also: command line arguments; argv; exit code; exitCode; process.exit; syntax check; node -c; stderr; stdout; console.log; LASTEXITCODE
code: \bprocess\.argv\b
-->
Start a program with `node program.js one two` and it receives two arguments. Inside it, `process.argv` is an array: element 0 is the path of the node executable, element 1 the path of the script, and your arguments begin at index 2.

```js
// args.js, run as: node args.js one two
console.log(process.argv.slice(2));   // [ 'one', 'two' ]
```

Every program in `assignments/` reads its input path from `process.argv[2]` and writes its output to the path in `process.argv[3]`. That's how the checker starts it, once per test, from assignment 01 on.

A finished process leaves a number behind: its exit code. 0 means success. An uncaught error gives 1, and the harness uses 99 for `not implemented`. The checker reads them this way: 0 moves on to comparing the output file, 99 becomes "Not implemented yet", anything else is a Runtime Error. To see the code of the last command, type `echo $?` in a macOS or Linux shell, `$LASTEXITCODE` in PowerShell or `%ERRORLEVEL%` in cmd.

`node --check file.js` parses a file and reports a syntax error without running anything, and prints nothing when the file is fine. The checker's build step runs it over every `.js` file of your project before any test starts. That is why a typo in an unrelated file turns up as a Compile Error with its file and line.

```
node --check src/didact/dom.js
```

Learn more:
- [Node.js: process.argv and process exit codes](https://nodejs.org/api/process.html)
- [Node.js: command-line options (--check)](https://nodejs.org/api/cli.html)

## The checker: `check`, `-Case`, `-Fresh`, `-Dispute`
<!--
id: workbook-check
also: check; .\check; check.sh; verdict; Accepted; Wrong Answer; Compile Error; Runtime Error; Time Limit Exceeded; not implemented yet; fresh tests; dispute; case; run tests; printed by your program
-->
`.\check NN` (`./check.sh NN` on macOS and Linux) tells you whether assignment NN works. It runs the syntax check over your project, starts the assignment's program on every test in `tests/NN/`, and compares the lines it writes with the expected ones word by word. Line endings and extra spaces don't matter outside quoted strings.

```
.\check 07                           every test of assignment 7
.\check 07 -Case <test-id>           one test in full: input, expected output, yours
.\check 07 -Fresh                    a newly generated set of tests (a new random seed)
.\check 07 -Dispute <test-id> "why"  set a test aside
```

The report groups tests by requirement (`R1`, `R2`, and so on). Each failing group lists its first failures, with a guess at the requirement behind them, the source of the expected value and a command that reproduces the test.

Accepted means every test passed. Wrong Answer means the program ran and wrote something different. A syntax error in any file of the project, found by `node --check`, gives Compile Error, and a crash or non-zero exit gives Runtime Error. Time Limit Exceeded comes after 10 seconds on one test, which an endless loop will earn you. "Not implemented yet" means the run hit a `throw` stub you haven't replaced.

Debug with `console.log`. What your program prints stays out of the comparison; `-Case` lists it under "printed by your program" and the book shows it under the test result.

`-Fresh` gives you tests you haven't seen, which catches code that only works for the examples. Most assignments draw their expected output from React, so run `npm install` once in `tools/oracle` first (see [where the expected output comes from](#primer/workbook-oracle)). `-Dispute` stops one test from counting, adds `(1 disputed)` to the verdict and writes your reason to `disputes.json`. After that, ask your coding assistant to "review my disputes", and it rechecks the expected value against its independent source.

Learn more:
- [Node.js: process exit codes](https://nodejs.org/api/process.html)
- [Node.js: command-line options (--check)](https://nodejs.org/api/cli.html)

## The harness and scenario files
<!--
id: workbook-harness
also: runScenarioFile; scenario; scenario file; env.js; minidom; dump; markup; catalog; test harness; fake DOM; ops; idle; flush
code: \brunScenarioFile\b
-->
Return values alone can't test a DOM library. The tests need a document to draw in, idle time to hand out and a way to say "click that button". The harness in `solutions/harness/` supplies them. You never edit it. It holds a small DOM that also counts what your code does to it (`minidom.js`), a scheduler the tests control (`env.js`), a printer that turns a tree into text, a short syntax for writing trees, the function components the tests use, and the runner (`scenario.js`).

A test input is a scenario, one command per line, with `#` for comments.

```
# a button and some text: draw, click, print
tree t <div id="a"><button id=go onClick=@bump>+</button>hello</div>
render t
flush
click #go
dump
log
```

The program writes out whatever the printing commands ask for:

```
dump 1
node 0 a div "id=a"
node 1 b button "id=go"
text 2 "+"
text 1 "hello"
log bump
```

Each program in `assignments/` is one call, `runScenarioFile(inputPath, outputPath, lib)`. It runs the scenario against `lib` (the functions, or the `Didact` object, under test) and writes the printed lines to the output file for the checker to compare. From assignment 04 the program's first import is `../harness/env.js`, which installs `document` and a `requestIdleCallback`. Your library calls that function as it loads, and Node doesn't have one, which makes the import order matter.

| Command | What it does | Prints |
|---|---|---|
| `call`, `props`, `show` | 01: call `createElement`, keep a props object, show it again | `element`, `props` |
| `create`, `update` | 02: make one node, update it | nothing |
| `tree`, `render`, `flush` | name a tree, draw it, run all pending work | nothing |
| `idle k` | one idle period of `k` units of work | `idle <units>` |
| `click`, `type`, `submit`, `poke` | send an event or a state change, then `flush` | nothing |
| `dump`, `ops`, `log` | show the container, the DOM operation counts, the recorded handler and effect calls | `dump n` and the tree, `ops` numbers, `log` lines |

A dump line is `node <depth> <label> <tag> "<props>"` or `text <depth> "<text>"`. An element gets a label (`a`, `b`, ... `z`, `aa`) the first time a dump shows it and keeps it. The same label in two dumps means the same DOM node, and that's how a test can tell that you kept a node rather than rebuilt it. `harness/README.md` lists the remaining choices, such as what `type` does with spaces.

Learn more:
- [MDN: import, for side-effect imports](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import)
- [MDN: requestIdleCallback()](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)

## Where the expected output comes from (React 19 on jsdom)
<!--
id: workbook-oracle
also: oracle; expected output; jsdom; React 19; independent source; reference solution; fresh tests; npm install; test generator; act
-->
Every test is a scenario plus the lines a correct program must print for it. Those lines don't come from the author's solution, since a solution can only prove its author agrees with themselves. They come from an oracle: a small program in `tools/oracle/` that runs the same scenario on real React 19.3.1 on jsdom 30.1.3, an implementation of the browser's DOM written in JavaScript that runs under Node. Renders and clicks run inside React's `act`, the test helper that applies pending updates before anyone looks. The oracle reuses the harness's own markup, components and dump format. The only difference between the two runs is what sits underneath, React in one and your library in the other. Where React's behaviour is the specification, as with the order effects run in (assignment 11), the tests pin what version 19.3.1 does.

React can't answer two questions: how many units of work an idle period gets through, and how many DOM calls your library made. Small independent models in the test generators answer them, a formula over the number of fibers for the first and counting by definition for the second. Assignments 01 and 02 test functions React doesn't expose in that form. There the generators work out the expected values by hand and cross-check them against React where the two overlap. The reference solution is never a source. It has to pass these tests, and it doesn't define them.

The tests in `tests/` ship with the workbook, generated once, which is why `.\check NN` needs no React on your machine. Only `-Fresh` runs the oracle. Install it once:

```
cd tools/oracle
npm install
```

That fetches the exact versions pinned in `package-lock.json`, and needs Node 26.

Learn more:
- [React: act](https://react.dev/reference/react/act)
- [React: createRoot](https://react.dev/reference/react-dom/client/createRoot)
- [jsdom on GitHub](https://github.com/jsdom/jsdom)

## `py -P` and Python 3.11 for the tools
<!--
id: python-launcher
also: python; python3; py launcher; PYTHONSAFEPATH; python --version; Microsoft Store python; python not found
-->
Your project is JavaScript, but the checker, the test generators and the study script that serves the book are Python programs. They need Python 3.11 or newer. On Windows, start Python with `py`, the launcher the Python installer adds; on macOS and Linux the command is `python3`. Windows also has a `python` shortcut that opens the Microsoft Store when Python is missing, which is why you type `py`.

The tools run as `py -P tools/check.py`. The `-P` switch, new in Python 3.11, keeps Python from putting the script's own folder first on its import path, so a file called `random.py` or `json.py` lying next to a script can't take the place of the standard library module of that name. `.\check` and `./check.sh` pass it for you; you type it yourself only when a page tells you to, as in `py -P tools/check.py 01`.

```
# Windows
winget install Python.Python.3.12

# macOS, with Homebrew
brew install python3

# Debian and Ubuntu
sudo apt install python3
```

Check it from a new terminal:

```
py --version         # Windows
python3 --version    # macOS and Linux
```

You need 3.11 or higher. If a Linux distribution's `python3` is older, get a newer one from python.org or from a repository your distribution offers for it.

It bites at assignment 01: `.\check 01` is a Python script.

Learn more:
- [Python: command line and environment (the -P option)](https://docs.python.org/3/using/cmdline.html)
- [Python: using Python on Windows](https://docs.python.org/3/using/windows.html)
- [Python: Downloads](https://www.python.org/downloads/)

## Serving `index.html` locally
<!--
id: static-server
also: http.server; local web server; file://; CORS; localhost; port 8000; ES modules in the browser; live server; blank page
-->
Assignment 12 ends with a page: `index.html` loads `src/main.js` through `<script type="module">`. Double-click `index.html` and it opens under a `file://` address, where a browser refuses to load modules. It treats each local file as cross-origin; the console shows a CORS error and the page stays empty. Serve the folder over HTTP instead. From `solutions/`, run:

```
py -m http.server 8000         # python3 -m http.server 8000 on macOS and Linux
```

Then open http://localhost:8000/ in a browser and stop the server with Ctrl+C when you're finished. Port 8000 is the default; give another number if something else is using it. From the workbook folder, `py -m http.server 8000 --directory solutions` does the same job.

By default `http.server` listens on every network interface of your computer; add `--bind 127.0.0.1` to keep it to yourself. Files go out as they are on disk, so there is no live reload: save, then refresh. Errors from your modules land in the browser's developer tools (F12), under Console.

Nothing else needs installing. There is no build step, because the browser reads your modules as they are. The tests for 12 don't open a browser; they run the same app on the harness's DOM. The page is there for watching the thing work.

Learn more:
- [Python: http.server](https://docs.python.org/3/library/http.server.html)
- [MDN: JavaScript modules (testing locally)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [MDN: Set up a local testing server](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Tools_and_setup/set_up_a_local_testing_server)
