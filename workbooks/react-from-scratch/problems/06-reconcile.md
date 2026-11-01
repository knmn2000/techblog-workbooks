# 06 · Reconcile children by position

**Difficulty:** Hard · **Assignment** 6 of 12 · **Check:** `.\check 06`

**Tags**
- *Language:* [optional chaining](#primer/js-optional-chaining) · [===, Object.is, truthy and falsy](#primer/js-equality)
- *Library:* [appendChild, insertBefore, removeChild](#primer/dom-tree-editing) · [listeners, event types and bubbling](#primer/dom-events) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [reconciliation by type and position](#primer/react-reconciliation) · [trees of elements](#primer/react-tree) · [fibers](#primer/react-fibers)

## Read in the blog first

The page is self-contained. Pombo covers this in [Step VI: Reconciliation](https://pomb.us/build-your-own-react/#step-vi-reconciliation). Read from the start through the three-way comparison of an element with the old fiber, and on through the effect tags, the list of fibers to remove and the new `commitWork`. The part on `updateDom` and listeners is what you wrote in 02. Stop before the code frames, and expect a few places where the post's own code and the rules below disagree. The section after you pass names them.

## Learning material

- [Reconciliation by type and position](#primer/react-reconciliation): the same type at the same place keeps its node, another type gets a new one, and the leftovers go.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): a new node has to go before a particular sibling, not at the end, and a node that is removed is gone for good, so removing it twice is an error.
- [Listeners, event types and bubbling](#primer/dom-events): a node that is kept has to end up with the new handler and none of the old.
- [Trees of elements](#primer/react-tree): two renders give two trees, and the library has to see what separates them.
- [Fibers](#primer/react-fibers): a fiber now points at its twin from the previous render.
- [Optional chaining `?.` and `??`](#primer/js-optional-chaining): the first render has no earlier tree, so looking for its children comes back empty.
- [`===`, `Object.is`, truthy and falsy](#primer/js-equality): two elements match when their types are equal under `===`.

## Source material

- Rodrigo Pombo, [Step VI: Reconciliation](https://pomb.us/build-your-own-react/#step-vi-reconciliation)
- React's older documentation, [Reconciliation](https://legacy.reactjs.org/docs/reconciliation.html), for the diffing rules
- react.dev, [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
- MDN: [Node.insertBefore](https://developer.mozilla.org/en-US/docs/Web/API/Node/insertBefore) and [Node.removeChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/removeChild)

## Where this fits

Up to now the container was empty when a render began. Here the second `render` meets a page that already holds the first tree, and it has to change that page into the new one while keeping every node it can. No file is new. `state.js` and `render.js` hold on to the last tree on the page, `reconcile.js` compares, and `commit.js` carries out the verdicts. Assignment 07 refines the comparison, and until then position is the only identity a child has.

## The problem

Render a tree, then render another one into the same container, and make the page match the second tree with as few changes as the rules allow. The tests see which DOM nodes survived, so a library that clears the container and draws again fails them even though its page looks right.

### Matching children

Compare the tree on the page (the old one) with the new element tree one parent at a time. The top element of the new tree is compared with the top node of the old one, as the only child of the container. For two children that match, their own children are compared in the same way.

A child's position is its index among its siblings. For every position `i` under one parent, take the old child at `i`, if there is one, and the new element at `i`, if there is one, and apply the first row that fits.

| Old child at `i` | New element at `i` | What happens |
|---|---|---|
| exists, same type | exists | The old DOM node stays. The props that changed are applied to it, and a text node gets the new text. Then the two sets of children are compared. |
| exists, other type | exists | A new node is made. The old node leaves the page together with everything below it. The new node takes position `i` among its siblings, so the children keep the order of the new element's list. |
| exists | none | The old node leaves the page, with everything below it. |
| none | exists | A new node is made, and goes after the siblings already there. |

Two things have the same type when their `type` values are `===`: the same tag name, or both text pieces (`"TEXT_ELEMENT"`). An element and a text piece at one position are different types. Nothing is compared below a node that was replaced or removed. Its subtree is gone, and every element under a new node is new as well.

Matching goes by position alone. When the list `A, B, C` becomes `A, C`, the node that showed `B` now shows `C`, and the node that showed `C` is the one that leaves. Nothing in this assignment looks at `key`, and no scenario gives one.

### Props, handlers and the log

A node that stays is brought up to date with `updateDom(dom, oldProps, newProps)` from `dom.js`. It writes the props that are new or changed, clears the ones that are gone and swaps a handler whose function changed. After the render the node shows the new element's props and has the new element's listeners and no others, and a prop named `onClick` listens to `click`.

A node that is new gets its props from `createDom`, as in 04.

### Renders in a row

A scenario renders two or more trees into the same container, each one compared with the one on the page, never with an older one. A fiber that was removed by one render must not be removed again by the next. After each `render` comes a `flush` before anything else in the scenario. What the library does with a `render` that follows another before any work has run is not tested.

### Input

The checker runs `node assignments/assignment_06_reconcile.js <input-file> <output-file>`. Its work is the same three steps as in 04 and 05. It loads `../harness/env.js` first, since `render.js` asks for `requestIdleCallback` while it loads, imports `Didact` from `../src/didact/index.js` and `runScenarioFile` from `../harness/scenario.js`, and ends by awaiting `runScenarioFile` with `process.argv[2]`, `process.argv[3]` and `Didact`. It comes finished with the Boilerplate, and from scratch you write it.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Stores a tree under a name for the `render` lines to use. No output. |
| `render <name>` | Calls `Didact.render(element, container)`, always with the same container. Prints nothing and runs no work. |
| `flush` | Runs idle periods until the work is done, then returns. No output. |
| `dump` | Prints the container. |
| `click #<id>` | Dispatches a bubbling `click` on the element whose id is `<id>`, then does a `flush`. Prints nothing. |
| `log` | Prints one line for each handler call since the previous `log`. |

A tree is one line of HTML-like text, for instance `<div id=box className="a b"><p onClick=@one>hi</p></div>`. Values are strings, a bare name means `true`, and text keeps its inner spaces. A value that starts with `@` is a handler: `@one` is one function that adds the word `one` to the log when it runs, and every `@one` in a scenario is that same function. A `click` runs the listeners of the target and then those of each ancestor, up to the root, in that order.

### Output

```
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
log <name>
```

A `dump` prints `dump <i>`, numbering the dumps of the run from 1, then the container's children in document order with their depth from 0: `node` for an element, `text` for a piece of text. An element gets a label the first time a dump shows it, `a` then `b` and on through `z`, `aa`, `ab`, and the same DOM node keeps that label in every later dump. A node that your library replaced is a new node and gets the next unused label, which is how the tests tell a kept node from a rebuilt one. Text nodes have no label, and the tests cannot tell a reused text node from a new one.

After the tag comes the quoted prop list. In alphabetical order it can hold `className=...`, `disabled=true` (only on a `button`, `input` or `textarea`), `id=...`, `title=...` and `value=...` (only on an `input` or `textarea`), each present only when it has left its default, which is empty text or false. Spaces separate the entries, and a node with none of them prints `""`. Inside a value, whitespace, `"` and `%` are percent-encoded, so `a b` is written `a%20b`. In a `text` line the characters `%`, `"` and line breaks are percent-encoded and spaces are left alone, and text nodes that touch print as a single line.

A `log` line is `log <name>` for each call of a `@name` handler since the last `log`, in order.

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

input:
```
tree a <div><p>A</p><b>B</b><i>C</i></div>
tree b <div><p>A</p><u>B</u><i>C</i></div>
render a
flush
dump
render b
flush
dump
```
output:
```
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

The `div`, the `p` and the `i` are the same nodes, so they keep `a`, `b` and `d`. The `b` became a `u`, so the old node left and a new one, labelled `e`, took its place between the other two. Appending the new node to the `div` would put `u` after `i` and the second dump would print `i` before `u`.

### Example 2: two adjacent removals (test `06-R5-four-to-two`)

input:
```
tree a <ul><li>a</li><li>b</li><li>c</li><li>d</li></ul>
tree b <ul><li>a</li><li>b</li></ul>
render a
flush
dump
render b
flush
dump
```
output:
```
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

The last two `li` nodes have no element left, and they stand next to each other. Each one has to be taken out of the `ul` once. If the removal of the first goes on to touch the second, as it does when a deleted fiber's removal also follows its siblings, the same node is removed twice and the run ends with a `NotFoundError` from `removeChild`.

### Example 3: the latest handler only (test `06-R6-handler-replaced`)

input:
```
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
```
output:
```
dump 1
node 0 a button "id=b"
text 1 "x"
log one
dump 2
node 0 a button "id=b"
text 1 "x"
log two
```

The button is kept, so it is `a` in both dumps. The second render gives it a different function, `two`. The old listener has to come off and the new one go on, or the second click would print `log one` and `log two`.

## Constraints

Trees have up to 28 nodes, use any tag name and only the props `id`, `className`, `title`, `disabled` and `onClick`, and never contain a function component or a key. A scenario renders two to five trees, with a `flush` after each, and no scenario uses `idle` or `ops`. A `click` always names an element with a unique id. The 54 tests are hand-made pairs and sequences for each requirement, two full sessions, and eight random ones: four edits of one tree, two chains of edits, two unrelated trees. `-Fresh` replaces the random ones. Ten seconds a test is far more than needed.

## Hints

<details><summary>Hint 1: where to start</summary>

Do the removals and the replacements last. First make the same tree rendered twice come out with every label unchanged; that needs only the last committed tree, a link from each new fiber to its twin, and `updateDom` in the commit. Then add one more behaviour at a time in this order: a changed type, extra new children, missing children.
</details>

<details><summary>Hint 2: the approach</summary>

After each commit, remember the root of the tree that went onto the page. `render` builds the next root with a link to that tree. When `reconcileChildren` makes the child fibers of a fiber, it walks the new elements and the old children of the fiber's twin together, one pair per position. For a pair of the same type it makes a fiber that reuses the old node and is tagged `UPDATE`. For any other pair it makes a fiber with no node that is tagged `PLACEMENT`, and puts the old child, if there is one, on a list of fibers to remove. When the elements run out, every old child left over goes on that list too. The commit first takes off every fiber on the list, then walks the new tree: the node of a `PLACEMENT` fiber goes into its parent, in front of the next sibling that is already on the page, and an `UPDATE` fiber gets `updateDom` with the props of its twin and its own.
</details>

<details><summary>Hint 3: the traps</summary>

- Compare `type` with `type`. Comparing an element with a fiber, or two props objects, never matches.
- After each element, step to the next old sibling, and when the elements are used up, go on through the old siblings that are left.
- Appending a new node to its parent is wrong. It goes in front of the node of the next sibling that is already on the page. Later siblings that are new themselves are not on the page yet and have to be skipped.
- Put a removed fiber on the list once. Do not walk on from it to its siblings or its children, since each of those has its own entry or goes with the parent.
- Start every render with an empty list of fibers to remove, or the next render takes last time's nodes out again.
- Remember the committed tree at the end of the commit, not at the start of the render. Do not change the committed fibers while a render is going on.
- Give `updateDom` the old fiber's props. Empty old props cannot clear a prop or remove a listener.
- The first render has no twin. Reading `alternate.child` of nothing throws; `alternate?.child` is undefined.
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

A commit that appends every new node to its parent fails like this:

```
  R3  a different type at a position gets a new node, and it stays at t... .    3 / 8   FAILED
      x 06-R3-middle-child  the middle of three children changes tag
          node[0]: expected (depth=1, label=e, tag=u, props=""), got (depth=1, label=d, tag=i, props="") - differs in label, tag  (in `dump 2`)
          likely cause: R3 - a different type at a position gets a new node, and it stays at that position among its siblings
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle), cross-checked line by line against a positional model in tools/gen_p06.py
          reproduce: py -P tools/run_js.py solutions 06 build/cases/06/06-R3-middle-child.in build/cases/06/06-R3-middle-child.out
```

## After you pass: compare with the author's code

[Pombo's Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation) keeps the last committed tree in `currentRoot` and gives every fiber an `alternate`, the old fiber at the same place, or `null` for a new one. `reconcileChildren(wipFiber, elements)` walks the elements and the old fibers together, in one loop that runs until both are used up, and tags each new fiber `UPDATE` or `PLACEMENT`. An old fiber to remove gets the tag `DELETION` and goes into a `deletions` array that `render` empties. `commitRoot` runs `commitWork` over `deletions`, then over `wipRoot.child`, and sets `currentRoot`. `commitWork` handles the three tags, calling `updateDom` for an update, as in 02. This is the structure the rules above describe. Here `currentRoot` and `deletions` live in `state`, and a removed fiber is only put on the list, with no `DELETION` tag written onto it (the last paragraph says why).

Two places in the post's `commitWork` break what the tests need. A fiber with `PLACEMENT` is added with `domParent.appendChild(fiber.dom)`, so a replaced child that has later siblings ends up after them, and the first example here fails. And `commitWork` goes on to `fiber.child` and `fiber.sibling` for every tag, a deleted fiber included. When two removals are adjacent, the walk from the first one reaches the second, which is tagged for deletion as well, removes it, and then the `deletions` array removes it again. That second removal of the same node makes `removeChild` throw `NotFoundError`, the commit stops before the kept nodes get their new props, and since the post's loop registers itself again only as its last statement, the library never runs again. Any render that removes or replaces two neighbouring children runs into it, for example a list that shrinks by two. Both are why the page asks for placement in front of a sibling and for each node to be removed once.

The same walk over deleted fibers re-applies old tags to the siblings and children it passes, which costs extra DOM calls that a dump does not show. The post also writes the tag `DELETION` onto a fiber that is already on the page. Its epilogue says that an update arriving in the middle of a render makes Didact throw the unfinished tree away and start again from the root. The tag outlives that restart, so a later render can remove a live node. The tests render only after a `flush`, so none of them restarts work, and they cannot show this. Hint 3 asks you to leave the committed fibers alone for that reason, and a list entry is all a removal needs. React matches unkeyed children by position, as here, and by key when there are keys; [React today](docs/react-today.md) lists the other differences, including how it sets props. The post's aside says React also uses keys, and 07 adds them. One more difference the tests cannot see: every `alternate` link keeps the previous render's fiber alive, and that fiber's own `alternate` reaches back further, so the post never lets go of an old tree.
