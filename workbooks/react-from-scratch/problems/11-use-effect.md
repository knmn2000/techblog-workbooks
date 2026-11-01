# 11 · useEffect

**Difficulty:** Hard · **Assignment** 11 of 12 · **Check:** `.\check 11`

**Tags**
- *Language:* [arrow functions and closures](#primer/js-functions-closures) · [equality and `Object.is`](#primer/js-equality) · [array methods](#primer/js-arrays)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [useEffect: after the DOM is updated](#primer/react-effects) · [the render phase and the commit phase](#primer/react-render-commit) · [useState and the rules of hooks](#primer/react-state) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

Neither post builds `useEffect`. This one is an extension: nothing in either author's code corresponds to it, and the behaviour is React 19.3.1's, the version the expected output comes from. Jongeneel has the same three moments as class methods: componentDidMount in [5.2 Mounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components), componentDidUpdate in [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and componentWillUnmount in [5.6 Unmounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.6%20Unmounting%20components). A figure of those lifecycle hooks opens [section 5](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.%20Components%20and%20reactive%20scopes), and it is worth reading, with the text around it, if you want the idea. Skip his code, since his mount and update hooks run from timers and this assignment follows React. Pombo's [epilogue](https://pomb.us/build-your-own-react/#epilogue) lists `useEffect` as an easy addition and goes no further. You can do the assignment without either.

## Learning material

- [useEffect: after the DOM is updated](#primer/react-effects): effects and cleanups, what a deps array promises, and why the order effects run in is a rule and not an accident.
- [The render phase and the commit phase](#primer/react-render-commit): effects are the first work that has to wait until the commit is over. The render phase may only remember them.
- [Arrow functions and closures](#primer/js-functions-closures): an effect and the cleanup it returns close over the props of the render that ran them, and the tests check that they stay that way.
- [Equality and `Object.is`](#primer/js-equality): every render builds a new deps array, so two renders can hold equal contents in two different arrays.
- [Reconciliation by type and position](#primer/react-reconciliation): the fibers your reconciler discards still own cleanups.

## Source material

- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d): the lifecycle figure at the start of [section 5](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.%20Components%20and%20reactive%20scopes), [5.2 Mounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components), [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and [5.6 Unmounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.6%20Unmounting%20components)
- Rodrigo Pombo, [Epilogue](https://pomb.us/build-your-own-react/#epilogue)
- React documentation: [useEffect](https://react.dev/reference/react/useEffect) and [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)

## Where this fits

Since 10 a function component can remember. It still cannot touch anything outside the tree, a page title or a timer for instance. `useEffect` joins `useState` in `hooks.js` and takes slots the same way, and `commit.js` runs whatever the hook noted down once the DOM matches the new tree.

## The problem

Add `useEffect(effect, deps)` to `Didact`. Some catalog components write a line to the run's log from their effects and cleanups. A scenario mounts, updates and removes them and reads the log after each step, and your log is checked against the one React 19 produces.

### Input

The entry program is the one you know, started with `node assignments/assignment_11_use_effect.js <input-file> <output-file>`: `../harness/env.js` imported first (it sets up `document` and a controllable `requestIdleCallback` before your library loads), then `Didact` from `../src/didact/index.js`, then a last line `await runScenarioFile(process.argv[2], process.argv[3], Didact)` that runs the scenario on your library and writes the output file. The Boilerplate ships it finished. Blank start: write those lines. These are the scenario lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Names a tree with one root element. A capitalised tag such as `<LoggerDeps name=x dep=1/>` is a catalog component, and attribute values are strings. Redefining a name is allowed. |
| `render <name>` | Calls `Didact.render(tree, container)`. No work happens yet. |
| `idle <k>` | Runs one idle period in which your work loop may do at most `k` units of work, then prints `idle <units done>`. |
| `flush` | Runs idle periods until no work is left. |
| `click #<id>` | A bubbling `click` on the element with that id, then a flush. |
| `log` | Prints the log entries recorded since the previous `log`. |
| `dump` | Prints the page. |

Between one `render` and the next there is always a `flush`.

### Output

Every entry recorded since the last `log` comes out as one line, in the order recorded. A stretch with no entries prints nothing:

```
log <text>
```

`dump` prints `dump <n>` and the page in the usual format: `node <depth> <label> <tag> "<props>"` for each element, `text <depth> "<text>"` for each run of text, parents first, container left out. A label is a letter handed to an element by the first dump that shows it and kept after that, so a letter identifies a node. `idle <k>` prints `idle <units>`, the number of units your loop got through in that period: `k` when at least `k` units are left, fewer when the work runs out.

Most scenarios finish each step with `log` and `dump`. The dump marks the boundary between two steps, and a line that shows up one step late fails the test.

### The components the scenarios use

Also in `harness/catalog.js`. Every effect writes the text shown here to the log, and names are single words.

| Component | Props | Renders | Effect |
|---|---|---|---|
| `Logger` | `name` | `<em>{name}</em>` | deps `[]`. Logs `mount <name>`; the cleanup logs `cleanup <name>`. |
| `LoggerDeps` | `name`, `dep` | `<em>{name}:{dep}</em>` | deps `[dep]`. Logs `run <name> <dep>`; the cleanup logs `clean <name> <dep>`. |
| `LoggerEvery` | `name` | `<div><em>{name}:{count}</em><button id="{name}-btn">bump</button></div>` | no deps array. Logs `run <name>`; the cleanup logs `clean <name>`. The button adds 1 to a `useState` counter. |
| `Outer` | `name` | `<div>` holding `<Logger name="{name}.inner"/>` | deps `[]`. Logs `mount <name>`; the cleanup logs `cleanup <name>`. |
| `Frame`, `Counter` | as before | as before | none. `Counter`'s button has the id `c-inc`. |

A tree never holds more than one `LoggerEvery`.

### What `useEffect` does

Write `useEffect(effect, deps)` in `src/didact/hooks.js`, next to `useState`, and export it on the `Didact` object. `effect` is a function that may return another function, the cleanup. `deps` is an array or is left out (`undefined`, and `null` counts the same). No array means the effect is due on every render. The catalog passes an array or nothing, and an array never changes length between two renders of a component, so a change of length is untested. Comparing item by item up to the shorter length is fine, and so is treating a different length as a change.

While a component's function runs, no effect runs. The function registers it and that is all. Once the render phase is over and the commit has put the new tree on the page, the effects that are due run, still inside the same flush. An effect is due when its component mounts, when `deps` is `undefined`, or when `deps` differs from the deps of the previous run. The comparison goes item by item with `Object.is`, not array against array, because every render makes a new array. An effect that is not due neither runs nor cleans up. A cleanup runs before the effect that replaces it and when the component is removed, in the sequence given under "The order" below.

An effect holds on to the function and the cleanup from the render that ran it. If a later render brings new props but unchanged deps, nothing happens, and the cleanup that runs on removal still reports the old props.

### The order

These are React 19.3.1's orders, and the tests pin them:

1. Mount, post-order: the effects of a component's children run before the component's own, and siblings run left to right. `Outer` mounts `name.inner` first, then `name`.
2. Removal, pre-order: when a subtree is removed, a component's cleanup runs before the cleanups of the components below it, and siblings run left to right. `Outer` cleans `name` first, then `name.inner`. The cleanup runs for every component in the subtree, however deep, also below plain elements.
3. A commit that keeps its components and re-runs some effects: every cleanup of the commit first, then every effect. Within each group siblings go left to right.
4. A commit that replaces a subtree and mounts another one: every cleanup of what goes away runs before any effect of what is new.

No test mixes a removal and a re-run in one commit, so how the cleanups of the removed subtree interleave with the cleanups of re-running effects is untested. No test re-runs the effects of a component and of one of its descendants together, and none mounts a component in a commit that also re-runs another effect. The order in those situations is yours to pick. When a component and one of its descendants re-run together, React runs the descendants' cleanups and effects first.

## Requirements

A test belongs to one requirement. The report shows how many of each group pass and names the requirement most failures point at.

- **R1** An effect runs once per mount, and only after the render that created it has been committed: while units of work are still left, nothing has been logged and the page is empty.
- **R2** An effect with `[]` runs once. Rendering again, new props, a changed parent and a click elsewhere do not run it again.
- **R3** An effect with a deps array runs again only when an item of the array differs from the last run's, and the cleanup of that last run goes first. The same values in a new array change nothing.
- **R4** An effect without a deps array runs after every render of its component, the previous cleanup first.
- **R5** Removing a subtree runs the cleanups of every component in it, a parent's before its children's, siblings in order.
- **R6** On mount, children's effects run before their parent's, and siblings' effects in order.
- **R7** In one commit every cleanup runs before any effect.
- **R8** An effect and its cleanup are the ones from the render that ran the effect: a new prop that does not change the deps changes neither.
- **E2E** Longer sessions mixing all of it, among them seeded random ones.

## Examples

### Example 1: nothing before the commit (test `11-R1-nothing-runs-before-the-commit`)

```
input:   tree t <div><Logger name=a/><Logger name=b/></div>
         render t
         idle 4
         log
         dump
         flush
         log
         dump

output:  idle 4
         dump 1
         log mount a
         log mount b
         dump 2
         node 0 a div ""
         node 1 b em ""
         text 2 "a"
         node 1 c em ""
         text 2 "b"
```

The tree comes to 8 units of work: the container's root, the `div`, two `Logger` components, their two `em` elements and two text nodes. `idle 4` gets through four of them, enough for the first `Logger`'s function to have run, yet the log is empty and so is the page (`dump 1` has no lines). The `flush` finishes the render, commits and runs both effects.

### Example 2: cleanups before effects (test `11-R7-both-siblings-change`)

```
input:   tree t <div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>
         render t
         flush
         log
         dump
         tree t <div><LoggerDeps name=a dep=2/><LoggerDeps name=b dep=2/></div>
         render t
         flush
         log
         dump
         tree t <div><LoggerDeps name=a dep=2/><LoggerDeps name=b dep=3/></div>
         render t
         flush
         log
         dump

output:  log run a 1
         log run b 1
         dump 1
         node 0 a div ""
         node 1 b em ""
         text 2 "a:1"
         node 1 c em ""
         text 2 "b:1"
         log clean a 1
         log clean b 1
         log run a 2
         log run b 2
         dump 2
         node 0 a div ""
         node 1 b em ""
         text 2 "a:2"
         node 1 c em ""
         text 2 "b:2"
         log clean b 2
         log run b 3
         dump 3
         node 0 a div ""
         node 1 b em ""
         text 2 "a:2"
         node 1 c em ""
         text 2 "b:3"
```

Step two makes both effects due. `clean a 1`, `run a 2`, `clean b 1`, `run b 2` would be tidier, and React does not do that: every `clean` line comes before any `run` line. In step three `a` keeps `dep=2` and its effect stays asleep, which leaves two lines for `b`. Each line names the dep of the run it belongs to, hence `clean b 2` and not `clean b 3`.

### Example 3: mounting and removing are mirror images (test `11-R5-outer-and-logger-removed`)

```
input:   tree t <div><Outer name=o/><Logger name=l/></div>
         render t
         flush
         log
         dump
         tree t <p>x</p>
         render t
         flush
         log
         dump

output:  log mount o.inner
         log mount o
         log mount l
         dump 1
         node 0 a div ""
         node 1 b div ""
         node 2 c em ""
         text 3 "o.inner"
         node 1 d em ""
         text 2 "l"
         log cleanup o
         log cleanup o.inner
         log cleanup l
         dump 2
         node 0 e p ""
         text 1 "x"
```

Mount goes inner `Logger`, `Outer`, sibling. Removal goes `Outer`, the `Logger` inside it, sibling. The fiber deleted in this example is the root `div`, with the components sitting inside it, which means your commit has to look inside deleted fibers.

## Constraints

The 48 tests are each requirement's cases, two scripted sessions and five seeded random sessions (`-Fresh` draws five new). The longest scenario has 87 lines, no tree has more than 5 components, and the dumps are small, while a random session mixes prop changes, clicks, replacing the root, removing everything, and adding or removing items at the end of the list. The limit is 10 seconds a test, and a correct solution needs far less.

## Hints

<details><summary>Hint 1: where to start</summary>

Compare `useEffect` with `useState`. Both keep something on the fiber between renders, and the slot and `hookIndex` machinery from 10 carries over unchanged. The difference is timing: a state update is applied while the component renders, and an effect cannot be.
</details>

<details><summary>Hint 2: the approach</summary>

`useEffect` takes a slot and fills it in: the effect, the new deps, the deps and cleanup of the last run, and whether the effect is due (no deps array, no earlier run, or an item that differs). Nothing runs at this point. Run things at the end of `commitRoot`, once the DOM matches the new tree, and walk the fibers twice: cleanups first, effects second. Removed components are no longer in the new tree. The commit has to learn about them from the render phase, as it already does for deleted nodes. Store each run's cleanup in the slot and never rebuild it from newer props.
</details>

<details><summary>Hint 3: the traps</summary>

- `===` or `!==` on the `deps` arrays reports a difference on every render. Compare item by item.
- `undefined` and `[]` mean different things. The first is due on every render, the second on the first render only.
- Your work loop visits a parent before its children, and an effect list built in that order has the parent first. Mount wants children first.
- Cleanup then effect, component by component, interleaves the two. Every cleanup has to run before the first effect.
- A removed component may sit under a plain element that went with it. A walk over only the top fiber of the deleted subtree misses every cleanup below.
- Removal wants a parent's cleanup before its children's, the reverse of mount order. One walk order serves only one of them.
- The cleanup to call is the one the previous run returned. Let a newer render overwrite it and `clean a 1` turns into `clean b 1`.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
useEffect(effect, deps):
    slot = the old fiber's slot at hookIndex, or { deps: none, cleanup: none }
    slot.effect = effect
    slot.nextDeps = deps
    slot.due = slot.deps is none or deps is none or some item differs from slot.deps (Object.is)
    wipFiber.hooks.push(slot); hookIndex += 1

at the end of commitRoot, after the DOM is updated:
    for each deleted fiber, parent first, then each of its descendants: run the cleanup of its slots
    for each fiber of the new tree: run the cleanup of its due slots
    for each fiber of the new tree, children before parents:
        for each due slot: slot.cleanup = slot.effect(); slot.deps = slot.nextDeps; slot.due = false

run a cleanup: if the slot has one, call it and forget it
```
</details>

## Checking your solution

```
.\check 11                          every test, grouped by requirement
.\check 11 -Case 11-R6-outer-inner-first   one test: its scenario, the log you should get and yours
.\check 11 -Fresh                   five new random sessions
.\check 11 -Dispute <id> "why"      set a test aside when you are sure it is wrong
```

Running the effects during the component function fails like this:

```
  R1  An effect runs once per mount, and only after the render that cre... .    4 / 6   FAILED
      x 11-R1-nothing-runs-before-the-commit  two Loggers in a div: after 4 units of work no effect has run, after the flus...
          line 2: expected `dump 1`, got `log mount a`  (in `idle 4`)
          likely cause: R1 - An effect runs once per mount, and only after the render that created it has been committed
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog; orders pinned in _source/react-observed.md
          reproduce: py -P tools/run_js.py build/bugs/11/effects-in-render 11 build/cases/11/11-R1-nothing-runs-before-the-commit.in build/cases/11/11-R1-nothing-runs-before-the-commit.out
```

## After you pass: compare with the author's code

In Jongeneel's class [`Component`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components) the three moments are methods. `notifyMounted` schedules `componentDidMount`, `getUpdateDiff` schedules `componentDidUpdate`, and `unmount` calls `componentWillUnmount`. Mapped onto hooks, `componentDidMount` is an effect with `[]`, `componentDidUpdate` is an effect with no deps array (which also runs after the mount, where his hook does not) and `componentWillUnmount` is the cleanup. He has no deps lists and no cleanup that runs between updates.

Where the post's version parts company with the tests, most important first.

`unmount` is called only for a component that is a direct member of a removed child list, or that gets replaced by a non-text node, which means a component below a removed element, or below another removed component, never hears about it. In the repository a parent whose tag changes is replaced without unmounting what it held, and a component replaced by text is not unmounted either. R5 checks the nested case with `Outer`. React cleans up every component of the removed subtree.

His mount and update hooks run from `setTimeout`, after the diff has been applied. `componentDidMount` reaches every component that mounts, nested ones too, because `renderElement` recurses. `componentDidUpdate` is queued on every re-render of a component, even when the diff is empty, and it is queued before the DOM is patched. In an update, the mount hook of a component that appears in the update runs after its parent's update hook; React runs the new child's mount hook first. A hook queued before an unmount still fires afterwards, on an instance without an element. `componentWillUnmount` is the exception to the timers: `unmount` calls it at once, before the update touches the DOM. Mounting is the one place the two orders agree, since nested components queue their timers bottom-up and children mount before parents.

His `setState` is synchronous and unbatched: three calls render three times, where React renders once and your `useState` queues. The "Effects" row of [React today](docs/react-today.md) covers where React 19 differs from both posts.
