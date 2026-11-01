# 09 · Function components

**Difficulty:** Medium · **Assignment** 9 of 12 · **Check:** `.\check 09`

**Tags**
- *Language:* [`typeof` and the types you meet](#primer/js-typeof)
- *Library:* [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [function components](#primer/react-function-components) · [elements and `props.children`](#primer/react-elements) · [fibers](#primer/react-fibers) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

The page below is complete without the post. Pombo's [Step VII: Function Components](https://pomb.us/build-your-own-react/#step-vii-function-components) is short and worth reading in full, up to the heading of Step VIII. The code he shows beside the text is the author's answer to this assignment, so read the words and skip the frames.

## Learning material

- [Function components](#primer/react-function-components): a function that takes props and returns the element to draw, and the two ways its fiber differs from an element's.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): used in a new way. A component has no node, so the parent of a node and the node to remove have to be found by walking through the fibers that have none.
- [Elements and `props.children`](#primer/react-elements): used in a new way. The elements written between a component's tags reach the function as `props.children`, and the function decides where they go.
- [Fibers](#primer/react-fibers): used in a new way. A fiber can now be a unit of work without being a DOM node.
- [Reconciliation by type and position](#primer/react-reconciliation): used in a new way. For a component the type is the function itself, so two renders of `Greeting` agree and `FnA` against `FnB` do not.
- [Keys](#primer/react-keys): used in a new way. A keyed component keeps its nodes through insertions, removals and reorders like a keyed element does.

## Source material

- Rodrigo Pombo, [Step VII: Function Components](https://pomb.us/build-your-own-react/#step-vii-function-components)
- React documentation: [Your first component](https://react.dev/learn/your-first-component) and [Passing props to a component](https://react.dev/learn/passing-props-to-a-component)

## Where this fits

Until now every fiber stood for a node, and a fiber's children were the elements written under it. A function component breaks both habits. Hooks in 10 and 11 will live on component fibers, and the todo app of 12 is made of components. You change `render.js` to call the function and `commit.js` to cope with fibers that have no node.

## The problem

Let a function be the `type` of an element. A scenario builds trees that use the catalog's components, renders and re-renders them, clicks a button now and then and dumps the page. The checker compares your dumps and logs with React's, and in a few tests the sizes of your idle periods with a formula.

### Input

The entry program, `node assignments/assignment_09_function_components.js <input-file> <output-file>`, has the same small job as the one in 06 to 08. It imports `../harness/env.js` first, then `Didact` from `src/didact/index.js`, and awaits `runScenarioFile` from `../harness/scenario.js` with the input path, the output path and `Didact`. The Boilerplate has it ready; with a blank start you write it. The lines the scenarios use:

| Line | What happens |
|---|---|
| `tree <name> <markup>` | Stores a tree under a name. A tag with a capital letter, as in `<Frame title=News>`, is a catalog component and is given its attributes as props, as strings. |
| `render <name>` | Calls `Didact.render` with the tree and the container. Nothing runs yet. |
| `flush` | Runs idle periods until the loop is idle. Except in the units tests, a `flush` comes after every `render`. |
| `idle <k>` | Runs one idle period in which `timeRemaining()` allows `k` units, and prints `idle <units run>`. |
| `click #<id>` | Fires a bubbling `click` on the element with that id, then flushes. |
| `log` | Prints one `log <name>` line per handler call since the previous `log` line. |
| `dump` | Prints the page. |

Handlers are written `onClick=@name`. Calling one adds `name` to the log. `key="a"` and `key=a` mean the same.

### Output

A dump lists the nodes under the container, in document order, and leaves the container out.

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

`<tag>` is lower case. The props field shows `className`, `id`, `title` and (on inputs) `value` when they are not at their defaults, sorted by name; spaces, quotes and `%` are percent-encoded. Neighbouring text nodes become one `text` line. The `<label>` is the thing to watch: elements are named `a`, `b`, ... in the order dumps first show them, and the name sticks to the node. If two dumps show the same label, it is the same DOM node. A node that your library threw away and built again gets a new label.

A dump taken while a first render is still waiting for idle periods shows an empty container, because nothing is committed before the last unit. An `idle` line prints the number of units that period ran, and `idle 0` once nothing is left.

### The components

The harness has more of them (`harness/catalog.js`), but the ones that need `useState` or `useEffect` have to wait for 10 and 11. These four are what the tests use.

| Component | Props | What it returns |
|---|---|---|
| `Greeting` | `name` | `<h1>` with the two text children `Hi ` and the name, which a dump shows as the single line `Hi Ann` |
| `Frame` | `title` and children | `<section>` that holds an `<h2>` with the title, followed by every child it was given |
| `FnA` | none | `<i>a</i>` |
| `FnB` | none | `<b>b</b>` |

Each returns one element. `Frame` puts `props.children` into the new element's children as they are: elements, components and text alike.

### What the library does with a component

- A function used as `type` is a component. Call it with the element's `props` (the `children` array included), and take the one element it returns as the single child of the component's fiber.
- A component's fiber has no node. It still is a unit of work: for the idle periods, the unit count of a tree is 1 for the container's root fiber, plus 1 for every element and every text node, plus 1 for every component.
- A node's parent in the page is the node of the nearest ancestor fiber that has one. A component at the top of the tree has the container as its parent.
- A component's own node is the first node below it, looking through any components it returns. That is the node to place, to move and to remove for the component.
- Types are compared as before, and for components the type is the function. The same function at the same position (or with the same key) keeps the old nodes and gets the new props. Another function, or an element with a tag, replaces them in place.
- A component that goes away takes its node out of the page, together with everything below the node. Removal works the same whenever the component was mounted, including in the render right before.
- Keys on components follow the rules of 07 and 08. The `key` stays in the `props` object the function receives, as it does for elements, and the catalog's components ignore it.
- A component never returns `null`, `undefined` or an array in the tests.

## Requirements

The report groups the tests by requirement, and each test belongs to a single one.

- **R1** A function component's output is rendered, and the function receives its element's props.
- **R2** Components nest, stand next to each other and can be the whole tree.
- **R3** `props.children` carries the elements, text and components that were written inside a component, in order.
- **R4** A component of the same type at the same position keeps its nodes and takes new props, text and handlers.
- **R5** Another component, or a plain element, at that position replaces the component's nodes in place, also in front of another component.
- **R6** A component that disappears takes its nodes out of the page, and only those.
- **R7** A component mounted by one render can be removed or replaced by the very next render, and by a later one.
- **R8** Keyed components keep their nodes and typed values when others are inserted, removed or reordered.
- **R9** A component is a unit of work of its own: it adds one to the count and has no node.
- **E2E** Whole sessions with several components, clicks and logs.

## Examples

### Example 1: a Frame with a component, an element and text inside (test `09-R3-frame-mixed-children`)

```
input:   tree t1 <Frame title=Mix><Greeting name=A/><FnB/><em>e</em>tail</Frame>
         render t1
         flush
         dump

output:  dump 1
         node 0 a section ""
         node 1 b h2 ""
         text 2 "Mix"
         node 1 c h1 ""
         text 2 "Hi A"
         node 1 d b ""
         text 2 "b"
         node 1 e em ""
         text 2 "e"
         text 1 "tail"
```

The whole tree is one component, so the container's first child is the `section` that `Frame` returned. It holds the `h2`, then what was written inside `Frame`: the `h1` of the `Greeting`, the `b` of `FnB`, the `em`, and the text `tail`, which is a node of its own at depth 1. None of the three components shows up in the dump, because a component has no node.

### Example 2: mounted, then removed by the next render (test `09-R7-mount-then-remove`)

```
input:   tree t1 <div><p>a</p><FnA/></div>
         render t1
         flush
         dump
         tree t2 <div><p>a</p></div>
         render t2
         flush
         dump

output:  dump 1
         node 0 a div ""
         node 1 b p ""
         text 2 "a"
         node 1 c i ""
         text 2 "a"
         dump 2
         node 0 a div ""
         node 1 b p ""
         text 2 "a"
```

The second dump is the point of the test. The `i` was put into the page by the render that mounted `FnA`, and the very next render removes it. A program that goes on committing the removed fiber's children after taking the node out puts the `i` back, and the page keeps a node that no tree describes.

### Example 3: units of a component (test `09-R9-units-greeting`)

```
input:   tree t1 <Greeting name=Ann/>
         render t1
         dump
         idle 2
         idle 2
         dump
         idle 2
         dump
         idle 2

output:  dump 1
         idle 2
         idle 2
         dump 2
         idle 1
         dump 3
         node 0 a h1 ""
         text 1 "Hi Ann"
         idle 0
```

The units are the root fiber, the `Greeting`, its `h1` and two text nodes, so five: 2, 2 and 1 over three periods. The page stays empty through the first two periods and the commit lands in the third. Without a unit for the component there would only be four, and the periods would read 2, 2, 0.

## Constraints

Scenarios have at most 42 lines and at most 12 renders. Texts are short, and every `Greeting` gets a name. The 45 tests cover each requirement, two longer sessions and five seeded random runs (a fresh seed gives five new ones), and the three units tests are the only ones with `idle` lines. A case has a 10-second limit and needs a small fraction of it.

## Hints

<details><summary>Hint 1: where to start</summary>

Find the two places that assume a fiber has a node: the unit that creates it, and the commit that appends, updates and removes it. In the first one, a component needs the function called instead. In the second, `fiber.parent.dom` is null whenever the parent is a component, and `fiber.dom` is null for the component itself.
</details>

<details><summary>Hint 2: the approach</summary>

Split `performUnitOfWork` in two, the way Pombo does with `updateFunctionComponent` and `updateHostComponent`: a function component branch that calls the function and passes its single result to `reconcileChildren`, and the branch you already have, which makes the node and reconciles the children from the props. The reconciler needs no change, since it only compares types. In the commit, write one helper that finds the DOM parent by climbing `parent` until a fiber has a `dom`, and one that finds a fiber's own node by descending `child` until a fiber has a `dom`. Use them for placing and for removing. The node a component is placed before is the first later sibling whose node, found by descending, is already in the page, and that search may have to go up through components.
</details>

<details><summary>Hint 3: the traps</summary>

- Do not give a component fiber a DOM node, and do not call `updateDom` on it. Guard on `fiber.dom`.
- A component's props include the children. The function gets the whole props object, `children` included.
- In the commit, a deleted fiber is only removed. If you go on to commit its children, they still carry the tags from the render that mounted them, and a component mounted by the render right before is put back into the page. A fiber that has been rendered once more is not affected, which is why this passes the easy tests.
- A component and its siblings put their nodes into one DOM parent: the first ancestor fiber that has a node. Climb through components for the parent, and descend through them for a node.
- When the node to insert before belongs to a sibling that is a component, take the first node below that component: the component has no node itself.
- `FnA` and `FnB` have the same shape and different types. Compare the function, not what it returns.
- Mount one component with several siblings and give it a new type in the next render: the new node must land in the old node's place, not at the end of the parent.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
performUnitOfWork(fiber):
    if fiber.type is a function:
        children = [ fiber.type(fiber.props) ]
    else:
        if fiber has no dom: fiber.dom = createDom(fiber)
        children = fiber.props.children
    reconcileChildren(fiber, children)
    return the next fiber (child, else sibling, else an ancestor's sibling)

parentDom(fiber):  climb fiber.parent until a fiber has dom; return that dom
ownDom(fiber):     descend fiber.child until a fiber has dom; return that dom

commit of a placement:  parentDom(fiber).insertBefore(ownDom(fiber), node in the page after fiber, or null)
commit of an update:    updateDom(fiber.dom, ...) only when fiber.dom exists
commit of a removal:    parentDom(fiber).removeChild(ownDom(fiber)); then stop, do not walk the fiber's children
```
</details>

## Checking your solution

```
.\check 09                          every test, grouped by requirement
.\check 09 -Case 09-R7-mount-then-remove   one test with its input, the expected dumps and yours
.\check 09 -Fresh                   five new random sessions, to try your code on scenarios you haven't seen
.\check 09 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A commit that keeps walking the children of a removed fiber, as the post's does, fails R7 like this:

```
  R7  A component mounted in one render can be removed or replaced by ... .    1 / 8   FAILED
      x 09-R7-mount-then-remove  FnA is mounted and removed by the very next render
          unexpected extra output at line 11: `node 1 c i ""`
          likely cause: R7 - A component mounted in one render can be removed or replaced by the very next render, with or without a render in between
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle)
          reproduce: py -P tools/run_js.py build/bugs/09/stale-deletion 09 build/cases/09/09-R7-mount-then-remove.in build/cases/09/09-R7-mount-then-remove.out
```

## After you pass: compare with the author's code

[Pombo's Step VII](https://pomb.us/build-your-own-react/#step-vii-function-components) checks `fiber.type instanceof Function` in `performUnitOfWork` and calls `updateFunctionComponent` or `updateHostComponent`. The first calls `fiber.type(fiber.props)` and hands the result to `reconcileChildren` as a one-element list, the second creates the node and reconciles `props.children`. In `commitWork` a loop climbs `fiber.parent` until it finds a fiber with a `dom`, and `commitDeletion` descends `fiber.child` until it finds one. The workbook splits his single file: `performUnitOfWork` and the two update functions sit in `render.js`, the commit in `commit.js`. Hint 4 makes the climb and the descent helpers of their own, `parentDom` and `ownDom`, where his `commitWork` has the climb inline and `commitDeletion` takes the parent node as an argument.

His deletion leaves a node behind when the component was mounted by the render right before. In the post's `commitWork` a deleted fiber is removed, and then its `child` and `sibling` are walked like those of any other fiber. The children of a component mounted one render ago carry `PLACEMENT` yet, and their climb for a DOM parent now passes through the component to the live parent, so `appendChild` puts the node back. For a plain element the same walk only appends into a node that has been detached a moment ago, which hides it. After one more render the tags read `UPDATE` and the problem is gone, and the post's own examples, `App` and `Counter`, never remove a component. Swapping `FnA` for `FnB` is hit in the same way, and the new node is appended at the end of the parent, where the old one stood in the middle. R7 asks for removal and replacement in the very next render, with and without a render in between.

A component that returns `null` renders nothing in his code, and removing it later throws inside `commitDeletion`. The tests never return `null` from a component, so that case, like arrays and fragments, stays outside the workbook. The page for 10 says what that exception does to his work loop. [React today](docs/react-today.md) collects the other places where React 19 and the post differ.
