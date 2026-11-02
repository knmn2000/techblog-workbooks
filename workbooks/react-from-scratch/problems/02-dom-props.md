# 02 · DOM nodes and props

**Difficulty:** Medium · **Assignment** 2 of 12 · **Check:** `.\check 02`

**Tags**
- *Language:* [closures](#primer/js-functions-closures) · [Object.keys, entries and in](#primer/js-object-keys) · [=== and falsy values](#primer/js-equality) · [string methods](#primer/js-string-methods)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [the DOM tree](#primer/dom-tree) · [createElement and createTextNode](#primer/dom-create) · [properties and attributes](#primer/dom-properties) · [listeners, event types and bubbling](#primer/dom-events)

## Read in the blog first

You do not need the post for this one. If you want Pombo's account anyway, there are two stretches. In [Step II](https://pomb.us/build-your-own-react/#step-ii-the-render-function), the paragraphs that make a text node for a text element, then the ones that [assign the props](https://pomb.us/build-your-own-react/#:~:text=The%20last%20thing%20we%20need%20to%20do%20here). In Step VI, from [One special kind of prop](https://pomb.us/build-your-own-react/#:~:text=One%20special%20kind%20of%20prop) and the three paragraphs ahead of it, up to the link to the sandbox. The code in both is the author's version of what you are about to write.

## Learning material

- [Arrow functions and closures](#primer/js-functions-closures): the handlers in the tests are plain functions, and the same function is what tells an unchanged handler from a new one.
- [Object.keys, Object.entries, Object.hasOwn and in](#primer/js-object-keys): walking the names of a props object, and asking whether a name is still there.
- [===, Object.is, truthy and falsy](#primer/js-equality): `===` decides whether two values are the same prop. The empty string is falsy, which matters when you ask whether a prop was given.
- [String methods](#primer/js-string-methods): turning `onClick` into `click`.
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

Write two functions that connect elements to real DOM nodes. `createDom` builds the node for an element. `updateDom` takes a node that already shows one set of props and changes it to show another, doing as little work on the node as it can.

### What a DOM node is

A DOM node is the browser's object for one thing on a page: an element such as a `<button>`, or a piece of text. You make one with `document.createElement("button")` or `document.createTextNode("hi")`. You change it by assigning properties, as in `node.id = "b"`, and you attach code to it with `node.addEventListener("click", fn)`, which calls `fn` whenever the node is clicked. A node you have just made is not on any page yet. Later assignments attach it.

Both functions reach the DOM through the global `document`. Read it inside the functions, not at the top of the file: it may be installed after your module loads.

### The two functions

| Function | Takes | Returns |
|---|---|---|
| `createDom(element)` | an element `{ type, props }` from assignment 01 | a new DOM node, not attached to anything: a text node when `type` is `"TEXT_ELEMENT"`, otherwise an element whose tag is `type` |
| `updateDom(dom, prevProps, nextProps)` | `dom`, a node; `prevProps`, an object with the props the node shows now; `nextProps`, an object with the props it should show | nothing. It changes `dom` |

`createDom` puts the props on its new node the same way `updateDom(dom, {}, element.props)` would, so the rules below are really the rules of `updateDom`.

For example, a button with an id and a click handler:

```js
const dom = createDom({ type: "button", props: { id: "b", onClick: handlerA, children: [] } })
// dom is a <button> node: dom.id is "b", and a "click" listener handlerA is attached

updateDom(dom, { id: "b", onClick: handlerA }, { id: "c", onClick: handlerB })
// id changed: dom.id = "c".  onClick changed: handlerA comes off the node and handlerB goes on.
```

### What each prop becomes on a node

| Prop | Example | What you do to the node |
|---|---|---|
| `children` and `key` | `children: []` | nothing. They are never put on a node |
| a name that starts with `on` | `onClick: handlerA` | a listener. Its event type is the rest of the name in lower case, so `onClick` listens for `click`. It is never assigned as a property |
| anything else | `id: "b"`, `disabled: true`, `value: "hi"` | a property: `dom[name] = value` |

A text element looks like `{ type: "TEXT_ELEMENT", props: { nodeValue: "hello", children: [] } }`. Create the text node empty, then give it its text by assigning `nodeValue`, like any other property. A text node therefore costs one create and one write, even when the text is the empty string, and a later change of the text is a write of `nodeValue` under the same rules.

### Writing as little as possible

Every name that appears in `prevProps` or `nextProps` falls into one of four groups: new if only `nextProps` has it, gone if only `prevProps` has it, changed if both have it with values that are not `===`, and unchanged otherwise. What each group costs:

| Group | A property `name` | A handler `onX` with event type `x` |
|---|---|---|
| new | `dom[name] = value` | `addEventListener(x, handler)` |
| changed | `dom[name] = value` | `removeEventListener(x, oldHandler)`, then `addEventListener(x, newHandler)` |
| gone | `dom[name] = ""`, which makes the node report its default again | `removeEventListener(x, oldHandler)` |
| unchanged | nothing | nothing |

Take one call, name by name:

```js
updateDom(dom,
  { id: "b", title: "t", value: "v", onClick: handlerA },   // prevProps
  { id: "b",             value: "w", onClick: handlerB })   // nextProps
```

| Name | Group | What your code does to `dom` |
|---|---|---|
| `id` | unchanged | nothing |
| `value` | changed | `dom.value = "w"` |
| `title` | gone | `dom.title = ""` |
| `onClick` | changed | `removeEventListener("click", handlerA)`, then `addEventListener("click", handlerB)` |

Doing less is the point. The tests count four things your code does to a node: `createElement` and `createTextNode` calls, property assignments (`nodeValue` and made-up names included), `addEventListener` calls and `removeEventListener` calls, each whether or not it changes anything. An update that changes nothing must cost nothing. A falsy new value such as `""` is still a value and gets written. A handler is unchanged when it is the same function; to swap one, remove the old function, which you find in `prevProps`, and add the new one. The props are plain objects with their own names, so to tell that a name is gone, ask `Object.hasOwn(nextProps, name)`. (`name in nextProps` also finds inherited names such as `toString`.)

### What the tests look at

The tests call `createDom` and `updateDom` with props like the ones above (values are strings, `true`, or handler functions), then look at the node: its tag or text, and `id`, `className`, `title`, `value` and `disabled`. They also read the four counts, and click the node to see which handlers run. The entry program that hands your two functions to the tests is finished in the Boilerplate, and the Start here card says what it is if you start from scratch.

Each example below shows the calls in JavaScript. The test itself, in the checker's own text, is in the example's input and output boxes: there `dump` means "show the node" and `ops` means "show the four counts", in the order of the list above.

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
- **E2E** End to end: longer sequences of creates, updates and clicks.

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

```js
createDom({ type: "TEXT_ELEMENT", props: { nodeValue: "hello", children: [] } })
```

The result is a text node holding `hello`, made with one create and one write. The create is the text node. The write is `nodeValue`, assigned once the node exists, like any other prop. Build the node with its text already inside and skip the assignment, and the test sees no write. That fails.

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

```js
const dom = createDom({ type: "input", props: { id: "i", value: "v", disabled: true, children: [] } })
updateDom(dom, { id: "i", value: "v", disabled: true }, { id: "i" })
```

The test looks at the node after each call and reads the counts once, at the end. After `createDom` the `<input>` shows its id, value and `disabled` flag. After `updateDom`, `id` is unchanged and costs nothing, while `value` and `disabled` are gone and are cleared with one write each, so the node is back to its defaults. Creation wrote three props and the update wrote two: five writes.

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

```js
const dom = createDom({ type: "button", props: { id: "b", onClick: handlerA, children: [] } })
// click the button: handlerA runs. Creation cost one write (id) and one addEventListener.

updateDom(dom, { id: "b", onClick: handlerA }, { id: "b", onClick: handlerB })
// click the button: only handlerB runs.
```

`id` is unchanged, and `handlerA` and `handlerB` are different functions, so the update removes one listener and adds one: no writes, one `addEventListener`, one `removeEventListener`. With `handlerA` still attached, the last click would run both handlers.

## Constraints

Values are ASCII strings, `true` or handler functions, and the handler props are `onClick`, `onclick`, `onMouseDown` and `onInput`. No name that starts with `on` gets a value other than a handler. Only nodes with a click handler are clicked. A test is at most 40 steps long. The 50 tests are each requirement's cases plus two long scripted sequences and six seeded random ones (`-Fresh` draws six new ones). Milliseconds is what a correct solution takes; the limit is 10 seconds per test.

## Hints

<details><summary>Hint 1: where to start</summary>

Start with a plain element: `createDom({ type: "div", props: { id: "a", children: [] } })`. Then call `updateDom` on it with the same props, and the right amount of work is none. Every rule here comes down to which props earn a write and which listeners earn a call, and the counts in the examples show you which.
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
