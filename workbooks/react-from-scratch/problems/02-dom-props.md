# 02 · DOM nodes and props

**Difficulty:** Medium · **Assignment** 2 of 12 · **Check:** `.\check 02`

**Tags**
- *Language:* [closures](#primer/js-functions-closures) · [Object.keys, entries and in](#primer/js-object-keys) · [=== and falsy values](#primer/js-equality) · [string methods](#primer/js-string-methods)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [the DOM tree](#primer/dom-tree) · [createElement and createTextNode](#primer/dom-create) · [properties and attributes](#primer/dom-properties) · [listeners, event types and bubbling](#primer/dom-events)

## Read in the blog first

You do not need the post for this one. If you want Pombo's account anyway, there are two stretches. In [Step II](https://pomb.us/build-your-own-react/#step-ii-the-render-function), the paragraphs that make a text node for a text element, then the ones that [assign the props](https://pomb.us/build-your-own-react/#:~:text=The%20last%20thing%20we%20need%20to%20do%20here). In Step VI, from [One special kind of prop](https://pomb.us/build-your-own-react/#:~:text=One%20special%20kind%20of%20prop) and the three paragraphs ahead of it, up to the link to the sandbox. The code in both is the author's version of what you are about to write.

## Learning material

- [Arrow functions and closures](#primer/js-functions-closures): the handlers in the scenarios are plain functions. A name always stands for the same function, and that is how an unchanged handler differs from a new one.
- [Object.keys, Object.entries, Object.hasOwn and in](#primer/js-object-keys): walking the names of a props object, and asking whether a name is still there.
- [===, Object.is, truthy and falsy](#primer/js-equality): `===` decides whether two values are the same prop. The empty string is falsy, which matters when you ask whether a prop was given.
- [String methods](#primer/js-string-methods): `onClick` to `click`.
- [The DOM tree: elements and text nodes](#primer/dom-tree): a text node has nothing of its own but its text.
- [createElement and createTextNode](#primer/dom-create): one call per kind of node.
- [Properties and attributes](#primer/dom-properties): assigning `id`, `className`, `title`, `value`, `disabled` and `nodeValue` as properties.
- [Listeners, event types and bubbling](#primer/dom-events): a listener belongs to an event type, and it comes off only when you pass the function that went on.

## Source material

- Rodrigo Pombo, [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function) and, in [Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation), the part on `updateDom` and event listeners
- MDN: [document.createElement](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement), [document.createTextNode](https://developer.mozilla.org/en-US/docs/Web/API/Document/createTextNode), [Node.nodeValue](https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeValue), [addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) and [removeEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener)
- Wim Jongeneel, [Rendering a virtual DOM](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.1%20Rendering%20a%20virtual%20DOM) and [Applying a diff to a HTML element](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.2%20Applying%20a%20diff%20to%20a%20HTML%20element), for a version that assigns props as properties
- The harness's own DOM, `harness/minidom.js`, which counts what your code does to it

## Where this fits

Elements from 01 only describe a page. Here Didact first touches a real node. The first render in 03 calls `createDom`, and once the library can compare two renders, the commit calls `updateDom` on a node it keeps. Your file is `src/didact/dom.js`.

## The problem

Write the two functions that put props on a DOM node. `createDom(element)` makes the node for an element, and `updateDom(dom, prevProps, nextProps)` moves a node from one set of props to the next, touching as little as it can. A scenario creates a node, updates it, clicks it, then prints the node's state along with a count of what your code did to it.

### The module

`src/didact/dom.js` exports:

| Export | Meaning |
|---|---|
| `createDom(element)` | `element` is `{ type, props }`. Returns a new node that is not attached to anything: a text node when `type` is `"TEXT_ELEMENT"`, otherwise an element whose tag is `type`. The props are put on it as in `updateDom(dom, {}, element.props)`. |
| `updateDom(dom, prevProps, nextProps)` | Changes `dom` so that it reflects `nextProps`, given that it reflects `prevProps` already. Returns nothing. |

Both reach the DOM through the global `document`. The harness installs it before calling your functions, but possibly after your module has loaded, so read `document` inside the functions and leave the top of the file alone.

### Input

Each test is `node assignments/assignment_02_dom_props.js <input-file> <output-file>`, run by the checker. The entry program is built like the one in 01 with a different library object: it imports `createDom` and `updateDom` from your `dom.js` and `runScenarioFile` from `../harness/scenario.js`, then awaits `runScenarioFile(process.argv[2], process.argv[3], { createDom, updateDom })`. The Boilerplate ships it finished. From scratch, write them first. The commands are:

| Line | What the harness does |
|---|---|
| `create <tag\|text> [prop ...]` | Calls `createDom({ type, props })`, with `text` standing for the type `TEXT_ELEMENT`, and keeps the node it returns. Any node kept earlier is dropped. |
| `update [prop ...]` | Calls `updateDom(node, prev, next)` on the kept node, where `prev` is the props of the last `create` or `update` and `next` is the props on this line. Then `next` becomes `prev`. |
| `click #<id>` | Dispatches a bubbling `click` on the kept node, which must have that id. The node is not in any document, and the harness finds it anyway. |
| `dump` | Prints the kept node. |
| `ops create write addListener removeListener` | Prints four counters, described under Output. |
| `log` | Prints the handler calls recorded since the last `log`. |

Props are written like attributes: `id=a`, `title="two words"`, `title='say "hi"'`. Every value is a string, a bare name such as `disabled` means `true`, and `onClick=@one` is a handler, where `@one` is a single function that records the word `one` in the log when it is called (every `@one` in a scenario is that same function). The props object that `create` and `update` hand you carries `children: []` next to the listed props.

### Output

`dump` prints `dump <n>`, where `n` counts the dumps, then one line for the kept node:

```
node 0 <label> <tag> "<props>"
text 0 "<text>"
```

A dump labels the first node it shows `a` and the next new one `b`, and so on; a node keeps its label from then on. `<tag>` is lower case. `<props>` lists the values that differ from the default for `className`, `disabled` (on `button`, `input` and `textarea`), `id`, `title` and `value` (on `input` and `textarea`). They come sorted by name and joined with single spaces, each as `name=value`, with `true` printed for a boolean. A value that contains whitespace, a double quote or `%` is percent-encoded (`encodeURIComponent`), so `two words` prints as `two%20words`. An element with nothing to list prints `""`. Props the dump has never heard of, `lang` for one, do not show. A text node prints its `nodeValue`, with `%`, `"` and line breaks encoded and spaces kept, and prints no line at all while its text is empty.

After `ops create write addListener removeListener` the output is one line, `ops <create> <write> <addListener> <removeListener>`, and the counters go back to 0. They measure what your code did to DOM objects since the previous `ops` or the start of the scenario:

| Counter | Counts |
|---|---|
| `create` | calls of `document.createElement` and `document.createTextNode` |
| `write` | assignments to a property of the node, `nodeValue` and made-up property names included |
| `addListener` | calls of `addEventListener`, whether or not they change anything |
| `removeListener` | calls of `removeEventListener`, the same |

Each run of a `@name` handler since the last `log` produces one `log <name>` line, in the order they ran.

### How props reach a node

Every name in `prevProps` or `nextProps` falls into one of four groups. It is new if only `nextProps` has it, gone if only `prevProps` has it, changed if both have it with values that are not `===`, and unchanged otherwise.

| Kind of name | Rule |
|---|---|
| `children` and `key` | Ignored, in every group. |
| starts with `on` | A handler. Its event type is the rest of the name in lower case (`onClick` listens to `click`). Not assigned as a property. |
| anything else | A property of the node: `dom[name] = value`. |

What each group costs, for a property and for a handler:

| Group | Property `name` | Handler `onX` with type `x` |
|---|---|---|
| new | `dom[name] = value` | `addEventListener(x, handler)` |
| changed | `dom[name] = value` | `removeEventListener(x, oldHandler)`, then `addEventListener(x, newHandler)` |
| gone | `dom[name] = ""`, which makes the node report its default again | `removeEventListener(x, oldHandler)` |
| unchanged | nothing | nothing |

A new value that happens to be falsy, `""` say, is still a value and gets written. A handler is unchanged when it is the same function, and the scenario's `@one` is the same function wherever it appears. The props are plain objects with their own names, so to tell that a name is gone, `name in nextProps` and `Object.hasOwn(nextProps, name)` both work.

A text element looks like `{ type: "TEXT_ELEMENT", props: { nodeValue, children: [] } }`. Create the text node empty and give it its text by writing `nodeValue`, as you would for any other property. That write is the node's only cost, which makes a text node one create and one write. Later changes to the text are updates of `nodeValue` under the same rules.

## Requirements

- **R1** `createDom` returns an element whose tag is the element's type.
- **R2** `children` and `key` are never assigned to the node, by `createDom` or by `updateDom`.
- **R3** A `TEXT_ELEMENT` becomes a text node holding its `nodeValue`, at a cost of one create and one write.
- **R4** Props are assigned as properties of the node, at creation and when new in an update.
- **R5** A prop whose name starts with `on` becomes a listener for the lower-cased rest of the name, and is not assigned as a property.
- **R6** `updateDom` writes only props that are new or whose value differs from before, falsy values included.
- **R7** A prop that is missing from `nextProps` is cleared with one write, and the node reports its default again.
- **R8** A changed handler loses its old listener and gets the new one, an unchanged handler is left alone, a removed handler is removed.
- **R9** `updateDom` on a text node writes a changed `nodeValue` and clears it when it is gone.
- **E2E** Longer sequences of `create`, `update`, `click` and `ops`.

## Examples

### Example 1: a text node (test `02-R3-text`)

```
input:
create text nodeValue=hello
dump
ops create write addListener removeListener

output:
dump 1
text 0 "hello"
ops 1 1 0 0
```

One prop in the scenario, and the counters read one create and one write. The create is the text node. The write is `nodeValue`, assigned once the node exists, like any other prop. Build the node with its text already inside and skip the assignment, and you get `ops 1 0 0 0`. That fails.

### Example 2: three props, then none of the two (test `02-R7-input`)

```
input:
create input id=i value=v disabled
dump
update id=i
dump
ops create write addListener removeListener

output:
dump 1
node 0 a input "disabled=true id=i value=v"
dump 2
node 0 a input "id=i"
ops 1 5 0 0
```

`ops` comes only at the end, so its counters add up both steps. Creation writes three props, `id`, `value` and `disabled`. The update leaves `id` alone and clears `value` and `disabled` with one write each: three plus two is five. The second dump shows both back at their defaults.

### Example 3: a handler swapped (test `02-R8-swap`)

```
input:
create button id=b onClick=@a
click #b
log
ops create write addListener removeListener
update id=b onClick=@b
ops create write addListener removeListener
click #b
log

output:
log a
ops 1 1 1 0
ops 0 0 1 1
log b
```

Creation writes `id` and adds a listener, which gives `1 1 1 0` on the first `ops`. The update changes only the handler. `id` is unchanged, and `@a` and `@b` are different functions, and the old listener comes off while the new one goes on: `0 0 1 1`. The second click then calls `b` and nothing else. With `a` still registered, the last `log` would print both.

## Constraints

Values are ASCII strings, with a leading `@` only on handlers, and the handler props are `onClick`, `onclick`, `onMouseDown` and `onInput`. `click` is only used on a node that has an id and, where it is meant to produce a log line, a click handler. No scenario passes `children` as a listed prop, and no name that starts with `on` gets a value other than a handler. A scenario has 40 lines at most. The 50 tests are each requirement's cases plus two long scripted sequences and six seeded random ones (`-Fresh` draws six new ones). Milliseconds is what a correct solution takes; the limit is 10 seconds per test.

## Hints

<details><summary>Hint 1: where to start</summary>

Start with `create div id=a` and a `dump`. Add an `update` with the same props and a second `ops`, and the right answer is four zeros. Every rule here comes down to which props earn a write and which listeners earn a call. `ops` shows you which.
</details>

<details><summary>Hint 2: the approach</summary>

Two small predicates help, one for "this name is a handler" and one for "this name is a property I should write", plus a function that turns `onClick` into `click`. Then make four passes over the two props objects: take off the handlers that are gone or changed, clear the properties that are gone, set the properties that are new or changed, and put on the handlers that are new or changed. After that `createDom` is little more than picking the node kind and calling `updateDom` with empty previous props.
</details>

<details><summary>Hint 3: the traps</summary>

- Gone and falsy are different things. A prop still in `nextProps` with the value `""` is not gone, and it gets written.
- Remove a listener with the function you added, which is the one in `prevProps`. The new function matches nothing.
- Remove the old listener before you add the new one, or the node listens twice.
- A handler is not a property. Assign it as `dom.onClick` too and `write` comes out one too high.
- Lower-case `onClick` to `click`, or nothing ever hears the click.
- Every props object you get has `children` in it. Skip it, and skip `key` as well.
- A text node gets its text through the same path as the other props, which is what makes it count as a write.
- A removed handler leaves no property behind, so there is no `""` to write for it.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
isEvent(name):     name starts with "on"
isProperty(name):  name is not "children", not "key", and not isEvent(name)
eventType(name):   lower-case the name and drop the first two letters

createDom(element):
    dom = a text node containing "" if element.type is "TEXT_ELEMENT", else an element with that tag
    updateDom(dom, {}, element.props)
    return dom

updateDom(dom, prevProps, nextProps):
    for each handler name in prevProps that is gone or has another function in nextProps:
        removeEventListener(eventType(name), prevProps[name])
    for each property name in prevProps that is not in nextProps:
        dom[name] = ""
    for each property name in nextProps whose value differs from prevProps[name]:
        dom[name] = nextProps[name]
    for each handler name in nextProps whose function differs from prevProps[name]:
        addEventListener(eventType(name), nextProps[name])
```
</details>

## Checking your solution

```
.\check 02                          every test, grouped by requirement
.\check 02 -Case 02-R8-swap         one test with its full input, the expected lines and yours
.\check 02 -Fresh                   six new random sequences, to try your code on scenarios you have not seen
.\check 02 -Dispute <id> "why"      set aside a test you are sure is wrong
```

An `updateDom` that adds the new handler and forgets to remove the old one fails like this, with the first handler still running:

```
  R8  A changed handler loses its old listener and gets a new one, an u... .    4 / 10  FAILED
      x 02-R8-swap-three-times  a, b, c, a: each click runs exactly the current handler
          log[0]: expected (text=b), got (text=a) - differs in text
          likely cause: R8 - A changed handler loses its old listener and gets a new one, an unchanged one is left alone, a removed one is removed
          expected values from: definition-level model in tools/gen_p02.py (property slots, listener map keyed by event type, set arithmetic over prop maps)
          reproduce: py -P tools/run_js.py build/bugs/02/changed-handler-keeps-old-listener 02 build/cases/02/02-R8-swap-three-times.in build/cases/02/02-R8-swap-three-times.out
```

## After you pass: compare with the author's code

[Pombo's post](https://pomb.us/build-your-own-react/#step-vi-reconciliation) splits the DOM work into two functions. `createDom(fiber)` makes the node and calls `updateDom(dom, {}, fiber.props)` (it takes a fiber where this page takes an element, but both carry `type` and `props`), and `updateDom(dom, prevProps, nextProps)` does the rest. Four helpers, `isEvent`, `isProperty`, `isNew` and `isGone`, pick the names for four passes: remove the listeners that are gone or changed, blank the properties that are gone, assign the properties that are new or changed, add the listeners that are new or changed. The event type is the prop name in lower case without its first two letters. The tests assume this structure.

The post's `isProperty` leaves out `children` and the event names and nothing else, so a `key` prop lands on its node as a property of its own. The spec here writes no such thing: R2 fails the post's version, and so do the longer tests that put a `key` in their props. The post also treats any name that starts with `on` as a handler, `once` or `online` included, and an event name such as `onDoubleClick` becomes `doubleclick`, which no browser fires. The tests use neither.

Jongeneel's [renderer](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.1%20Rendering%20a%20virtual%20DOM) assigns every prop as a property, handlers too (`elem.onclick = fn`), so a changed handler replaces the old one without a removal. It also creates a text node with its text already inside, and changed text becomes a new node instead of a `nodeValue` write. R3 and R9 would fail both. When he [applies a diff](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.2%20Applying%20a%20diff%20to%20a%20HTML%20element), the loop that removes props runs over array indexes, and the list it runs over was [worked out](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.1%20Creating%20the%20diff%20of%20an%20element) against the wrong object, so no removed prop is ever cleared and R7 catches it. React 19 works another way again: it sets most props as attributes and keeps listeners on the root. [React today](docs/react-today.md) has the rows "Props on DOM nodes" and "Events".
