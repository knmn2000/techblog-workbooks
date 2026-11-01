# 11 · useEffect

**Difficulty:** Hard · **Assignment** 11 of 12 · **Check:** `.\check 11`

**Tags**
- *Language:* [arrow functions and closures](#primer/js-functions-closures) · [equality and `Object.is`](#primer/js-equality) · [array methods](#primer/js-arrays)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [useEffect: after the DOM is updated](#primer/react-effects) · [the render phase and the commit phase](#primer/react-render-commit) · [useState and the rules of hooks](#primer/react-state) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

Neither post builds `useEffect`, so this assignment is an extension: nothing in either author's code corresponds to it, and the behaviour comes from React 19.3.1, which the checker runs. Jongeneel's article has the same three moments as class methods: componentDidMount in [5.2 Mounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components), componentDidUpdate in [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and componentWillUnmount in [5.6 Unmounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.6%20Unmounting%20components). A figure of the lifecycle hooks opens [section 5](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.%20Components%20and%20reactive%20scopes); read it and the text around it if you want the idea, and skip his code, since his mount and update hooks run from timers and this assignment follows React. Pombo's [epilogue](https://pomb.us/build-your-own-react/#epilogue) lists `useEffect` as an easy addition and says no more. This page is complete without either.

## Learning material

- [useEffect: after the DOM is updated](#primer/react-effects): what an effect and a cleanup are, what a deps array promises, and why the order of effects is a rule instead of an accident.
- [The render phase and the commit phase](#primer/react-render-commit): used in a new way. Effects are the first thing that must wait for the commit to be over, so the render phase may only remember them.
- [Arrow functions and closures](#primer/js-functions-closures): an effect and the cleanup it returns close over the props of the render that ran them, and the tests check that they keep doing so.
- [Equality and `Object.is`](#primer/js-equality): the deps of two renders are two different arrays with equal contents.
- [Reconciliation by type and position](#primer/react-reconciliation): used in a new way. The fibers you throw away still own cleanups.

## Source material

- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d): the lifecycle figure at the start of [section 5](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.%20Components%20and%20reactive%20scopes), [5.2 Mounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components), [5.3 Updating a component](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.3%20Updating%20a%20component) and [5.6 Unmounting components](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.6%20Unmounting%20components)
- Rodrigo Pombo, [Epilogue](https://pomb.us/build-your-own-react/#epilogue)
- React documentation: [useEffect](https://react.dev/reference/react/useEffect) and [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)

## Where this fits

Function components can render and, since 10, remember. They still cannot do anything about the world outside the tree, such as setting a page title or starting a timer. `useEffect` goes into `hooks.js` beside `useState` and uses the same slots, and `commit.js` runs what the hook has remembered once the DOM matches the new tree. Assignment 12 uses one effect to keep `document.title` in step with a todo list.

## The problem

Add `useEffect(effect, deps)` to `Didact`. The catalog has components that write a line to the run's log from their effects and cleanups; a scenario mounts, updates and removes them, reads the log after each step, and the checker compares your log with the one React 19 produces.

### Input

The checker runs `node assignments/assignment_11_use_effect.js <input-file> <output-file>`. The program imports `../harness/env.js` first, so `document` and a controllable `requestIdleCallback` exist before your library loads, then imports `Didact` from `../src/didact/index.js`, and ends with `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, which reads the scenario, runs it against your library and writes the output file. The Boilerplate has it finished; from a blank start you write those lines yourself. The scenario file uses these lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Names a tree with one root element. A capitalised tag such as `<LoggerDeps name=x dep=1/>` is a catalog component, and attribute values are strings. Redefining a name is allowed. |
| `render <name>` | Calls `Didact.render(tree, container)`. No work happens yet. |
| `idle <k>` | Runs one idle period in which your work loop may do at most `k` units of work, then prints `idle <units done>`. |
| `flush` | Runs idle periods until no work is left. |
| `click #<id>` | A bubbling `click` on the element with that id, then a flush. |
| `log` | Prints the log entries recorded since the previous `log`. |
| `dump` | Prints the page. |

Every `render` that is followed by another `render` has a `flush` in between.

### Output

`log` prints one line per entry, in the order the entries were recorded, and nothing when there are none:

```
log <text>
```

`dump` prints `dump <n>` and then the page as in the earlier assignments: `node <depth> <label> <tag> "<props>"` for each element and `text <depth> "<text>"` for each run of text, parents first, the container left out. A label is a letter given to an element the first time a dump shows it and kept for good, so the same letter means the same node. `idle <k>` prints `idle <units>`, the number of units your loop did in that period: `k` while at least `k` units are left, fewer when the work finishes.

Most scenarios end every step with `log` and `dump`. The dump is the boundary between two steps, so a line that shows up one step late fails the test.

### The components the scenarios use

They live in `harness/catalog.js`. Each effect writes the text shown here to the log (names are single words).

| Component | Props | Renders | Effect |
|---|---|---|---|
| `Logger` | `name` | `<em>{name}</em>` | deps `[]`. Logs `mount <name>`; the cleanup logs `cleanup <name>`. |
| `LoggerDeps` | `name`, `dep` | `<em>{name}:{dep}</em>` | deps `[dep]`. Logs `run <name> <dep>`; the cleanup logs `clean <name> <dep>`. |
| `LoggerEvery` | `name` | `<div><em>{name}:{count}</em><button id="{name}-btn">bump</button></div>` | no deps array. Logs `run <name>`; the cleanup logs `clean <name>`. The button adds 1 to a `useState` counter. |
| `Outer` | `name` | `<div>` holding `<Logger name="{name}.inner"/>` | deps `[]`. Logs `mount <name>`; the cleanup logs `cleanup <name>`. |
| `Frame`, `Counter` | as before | as before | none. `Counter`'s button has the id `c-inc`. |

A tree never holds more than one `LoggerEvery`.

### What `useEffect` does

You write `useEffect(effect, deps)` in `src/didact/hooks.js` and export it on the `Didact` object. `effect` is a function that may return another function, the cleanup. `deps` is an array, or left out (`undefined`; `null` counts the same). No array means the effect is due on every render. The catalog passes an array or nothing, and an array never changes its length from one render of a component to the next, so a change of length is untested: comparing item by item up to the shorter length is fine, and so is calling a different length a change.

An effect never runs while a component's function is running. The function only registers it. After the render phase has finished and the commit has put the new tree on the page, the effects that are due run, all inside the same flush. An effect is due when its component has mounted, when `deps` is `undefined`, or when `deps` differs from the deps of the run before, compared item by item (`Object.is`) and not as arrays: every render makes a new array. An effect that is not due does not run and does not clean up. A cleanup runs before the effect that replaces it and when the component is removed, in the order given under "The order" below.

An effect keeps the function and the cleanup of the render that ran it. A later render that brings new props but no new deps changes nothing, so when the component is removed, its cleanup still reports the old props.

### The order

React 19.3.1 does this, and the tests pin it:

1. Mount, post-order: the effects of a component's children run before the component's own, and siblings run left to right. `Outer` mounts `name.inner` first, then `name`.
2. Removal, pre-order: when a subtree is removed, a component's cleanup runs before the cleanups of the components below it, and siblings run left to right. `Outer` cleans `name` first, then `name.inner`. The cleanup runs for every component in the subtree, however deep, also below plain elements.
3. A commit that keeps its components and re-runs some effects: every cleanup of the commit first, then every effect. Within each group siblings go left to right.
4. A commit that replaces a subtree and mounts another one: every cleanup of what goes away runs before any effect of what is new.

No test mixes a removal and a re-run in one commit: no commit removes a component while another component's effect runs again, so how the cleanups of the removed subtree interleave with the cleanups of re-running effects is untested. No test re-runs the effects of a component and of one of its descendants together, and none mounts a component in a commit that also re-runs another effect. The order in those situations is yours to pick. React runs the descendants' cleanups and effects first in the second one.

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

The tree has 8 units of work: the container's root, the `div`, two `Logger` components, their two `em` elements and two text nodes. `idle 4` does four of them, which is enough for the first `Logger`'s function to have run, and still no effect appears in the log and the page is empty (`dump 1` has no lines). The `flush` finishes the render, commits, and runs both effects.

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

In the second step both effects are due. Doing `clean a 1`, `run a 2`, `clean b 1`, `run b 2` would be tidier, and React does not do it: all the `clean` lines come first. In the third step `a` keeps `dep=2`, so its effect stays asleep, and the log has only the two lines for `b`. Each line names the dep of the run it belongs to, `clean b 2` and not `clean b 3`.

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

On mount the inner `Logger` goes first, then `Outer`, then the sibling. On removal `Outer` goes first, then the `Logger` inside it, then the sibling. The whole `div` is removed here, so the components are not direct children of anything that was deleted: your commit has to look inside the deleted fibers.

## Constraints

48 tests: the cases of each requirement, two scripted sessions and five seeded random ones (`-Fresh` draws five new). The longest scenario has 87 lines, no tree has more than 5 components, and the dumps are small. The random sessions mix prop changes, clicks, replacing the root, removing everything, and adding or removing items at the end of the list. Each test has a 10-second limit and a correct solution needs far less.

## Hints

<details><summary>Hint 1: where to start</summary>

Ask what `useEffect` has in common with `useState` and what is different. Both remember something on the fiber between renders, so the slot and `hookIndex` machinery from 10 applies as it is. They differ in when the work happens: a state update is applied while the component renders, an effect cannot be.
</details>

<details><summary>Hint 2: the approach</summary>

Make `useEffect` take a slot and fill it in: the effect, the new deps, the deps and cleanup of the last run, and whether the effect is due (no deps array, no earlier run, or an item that differs). Nothing runs. At the end of `commitRoot`, once the DOM matches the new tree, go through the fibers: first the cleanups, then the effects. Removed components are no longer in the new tree, so the commit has to remember them from the render phase, as it already does for deleted nodes. Keep the cleanup that each run returned in the slot, and never rebuild it from newer props.
</details>

<details><summary>Hint 3: the traps</summary>

- Comparing `deps` arrays with `===` or `!==` finds a difference on every render. Compare them item by item.
- `undefined` and `[]` are different: the first is due on every render, the second only on the first.
- Collecting effects in the order your work loop visits fibers puts a parent before its children. Mount wants the opposite.
- Running a cleanup and then its effect, component by component, interleaves them. Run every cleanup before the first effect.
- A removed component can sit under a plain element that was removed with it. Walking only the top fiber of a deleted subtree misses every cleanup below it.
- A removal wants a parent's cleanup before its children's, which is the reverse of the mount order. One walk order serves only one of them.
- The cleanup that runs is the one the previous run returned. If a new render replaced it with its own, `clean a 1` turns into `clean b 1`.
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

An implementation that runs effects while the component function runs fails like this:

```
  R1  An effect runs once per mount, and only after the render that cre... .    4 / 6   FAILED
      x 11-R1-nothing-runs-before-the-commit  two Loggers in a div: after 4 units of work no effect has run, after the flus...
          line 2: expected `dump 1`, got `log mount a`  (in `idle 4`)
          likely cause: R1 - An effect runs once per mount, and only after the render that created it has been committed
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog; orders pinned in _source/react-observed.md
          reproduce: py -P tools/run_js.py build/bugs/11/effects-in-render 11 build/cases/11/11-R1-nothing-runs-before-the-commit.in build/cases/11/11-R1-nothing-runs-before-the-commit.out
```

## After you pass: compare with the author's code

Jongeneel's class [`Component`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=5.2%20Mounting%20components) has the three moments as methods. `notifyMounted` schedules `componentDidMount`, `getUpdateDiff` schedules `componentDidUpdate`, and `unmount` calls `componentWillUnmount`. `componentDidMount` plays the part of an effect with `[]`, `componentDidUpdate` of an effect with no deps array (which also runs after the mount, where his hook does not), and `componentWillUnmount` of the cleanup. He has no deps lists and no cleanup that runs between updates.

The post's version departs from the tests in these places, the most important first:

`unmount` is called only for a component that is a direct member of a removed child list or that is replaced by a non-text node, so a component below a removed element, or below another removed component, never hears about it. In the repository, a parent whose tag changes is replaced without unmounting what it held, and a component replaced by text is not unmounted either. R5 checks the nested case with `Outer`, and React cleans up every component of the removed subtree.

The mount and update hooks run from `setTimeout`, after the diff has been applied. `componentDidMount` reaches every component that mounts, nested ones included, because `renderElement` recurses. `componentDidUpdate` is queued by every re-render of a component, even one whose diff is empty, and it is queued before the DOM is patched. The mount hook of a component that appears in an update runs after its parent's update hook, where React runs the new child's mount hook first. A hook queued before an unmount still fires afterwards, on an instance without an element. `componentWillUnmount` is the exception to the timers: `unmount` calls it at once, before that update touches the DOM. Mounting is the one place the orders agree: nested components queue their timers bottom-up, so children mount before parents.

`setState` there is synchronous and unbatched, so three calls render three times, where React renders once and your `useState` queues. [React today](docs/react-today.md) has an "Effects" row on where React 19 differs from both posts.
