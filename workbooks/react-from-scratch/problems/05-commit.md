# 05 · Render phase, then commit

**Difficulty:** Medium · **Assignment** 5 of 12 · **Check:** `.\check 05`

**Tags**
- *Language:* [module-level state](#primer/js-global-state)
- *Library:* [appendChild, insertBefore, removeChild](#primer/dom-tree-editing) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [the render phase and the commit phase](#primer/react-render-commit) · [fibers](#primer/react-fibers)

## Read in the blog first

This page is enough to pass. If you want Pombo's version, read [Step V: Render and Commit Phases](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases). It is six short paragraphs with the code frames in between: why attaching a node in every unit is a problem, what `wipRoot` is, and how a finished tree gets appended. Read the paragraphs and leave the frames until you have a solution of your own.

## Learning material

- [The render phase and the commit phase](#primer/react-render-commit): the units build the tree and leave the page alone, and one uninterrupted pass then attaches it.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): attaching a node to a parent. The harness counts an `insert` for a node that has no parent yet and a `move` for one that already has one.
- [Fibers](#primer/react-fibers): the commit walks the finished fiber tree through `child` and `sibling`, and each fiber carries the node to attach.
- [Module-level state and why `state.js` is an object](#primer/js-global-state): `render.js` leaves the finished root where `commit.js` can find it.
- [The harness and scenario files](#primer/workbook-harness): `dump` now sits between idle periods, and `ops` reads the page's counters.

## Source material

- Rodrigo Pombo, [Step V: Render and Commit Phases](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases)
- react.dev, [Render and commit](https://react.dev/learn/render-and-commit)
- MDN: [Node.appendChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
- `harness/minidom.js`, which says how `insert`, `move` and `remove` are counted

## Where this fits

In 04 a unit could append its node, as the post's does, so the page could grow while the browser was free to paint it. This one closes that gap. You add `src/didact/commit.js` and change the loop in `render.js`. The walk, `reconcile.js` and `state.js` are the 04 versions.

## The problem

Build the tree without showing any of it, and put the whole tree on the page in one pass at the end. A scenario renders a tree, runs idle periods of its own choosing, dumps the container after some of them, and asks the harness how many nodes your code has attached.

### The modules

| File | Export | What it is |
|---|---|---|
| `src/didact/commit.js` | `commitRoot()` | Attaches the finished tree to the container and clears the tree under construction. |
| `src/didact/commit.js` | `commitWork(fiber)` | Attaches one fiber's node to the node of its parent fiber and goes on to the fibers below it. |
| `src/didact/render.js` | `workLoop`, `performUnitOfWork` | The 04 loop and unit, changed: no unit touches the page, and the loop calls `commitRoot` when the work is done. |

`state` keeps the fields it had in 04, and you may add more.

### Input

The checker runs `node assignments/assignment_05_commit.js <input-file> <output-file>`. The file has the shape it had in 04: `../harness/env.js` is imported first, because the loop needs `requestIdleCallback` as soon as `render.js` loads; then `Didact` comes in from `../src/didact/index.js` and `runScenarioFile` from `../harness/scenario.js`; the last line awaits `runScenarioFile(process.argv[2], process.argv[3], Didact)`. The Boilerplate has it finished, and a from-scratch start has to write it. A scenario renders one tree onto the empty container and never renders again.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Defines a tree from one line of HTML-like text, for instance `<ul id=l><li>one</li><li>two</li></ul>`. Prints nothing. |
| `render <name>` | Calls `Didact.render(element, container)`. Prints nothing and runs no work. |
| `idle <k>` | One idle period. `timeRemaining()` returns 1 until call number `k`, then 0 (with `inf`, always 1). Prints the number of calls. `k` is 1 or more, or `inf`. |
| `flush` | Keeps running unlimited periods until one finds nothing to do, meaning a period that never reads the clock. No output. |
| `dump` | Prints the container's contents. |
| `ops insert move remove` | Prints three counters, then sets all counters back to 0. |

The three counters measure your code's calls on DOM nodes since the previous `ops` or the start of the scenario. `insert` counts `appendChild` and `insertBefore` calls whose node had no parent yet. `move` counts the same calls when the node already had a parent. `remove` counts `removeChild` and `remove` calls. No other counter is asked for here, so how many nodes you create and how many properties you write is your own business.

### Output

```
idle <n>
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
ops <insert> <move> <remove>
```

`idle <n>` is how many times `timeRemaining()` was called in the period. A `dump` prints `dump <i>`, numbering the dumps of the run from 1, and then the children of the container in document order, indented by depth from 0, each element as a `node` line and each text as a `text` line. Nothing follows the `dump` line when the container is empty. Elements are labelled `a`, `b`, `c` and onwards in the order a dump first meets them. The quoted `<props>` at the end of a `node` line list what differs from the defaults, as `name=value`, in alphabetical order. Five props can show: `className`, `id` and `title` when not empty, `disabled` on buttons, inputs and textareas (as `disabled=true`), and `value` on inputs and textareas when not empty. Values with whitespace, `"` or `%` in them go through `encodeURIComponent`, so a space is `%20`. Nothing to list means `""`. In a `text` line, `%`, `"` and line breaks are encoded and spaces stay.

### While the units run

Units are counted as in assignment 04: the root fiber, then one per element and one per text node, so a tree with `E` elements and `T` text pieces takes `1 + E + T` units. A period with budget `k` does `k` units if that many are waiting, and all of them otherwise. It reads `timeRemaining()` once after each unit, the last unit of the tree included, and not at all when there is nothing to do.

The page is what changes. A unit may create the node of its fiber and set its props, but it may not attach anything to the container or to another node. A `dump` taken after a period that leaves units undone shows an empty container, and `ops insert move remove` shows `0 0 0`.

### The period that ends the work

The period whose last unit finishes the tree also commits: right after that unit, in the same call of the loop, every element and text node of the finished tree is attached to its parent's node. When `idle` returns, the container holds the whole tree. The pass does not count as a unit and does not call `timeRemaining()`, so `idle` prints what it printed in 04.

When a period uses up the last of the work with its final unit, as `idle 9` does on a tree of 9 units, the commit still happens in that period. There is no extra period for it.

The pass attaches each node once, so the three counters read `N 0 0` for the period of the commit, where `N` is the number of elements plus text nodes (the root fiber has no node of its own to attach, so `N` is one less than the units). The order in which the pass visits the fibers is not visible to the checker, so a parent may go in before or after its children and the walk may be recursive or a loop. It has to reach every fiber, siblings included, and the siblings of one parent have to be attached in their tree order, or the children end up in the wrong order.

### After the commit

The tree is on the page, so later periods, and `flush`, have nothing to do. They print 0, leave the container alone, and the counters stay at 0. A loop that forgets to clear its finished root commits again on every period, and its `move` counter shows it.

## Requirements

- **R1** While units run the container stays empty: a `dump` after a period that leaves work undone shows no node.
- **R2** The period that runs the last unit also commits: a `dump` right after it shows the whole tree.
- **R3** The commit adds no unit and no `timeRemaining()` read, so `idle k` still prints the smaller of `k` and the units left, and later periods print 0.
- **R4** Each node is inserted once, by the commit: `ops insert move remove` prints `0 0 0` while work is waiting, `N 0 0` after the period of the last unit (N is the number of elements plus text nodes), and `0 0 0` after that.
- **R5** The committed tree has the right shape: nesting, sibling order, props and text.
- **E2E** Whole scenarios mixing periods, dumps and counters.

## Examples

### Example 1: dumping after every period (test `05-R1-empty-between-periods`)

input:
```
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 3
dump
idle 3
dump
idle 3
dump
```
output:
```
idle 3
dump 1
idle 3
dump 2
idle 3
dump 3
```

Ten units, and three periods of three leave one undone. Nothing has been committed, so all three dumps stop after their header line. Nodes may already exist, since the units create them, and they are all detached.

### Example 2: the period that commits (test `05-R2-last-period-of-three`)

input:
```
tree a <div><section><article><span><em><b><div></div></b></em></span></article></section></div>
render a
idle 3
idle 3
idle 3
dump
```
output:
```
idle 3
idle 3
idle 2
dump 1
node 0 a div ""
node 1 b section ""
node 2 c article ""
node 3 d span ""
node 4 e em ""
node 5 f b ""
node 6 g div ""
```

The chain has seven elements and a root fiber, so eight units. The third period has two units left. It does them, prints 2 (no ninth read for the commit), and has the whole chain on the page by the time `dump` runs. A solution that commits at the start of the next period prints the same numbers and then dumps an empty container.

### Example 3: counting inserts (test `05-R4-insert-at-commit`)

input:
```
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 4
ops insert move remove
idle 4
ops insert move remove
idle 4
ops insert move remove
```
output:
```
idle 4
ops 0 0 0
idle 4
ops 0 0 0
idle 2
ops 9 0 0
```

The tree has 5 elements and 4 text pieces. Nine nodes go in at the commit, in one period, and none of them has been in the DOM before, so every call counts as an `insert`. A `move` would mean you appended a node that already had a parent, which is what attaching in the unit and again in the commit does.

## Constraints

The trees hold between 2 and 60 units of plain elements and text, with no handlers, components or keys, and each scenario renders one tree. Budgets are whole numbers from 1 up or `inf`. An `ops` line always names `insert move remove`. There are 44 tests: hand-picked trees for every requirement, two whole scenarios and five seeded random ones, two of which dump after each period; `-Fresh` draws five new ones. A test may take 10 seconds; a correct solution finishes in milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Take a scenario that dumps after each period and look at 04's loop: the only thing that has to go from the unit is the line that puts a node into its parent. Then ask what is left after the last unit, and where in the loop you would learn that the work is over.
</details>

<details><summary>Hint 2: the approach</summary>

Let `render` remember the root fiber it creates, as the tree under construction, next to the fiber to work on. A unit stops attaching. After the `while` loop in `workLoop`, if no fiber is left to do and there is a tree under construction, commit it: walk from the root's first child, attach each fiber's node to the node of its parent fiber, then do its children and its siblings. Clear the remembered root at the end so a later period does not do it again.
</details>

<details><summary>Hint 3: the traps</summary>

- Leave nothing in the unit that attaches. Even one `appendChild` in a unit makes the dump after the first period non-empty.
- Commit inside the same call that did the last unit. Checking at the top of the next call is one period late.
- The commit is not a unit: no extra read of `timeRemaining()`, and no waiting for the clock before committing.
- Walk the siblings as well as the children. A walk that follows only `child` attaches the first branch and nothing else.
- Skip the root fiber: its node is the container, and it is not attached to anything. The walk starts at its child.
- Clear the finished root after the commit. Otherwise every later period, even an idle one, appends the whole tree again.
- The commit needs the tree under construction and the next fiber to work on in the same state object `render.js` writes to.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
workLoop(deadline):
    while nextUnitOfWork exists:
        nextUnitOfWork = performUnitOfWork(nextUnitOfWork)
        if deadline.timeRemaining() < 1: leave the while loop
    if no nextUnitOfWork and wipRoot exists:
        commitRoot()
    requestIdleCallback(workLoop)

performUnitOfWork(fiber):
    fiber.dom = createDom(fiber) if it has none
    reconcileChildren(fiber, fiber.props.children)
    return the next fiber                    # nothing attached here any more

commitRoot():
    commitWork(wipRoot.child)
    wipRoot = nothing

commitWork(fiber):
    fiber.parent.dom.appendChild(fiber.dom)
    for each child of fiber, in order: commitWork(child)
```
</details>

## Checking your solution

```
.\check 05                         all tests, grouped by requirement
.\check 05 -Case 05-R2-short-last-period   one test with the input, the expected lines and your output
.\check 05 -Fresh                  five new random scenarios
.\check 05 -Dispute <id> "why"     set aside a test you think is wrong
```

A loop that commits at the start of the next period instead of at the end of this one fails like this:

```
  R2  the period that runs the last unit also commits: a dump right aft... .    0 / 7   FAILED
      x 05-R2-last-period-of-three  8 units in periods of 3: the third one runs the last two and commits
          output ends early - expected line 5: `node 0 a div ""`  (in `idle 2`)
          likely cause: R2 - the period that runs the last unit also commits: a dump right after it shows the whole tree
          expected values from: React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula for the idle lines; a model in tools/gen_p05.py for the ops lines
          reproduce: py -P tools/run_js.py solutions 05 build/cases/05/05-R2-last-period-of-three.in build/cases/05/05-R2-last-period-of-three.out
```

## After you pass: compare with the author's code

[Pombo's Step V](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases) is the fix for the half-drawn page of Step IV. It keeps the root of the tree under construction in `wipRoot`, removes the node attachment from `performUnitOfWork`, and calls `commitRoot()` from `workLoop` when there is no next unit of work and `wipRoot` is set. `commitRoot` calls `commitWork(wipRoot.child)` and clears `wipRoot`. `commitWork` appends `fiber.dom` to `fiber.parent.dom`, so a parent goes in before the fibers below it, and then recurses into `child` and `sibling`. That is the shape the tests assume, including the commit in the call of the last unit, although they accept the other order of parent and children as well. In the post all of this shares a file with the loop and reads `wipRoot` as a variable; here `commit.js` reads it from `state`.

Two things in the post's commit go beyond what the checker needs, and neither is exercised here. The post's `commitWork` recurses along `sibling`, so a parent with enough children can overflow the call stack (a test of the post's Step V code on Node 26 passed at fifteen thousand siblings and overflowed at twenty thousand; the limit depends on the engine); the trees here have a few dozen nodes at most. And the whole tree is walked in the commit. The post's epilogue says React keeps a linked list of the fibers that have effects and visits only those, and [React today](docs/react-today.md) says when React can pause a render at all.

The commit runs inside `workLoop`, ahead of the final `requestIdleCallback(workLoop)`, so an exception thrown by it ends the loop for good, as one thrown in a unit does. No test throws from the commit, and 06 names a bug in the post that does.
