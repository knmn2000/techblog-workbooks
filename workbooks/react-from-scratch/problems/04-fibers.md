# 04 · Work in units: fibers

**Difficulty:** Medium · **Assignment** 4 of 12 · **Check:** `.\check 04`

**Tags**
- *Language:* [optional chaining](#primer/js-optional-chaining) (optional) · [module-level state](#primer/js-global-state)
- *Library:* [requestIdleCallback and timeRemaining()](#primer/dom-idle-callback) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [elements](#primer/react-elements) · [fibers](#primer/react-fibers) · [units of work and the work loop](#primer/react-work-loop)

## Read in the blog first

You can skip the post and still pass. If you do read Pombo, two parts pay off. [Step III: Concurrent Mode](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) says why one long render hurts and brings in `requestIdleCallback`; stop where the text announces the first unit of work and a `performUnitOfWork` that returns the next one, because code frames follow. [Step IV: Fibers](https://pomb.us/build-your-own-react/#step-iv-fibers) has the picture of the fiber tree and the paragraphs on finding the next fiber: child, sibling, the parent's sibling, then further up until the root. Stop before the code frames that come after them.

## Learning material

- [Fibers](#primer/react-fibers): the tree you walk. A fiber for every element and text node, one more for the container, tied together with `parent`, `child` and `sibling`. Each fiber is one unit of work.
- [Units of work and the work loop](#primer/react-work-loop): do a unit, look at the clock, quit when it says time is up.
- [`requestIdleCallback` and `timeRemaining()`](#primer/dom-idle-callback): the harness has a stand-in for the browser that you drive by hand, and `idle` prints how often your code read the clock.
- [Module-level state and why `state.js` is an object](#primer/js-global-state): `render.js` and `reconcile.js` have to see the same "next fiber".
- [Optional chaining `?.` and `??`](#primer/js-optional-chaining): the end of the work is a missing link, and the walk meets one often.
- [Elements, and what JSX turns into](#primer/react-elements): the children array and the `TEXT_ELEMENT` shape from 01 settle how many fibers a tree gets.
- [The harness and scenario files](#primer/workbook-harness): `idle` and `flush` are new here.

## Source material

- Rodrigo Pombo, [Step III: Concurrent Mode](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) and [Step IV: Fibers](https://pomb.us/build-your-own-react/#step-iv-fibers)
- MDN: [requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback) and [IdleDeadline.timeRemaining](https://developer.mozilla.org/en-US/docs/Web/API/IdleDeadline/timeRemaining)
- Andrew Clark, [React Fiber Architecture](https://github.com/acdlite/react-fiber-architecture)
- `harness/env.js`, the file that installs the `requestIdleCallback` the tests drive

## Where this fits

Assignment 03 drew a whole tree in one recursive call, and a recursion can't be paused halfway. Here the same job turns into a loop over small pieces. `renderSync.js` stays on the shelf. The new library starts with four files, `state.js`, `render.js`, `reconcile.js` and `index.js`, and takes only `createDom` from `dom.js`.

## The problem

Write the half of a renderer that can stop partway. `render` queues a job and returns. When the browser is idle it calls `workLoop`, which builds the tree one fiber at a time and gives the thread back once time runs out. In the tests a scenario plays the browser: it sets how many units of work each idle period may do, and looks at the container before and after.

### The modules

| File | Export | What it is |
|---|---|---|
| `src/didact/state.js` | `state` | One shared object holding the fiber to work on next and the root of the tree under construction. The field names are yours. |
| `src/didact/render.js` | `render(element, container)` | Queues the job. Does no work and touches nothing. |
| `src/didact/render.js` | `workLoop(deadline)` | The idle callback. Register it when the module loads, and again at the end of every call. |
| `src/didact/render.js` | `performUnitOfWork(fiber)` | Does one fiber's work and returns the fiber to do next, or nothing after the last one. |
| `src/didact/reconcile.js` | `reconcileChildren(wipFiber, elements)` | Gives `wipFiber` one new child fiber per element, linked in order. |
| `src/didact/index.js` | default `Didact` | `{ createElement, render }`, the object the entry program hands to the harness. Exporting the same two names as named exports too is fine. |

A fiber is a plain object with `type`, `props`, `dom`, `parent`, `child` and `sibling`. A link that goes nowhere (the root's `parent` and `sibling`, a leaf's `child`) can be `null` or `undefined`; nothing tells them apart. The root fiber has no type. Its `dom` is the container and its `props.children` is `[element]`. Elements are `{ type, props }` with `props.children` always an array, and a text piece is `{ type: "TEXT_ELEMENT", props: { nodeValue, children: [] } }`. The scenarios build their elements with the harness's own `h`, so your `createElement` is not involved. For a DOM node, call `createDom` from `dom.js`. It takes a fiber without complaint, since a fiber has a `type` and `props`.

### Input

Each test runs `node assignments/assignment_04_fibers.js <input-file> <output-file>`. The file is short. It imports `../harness/env.js` first, which gives you `document` and `requestIdleCallback` before `render.js` loads. Then come your `Didact` from `../src/didact/index.js` and `runScenarioFile` from `../harness/scenario.js`, and a last line, `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, which reads the scenario, runs it against your library and writes the output. The Boilerplate ships it complete. Starting from scratch, you write those lines yourself.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Names a tree for later. No output. |
| `render <name>` | `Didact.render(element, container)` on the named tree, with the page's `#root` div as the container. No output. |
| `idle <k>` | One idle period with budget `k`, a whole number from 1 up or the word `inf`. Prints one line. |
| `flush` | Idle periods with an unlimited budget, repeated until one never calls `timeRemaining()`. No output. |
| `dump` | Prints what the container holds. |

A tree is one line of HTML-like text, like `<div id=a className="big one">text <b>bold</b></div>`. Attribute values are strings and a bare name means `true`. Text keeps its inner spaces; whitespace between two tags is dropped. `input`, `br` and `hr` have no closing tag. Each piece of text becomes a text element, and each thing in angle brackets an element.

One idle period goes like this:

- Every callback registered when the period starts is called with the same deadline, `{ didTimeout: false, timeRemaining() }`. A callback registered during the period waits for the next one.
- `timeRemaining()` counts the calls made during the period. Calls before number `k` return 1, and call `k` and every later call return 0. With `inf` it returns 1 every time.
- The period prints how many calls it counted.

### Output

```
idle <n>
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

`idle <n>` is how many times your code called `timeRemaining()` during that period. `dump <i>` numbers the dumps of the run from 1, and the lines under it describe the container's children in document order, indented by depth from 0. The container itself is not listed. An empty container prints the `dump` line and nothing else.

A `node` line carries the element's tag in lower case and a label. The first element a dump shows is `a`, then `b`, on through `z`, then `aa`, `ab`. Between the quotes sit the props that differ from their defaults, written `name=value`, alphabetical, one space apart. Only these five can appear:

| Prop | Shown when |
|---|---|
| `className`, `id`, `title` | the value is not empty |
| `disabled` | it is true, on a `button`, `input` or `textarea`; printed `disabled=true` |
| `value` | the value is not empty, on an `input` or `textarea` |

A value containing whitespace, a `"` or a `%` goes through `encodeURIComponent`, so `big one` prints as `big%20one`. An element with nothing to show gets `""`. A `text` line encodes `%`, `"` and line breaks and leaves spaces alone. Text nodes that touch print as one line, and an empty text node prints nothing.

### Units of work

A unit of work is one fiber. A render has these:

- the root fiber, for the container,
- one for every element in the tree,
- one for every text node.

With `E` elements and `T` text pieces, a tree takes `1 + E + T` units. `<p>hello</p>` takes 3: the root, `p` and the text. The root counts even though it has no node to make, and a text piece counts even though it has no children.

Doing a unit takes three steps. One: give the fiber its node with `createDom`, unless it already has one (the root does; its node is the container). Two: make its children, a fiber for each element in `fiber.props.children`, in order. Each points back with `parent`, `child` goes to the first, `sibling` chains the rest, and none of them holds a node yet. Three: choose the fiber to do next.

The next fiber is the first match in this list:

1. the fiber's `child`
2. its `sibling`
3. the `sibling` of its parent (the post calls it the uncle), and if the parent has none, the sibling of the grandparent, and so on up the `parent` chain
4. nothing, once the climb has passed the root: the render is finished.

Take `div > (h1 > (p, a), h2)`. The units go root, `div`, `h1`, `p`, `a`, `h2`. After `a` there is no child and no sibling: the walk climbs to `h1` and takes its sibling `h2`.

### Reading the clock

`workLoop` does one unit, calls `timeRemaining()` once, and stops if the value is below 1; otherwise it does another unit. With budget `k` that means `k` units when at least `k` are waiting, and all of them when fewer are. The period prints its number of reads, which makes `idle k` print the smaller of `k` and the units left.

The read comes after every unit, the last unit of the tree included, and never when there is no unit to do. At the end of every call the loop registers itself for the next period, whether or not it did anything. Forget that and it stops being called; a `render` that arrives after a quiet period never runs.

### What may be on the page

`render` leaves the container alone and runs no unit. When a unit attaches its node to the page is left open here. Attaching in every unit, as the post does, passes, and so does attaching the whole tree after the last unit, which is what 05 asks for. A scenario can therefore look at the container at two moments only: before the first period has run, when it must be empty, and after `flush`, when it must hold the whole tree in order. A scenario calls `render` at most once.

## Requirements

- **R1** `render` only schedules the work: right after it the container is still empty and no unit has run.
- **R2** There is one unit of work per fiber: the root fiber, every element and every text node, and nothing else.
- **R3** The loop reads `timeRemaining()` once after each unit, so `idle k` prints the smaller of `k` and the units left.
- **R4** The walk reaches every fiber, depth first: child, then sibling, then the parent's sibling and so on up. After `flush` the container holds the whole tree in order.
- **R5** With no work left, a period reads nothing and prints 0, before any `render` and after the tree is done, whatever the budget.
- **R6** Every node carries the props and the text of its element.
- **E2E** Whole scenarios: the empty page, uneven periods, the finished page.

## Examples

### Example 1: six units without any text (test `04-R2-units-post-shape`)

```
input:
tree a <div><h1><p></p><a></a></h1><h2></h2></div>
render a
idle inf
idle inf

output:
idle 6
idle 0
```

Six fibers: the root, `div`, `h1`, `p`, `a` and `h2`. The unlimited period reads the clock after each of them, which makes 6, and the second period finds nothing and reads nothing. A first line saying 5 means the root went uncounted, or the walk stopped at `a` instead of climbing to `h2`.

### Example 2: periods of three (test `04-R3-budget-3-post-text`)

```
input:
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 3
idle 3
idle 3
idle 3
idle 3

output:
idle 3
idle 3
idle 3
idle 1
idle 0
```

5 elements, 4 text pieces and the root make 10 units, and three periods use up 9 of them. The fourth does the last unit, reads the clock once and finds nothing more. The fifth has nothing from the start and prints 0.

### Example 3: stop, then flush (test `04-E2E-resume-after-periods`)

```
input:
tree a <div><div><div><p>a</p><p>b</p></div><p>c</p></div><p>d</p></div>
render a
idle 4
idle 1
flush
dump

output:
idle 4
idle 1
dump 1
node 0 a div ""
node 1 b div ""
node 2 c div ""
node 3 d p ""
text 4 "a"
node 3 e p ""
text 4 "b"
node 2 f p ""
text 3 "c"
node 1 g p ""
text 2 "d"
```

Twelve units in all. After the two periods five are done, and the next fiber waits in `state` while the browser has the thread. `flush` has to pick the walk up where it stopped. This is the first `dump` of the scenario, so it is number 1.

## Constraints

Trees run from 2 to 60 units and hold plain elements and text only: no handlers, components or keys. A scenario renders at most once. Budgets are whole numbers from 1 up, or `inf`; `idle 0` never appears. A `dump` comes only right after `render` or after `flush`. The 47 tests are examples of each requirement on hand-picked trees, three whole scenarios and six seeded random ones, three on period sizes and three on whole trees. `-Fresh` replaces the random ones. Each test gets 10 seconds, and a correct solution takes a few milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Count first, page later. Have `render` store a root fiber, write the loop around a `performUnitOfWork` that does nothing except return the next fiber, and run `render a`, `idle inf` on the tree `<br>`. It has to print `idle 2`. The `idle` lines depend on the loop alone, which lets you check them while everything else is still a stub.
</details>

<details><summary>Hint 2: the approach</summary>

Keep the next fiber to do in the shared state. `render` sets it to a fresh root fiber and returns. The loop takes that fiber, performs it, stores what comes back, reads the clock, and goes round again while a fiber is stored and the clock allows. To perform a fiber, make its node, ask `reconcileChildren` for its children and walk to the next fiber: the child first, then the sibling, then up through the parents until one has a sibling. Register the loop once when `render.js` loads, and again at the end of each call.
</details>

<details><summary>Hint 3: the traps</summary>

- Count the root fiber as a unit like the rest. Its node is already there, the container, so don't make it another.
- Text pieces are fibers too. An empty `props.children` is no reason to skip one.
- One read per unit, taken after it. Two units per read, a read before the unit, or a read in a call that had no work all change what `idle` prints.
- End every call with `requestIdleCallback(workLoop)`, the ones that found nothing to do included.
- No child and no sibling does not mean the end. Climb through `parent` to the first fiber that has a sibling; the walk is over only when the climb runs out.
- `render` runs nothing, not even the root's unit. A `dump` straight after it has to be empty.
- Assign to `state.nextUnitOfWork`. A module may not reassign an imported variable.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
render(element, container):
    root = fiber with dom = container and props.children = [element]
    state.wipRoot = root
    state.nextUnitOfWork = root

workLoop(deadline):
    while state.nextUnitOfWork exists:
        state.nextUnitOfWork = performUnitOfWork(state.nextUnitOfWork)
        if deadline.timeRemaining() < 1: leave the while loop
    requestIdleCallback(workLoop)

requestIdleCallback(workLoop)          once, at the bottom of the module

performUnitOfWork(fiber):
    fiber.dom = createDom(fiber) if it has none
    attach it to fiber.parent.dom, if there is a parent (optional in this assignment)
    reconcileChildren(fiber, fiber.props.children)
    return the next fiber, or nothing

next fiber:
    if fiber has a child: that child
    walk f from fiber up through parent: the first f with a sibling gives that sibling
    otherwise nothing
```
</details>

## Checking your solution

```
.\check 04                         every test, grouped by requirement
.\check 04 -Case 04-R3-mixed-budgets   one test: its input, the expected lines, and what you printed
.\check 04 -Fresh                  six new random scenarios, for a run on trees you have not seen
.\check 04 -Dispute <id> "why"     set a test aside that you are sure is wrong
```

With a walk that never climbs past a fiber without a sibling, the report looks like this:

```
  R2  one unit of work per fiber: the root fiber, every element and eve... .    4 / 8   FAILED
      x 04-R2-units-post-shape  div > (h1 > (p, a), h2): six units without text
          idle[0]: expected (units=6), got (units=5) - differs in units
          likely cause: R2 - one unit of work per fiber: the root fiber, every element and every text node, and nothing else
          expected values from: React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula (1 root fiber + elements + text nodes) for the idle lines
          reproduce: py -P tools/run_js.py solutions 04 build/cases/04/04-R2-units-post-shape.in build/cases/04/04-R2-units-post-shape.out
```

## After you pass: compare with the author's code

[Pombo's Step IV](https://pomb.us/build-your-own-react/#step-iv-fibers) builds this same machine out of `render`, `workLoop`, `performUnitOfWork` and `createDom`. `render` points `nextUnitOfWork` at a root fiber whose `dom` is the container. `performUnitOfWork` creates the node, makes one fiber per child, and returns the child, the sibling or the uncle. The post's `workLoop(deadline)` carries a `shouldYield` flag and reads `timeRemaining()` after each unit, the last one included, which is what the tests expect. Its unit also attaches its node to `fiber.parent.dom` in the same step, and the page fills up while the work runs. That is allowed here, and 05 is where it changes ([Step V](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases)).

The post keeps `nextUnitOfWork` as a variable in its one file. An ES module cannot reassign a variable it imported, so here it lives in `state`, beside `wipRoot`, which the post brings in only at Step V. In the post the loop over a fiber's children sits inside `performUnitOfWork` until Step VI pulls it out as `reconcileChildren`. That function exists from the start here, to give 06 something to replace. Nothing in the post counts units. The harness counts your `timeRemaining()` reads instead, and they equal the units because the loop reads once per unit.

In the post, `requestIdleCallback(workLoop)` is the loop's last statement, so an exception inside a unit means it is never scheduled again. Registering it from a `finally` block keeps the loop alive after an error. No test throws from a unit, and 06 names a bug in the post that ends the loop this way. The post also says React no longer uses `requestIdleCallback`. [React today](docs/react-today.md) lists what it uses instead and when a render can pause.
