# 04 · Work in units: fibers

**Difficulty:** Medium · **Assignment** 4 of 12 · **Check:** `.\check 04`

**Tags**
- *Language:* [optional chaining](#primer/js-optional-chaining) (optional) · [module-level state](#primer/js-global-state)
- *Library:* [requestIdleCallback and timeRemaining()](#primer/dom-idle-callback) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [elements](#primer/react-elements) · [fibers](#primer/react-fibers) · [units of work and the work loop](#primer/react-work-loop)

## Read in the blog first

You can pass with this page alone. Pombo's account has two parts worth reading. [Step III: Concurrent Mode](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) explains why one long render hurts and introduces `requestIdleCallback`. Stop where the text announces the first unit of work and a `performUnitOfWork` that returns the next one, because code frames follow. [Step IV: Fibers](https://pomb.us/build-your-own-react/#step-iv-fibers) has the picture of the fiber tree and the paragraphs on how to find the next fiber: child, sibling, the parent's sibling, and further up until the root. Stop before the code frames that come after them.

## Learning material

- [Fibers](#primer/react-fibers): one fiber for each element and text node, plus one for the container, linked by `parent`, `child` and `sibling`. Each fiber is one unit of work.
- [Units of work and the work loop](#primer/react-work-loop): the loop that does a unit, checks the clock and stops when the time is up.
- [`requestIdleCallback` and `timeRemaining()`](#primer/dom-idle-callback): the harness plays the browser with a stand-in you drive by hand, and `idle` prints how often you read the clock.
- [Module-level state and why `state.js` is an object](#primer/js-global-state): `render.js` and `reconcile.js` have to see the same "next fiber".
- [Optional chaining `?.` and `??`](#primer/js-optional-chaining): the end of the work is a missing link, and the walk meets it often.
- [Elements, and what JSX turns into](#primer/react-elements): the children array and the `TEXT_ELEMENT` shape from 01 decide how many fibers a tree gets.
- [The harness and scenario files](#primer/workbook-harness): `idle` and `flush` are new here.

## Source material

- Rodrigo Pombo, [Step III: Concurrent Mode](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) and [Step IV: Fibers](https://pomb.us/build-your-own-react/#step-iv-fibers)
- MDN: [requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback) and [IdleDeadline.timeRemaining](https://developer.mozilla.org/en-US/docs/Web/API/IdleDeadline/timeRemaining)
- Andrew Clark, [React Fiber Architecture](https://github.com/acdlite/react-fiber-architecture)
- `harness/env.js`, the file that installs the `requestIdleCallback` the tests drive

## Where this fits

Assignment 03 drew a whole tree in one recursive call, and nothing can stop a recursion halfway. Here the same job becomes a loop over small pieces. `renderSync.js` stays on the shelf. The new library starts with four files, `state.js`, `render.js`, `reconcile.js` and `index.js`, and borrows only `createDom` from `dom.js`.

## The problem

Write the half of a renderer that can stop partway. `render` queues a job and returns. Whenever the browser is idle it calls `workLoop`, which builds the tree one fiber at a time and hands the thread back when time is up. A scenario plays the browser: it decides how many units of work each idle period may do, and looks at the container before and after.

### The modules

| File | Export | What it is |
|---|---|---|
| `src/didact/state.js` | `state` | One shared object. It holds the fiber to work on next and the root of the tree under construction. Name the fields as you like. |
| `src/didact/render.js` | `render(element, container)` | Queues the job. Does no work and touches nothing. |
| `src/didact/render.js` | `workLoop(deadline)` | The idle callback. Register it when the module loads, and again at the end of every call. |
| `src/didact/render.js` | `performUnitOfWork(fiber)` | Does the work of one fiber and returns the fiber to do next, or nothing after the last fiber. |
| `src/didact/reconcile.js` | `reconcileChildren(wipFiber, elements)` | Gives `wipFiber` one new child fiber per element, linked in order. |
| `src/didact/index.js` | default `Didact` | `{ createElement, render }`, the object the entry program hands to the harness. Exporting the same two names as named exports too is fine. |

A fiber is a plain object with `type`, `props`, `dom`, `parent`, `child` and `sibling`. A link that leads nowhere (the root's `parent` and `sibling`, a leaf's `child`) may be `null` or `undefined`; nothing looks at the difference. The root fiber has no type: its `dom` is the container and its `props.children` is `[element]`. An element is `{ type, props }` with `props.children` always an array, and a text piece is `{ type: "TEXT_ELEMENT", props: { nodeValue, children: [] } }`. The scenarios build their elements with the harness's own `h`, so your `createElement` is not involved. To make a DOM node, call `createDom` from `dom.js`; it accepts a fiber, since a fiber has a `type` and `props`.

### Input

The checker runs `node assignments/assignment_04_fibers.js <input-file> <output-file>`. That file is short. It imports `../harness/env.js` before anything else, so that `document` and `requestIdleCallback` exist by the time `render.js` loads. It imports your `Didact` from `../src/didact/index.js` and `runScenarioFile` from `../harness/scenario.js`, and it finishes with `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, which reads the scenario, runs it against your library and writes the output. The Boilerplate has it finished; from scratch, write those lines yourself.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Defines a tree. Prints nothing. |
| `render <name>` | Calls `Didact.render(element, container)` with the element built from the tree and the page's `#root` div as the container. Prints nothing. |
| `idle <k>` | Runs one idle period with budget `k`, a whole number from 1 up or the word `inf`, and prints one line. |
| `flush` | Runs periods with an unlimited budget until one of them never calls `timeRemaining()`. Prints nothing. |
| `dump` | Prints what the container holds. |

Trees are one line of HTML-like text, as in `<div id=a className="big one">text <b>bold</b></div>`. Attribute values are strings, a bare name stands for `true`, and text keeps its inner spaces. Whitespace between two tags is ignored, and `input`, `br` and `hr` take no closing tag. Every text piece becomes a text element and everything in angle brackets becomes an element.

An idle period works like this:

- It calls each callback that is registered when it starts, handing every one the same deadline, `{ didTimeout: false, timeRemaining() }`. A callback registered while the period runs waits for the next period.
- `timeRemaining()` counts its calls during the period. It returns 1 until the call whose number is `k`, and from that call on it returns 0. With `inf` it always returns 1.
- The period prints the number of calls it counted.

### Output

```
idle <n>
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

`idle <n>` is the number of times your code called `timeRemaining()` during the period. `dump <i>` counts the dumps of the run from 1, and the lines after it describe the container's children in document order, the container itself left out, children indented by depth, starting at 0. An empty container prints the `dump` line alone.

A `node` line gives the element's tag in lower case and a label. The first element a dump shows is `a`, the next `b`, and so on through `z` and then `aa`, `ab`. Between the quotes go the props that have left their defaults, each as `name=value`, alphabetically, one space apart. Only these five can appear:

| Prop | Shown when |
|---|---|
| `className`, `id`, `title` | the value is not empty |
| `disabled` | it is true, on a `button`, `input` or `textarea`; printed `disabled=true` |
| `value` | the value is not empty, on an `input` or `textarea` |

Run a value through `encodeURIComponent` when it contains whitespace, a `"` or a `%`: `big one` turns into `big%20one`. An element with nothing to show prints `""`. A `text` line shows the text with `%`, `"` and line breaks encoded and spaces kept. Text nodes that touch print as one line, and an empty text node prints nothing.

### Units of work

A unit of work is one fiber, and a render consists of these fibers:

- the root fiber, for the container,
- one for every element in the tree,
- one for every text node.

A tree with `E` elements and `T` text pieces takes `1 + E + T` units. `<p>hello</p>` takes 3: the root, `p` and the text. The root counts although it has no node to make, and a text piece counts although it has no children.

Doing a unit has three steps. First, give the fiber its node by calling `createDom`, unless it has one (the root has: it is the container). Second, give it its children: a fiber for each element in `fiber.props.children`, in order, each pointing back with `parent`, with `child` set to the first and `sibling` chaining the rest, and none of them holding a node yet. Third, pick the fiber to do next.

The next fiber is the first match in this list:

1. the fiber's `child`
2. its `sibling`
3. the `sibling` of its parent (the post calls it the uncle), and if the parent has none, the sibling of the grandparent, and so on up the `parent` chain
4. nothing, once the climb has passed the root: the render is finished.

For `div > (h1 > (p, a), h2)` the units go root, `div`, `h1`, `p`, `a`, `h2`. After `a` there is no child and no sibling, so the walk climbs to `h1` and takes its sibling `h2`.

### Reading the clock

`workLoop` does a unit, then calls `timeRemaining()` once. If the value is below 1 it stops, otherwise it does the next unit. A period with budget `k` therefore does `k` units when `k` or more are waiting, and all of them when fewer are. Since the period prints the number of reads, `idle k` prints the smaller of `k` and the units left.

The loop reads the clock after every unit, the last one of the tree included, and never when there is no unit to do. At the end of every call it registers itself for the next period, whether or not it did anything. A loop that forgets stops being called, and a `render` after a quiet period would never run.

### What may be on the page

`render` leaves the container alone and does not run a unit. This assignment leaves open when a unit attaches its node to the page. Attaching in each unit, as the post does, and attaching the whole tree after the last unit both pass; assignment 05 asks for the second. A scenario can therefore look at the container at two moments only. Before the first period has run it must be empty, and after `flush` it must hold the whole tree in order. Each scenario calls `render` at most once.

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

input:
```
tree a <div><h1><p></p><a></a></h1><h2></h2></div>
render a
idle inf
idle inf
```
output:
```
idle 6
idle 0
```

The fibers are the root, `div`, `h1`, `p`, `a` and `h2`. The unlimited period reads the clock once after each, which makes 6, and the second period has nothing left and reads nothing. If your first line says 5, the root was not counted, or the walk stopped at `a` instead of climbing to `h2`.

### Example 2: periods of three (test `04-R3-budget-3-post-text`)

input:
```
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 3
idle 3
idle 3
idle 3
idle 3
```
output:
```
idle 3
idle 3
idle 3
idle 1
idle 0
```

The tree has 5 elements and 4 text pieces, so 10 units with the root. Three periods use up 9. The fourth has one unit left, does it, reads the clock once, and finds no more work. The fifth finds none from the start and prints 0.

### Example 3: stop, then flush (test `04-E2E-resume-after-periods`)

input:
```
tree a <div><div><div><p>a</p><p>b</p></div><p>c</p></div><p>d</p></div>
render a
idle 4
idle 1
flush
dump
```
output:
```
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

Twelve units in all. Five are done after the two periods, and the next fiber is waiting in `state` while the browser has the thread. `flush` carries on from there, and it must pick up the walk where it stopped. The `dump` is the first one in the scenario, so it is number 1.

## Constraints

The trees have between 2 and 60 units and consist of plain elements and text, with no handlers, components or keys. Each scenario renders at most once. Budgets are whole numbers from 1 up, or `inf`, and `idle 0` does not occur. Dumps come only right after `render` or after `flush`. The 47 tests are examples of each requirement on hand-picked trees, three whole scenarios and six seeded random ones, three of them on period sizes and three on whole trees; `-Fresh` replaces the random ones. Each test gets 10 seconds, and a correct solution takes a few milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Get the count right before you worry about the page. Make `render` store a root fiber, write the loop around a `performUnitOfWork` that only returns the next fiber, and try `render a`, `idle inf` on the tree `<br>`. It has to print `idle 2`. The `idle` lines depend on the loop alone, so you can check them while the rest is still a stub.
</details>

<details><summary>Hint 2: the approach</summary>

Put the next fiber to do in the shared state. `render` sets it to a fresh root fiber and returns. The loop takes the fiber, performs it, stores what comes back, reads the clock, and goes round again while the stored fiber exists and the clock allows. Performing a fiber means making its node, asking `reconcileChildren` for its children, and walking to the next one: child first, then sibling, then up the parents until one has a sibling. Register the loop once when `render.js` loads, and again at the end of each call.
</details>

<details><summary>Hint 3: the traps</summary>

- The root fiber is a unit like any other. It already holds a node, the container, so it must not get another one.
- Text pieces are fibers. Their `props.children` is an empty array, which is no reason to skip them.
- Read the clock once, after the unit. Two units per read, or a read before the unit, changes what `idle` prints; so does a read in a call that had no work.
- Call `requestIdleCallback(workLoop)` at the end of every call, including the ones that found nothing to do.
- A fiber with no child and no sibling is not the end. Climb through `parent` until you find a sibling, and stop only when the climb runs out.
- `render` must not run anything, not even the root's unit. A `dump` right after it has to be empty.
- Assign to `state.nextUnitOfWork`, not to an imported variable, which a module may not reassign.
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

A walk that never climbs past a fiber without a sibling fails like this:

```
  R2  one unit of work per fiber: the root fiber, every element and eve... .    4 / 8   FAILED
      x 04-R2-units-post-shape  div > (h1 > (p, a), h2): six units without text
          idle[0]: expected (units=6), got (units=5) - differs in units
          likely cause: R2 - one unit of work per fiber: the root fiber, every element and every text node, and nothing else
          expected values from: React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula (1 root fiber + elements + text nodes) for the idle lines
          reproduce: py -P tools/run_js.py solutions 04 build/cases/04/04-R2-units-post-shape.in build/cases/04/04-R2-units-post-shape.out
```

## After you pass: compare with the author's code

[Pombo's Step IV](https://pomb.us/build-your-own-react/#step-iv-fibers) builds the same machine from `render`, `workLoop`, `performUnitOfWork` and `createDom`. `render` sets `nextUnitOfWork` to a root fiber whose `dom` is the container, the loop reads `timeRemaining()` after each unit, and `performUnitOfWork` creates the node, makes one fiber per child, and returns the child, the sibling or the uncle. The loop in the post is `workLoop(deadline)` with a `shouldYield` flag, which is what the tests expect, including the read after the last unit. The post's own unit creates its node and attaches it to `fiber.parent.dom` in the same step, so the page fills up while the work runs. That is allowed here and is what 05 changes ([Step V](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases)).

The post keeps `nextUnitOfWork` as a variable of its single file, and an ES module cannot reassign a variable it imported, so this library keeps it in `state`, together with `wipRoot`, which the post introduces only in Step V. In the post the loop over a fiber's children sits inside `performUnitOfWork` until Step VI pulls it out as `reconcileChildren`; here that function exists from the start, so that 06 can replace it. The post has nothing that counts units: the harness counts your `timeRemaining()` reads, which equal the units because the loop reads once per unit.

The post's loop ends with `requestIdleCallback(workLoop)` as its last statement, so an exception inside a unit means the loop is never scheduled again. Registering the callback from a `finally` block keeps the loop alive after an error. No test throws from a unit, and 06 names a bug in the post that ends the loop this way. The post also says React no longer uses `requestIdleCallback`, and [React today](docs/react-today.md) lists what it uses instead and when a render can pause.
