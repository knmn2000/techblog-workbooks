# 02 · DOM nodes and props

**Difficulty:** Medium · **Assignment** 2 of 12 · **Check:** `.\check 02`

**Tags**
- *Language:* [closures](#primer/js-functions-closures) · [Object.keys, entries and in](#primer/js-object-keys) · [=== and falsy values](#primer/js-equality) · [string methods](#primer/js-string-methods)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [the DOM tree](#primer/dom-tree) · [createElement and createTextNode](#primer/dom-create) · [properties and attributes](#primer/dom-properties) · [listeners, event types and bubbling](#primer/dom-events)

## Read in the blog first

This page stands on its own. If you want Pombo's account first, read two stretches of the post. In [Step II](https://pomb.us/build-your-own-react/#step-ii-the-render-function) take the paragraphs that make a text node for a text element and then [assign the props](https://pomb.us/build-your-own-react/#:~:text=The%20last%20thing%20we%20need%20to%20do%20here). In Step VI start at [One special kind of prop](https://pomb.us/build-your-own-react/#:~:text=One%20special%20kind%20of%20prop), together with the three paragraphs before it, and stop before the link to the sandbox. The code in both stretches is the author's version of what you are about to write.

## Learning material

- [Arrow functions and closures](#primer/js-functions-closures): the handlers in the scenarios are plain functions, and one name is one function, which is how an unchanged handler differs from a new one.
- [Object.keys, Object.entries, Object.hasOwn and in](#primer/js-object-keys): going over the names of a props object and asking whether a name is still there.
- [===, Object.is, truthy and falsy](#primer/js-equality): two values are the same prop when `===` says so, and the empty string is falsy, which matters for the test "was this prop given".
- [String methods](#primer/js-string-methods): turning `onClick` into `click`.
- [The DOM tree: elements and text nodes](#primer/dom-tree): two kinds of node, and a text node has no props of its own besides its text.
- [createElement and createTextNode](#primer/dom-create): the two calls that make a node.
- [Properties and attributes](#primer/dom-properties): `id`, `className`, `title`, `value`, `disabled` and `nodeValue` are properties you assign.
- [Listeners, event types and bubbling](#primer/dom-events): a listener is registered for a type and removed with the same function that was added.

## Source material

- Rodrigo Pombo, [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function) and, in [Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation), the part on `updateDom` and event listeners
- MDN: [document.createElement](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement), [document.createTextNode](https://developer.mozilla.org/en-US/docs/Web/API/Document/createTextNode), [Node.nodeValue](https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeValue), [addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) and [removeEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener)
- Wim Jongeneel, [Rendering a virtual DOM](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.1%20Rendering%20a%20virtual%20DOM) and [Applying a diff to a HTML element](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.2%20Applying%20a%20diff%20to%20a%20HTML%20element), for a version that assigns props as properties
- The harness's own DOM, `harness/minidom.js`, which counts what your code does to it

## Where this fits

Elements from assignment 01 only describe a page. This file is where Didact first touches a real node. The first render in 03 calls `createDom`, and once the library can compare two renders, `updateDom` is what the commit calls on a node it keeps. You write `src/didact/dom.js`.

## The problem

Write the two functions that put props on a DOM node. `createDom(element)` makes the node for an element, and `updateDom(dom, prevProps, nextProps)` takes a node from one set of props to the next while touching as little as it can. A scenario creates a node, updates it, clicks it, and prints both its state and what you did to it.

### The module

`src/didact/dom.js` exports:

| Export | Meaning |
|---|---|
| `createDom(element)` | `element` is `{ type, props }`. Returns a new node that is not attached to anything: a text node when `type` is `"TEXT_ELEMENT"`, otherwise an element whose tag is `type`. The props are put on it as in `updateDom(dom, {}, element.props)`. |
| `updateDom(dom, prevProps, nextProps)` | Changes `dom` so that it reflects `nextProps`, given that it reflects `prevProps` already. Returns nothing. |

Both reach the DOM through the global `document`. The harness installs it before it calls your functions, though not necessarily before your module loads, so read `document` inside the functions and not at the top of the file.

### Input

The checker runs `node assignments/assignment_02_dom_props.js <input-file> <output-file>`. That entry program does the same job as in assignment 01 with a different library object: it imports `createDom` and `updateDom` from your `dom.js` and `runScenarioFile` from `../harness/scenario.js`, then awaits `runScenarioFile(process.argv[2], process.argv[3], { createDom, updateDom })`. The Boilerplate has it finished, and a start from scratch needs those lines before anything can run. The commands are:

| Line | What the harness does |
|---|---|
| `create <tag\|text> [prop ...]` | Calls `createDom({ type, props })`, with `text` standing for the type `TEXT_ELEMENT`, and keeps the node it returns. Any node kept earlier is dropped. |
| `update [prop ...]` | Calls `updateDom(node, prev, next)` on the kept node, where `prev` is the props of the last `create` or `update` and `next` is the props on this line. Then `next` becomes `prev`. |
| `click #<id>` | Dispatches a bubbling `click` on the kept node, which must have that id. The node is not in any document, and the harness finds it anyway. |
| `dump` | Prints the kept node. |
| `ops create write addListener removeListener` | Prints four counters, described under Output. |
| `log` | Prints the handler calls recorded since the last `log`. |

A prop is written like an attribute: `id=a`, `title="two words"`, `title='say "hi"'`. Every value is a string. A bare name such as `disabled` means `true`, and `onClick=@one` is a handler: `@one` is one function that records the word `one` in the log when it is called, and every `@one` in the scenario is that same function. The props object that `create` and `update` hand to you carries `children: []` next to the listed props.

### Output

`dump` prints `dump <n>`, where `n` counts the dumps, then one line for the kept node:

```
node 0 <label> <tag> "<props>"
text 0 "<text>"
```

The first node a dump shows gets the label `a`, the next new node `b`, and so on. The same node keeps its label. `<tag>` is lower case. `<props>` lists, sorted by name and joined with single spaces, the values that differ from the default for `className`, `disabled` (on `button`, `input` and `textarea`), `id`, `title` and `value` (on `input` and `textarea`), each as `name=value`, with `true` printed for a boolean. A value that contains whitespace, a double quote or `%` is percent-encoded (`encodeURIComponent`), so `two words` prints as `two%20words`. An element with nothing to list prints `""`. Props the dump does not know, `lang` for one, do not show. A text node prints its `nodeValue`, with `%`, `"` and line breaks encoded and spaces kept, and prints no line at all while its text is empty.

`ops create write addListener removeListener` prints one line, `ops <create> <write> <addListener> <removeListener>`, then sets the counters back to 0. The counters measure what your code did to DOM objects since the previous `ops` or the start of the scenario:

| Counter | Counts |
|---|---|
| `create` | calls of `document.createElement` and `document.createTextNode` |
| `write` | assignments to a property of the node, `nodeValue` and made-up property names included |
| `addListener` | calls of `addEventListener`, whether or not they change anything |
| `removeListener` | calls of `removeEventListener`, the same |

`log` prints one `log <name>` line for each time a `@name` handler ran since the last `log`, in the order they ran.

### How props reach a node

Sort each name in `prevProps` and `nextProps` into one of four groups. It is new when only `nextProps` has it, gone when only `prevProps` has it, changed when both have it with values that are not `===`, and unchanged otherwise.

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

A new value that is falsy, such as `""`, is a value like any other and gets written. A handler counts as unchanged when it is the same function: the scenario's `@one` is one function every time it appears. To find out that a name is gone, `name in nextProps` and `Object.hasOwn(nextProps, name)` both work, because the props are plain objects with their own names.

A text element is `{ type: "TEXT_ELEMENT", props: { nodeValue, children: [] } }`. Make the text node empty and give it its text with a write to `nodeValue`, like any other property. That write is the only one the node costs, so a text node is one create and one write. Later changes to the text are updates of `nodeValue` under the same rules.

## Requirements

- **R1** `createDom` returns an element whose tag is the element's type.
- **R2** `children` and `key` are never assigned to the node, whether they come with `createDom` or with `updateDom`.
- **R3** A `TEXT_ELEMENT` becomes a text node holding its `nodeValue`, at a cost of one create and one write.
- **R4** Props are assigned as properties of the node, when it is created and when they are new in an update.
- **R5** A prop whose name starts with `on` becomes a listener for the lower-cased rest of the name, and is not assigned as a property.
- **R6** `updateDom` writes only props that are new or whose value differs from before, falsy values included.
- **R7** A prop that is missing from `nextProps` is cleared with one write, and the node reports its default again.
- **R8** A changed handler loses its old listener and gets the new one, an unchanged handler is left alone, a removed handler is removed.
- **R9** `updateDom` on a text node writes a changed `nodeValue` and clears it when it is gone.
- **E2E** Longer sequences of `create`, `update`, `click` and `ops`.

## Examples

### Example 1: a text node (test `02-R3-text`)

input:
```
create text nodeValue=hello
dump
ops create write addListener removeListener
```
output:
```
dump 1
text 0 "hello"
ops 1 1 0 0
```

The scenario lists one prop, and the counters show one create and one write. The create is the text node. The write is `nodeValue`, which you assign after the node exists, as you would any other prop. A node made with its text already inside and no assignment afterwards would show `ops 1 0 0 0` and fail.

### Example 2: three props, then none of the two (test `02-R7-input`)

input:
```
create input id=i value=v disabled
dump
update id=i
dump
ops create write addListener removeListener
```
output:
```
dump 1
node 0 a input "disabled=true id=i value=v"
dump 2
node 0 a input "id=i"
ops 1 5 0 0
```

The counters sum both steps, because `ops` is only called at the end. Creation writes three props, `id`, `value` and `disabled`. In the update, `id` is unchanged and costs nothing, while `value` and `disabled` are gone and each costs one write, which makes five. The second dump shows them back at their defaults.

### Example 3: a handler swapped (test `02-R8-swap`)

input:
```
create button id=b onClick=@a
click #b
log
ops create write addListener removeListener
update id=b onClick=@b
ops create write addListener removeListener
click #b
log
```
output:
```
log a
ops 1 1 1 0
ops 0 0 1 1
log b
```

Creation writes `id` and adds one listener, so the first `ops` is `1 1 1 0`. The update changes only the handler: `id` is unchanged, `@a` is not the same function as `@b`, so the old listener comes off and the new one goes on, and the second `ops` is `0 0 1 1`. The second click then calls `b` and nothing else. If `a` were still registered, the last `log` would print both.

## Constraints

Values are ASCII strings without a leading `@` unless they are handlers, and handler props are `onClick`, `onclick`, `onMouseDown` and `onInput`. `click` is only used on a node that has an id and, for a log line, a click handler. No scenario passes `children` as a listed prop, and no test gives a name that starts with `on` a value other than a handler. No scenario has more than 40 lines. The 50 tests are the cases of each requirement, two long scripted sequences and six seeded random ones (`-Fresh` gives six new ones), and a correct solution takes milliseconds. Each test is allowed 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Begin with `create div id=a` and a `dump`. Then add an `update` with the same props and a second `ops`: the right answer is four zeros. Each rule in this assignment comes down to which props deserve a write and which listeners deserve a call, and `ops` shows you the answer.
</details>

<details><summary>Hint 2: the approach</summary>

Write two small predicates, one for "this name is a handler" and one for "this name is a property I should write", and a function that turns `onClick` into `click`. Then make four passes over the two props objects: take off the handlers that are gone or changed, clear the properties that are gone, set the properties that are new or changed, and put on the handlers that are new or changed. `createDom` then needs only the right node kind and a call to `updateDom` with empty previous props.
</details>

<details><summary>Hint 3: the traps</summary>

- Tell "gone" from "falsy": a prop that is still in `nextProps` with the value `""` is not gone, and must be written.
- Take a listener off with the function that was added, which is the one in `prevProps`. The new function would match nothing.
- Take the old listener off before you add the new one, or you listen twice.
- A handler is not a property. If it is also assigned as `dom.onClick`, `write` is one too high.
- `onClick` has to be lower-cased to `click`, or nothing ever hears the click.
- `children` is in every props object you get. Skip it, and skip `key` as well.
- Give a text node its text through the same path as the other props, so that it counts as a write.
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

An `updateDom` that adds the new handler and forgets to remove the old one fails like this (the first handler keeps running):

```
  R8  A changed handler loses its old listener and gets a new one, an u... .    4 / 10  FAILED
      x 02-R8-swap-three-times  a, b, c, a: each click runs exactly the current handler
          log[0]: expected (text=b), got (text=a) - differs in text
          likely cause: R8 - A changed handler loses its old listener and gets a new one, an unchanged one is left alone, a removed one is removed
          expected values from: definition-level model in tools/gen_p02.py (property slots, listener map keyed by event type, set arithmetic over prop maps)
          reproduce: py -P tools/run_js.py build/bugs/02/changed-handler-keeps-old-listener 02 build/cases/02/02-R8-swap-three-times.in build/cases/02/02-R8-swap-three-times.out
```

## After you pass: compare with the author's code

In [Pombo's post](https://pomb.us/build-your-own-react/#step-vi-reconciliation) the DOM work sits in `createDom(fiber)`, which makes the node and calls `updateDom(dom, {}, fiber.props)` (the post hands it a fiber, this page hands it an element, and both carry `type` and `props`), and in `updateDom(dom, prevProps, nextProps)`. The helpers `isEvent`, `isProperty`, `isNew` and `isGone` pick the names for four passes: remove the listeners that are gone or changed, blank the properties that are gone, assign the properties that are new or changed, and add the listeners that are new or changed. The event type is the prop name in lower case without its first two letters. This is the structure the tests assume.

The post's `isProperty` leaves out `children` and the event names, and nothing else, so a `key` prop is assigned to its node as a property of its own. The spec here does not write it, so R2 fails the post's version, and so do the longer tests that put a `key` in their props. The post also treats any name that starts with `on` as a handler, `once` or `online` included, and an event name such as `onDoubleClick` becomes `doubleclick`, which no browser fires. The tests use neither.

Jongeneel's [renderer](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.1%20Rendering%20a%20virtual%20DOM) assigns every prop as a property, handlers too (`elem.onclick = fn`), so a changed handler replaces the old one without a removal. His renderer also creates a text node with its text already inside, and a changed text becomes a new node instead of a `nodeValue` write; R3 and R9 would fail both. When he [applies a diff](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=4.2%20Applying%20a%20diff%20to%20a%20HTML%20element), the loop that removes props runs over array indexes, and the list it runs over was [worked out](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.1%20Creating%20the%20diff%20of%20an%20element) against the wrong object, so no removed prop is ever cleared, and R7 would catch that. React 19 works another way again: it sets most props as attributes and keeps listeners on the root. [React today](docs/react-today.md) has the rows "Props on DOM nodes" and "Events".
