# 06 · Reconcile children by position

**Difficulty:** Hard · **Assignment** 6 of 12 · **Check:** `.\check 06`

**Tags**
- *Language:* [optional chaining](#primer/js-optional-chaining) · [===, Object.is, truthy and falsy](#primer/js-equality)
- *Library:* [appendChild, insertBefore, removeChild](#primer/dom-tree-editing) · [listeners, event types and bubbling](#primer/dom-events) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [reconciliation by type and position](#primer/react-reconciliation) · [trees of elements](#primer/react-tree) · [fibers](#primer/react-fibers)

## Read in the blog first

[Step VI: Reconciliation](https://pomb.us/build-your-own-react/#step-vi-reconciliation) is where the post covers this, and you can pass without it. If you read it, go from the start through the three-way comparison of an element with the old fiber, then the effect tags, the list of fibers to remove and the new `commitWork`. The part on `updateDom` and listeners is what you wrote in 02. Stop before the code frames. In a few places the post's own code disagrees with the rules below; the section after you pass names them.

## Learning material

- [Reconciliation by type and position](#primer/react-reconciliation): same type at the same place keeps its node, a different type gets a new one, and the old children left over go.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): a new node goes in front of a particular sibling instead of at the end, and once a node is removed it is gone for good, which makes removing it a second time an error.
- [Listeners, event types and bubbling](#primer/dom-events): a node that is kept ends up with the new handler and none of the old.
- [Trees of elements](#primer/react-tree): two renders make two trees, and the library has to find what separates them.
- [Fibers](#primer/react-fibers): each fiber now links to its twin from the previous render.
- [Optional chaining `?.` and `??`](#primer/js-optional-chaining): the first render has no earlier tree, so asking for its children comes back empty.
- [`===`, `Object.is`, truthy and falsy](#primer/js-equality): two elements match when their types are equal under `===`.

## Source material

- Rodrigo Pombo, [Step VI: Reconciliation](https://pomb.us/build-your-own-react/#step-vi-reconciliation)
- React's older documentation, [Reconciliation](https://legacy.reactjs.org/docs/reconciliation.html), for the diffing rules
- react.dev, [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
- MDN: [Node.insertBefore](https://developer.mozilla.org/en-US/docs/Web/API/Node/insertBefore) and [Node.removeChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/removeChild)

## Where this fits

Until now the container was empty when a render began. From here the second `render` meets a page that already holds the first tree, and it has to turn that page into the new one while keeping every node it can. No new files: `state.js` and `render.js` remember the last tree on the page, `reconcile.js` compares, and `commit.js` carries out the verdicts. Position is the only identity a child has until 07 refines the comparison.

## The problem

Render a tree, render another into the same container, and make the page match the second one with as few changes as the rules allow. The tests can see which DOM nodes survived. A library that clears the container and draws again fails them, even though its page looks right.

### Matching children

Compare the tree on the page (the old one) with the new element tree, one parent at a time. The new tree's top element is compared with the old tree's top node, which is the only child of the container. When two children match, their own children get the same treatment.

A child's position is its index among its siblings. At each position `i` under a parent, take the old child at `i` (if there is one) and the new element at `i` (if there is one), and apply the first row of the table that fits.

| Old child at `i` | New element at `i` | What happens |
|---|---|---|
| exists, same type | exists | The old DOM node stays. Changed props are applied to it, or the new text if it is a text node. Then the two sets of children are compared. |
| exists, other type | exists | A new node is made and the old one leaves the page with everything below it. The new node takes position `i` among its siblings, so the children keep the order of the new element's list. |
| exists | none | The old node leaves the page, with everything below it. |
| none | exists | A new node is made and goes after the siblings already there. |

Same type means the `type` values are `===`: the same tag name, or both text pieces (`"TEXT_ELEMENT"`). An element and a text piece at one position are different types. Nothing below a replaced or removed node is compared. Its subtree is gone, and every element under a new node is new too.

Matching goes by position alone. Take the list `A, B, C` and turn it into `A, C`. The node that showed `B` now shows `C`, and the node that showed `C` is the one that leaves. `key` plays no part here, and no scenario gives one.

### Props, handlers and the log

A node that stays is updated with `updateDom(dom, oldProps, newProps)` from `dom.js`. It writes the props that are new or changed, clears the ones that are gone and swaps a handler whose function changed. After the render the node shows the new element's props and has the new element's listeners and no others. A prop named `onClick` listens to `click`.

A new node gets its props from `createDom`, as in 04.

### Renders in a row

A scenario renders two or more trees into the same container. Each is compared with what is on the page, never with an older tree, and a fiber removed by one render must not be removed again by the next. Every `render` is followed by a `flush` before anything else happens. What your library does with a `render` that follows another before any work has run is not tested.

### Input

The entry file is run as `node assignments/assignment_06_reconcile.js <input-file> <output-file>`, and you have met its three steps in 04 and 05. Load `../harness/env.js` first, since `render.js` asks for `requestIdleCallback` while it loads. Bring in `Didact` (`../src/didact/index.js`) and `runScenarioFile` (`../harness/scenario.js`). End by awaiting `runScenarioFile` with `process.argv[2]`, `process.argv[3]` and `Didact`. It comes done with the Boilerplate; from scratch you write it.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Keeps a tree under a name for later `render` lines. No output. |
| `render <name>` | `Didact.render(element, container)`, always with the same container. Nothing printed, no work run. |
| `flush` | Idle periods until the work is done. No output. |
| `dump` | Prints the container. |
| `click #<id>` | A bubbling `click` on the element whose id is `<id>`, followed by a `flush`. No output. |
| `log` | One line per handler call since the previous `log`. |

A tree is one line of HTML-like text, for instance `<div id=box className="a b"><p onClick=@one>hi</p></div>`. Values are strings, a bare name means `true`, and text keeps its inner spaces. A value starting with `@` is a handler. `@one` is a function that adds the word `one` to the log when it runs, and every `@one` in a scenario is that same function. A `click` runs the target's listeners first and then each ancestor's, up to the root.

### Output

```
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
log <name>
```

A `dump` prints `dump <i>`, counting dumps from 1, then the container's children in document order with their depth from 0: `node` for an element, `text` for a piece of text. An element is labelled when a dump first shows it, `a`, `b`, on through `z`, `aa`, `ab`, and the same DOM node keeps its label in every later dump. A node your library replaced is a new node and takes the next unused label, which is how the tests tell a kept node from a rebuilt one. Text nodes have no label. The tests can't tell a reused text node from a new one.

The quoted prop list follows the tag. Alphabetically it can hold `className=...`, `disabled=true` (only on a `button`, `input` or `textarea`), `id=...`, `title=...` and `value=...` (only on an `input` or `textarea`), and an entry appears only once its prop has left its default, which is empty text or false. Entries are separated by spaces. A node with none prints `""`. Whitespace, `"` and `%` inside a value are percent-encoded, so `a b` becomes `a%20b`. A `text` line percent-encodes `%`, `"` and line breaks and leaves spaces alone, and text nodes that touch print as a single line.

Each call of an `@name` handler since the last `log` becomes a `log <name>` line, in call order.

## Requirements

- **R1** The same type at the same position keeps its DOM node, with the same label in the next dump, and the new props and text are applied to it.
- **R2** A prop that is missing from the new element is cleared on the node that stays.
- **R3** A different type at a position gets a new node, and the new node stays at that position among its siblings.
- **R4** Elements beyond the old children are added after them.
- **R5** Old children beyond the new elements are removed, once each, however many are adjacent, and also when earlier renders removed some.
- **R6** After a render, a click runs the new handler once, and runs nothing for a handler that was removed.
- **R7** Changes at several depths in one render, kept, replaced, added and removed nodes together, give the right tree.
- **R8** Random trees, two or three renders in a row: the container ends up as the last tree, and the nodes that stay are the ones the rules above keep.
- **E2E** Whole sessions of renders, clicks and dumps.

## Examples

### Example 1: the replaced child stays in the middle (test `06-R3-middle-child`)

```
input:
tree a <div><p>A</p><b>B</b><i>C</i></div>
tree b <div><p>A</p><u>B</u><i>C</i></div>
render a
flush
dump
render b
flush
dump

output:
dump 1
node 0 a div ""
node 1 b p ""
text 2 "A"
node 1 c b ""
text 2 "B"
node 1 d i ""
text 2 "C"
dump 2
node 0 a div ""
node 1 b p ""
text 2 "A"
node 1 e u ""
text 2 "B"
node 1 d i ""
text 2 "C"
```

`div`, `p` and `i` are the same nodes, so they keep `a`, `b` and `d`. The `b` became a `u`: the old node left and a new one, labelled `e`, took its place between the other two. Appending that new node to the `div` would put `u` after `i`, and the second dump would print `i` before `u`.

### Example 2: two adjacent removals (test `06-R5-four-to-two`)

```
input:
tree a <ul><li>a</li><li>b</li><li>c</li><li>d</li></ul>
tree b <ul><li>a</li><li>b</li></ul>
render a
flush
dump
render b
flush
dump

output:
dump 1
node 0 a ul ""
node 1 b li ""
text 2 "a"
node 1 c li ""
text 2 "b"
node 1 d li ""
text 2 "c"
node 1 e li ""
text 2 "d"
dump 2
node 0 a ul ""
node 1 b li ""
text 2 "a"
node 1 c li ""
text 2 "b"
```

The last two `li` nodes have no element left. They sit side by side. Each has to come out of the `ul` once. If removing the first goes on to touch the second, which is what happens when a deleted fiber's removal also follows its siblings, that node is removed twice and the run dies with a `NotFoundError` from `removeChild`.

### Example 3: the latest handler only (test `06-R6-handler-replaced`)

```
input:
tree a <button id=b onClick=@one>x</button>
tree b <button id=b onClick=@two>x</button>
render a
flush
dump
click #b
log
render b
flush
dump
click #b
log

output:
dump 1
node 0 a button "id=b"
text 1 "x"
log one
dump 2
node 0 a button "id=b"
text 1 "x"
log two
```

The button is kept, so it is `a` in both dumps. The second render gives it another function, `two`. The old listener has to come off and the new one go on, or the second click prints `log one` and `log two`.

## Constraints

Up to 28 nodes per tree, any tag name, and only the props `id`, `className`, `title`, `disabled` and `onClick`; no function components, no keys. A scenario renders two to five trees with a `flush` after each, and never uses `idle` or `ops`. A `click` always names an element with a unique id. The 54 tests are hand-made pairs and sequences for each requirement, two full sessions and eight random ones: four edits of one tree, two chains of edits, two unrelated trees. `-Fresh` replaces the random ones. Ten seconds a test is far more than needed.

## Hints

<details><summary>Hint 1: where to start</summary>

Leave removals and replacements for last. Start by making the same tree rendered twice keep every label. That takes only the last committed tree, a link from each new fiber to its twin, and `updateDom` in the commit. Then add one behaviour at a time, in this order: a changed type, extra new children, missing children.
</details>

<details><summary>Hint 2: the approach</summary>

After each commit, remember the root of the tree that went onto the page, and have `render` build the next root with a link back to it. `reconcileChildren` walks the new elements and the old children of the fiber's twin together, one pair per position. A pair of the same type gives a fiber that reuses the old node and is tagged `UPDATE`. Any other pair gives a fiber with no node, tagged `PLACEMENT`, and the old child, if there is one, goes on a list of fibers to remove. Once the elements run out, every old child left over joins that list. The commit takes off everything on the list first, then walks the new tree. A `PLACEMENT` fiber's node goes into its parent in front of the next sibling already on the page, and an `UPDATE` fiber gets `updateDom` with its twin's props and its own.
</details>

<details><summary>Hint 3: the traps</summary>

- Compare `type` with `type`. An element against a fiber, or one props object against another, never matches.
- Step to the next old sibling after each element, and when the elements run out keep going through the old siblings that remain.
- Appending a new node to its parent is the wrong move. It goes in front of the node of the next sibling already on the page, and later siblings that are new themselves aren't on the page yet, so skip them.
- A removed fiber goes on the list once. Don't walk on from it to its siblings or children: each of those has its own entry or leaves with the parent.
- Begin every render with an empty removal list, or the next render takes last time's nodes out again.
- Remember the committed tree at the end of the commit, not at the start of the render, and leave the committed fibers alone while a render is going on.
- `updateDom` needs the old fiber's props. Empty old props can't clear a prop or remove a listener.
- The first render has no twin. `alternate.child` on nothing throws; `alternate?.child` is undefined.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
render(element, container):
    deletions = []
    wipRoot = fiber with dom = container, props.children = [element], alternate = currentRoot
    nextUnitOfWork = wipRoot

reconcileChildren(wipFiber, elements):
    oldFiber = wipFiber.alternate?.child
    for each element, in order:
        if oldFiber and oldFiber.type == element.type:
            fiber = type, props of element, dom of oldFiber, parent wipFiber, alternate oldFiber, "UPDATE"
        else:
            fiber = type and props of element, no dom, parent wipFiber, no alternate, "PLACEMENT"
            if oldFiber: add oldFiber to deletions
        oldFiber = oldFiber's sibling
        link fiber into wipFiber.child / previous fiber's sibling
    for each oldFiber still left: add it to deletions

commitRoot():
    for each fiber in deletions: fiber.parent.dom.removeChild(fiber.dom)
    commitWork(wipRoot)
    currentRoot = wipRoot
    wipRoot = nothing

commitWork(fiber):
    if fiber is "PLACEMENT": fiber.parent.dom.insertBefore(fiber.dom, dom of the next sibling that is not "PLACEMENT", or null)
    if fiber is "UPDATE": updateDom(fiber.dom, fiber.alternate.props, fiber.props)
    for each child: commitWork(child)
```
</details>

## Checking your solution

```
.\check 06                         the whole suite, grouped by requirement
.\check 06 -Case 06-R3-two-of-five   one test: the input, the expected output and yours
.\check 06 -Fresh                  eight new random sequences of renders
.\check 06 -Dispute <id> "why"     set aside a test that you can show is wrong
```

Appending every new node to its parent gets you this report:

```
  R3  a different type at a position gets a new node, and it stays at t... .    3 / 8   FAILED
      x 06-R3-middle-child  the middle of three children changes tag
          node[0]: expected (depth=1, label=e, tag=u, props=""), got (depth=1, label=d, tag=i, props="") - differs in label, tag  (in `dump 2`)
          likely cause: R3 - a different type at a position gets a new node, and it stays at that position among its siblings
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle), cross-checked line by line against a positional model in tools/gen_p06.py
          reproduce: py -P tools/run_js.py solutions 06 build/cases/06/06-R3-middle-child.in build/cases/06/06-R3-middle-child.out
```

## After you pass: compare with the author's code

[Pombo's Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation) keeps the last committed tree in `currentRoot` and gives every fiber an `alternate`: the old fiber at the same place, or `null` for a new one. `reconcileChildren(wipFiber, elements)` walks the elements and the old fibers together in one loop that runs until both are used up, and tags each new fiber `UPDATE` or `PLACEMENT`. An old fiber to remove gets the tag `DELETION` and goes into a `deletions` array that `render` empties. `commitRoot` runs `commitWork` over `deletions`, then over `wipRoot.child`, and sets `currentRoot`; `commitWork` handles the three tags and calls `updateDom` for an update, as in 02. That is the structure the rules above describe. Two things differ here. `currentRoot` and `deletions` live in `state`, and a removed fiber is only put on the list, with no `DELETION` tag written onto it (the last paragraph says why).

Two places in the post's `commitWork` break what the tests need. A fiber with `PLACEMENT` is added with `domParent.appendChild(fiber.dom)`, so a replaced child with later siblings ends up behind them, and the first example here fails. And `commitWork` goes on to `fiber.child` and `fiber.sibling` for every tag, a deleted fiber included. With two adjacent removals, the walk from the first one reaches the second, which is tagged for deletion as well, and removes it. Then the `deletions` array removes it again. That second removal of the same node makes `removeChild` throw `NotFoundError`, the commit stops before the kept nodes get their new props, and because the post's loop registers itself again only as its last statement, the library never runs again. Any render that removes or replaces two neighbouring children hits this; a list that shrinks by two is one example. Both are why the page asks for placement in front of a sibling and for each node to be removed once.

The same walk over deleted fibers re-applies old tags to the siblings and children it passes. That costs extra DOM calls, which a dump does not show. The post also writes the tag `DELETION` onto a fiber that is already on the page. Its epilogue says an update arriving in the middle of a render makes Didact throw the unfinished tree away and start again from the root, and the tag outlives that restart, so a later render can remove a live node. The tests render only after a `flush`, so none of them restarts work and none can show this. Hint 3 asks you to leave the committed fibers alone for that reason, and a list entry is all a removal needs.

React matches unkeyed children by position, as here, and by key when there are keys; [React today](docs/react-today.md) lists the other differences, including how it sets props. The post's aside says React also uses keys, and 07 adds them. One more difference the tests cannot see: every `alternate` link keeps the previous render's fiber alive, and that fiber's own `alternate` reaches back further, which means the post never lets go of an old tree.
