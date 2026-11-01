# 10 · useState

**Difficulty:** Hard · **Assignment** 10 of 12 · **Check:** `.\check 10`

**Tags**
- *Language:* [arrow functions and closures](#primer/js-functions-closures) · [module-level state](#primer/js-global-state) · [array methods](#primer/js-arrays)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [useState and the rules of hooks](#primer/react-state) · [several updates, one render](#primer/react-batching) · [function components](#primer/react-function-components) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

The page below is complete on its own. If you want Pombo's version first, read the opening of [Step VIII: Hooks](https://pomb.us/build-your-own-react/#step-viii-hooks), the four paragraphs that turn the example into a click counter, and stop before "We need to initialize some global variables". The rest of the step walks through the author's code, and writing that code is your job.

## Learning material

- [useState and the rules of hooks](#primer/react-state): what a hook is, why a component can call `useState` several times, and why the calls have to happen in the same order on every render.
- [Several updates, one render](#primer/react-batching): the counter with id `d` queues two updaters per click, and both must land in a single render.
- [Arrow functions and closures](#primer/js-functions-closures): a setter is a closure over the state it belongs to, and the tests call it long after the render that made it.
- [Reconciliation by type and position](#primer/react-reconciliation): used in a new way. The old fiber that your reconciler pairs with a new one now hands over a component's state along with its DOM node.
- [Keys](#primer/react-keys): used in a new way. Keyed counters keep their counts when the list is reordered.

## Source material

- Rodrigo Pombo, [Step VIII: Hooks](https://pomb.us/build-your-own-react/#step-viii-hooks)
- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d): [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and [5.4 Updating components with setState](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.4%20Updating%20components%20with%20setState), compared in "After you pass"
- React documentation: [useState](https://react.dev/reference/react/useState), [Queueing a series of state updates](https://react.dev/learn/queueing-a-series-of-state-updates), [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state) and the [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks)

## Where this fits

Until now a function component started from nothing on every render, so a counter could not count. Here each component gets a memory that lives on its fiber. You add `hooks.js` with `useState`, the shared `wipFiber` and `hookIndex` in `state.js`, and a few lines in `render.js` and `index.js` to hook it up. Assignment 11 puts `useEffect` into the same `hooks.js`.

## The problem

Give `Didact` a `useState`. A scenario builds trees out of the catalog's stateful components, clicks their buttons and dumps the page; your program prints what the page looks like at each dump, and the checker compares that with what React prints for the same scenario.

### Input

The checker runs your entry program as `node assignments/assignment_10_use_state.js <input-file> <output-file>`. The program has three jobs. It imports `../harness/env.js` first, so that `document` and a controllable `requestIdleCallback` exist before your library loads. It imports `Didact` from `../src/didact/index.js`. And it ends with `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, which reads the scenario file, runs it against your library and writes the output file. The Boilerplate has it finished; from a blank start, you write those lines yourself. The scenario file has these kinds of lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Defines a tree of one root element. A capitalised tag such as `<Counter id=a start=3/>` is a catalog component, and attribute values are strings. |
| `render <name>` | Calls `Didact.render(tree, container)`. It does not run any work. |
| `flush` | Runs idle periods until the work loop has nothing left to do. |
| `click #<id>` | Dispatches a bubbling `click` on the element with that id, then flushes. |
| `poke` | Calls the setter that the first `Keeper` of the run handed out, with `n => n + 1`, then flushes. |
| `dump` | Prints the page, as described below. |

Every `render` in the tests is followed by a `flush` before anything else happens, so the page is complete when the next line runs. `poke` only ever happens while the first `Keeper` is still on the page; what a poke does after that `Keeper` has been removed is not tested.

### Output

Each `dump` prints a header with its running number, then one line per element and per run of text in the container, parents first:

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

The container itself is not printed, so its first child sits at depth 0. A `node` line gives the tag in lower case and the properties that differ from their defaults, sorted by name and separated by spaces: `className`, `id`, `title` and, for inputs, `value` (a value with a space, a double quote or a percent sign is percent-encoded). Neighbouring text nodes print as one `text` line, and a number child prints as its digits.

The label is the part that matters here. The first time a dump shows an element it gets the next unused letter (`a`, `b`, `c`, ... `z`, `aa`, ...), in document order, and it keeps that letter in every later dump. Two dumps that show the same label show the same DOM node. A node your library threw away and rebuilt gets a new letter even if it looks identical, so the labels are how the tests tell a kept node from a replaced one.

### The components the scenarios use

These live in the harness (`harness/catalog.js`), so you can read them. They call `useState` with a number or a boolean and handlers that always use the updater form:

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

You write `useState(initial)` in `src/didact/hooks.js` and export it on the `Didact` object. It is called from inside a component's function, and it returns `[state, setState]`. The setter takes an updater, a function from the previous state to the next one (Pombo calls it an action). Plain values are not tested.

State lives with the fiber of the component that called `useState`. While a component's function runs, every `useState` call gets the next slot of that component, counting from 0, and nothing is shared with other components. For a component that already existed in the last committed tree, slot n holds what the same call left there on the last run, state and pending updates included. A component that did not exist (it is new at its position, or the type at its position changed) starts every slot from its `initial`.

`setState(updater)` changes nothing on the page. It records the updater and schedules a new render that starts at the root of the tree, as `render` does. The updater runs during that render, when the component asks for its state again. Updaters recorded before the next render all run, oldest first, in that one render. The setter handed out by the first render is as good as the one from the latest render: an update sent through it must not be lost, however many renders have happened since.

The state belongs to the position in the tree and the type there, or to the key when there is one. Rendering the same tree again, re-rendering from a parent whose props changed, and re-rendering because a neighbour's setter ran all keep it, and a prop such as `start` is read only on the first render. Moving a component to another position (a new sibling in front of it) makes it a new component. Without keys, two counters that swap places in the tree swap props but not state. With keys, the state follows the key.

`Toggle` shows what a changing root does. Its function returns a `div` and then a `section`, so every click replaces its root node and everything below. Its state is not on that node, so the count of `on` and `off` carries on, and the new `button` answers clicks.

## Requirements

Every test is aimed at one of these, and a failing run lists its failures under that requirement.

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

The second dump uses labels `d`, `e` and `f`: the `div` became a `section`, and a different type is a different node, so the old three nodes are gone and three new ones stand in their place. The state did not reset (the component says `on`), which is why this case sits next to the state requirements.

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

Nothing in the tree says which `Counter` is which except the `id` prop, and `id` is an ordinary prop. The first `Counter` slot still holds the 3, so after the swap the counter with id `b` shows 3 and the one with id `a` shows 1. Labels `b` to `g` are unchanged between dumps 1 and 2 because both are the same nodes, rewritten in place. The last click proves the handlers followed their elements: `#b-inc` is now the first counter's button.

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

`poke` uses the setter from the first render every time, and each poke is followed by a render. The first poke goes through the setter of the latest render by luck. At the second poke that setter is one render old, at the third two, at the fourth three, and the update must still arrive.

## Constraints

Scenarios are short: the longest has 54 lines and no tree has more than 8 components. Texts are single words or numbers, and every `render` is followed by a `flush`. The 46 tests are the cases of each requirement, two long scripted sessions and five seeded random ones (a fresh seed gives five new sessions), with at most a few hundred output lines each. A correct solution takes well under a second per test; the limit is 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Ask where a counter's number can live between two runs of its function. Not in the function: its locals are gone when it returns. Not in the DOM: the span is rewritten from the number, not the other way round. The fiber tree survives a render, and the previous fiber for the same component is reachable from the new one.
</details>

<details><summary>Hint 2: the approach</summary>

Give every function-component fiber a list of hook records, empty at the start of each run of its function. `useState` takes the next slot: it looks at the same slot of the old fiber, reuses that record if there is one, and otherwise makes a new record from `initial`. A record holds the state and a queue of updaters that the setter fills. Share one record per slot across renders: the next render picks up the record the old fiber had, so the setter you handed out earlier still points at the record that the next render reads. The setter schedules a render from the root, using the tree you last committed. Next time `useState` reads a slot, it runs the queue on the state before returning it. `wipFiber` and `hookIndex` have to be set before the component function is called, because `useState` has no other way to know which component is calling.
</details>

<details><summary>Hint 3: the traps</summary>

- The hook index starts at 0 for every component, not once per render. Two `Counter`s side by side would otherwise look in each other's slots.
- A setter that closes over a record from one render queues updates on that record. If the next render makes a new record, those updates are never read. Make sure the setter and every later render use the same record, or that updates reach the record a later render will read.
- The queue is emptied when it has been applied. Applying it twice adds twice.
- Apply every queued updater, in order. A handler that calls the setter twice must advance the state twice.
- Starting from `initial` on every render makes the page look right until the first click.
- Several setter calls before the next render restart the same render. Do not lose the tree you were about to commit when that happens.
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

A solution whose setter works only for the render that made it fails like this:

```
  R8  A setter from an earlier render still works: nothing is lost when... .    1 / 4   FAILED
      x 10-R8-poke-four-times  Keeper, four pokes, a dump after each
          text[0]: expected (depth=1, value="2"), got (depth=1, value="1") - differs in value  (in `dump 2`)
          likely cause: R8 - A setter from an earlier render still works: nothing is lost when it is called later
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog
          reproduce: py -P tools/run_js.py build/bugs/10/stale-setter 10 build/cases/10/10-R8-poke-four-times.in build/cases/10/10-R8-poke-four-times.out
```

## After you pass: compare with the author's code

[Pombo's hooks](https://pomb.us/build-your-own-react/#step-viii-hooks) go through `updateFunctionComponent`, which sets `wipFiber`, empties the fiber's `hooks` array and resets `hookIndex` before calling the component. `useState` then looks up `oldHook` in `wipFiber.alternate.hooks[hookIndex]`, copies its state into a new hook with a new queue, replays the old queue's actions on it, and returns the state with a `setState` that pushes onto that hook's queue.

The post makes a new hook object on every render, and its `setState` closes over the hook of the render that created it. An update sent through a setter from an earlier render lands in a queue that no later render reads, so Pombo's code loses it. R8 is that case: poke a `Keeper` four times through its first setter and the post's code shows 1 after every poke: the first update arrives and the other three are lost. React hands out one stable setter, and R8 asks the same of you.

The post differs from React in three smaller ways, and the tests touch none of them. Its `setState` throws when `currentRoot` is still `null`, because it builds the new root from the committed tree. It accepts functions only, and a plain value breaks the next render, where React takes it as the new state. And `useState` stores `initial` as given, so a function passed as the initial value is kept rather than called.

Two failures in the post's code end its work loop for good. One is the plain value above, which raises in the next render. The other is removing a component that returned `null`: it renders, with a null child fiber, and `commitDeletion` later reads `dom` of that null. `workLoop` asks for its next idle callback in its last statement, so an exception inside a unit or a commit leaves nothing registered, and the `render` and `setState` calls that follow schedule work that never runs. The tests cover neither.

Jongeneel's `Component` keeps its state on a class instance, and its [`setState`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.4%20Updating%20components%20with%20setState) applies the updater, renders, diffs and patches the DOM before it returns. Three calls in a handler render three times, where your `useState` and React render once. His [`getUpdateDiff`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) meets the situation `Toggle` creates, a component whose root element is replaced. The callback meant to point `mountedElement` at the new element is written in the post as an arrow function that nothing assigns or calls, so the component keeps the old, detached node, and every later `setState` patches a node that is no longer in the page. The post's tag comparison also never reports a changed tag, so with the post exactly as written this happens when a root turns from an element into text; the repository fixes both. R9 asks for the repository's behaviour: after a root changes, the next click reaches the live node.

[React today](docs/react-today.md) lists where React 19 departs from the posts; its "Setter identity", "Updater argument" and "Batching" rows are the ones this assignment touches.
