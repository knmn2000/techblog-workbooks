# 10 · useState

**Difficulty:** Hard · **Assignment** 10 of 12 · **Check:** `.\check 10`

**Tags**
- *Language:* [arrow functions and closures](#primer/js-functions-closures) · [module-level state](#primer/js-global-state) · [array methods](#primer/js-arrays)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [useState and the rules of hooks](#primer/react-state) · [several updates, one render](#primer/react-batching) · [function components](#primer/react-function-components) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

Everything you need is below. If you want Pombo's version first, read the start of [Step VIII: Hooks](https://pomb.us/build-your-own-react/#step-viii-hooks): the four paragraphs that turn the example into a click counter. Stop at "We need to initialize some global variables". After that comes the author's code, and writing it is your job.

## Learning material

- [useState and the rules of hooks](#primer/react-state): what a hook is, why one component can call `useState` several times, and why the calls must come in the same order on every render.
- [Several updates, one render](#primer/react-batching): the counter with id `d` queues two updaters per click, and both have to land in a single render.
- [Arrow functions and closures](#primer/js-functions-closures): a setter closes over the state it belongs to, and the tests call it long after the render that made it.
- [Reconciliation by type and position](#primer/react-reconciliation): the pairing of an old fiber with a new one used to decide which DOM node survives. It now decides whose state a component gets as well.
- [Keys](#primer/react-keys): counters with keys keep their counts when the list is reordered.

## Source material

- Rodrigo Pombo, [Step VIII: Hooks](https://pomb.us/build-your-own-react/#step-viii-hooks)
- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d): [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and [5.4 Updating components with setState](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.4%20Updating%20components%20with%20setState), compared in "After you pass"
- React documentation: [useState](https://react.dev/reference/react/useState), [Queueing a series of state updates](https://react.dev/learn/queueing-a-series-of-state-updates), [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state) and the [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks)

## Where this fits

Until now a function component began from nothing on every render, which is why a counter could not count. That ends here, with a memory that lives on each component's fiber. `hooks.js` is new and holds `useState`, the shared `wipFiber` and `hookIndex` go in `state.js`, and `render.js` and `index.js` get a few lines of wiring.

## The problem

Give `Didact` a `useState`. Scenarios build trees from the catalog's stateful components, click their buttons and dump the page. Your program prints the page at each dump, and the checker holds that against what React prints for the same scenario.

### Input

Your entry program is started as `node assignments/assignment_10_use_state.js <input-file> <output-file>`. It does three things, in this order. It imports `../harness/env.js`, which has to come first because it puts `document` and a controllable `requestIdleCallback` in place before your library loads. It imports `Didact` from `../src/didact/index.js`. And it finishes with `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, which reads the scenario, runs it on your library and writes the output file. The Boilerplate has all three. Starting blank, type them yourself. A scenario file is made of these lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Defines a tree of one root element. A capitalised tag such as `<Counter id=a start=3/>` is a catalog component, and attribute values are strings. |
| `render <name>` | Calls `Didact.render(tree, container)` and runs none of the work. |
| `flush` | Runs idle periods until the work loop is out of work. |
| `click #<id>` | Dispatches a bubbling `click` on the element with that id, then flushes. |
| `poke` | Calls the setter that the first `Keeper` of the run handed out, with `n => n + 1`, then flushes. |
| `dump` | Prints the page, as described below. |

In every test a `render` is followed straight away by a `flush`, and the page is complete before the next line runs. `poke` is only used while the first `Keeper` is still on the page. What it does once that `Keeper` is gone is not tested.

### Output

Each `dump` prints a header with its running number, then one line per element and per run of text in the container, parents first:

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

The container itself is not printed, so its first child sits at depth 0. A `node` line gives the tag in lower case and the properties that differ from their defaults, sorted by name and separated by spaces: `className`, `id`, `title` and, for inputs, `value` (a value with a space, a double quote or a percent sign is percent-encoded). Neighbouring text nodes print as one `text` line, and a number child prints as its digits.

Labels are what these tests are about. Each element is labelled the first time it appears in a dump, with the next unused letter (`a`, `b`, `c`, ... `z`, `aa`, ...) in document order, and it keeps that label from then on. Same label, same DOM node. If your library throws a node away and builds an identical one, the new node gets a new letter. That is how a test tells a node that was kept from one that was replaced.

### The components the scenarios use

The catalog is in `harness/catalog.js` and worth a read. Its components call `useState` with a number or a boolean, and their handlers always pass an updater:

```js
const [count, setCount] = useState(Number(start));
onClick: () => setCount((c) => c + 1)
```

| Component | Props | What it renders |
|---|---|---|
| `Counter` | `id` (default `c`), `start` (default 0) | `<div id={id}>`, then `<button id="{id}-inc">+</button>` and `<span id="{id}-count">` holding the count as a number. The button adds 1. The counter with id `d` calls its setter twice per click, so it adds 2. |
| `MultiCounter` | none | `<div id="mc">` with buttons `mc-a` and `mc-b` (text `a`, `b`) and spans `mc-av` and `mc-bv`. It has two `useState(0)` calls, one per button. |
| `Toggle` | none | `<div id="t">` while off and `<section id="t" className="on">` while on, each with `<button id="t-btn">toggle</button>` and `<span id="t-state">` reading `off` or `on`. The button flips the state. |
| `Keeper` | none | `<p id="keeper">` showing a number from `useState(0)`. The first `Keeper` to render stores its setter in the harness for `poke`. |
| `Frame`, `FnA` | `title` and children / none | From assignment 09: a `section` with an `h2` and the children, and `<i>a</i>`. |

### What `useState` does

`useState(initial)` goes in `src/didact/hooks.js`, exported on the `Didact` object. A component's function calls it and gets `[state, setState]` back. The setter takes an updater, a function from the previous state to the next (Pombo calls it an action). A plain value in place of an updater is not tested.

State belongs to the fiber of the component that called `useState`. As a component's function runs, each call takes the next slot of that component, counting from 0. No slot is shared between components. If the component was already in the last committed tree, slot n holds what the same call left there on the previous run, pending updates included. A component that was not there (new at its position, or a different type from the one that was there) starts every slot from its `initial`.

Calling `setState(updater)` does nothing to the page. It records the updater and schedules a new render from the root of the tree, the way `render` does. The updater runs during that render, when the component asks for its state again. Several updaters recorded before the next render all run in that one render, oldest first. The setter from the first render stays as good as the latest one: however many renders have passed, an update sent through it must not be lost.

Whose state it is depends on the position in the tree and the type there, or on the key when there is one. Rendering the same tree again keeps it. So does re-rendering from a parent whose props changed, or because a neighbour's setter ran. A prop like `start` is read on the first render only. Move a component to another position (a new sibling in front of it, say) and it is a new component. Two unkeyed counters that trade places trade props, but the state stays at the position. With keys the state follows the key.

`Toggle` is the case of a root that changes. Its function returns a `div` while the state is off and a `section` while it is on, so every click replaces the root node and everything below it. The state does not live on that node, which is why the on/off cycle carries on and the new `button` still answers clicks.

## Requirements

Each test targets one requirement, and a failing run groups its failures under it.

- **R1** `useState(initial)` returns `[state, setState]`, and on the first render of a component the state is `initial`.
- **R2** After a setter call and the flush that follows, the component has re-rendered with `updater(previous state)` as its state and the dump shows it. The elements that exist before and after are the same nodes.
- **R3** Each component instance has state of its own: two `Counter`s keep separate counts.
- **R4** A component may call `useState` several times. The n-th call gets slot n of that component, `MultiCounter`'s two buttons change two different numbers, and a component never reads another component's slots.
- **R5** Updaters queued before the next render all run, in call order, in one render (`Counter` `d`: +2 per click).
- **R6** State survives a re-render caused by `render` of a new tree that keeps the component's position and type, and one caused by another component's setter.
- **R7** A component keeps its state when the fiber at its position (or with its key) has the same type, and starts from `initial` otherwise.
- **R8** A setter obtained in an earlier render keeps working: `poke` after any number of renders adds 1.
- **R9** A component whose root tag changes (`Toggle`) keeps its state, and the new nodes respond to clicks.
- **E2E** Longer sessions mixing all of it, among them seeded random ones.

## Examples

### Example 1: a root that changes tag (test `10-R9-toggle-once`)

```
input:   tree t <Toggle/>
         render t
         flush
         dump
         click #t-btn
         dump

output:  dump 1
         node 0 a div "id=t"
         node 1 b button "id=t-btn"
         text 2 "toggle"
         node 1 c span "id=t-state"
         text 2 "off"
         dump 2
         node 0 d section "className=on id=t"
         node 1 e button "id=t-btn"
         text 2 "toggle"
         node 1 f span "id=t-state"
         text 2 "on"
```

Dump 2 has the labels `d`, `e` and `f`. The `div` became a `section`, a different type and so a different node, and all three old nodes are gone with three new ones in their place. The component still says `on`. Its state survived the swap, and that is why this case sits with the state requirements.

### Example 2: two counters trade places (test `10-R7-swap-positions`)

```
input:   tree a <div><Counter id=a/><Counter id=b/></div>
         tree b <div><Counter id=b/><Counter id=a/></div>
         render a
         flush
         click #a-inc
         click #a-inc
         click #a-inc
         click #b-inc
         dump
         render b
         flush
         dump
         click #b-inc
         dump

output:  dump 1
         node 0 a div ""
         node 1 b div "id=a"
         node 2 c button "id=a-inc"
         text 3 "+"
         node 2 d span "id=a-count"
         text 3 "3"
         node 1 e div "id=b"
         node 2 f button "id=b-inc"
         text 3 "+"
         node 2 g span "id=b-count"
         text 3 "1"
         dump 2
         node 0 a div ""
         node 1 b div "id=b"
         node 2 c button "id=b-inc"
         text 3 "+"
         node 2 d span "id=b-count"
         text 3 "3"
         node 1 e div "id=a"
         node 2 f button "id=a-inc"
         text 3 "+"
         node 2 g span "id=a-count"
         text 3 "1"
         dump 3
         node 0 a div ""
         node 1 b div "id=b"
         node 2 c button "id=b-inc"
         text 3 "+"
         node 2 d span "id=b-count"
         text 3 "4"
         node 1 e div "id=a"
         node 2 f button "id=a-inc"
         text 3 "+"
         node 2 g span "id=a-count"
         text 3 "1"
```

The only thing telling the two `Counter`s apart is their `id`, and `id` is an ordinary prop. The state at the first position is still 3, so after the swap the counter with id `b` shows 3 and the one with id `a` shows 1. Labels `b` to `g` stay put between dumps 1 and 2. Same nodes, rewritten in place. The last click checks that the handlers followed their elements, since `#b-inc` is now the first counter's button.

### Example 3: a setter from the first render (test `10-R8-poke-four-times`)

```
input:   tree t <Keeper/>
         render t
         flush
         poke
         dump
         poke
         dump
         poke
         dump
         poke
         dump

output:  dump 1
         node 0 a p "id=keeper"
         text 1 "1"
         dump 2
         node 0 a p "id=keeper"
         text 1 "2"
         dump 3
         node 0 a p "id=keeper"
         text 1 "3"
         dump 4
         node 0 a p "id=keeper"
         text 1 "4"
```

Every `poke` calls the setter from the first render, and every poke triggers a render. The first one happens to use the latest setter. By the second it is a render old, by the third two renders, by the fourth three. The update has to get through each time.

## Constraints

The longest scenario is 54 lines and no tree has more than 8 components. Texts are single words or numbers. That makes 46 tests: per-requirement cases, two long scripted sessions, and five random sessions drawn from a seed (a fresh seed gives five new sessions), each with at most a few hundred lines of output. A correct solution runs a test in well under a second. The limit is 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Think about where a counter's number can live between two runs of its function. The function's locals are gone once it returns. The DOM is downstream of the number: the span is written from it and never read back. What survives a render is the fiber tree, and the previous fiber for the same component can be reached from the new one.
</details>

<details><summary>Hint 2: the approach</summary>

Each function-component fiber carries a list of hook records, emptied at the start of every run of its function. `useState` takes the next slot, looks at the same slot on the old fiber and reuses the record found there, or builds a new one from `initial` when there is none. A record holds the state and a queue of updaters, which the setter fills. Share one record per slot across renders. Then the next render reads the record the old fiber had, and the setter you handed out earlier still points at it. The setter schedules a render from the root, on the tree you last committed. When `useState` reads a slot again, it runs the queue over the state before returning it. Set `wipFiber` and `hookIndex` before calling the component function; `useState` has no other way to find out who is calling.
</details>

<details><summary>Hint 3: the traps</summary>

- Reset the hook index to 0 for every component. One reset per render sends two `Counter`s side by side into each other's slots.
- A setter closes over the record of the render that made it. If the next render builds a fresh record, whatever was queued on the old one is never read. Either every render shares the one record, or updates have another way to reach the record a later render will read.
- Empty the queue after applying it. Apply it twice and every update counts twice.
- Apply every queued updater, in order. A handler that calls the setter twice has to move the state twice.
- A `useState` that starts from `initial` on every render looks right until the first click.
- Several setter calls before the next render restart the same render. Keep the tree you were about to commit when that happens.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
before calling a component function:
    state.wipFiber = fiber
    state.hookIndex = 0
    fiber.hooks = []

useState(initial):
    slot = wipFiber.alternate?.hooks[hookIndex]
    if slot is missing:
        slot = { state: initial, queue: [] }
        slot.setState = updater => { slot.queue.push(updater); schedule a render from the root }
    wipFiber.hooks.push(slot)
    hookIndex += 1
    for each updater in slot.queue, oldest first: slot.state = updater(slot.state)
    empty slot.queue
    return [slot.state, slot.setState]

schedule a render from the root:
    render(the root's element again, the root's container)
```
</details>

## Checking your solution

```
.\check 10                          every test, grouped by requirement
.\check 10 -Case 10-R8-poke-once    one test with its full input, the expected dumps and yours
.\check 10 -Fresh                   five new random sessions, to try your code on scenarios you have not seen
.\check 10 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A setter that only works for the render that made it fails like this:

```
  R8  A setter from an earlier render still works: nothing is lost when... .    1 / 4   FAILED
      x 10-R8-poke-four-times  Keeper, four pokes, a dump after each
          text[0]: expected (depth=1, value="2"), got (depth=1, value="1") - differs in value  (in `dump 2`)
          likely cause: R8 - A setter from an earlier render still works: nothing is lost when it is called later
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog
          reproduce: py -P tools/run_js.py build/bugs/10/stale-setter 10 build/cases/10/10-R8-poke-four-times.in build/cases/10/10-R8-poke-four-times.out
```

## After you pass: compare with the author's code

In [Pombo's hooks](https://pomb.us/build-your-own-react/#step-viii-hooks), `updateFunctionComponent` sets `wipFiber`, empties the fiber's `hooks` array and resets `hookIndex` before it calls the component. `useState` then finds `oldHook` at `wipFiber.alternate.hooks[hookIndex]`, copies its state into a new hook with a new queue, replays the old queue's actions onto it, and returns that state with a `setState` that pushes onto that hook's queue.

The post builds a new hook object on every render, and each `setState` closes over the hook from the render that made it. Send an update through a setter from an earlier render and it lands in a queue that no later render reads. Pombo's code drops it. That is R8: poke a `Keeper` four times through its first setter and the post's code shows 1 after every poke. The first update arrives, the other three vanish. React hands out one stable setter, and R8 wants the same from yours.

Pombo's code differs from React in three smaller ways, none of them tested. Its `setState` throws while `currentRoot` is still `null`, since it builds the new root from the committed tree. It accepts functions only, and a plain value breaks the next render, where React takes it as the new state. And `useState` stores `initial` as given, so a function passed as the initial value is kept rather than called.

Two failures in the post's code stop its work loop for good. One is the plain value above, which raises in the next render. The other is removing a component that returned `null`: the component renders with a null child fiber, and `commitDeletion` later reads `dom` from that null. `workLoop` requests its next idle callback in its last statement, so an exception inside a unit or a commit leaves nothing registered, and every later `render` or `setState` schedules work that never runs. Neither is tested.

Jongeneel's `Component` keeps its state on a class instance. Its [`setState`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.4%20Updating%20components%20with%20setState) applies the updater, renders, diffs and patches the DOM before it returns, so three calls in a handler render three times, where your `useState` and React render once. His [`getUpdateDiff`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) runs into the situation `Toggle` creates, a component whose root element is replaced. The callback meant to point `mountedElement` at the new element is written in the post as an arrow function that nothing assigns or calls. The component keeps the old, detached node, and every later `setState` patches a node that is no longer in the page. The post's tag comparison also never reports a changed tag, so in the post as written this happens when a root turns from an element into text. The repository fixes both, and R9 asks for the repository's behaviour: after a root changes, the next click reaches the live node.

[React today](docs/react-today.md) lists where React 19 departs from the posts. The rows to read for this assignment are "Setter identity", "Updater argument" and "Batching".
