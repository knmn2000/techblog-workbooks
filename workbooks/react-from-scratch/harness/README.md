# The test harness

Plain ES modules, no dependencies, Node 26. Every assignment program is a few lines that hand your library
to `runScenarioFile`:

```js
import "../harness/env.js";                          // FIRST: installs `document` and requestIdleCallback
import { createElement } from "./didact/createElement.js";
import { runScenarioFile } from "../harness/scenario.js";

await runScenarioFile(process.argv[2], process.argv[3], { createElement });
```

`env.js` has to come before your library, because a library may call `requestIdleCallback` while it is
being imported. `runScenarioFile(input, output, lib)` reads a scenario, runs its commands against `lib`,
and writes the output lines. An error whose message starts with `not implemented` ends with exit code 99
and no output file (that is how the starters say "not yet"); any other error prints its message and stack
and ends with exit code 1, also without an output file.

## Choices made where the design was silent

Anyone who writes scenarios or a second implementation needs these.

Scenario language
- Comment lines start with `#` (after optional leading blanks). Commands are matched by their first word.
- `type <#id> <text>`: the text is everything after the single space that follows the id; its other spaces,
  also trailing ones, are kept. `type #id` alone types the empty string.
- The `#` of `click #id`, `type #id ...` and `submit #id` is optional. `idle` takes a whole number or `inf`.
- `call <type> <props> [child ...]`: `<type>` is a bare word or a JSON string; `<props>` is JSON (it may
  contain spaces), `null`, or `@name`; a child is any JSON value or `$k`. `props <name> <json>` takes the rest
  of the line as JSON.
- `create` and `update` read props like markup attributes (`name=value`, `name="a b"`, `name='a "b"'`, a bare
  `name` means true, `@h` is a handler). Values are strings. The element handed to `createDom` and the
  props handed to `updateDom` always contain `children: []`, so `children` must be skipped by the library.
- `dump` prints the node made by `create` while there is one (a later `render` forgets it), otherwise the
  container. `click #id` can find a `create`d node by its id although it is not in the document.
- `poke` throws if no `Keeper` has rendered yet. `ops` throws on an unknown counter name.
- `ops` is measured from the start of the scenario; the start resets the statistics.

Markup
- Quotes are `"` or `'`, with no escapes and no character entities (use the other quote for a quote).
- `<input>`, `<br>`, `<hr>` and `<img>` need no closing tag. A lone space between tags is dropped, so a text
  node that is only whitespace cannot be written; `Greeting` produces `"Hi "` for tests of text with spaces.
- An element without attributes is built with props `null`.

Dump
- A prop value is percent-encoded (the whole value, `encodeURIComponent`) when it contains whitespace of
  any kind, a double quote or `%`. The design names the space; tabs and line breaks are included so a line
  can never be split.
- `disabled` and `value` are only shown for the tags the design names (button, input, textarea / input,
  textarea). Numbers print as text. Text: `%`, `"`, `\r` and `\n` are encoded, spaces stay.

minidom
- Events reach listeners added with `addEventListener` only: there are no `onclick` handler properties and no
  check for disabled controls. The one default action that exists is the browser's own for a click: a click that
  is not prevented, on an enabled submit button (`<button>` without `type`, or `type=submit`) inside a form,
  dispatches a bubbling, cancelable `submit` on that form. This happens in the `click` command, not in minidom.
- A node's `parentNode`, `tagName`, `childNodes` and the like cannot be assigned (TypeError). Assigning
  `nodeValue` to an element does nothing, like a browser. `textContent` works on elements (one text node).
- There is no `setAttribute`, `style` or `innerHTML`.
- `addListener` and `removeListener` count calls: adding the same function twice is ignored by the DOM but
  counted; removing something that is not registered is counted. `remove` counts one only when the node had
  a parent. A call that throws counts nothing. `replaceChild` counts one `remove` plus one `insert`/`move`.
- `idle(budget)`: `timeRemaining()` returns 0 on call number `budget` and on every later call.
- `click` and `submit` events are cancelable, `input` events are not; all of them bubble.

Catalog (details the design left open)
- `Toggle`: `<div id="t">` (off) or `<section id="t" className="on">` (on), each holding
  `<button id="t-btn">toggle</button>` and `<span id="t-state">off|on</span>`.
- `LoggerEvery`: `<div><em>{name}:{count}</em><button id="{name}-btn">bump</button></div>`;
  `LoggerDeps`: `<em>{name}:{dep}</em>`. Buttons of `Counter` and `MultiCounter` are labelled `+`, `a`, `b`.
- `Counter` with `id="d"` calls its setter twice per click (two queued updaters in one handler).

## The modules

| File | What it is for |
|---|---|
| `minidom.js` | the DOM your code draws into; also counts creates, inserts, moves, removes, property writes, listener adds and removes |
| `env.js` | installs `document` and a controllable `requestIdleCallback`; exports `container`, `stats()`, `resetStats()`, `idle(budget)`, `flush()` |
| `dump.js` | `makeLabeler`, `dumpTree`, `dumpNode`: the text form of a DOM tree that tests compare |
| `markup.js` | `parseMarkup`, `buildElement`, the harness's own `h`, the `@handler` functions |
| `scenario.js` | `parseScenario`, `runScenario`, `runScenarioFile`, `runCommands` and the command table |
| `catalog.js` | `makeCatalog(lib, log)`: the function components scenarios can use |

`minidom` is meant to be read. Its comments say how the counting works (every node is a Proxy; the node's own
bookkeeping is kept out of it, so only writes from outside code count).

## Reading a dump

```
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

A label is given to an element the first time a dump shows it (a, b, ... z, aa, ab, ...) and never changes, so
two dumps that show the same label show the same DOM node: that is how a test checks that your library
kept a node instead of rebuilding it. Text nodes have no label; neighbouring text nodes print as one line.

## Scenario commands

| Command | Prints |
|---|---|
| `call <type> <props> [child ...]`, `props <name> <json>`, `show <name>` | `element <k> <json>`, `props <name> <json>` |
| `create <tag\|text> [prop ...]`, `update [prop ...]` | nothing |
| `tree <name> <markup>`, `render <name>`, `flush` | nothing |
| `idle <k>` | `idle <units>` |
| `click <#id>`, `type <#id> <text>`, `submit <#id>`, `poke` | nothing (each ends with a `flush`) |
| `dump` | `dump <n>`, the tree lines, `title "<text>"` if `document.title` is not empty |
| `ops [name ...]` | `ops <numbers>` (resets the counters) |
| `log` | one `log <text>` line per handler or effect call since the last `log` |

The React oracle in `tools/oracle` runs the same scenarios on real React and prints the same kind of lines.
