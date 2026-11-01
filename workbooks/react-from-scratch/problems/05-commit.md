# 05 · Render phase, then commit

**Difficulty:** Medium · **Assignment** 5 of 12 · **Check:** `.\check 05`

**Tags**
- *Language:* [module-level state](#primer/js-global-state)
- *Library:* [appendChild, insertBefore, removeChild](#primer/dom-tree-editing) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [the render phase and the commit phase](#primer/react-render-commit) · [fibers](#primer/react-fibers)

## Read in the blog first

Pombo's version is [Step V: Render and Commit Phases](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases). Six short paragraphs with code frames between them cover why attaching a node in every unit is a problem, what `wipRoot` is, and how a finished tree gets appended. Read the paragraphs. Save the frames for after you have a solution of your own. The post is optional, and the page below is enough.

## Learning material

- [The render phase and the commit phase](#primer/react-render-commit): units build the tree and never touch the page; one uninterrupted pass then attaches it.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): how a node gets attached to a parent. The harness scores a node with no parent yet as an `insert` and one that already has a parent as a `move`.
- [Fibers](#primer/react-fibers): the commit walks the finished tree by `child` and `sibling`, and every fiber holds the node it will attach.
- [Module-level state and why `state.js` is an object](#primer/js-global-state): `render.js` leaves the finished root in it for `commit.js` to pick up.
- [The harness and scenario files](#primer/workbook-harness): `dump` can now come between idle periods, and `ops` reads the page's counters.

## Source material

- Rodrigo Pombo, [Step V: Render and Commit Phases](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases)
- react.dev, [Render and commit](https://react.dev/learn/render-and-commit)
- MDN: [Node.appendChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
- `harness/minidom.js`, which says how `insert`, `move` and `remove` are counted

## Where this fits

In 04 a unit was allowed to append its node, as the post's does. The page could grow piece by piece while the browser was free to paint it. This one closes that gap. The new file is `src/didact/commit.js`, and `render.js` changes. The walk, `reconcile.js` and `state.js` stay as 04 left them.

## The problem

Build the tree without showing any of it. Then put the whole thing on the page in one pass at the end. A scenario renders a tree, runs idle periods of its own choosing, dumps the container after some of them, and asks the harness for counts of what your code has attached.

### The modules

| File | Export | What it is |
|---|---|---|
| `src/didact/commit.js` | `commitRoot()` | Attaches the finished tree to the container and clears the tree under construction. |
| `src/didact/commit.js` | `commitWork(fiber)` | Attaches one fiber's node to the node of its parent fiber, then goes on to the fibers below it. |
| `src/didact/render.js` | `workLoop`, `performUnitOfWork` | The 04 loop and unit, with two changes: no unit touches the page, and the loop calls `commitRoot` when the work is done. |

`state` keeps its 04 fields, and you can add more.

### Input

Tests run `node assignments/assignment_05_commit.js <input-file> <output-file>`, a file shaped like 04's: `../harness/env.js` first, because the loop wants `requestIdleCallback` the moment `render.js` loads, then `../src/didact/index.js` for `Didact`, `../harness/scenario.js` for `runScenarioFile`, and a last line that awaits `runScenarioFile(process.argv[2], process.argv[3], Didact)`. The Boilerplate includes the file. From scratch, you write it. A scenario renders one tree onto the empty container and never renders again.

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Registers a tree from one line of HTML-like text, for instance `<ul id=l><li>one</li><li>two</li></ul>`. No output. |
| `render <name>` | `Didact.render(element, container)` on that tree. No output, and no work runs. |
| `idle <k>` | An idle period in which `timeRemaining()` answers 1 until call number `k` and 0 from then on (with `inf`, always 1). Prints the number of calls. `k` is 1 or more, or `inf`. |
| `flush` | Unlimited periods in a row, stopping after the first that finds nothing to do, meaning a period that never reads the clock. No output. |
| `dump` | Prints the container's contents. |
| `ops insert move remove` | Prints three counters, then zeroes all of them. |

The counters tally your code's calls on DOM nodes since the previous `ops`, or since the scenario began. `insert` is the `appendChild` and `insertBefore` calls whose node had no parent yet, `move` the same calls on a node that already had one, and `remove` the `removeChild` and `remove` calls. No other counter is asked for here, so how many nodes you create and how many properties you write is up to you.

### Output

```
idle <n>
dump <i>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
ops <insert> <move> <remove>
```

`idle <n>` is the number of `timeRemaining()` calls in that period. A `dump` prints `dump <i>`, counting dumps from 1, then what the container holds, in document order and indented by depth from 0: a `node` line per element, a `text` line per text node; an empty container gets the `dump` line and nothing after it. Elements are labelled `a`, `b`, `c` and on, in the order a dump first meets them.

The quoted `<props>` on a `node` line lists what differs from the defaults, as `name=value`, alphabetically, and five props can appear: `className`, `id` and `title` when not empty; `disabled` on buttons, inputs and textareas, written `disabled=true`; and `value` on inputs and textareas when not empty. A value with whitespace, `"` or `%` in it goes through `encodeURIComponent`, so a space becomes `%20`. Nothing to list prints `""`. In a `text` line, line breaks and the characters `%` and `"` are encoded; spaces stay.

### While the units run

Units count the way they did in assignment 04: the root fiber, then one per element and one per text node, `1 + E + T` for a tree with `E` elements and `T` text pieces. A period with budget `k` does `k` units if that many are waiting, and all of them otherwise. It reads `timeRemaining()` once after each, the last unit of the tree included. With nothing to do it reads nothing.

What changes is the page. A unit may create its fiber's node and set its props, but it may not attach anything to the container or to another node, which means a `dump` after a period that leaves units undone shows an empty container and `ops insert move remove` prints `0 0 0`.

### The period that ends the work

The period whose last unit finishes the tree commits as well. Straight after that unit, in the same call of the loop, every element and text node of the finished tree is attached to its parent's node, and by the time `idle` returns the container holds the whole tree. The pass is not a unit and does not call `timeRemaining()`, so `idle` prints what it printed in 04.

That holds even when the last unit also uses up the budget: `idle 9` on a tree of 9 units commits in that period. No extra period.

Each node is attached once, and the counters read `N 0 0` for the period of the commit. `N` is the number of elements plus text nodes; the root fiber has no node of its own to attach, which makes `N` one less than the units. The checker can't see in what order you visit the fibers, so a parent may go in before or after its children and the walk may be recursive or a loop. It does have to reach every fiber, siblings included, and attach the children of one parent in tree order. Otherwise they land in the wrong order.

### After the commit

With the tree on the page, later periods and `flush` have nothing to do. They print 0, leave the container alone and keep the counters at 0. A loop that forgets to clear its finished root commits again every period, and the `move` counter gives it away.

## Requirements

- **R1** While units run the container stays empty: a `dump` after a period that leaves work undone shows no node.
- **R2** The period that runs the last unit also commits: a `dump` right after it shows the whole tree.
- **R3** The commit adds no unit and no `timeRemaining()` read, so `idle k` still prints the smaller of `k` and the units left, and later periods print 0.
- **R4** Each node is inserted once, by the commit: `ops insert move remove` prints `0 0 0` while work is waiting, `N 0 0` after the period of the last unit (N is the number of elements plus text nodes), and `0 0 0` after that.
- **R5** The committed tree has the right shape: nesting, sibling order, props and text.
- **E2E** Whole scenarios mixing periods, dumps and counters.

## Examples

### Example 1: dumping after every period (test `05-R1-empty-between-periods`)

```
input:
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 3
dump
idle 3
dump
idle 3
dump

output:
idle 3
dump 1
idle 3
dump 2
idle 3
dump 3
```

Ten units. Three periods of three leave one undone, so nothing has been committed and all three dumps end after their header line. Nodes may already exist, because units create them, but every one is detached.

### Example 2: the period that commits (test `05-R2-last-period-of-three`)

```
input:
tree a <div><section><article><span><em><b><div></div></b></em></span></article></section></div>
render a
idle 3
idle 3
idle 3
dump

output:
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

Seven elements and the root fiber make eight units. Two are left for the third period. It does them, prints 2 (no ninth read for the commit) and leaves the whole chain on the page before `dump` runs. A solution that commits at the start of the next period prints the same numbers and then dumps an empty container. Right numbers, wrong page.

### Example 3: counting inserts (test `05-R4-insert-at-commit`)

```
input:
tree a <div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>
render a
idle 4
ops insert move remove
idle 4
ops insert move remove
idle 4
ops insert move remove

output:
idle 4
ops 0 0 0
idle 4
ops 0 0 0
idle 2
ops 9 0 0
```

5 elements and 4 text pieces make nine nodes. All nine are attached in the commit, in a single period, and none was in the DOM before, so each call counts as an `insert`. A `move` would mean a node that already had a parent was appended again. That is what happens when a unit attaches its node and the commit attaches it again.

## Constraints

Trees have 2 to 60 units of plain elements and text, with no handlers, components or keys, and a scenario renders one tree with budgets that are whole numbers from 1 up or `inf`, and an `ops` line that always names `insert move remove`. The 44 tests are hand-picked trees for every requirement, two whole scenarios and five seeded random ones, two of which dump after each period. `-Fresh` draws five new ones. A test may take 10 seconds; a correct solution finishes in milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Picture a scenario that dumps after every period and read your 04 loop with it in mind. The only thing that has to leave the unit is the line that puts a node into its parent. Then ask what is left to do after the last unit, and where in the loop you find out the work is over.
</details>

<details><summary>Hint 2: the approach</summary>

Have `render` keep the root fiber it creates, as the tree under construction, beside the fiber to work on next. Units stop attaching. After the `while` loop in `workLoop`, check whether a fiber is left and whether a tree under construction exists. With no fiber left and the tree there, commit it. Start at the root's first child, attach each fiber's node to its parent fiber's node, then do its children and its siblings. Clear the kept root at the end, so a later period does not do it all again.
</details>

<details><summary>Hint 3: the traps</summary>

- No attaching may stay in the unit. A single `appendChild` there makes the dump after the first period non-empty.
- Commit in the call that ran the last unit. Checking at the top of the next call is a period late.
- The commit is not a unit. It adds no read of `timeRemaining()` and does not wait for the clock.
- Follow the siblings as well as the children; a walk that follows only `child` attaches the first branch and stops.
- Skip the root fiber. Its node is the container and nothing attaches it. The walk starts at its child.
- Clear the finished root after the commit, or every later period, even an idle one, appends the whole tree again.
- `commit.js` reads the tree under construction and the next fiber to work on from the same state object `render.js` writes to.
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

If the commit waits for the next period instead of running at the end of this one, the report reads:

```
  R2  the period that runs the last unit also commits: a dump right aft... .    0 / 7   FAILED
      x 05-R2-last-period-of-three  8 units in periods of 3: the third one runs the last two and commits
          output ends early - expected line 5: `node 0 a div ""`  (in `idle 2`)
          likely cause: R2 - the period that runs the last unit also commits: a dump right after it shows the whole tree
          expected values from: React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula for the idle lines; a model in tools/gen_p05.py for the ops lines
          reproduce: py -P tools/run_js.py solutions 05 build/cases/05/05-R2-last-period-of-three.in build/cases/05/05-R2-last-period-of-three.out
```

## After you pass: compare with the author's code

[Pombo's Step V](https://pomb.us/build-your-own-react/#step-v-render-and-commit-phases) repairs the half-drawn page of Step IV. The root of the tree under construction goes in `wipRoot`, `performUnitOfWork` loses its attaching line, and `workLoop` calls `commitRoot()` when there is no next unit of work and `wipRoot` is set. `commitRoot` calls `commitWork(wipRoot.child)` and clears `wipRoot`, and `commitWork` appends `fiber.dom` to `fiber.parent.dom`, a parent before the fibers below it, and then recurses into `child` and `sibling`. The tests assume that shape, including the commit in the call of the last unit. They accept the other order of parent and children too. In the post it all shares a file with the loop and `wipRoot` is a plain variable; here `commit.js` reads it from `state`.

Two things in the post's commit go beyond what the checker needs, and neither is exercised here. First, the post's `commitWork` recurses along `sibling`, so a parent with enough children can overflow the call stack. A test of the post's Step V code on Node 26 passed at fifteen thousand siblings and overflowed at twenty thousand. The limit depends on the engine, and the trees here have a few dozen nodes at most. Second, the commit walks the whole tree, where the post's epilogue says React keeps a linked list of the fibers that have effects and visits only those. [React today](docs/react-today.md) says when React can pause a render at all.

The commit runs inside `workLoop`, ahead of the closing `requestIdleCallback(workLoop)`, so an exception from it ends the loop for good, as one from a unit does. No test throws from the commit. 06 names a bug in the post that does.
