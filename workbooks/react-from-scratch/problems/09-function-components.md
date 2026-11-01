# 09 · Function components

**Difficulty:** Medium · **Assignment** 9 of 12 · **Check:** `.\check 09`

**Tags**
- *Language:* [`typeof` and the types you meet](#primer/js-typeof)
- *Library:* [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing) · [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [function components](#primer/react-function-components) · [elements and `props.children`](#primer/react-elements) · [fibers](#primer/react-fibers) · [reconciliation by type and position](#primer/react-reconciliation)

## Read in the blog first

You can do the assignment from this page alone. Pombo's [Step VII: Function Components](https://pomb.us/build-your-own-react/#step-vii-function-components) is short and worth reading in full, up to the heading of Step VIII. Read his words and skip the code frames beside them. That code is the author's answer to this assignment.

## Learning material

- [Function components](#primer/react-function-components): a function from props to the element to draw, and the two ways its fiber differs from an element's.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): a new way to use it. A component has no node, so finding the parent of a node, or the node to remove, means walking through fibers that have none.
- [Elements and `props.children`](#primer/react-elements): used differently now. Whatever is written between a component's tags reaches the function as `props.children`, and the function decides where it goes.
- [Fibers](#primer/react-fibers): in a new role. A fiber can now be a unit of work without being a DOM node.
- [Reconciliation by type and position](#primer/react-reconciliation): applied to new things. The type of a component is the function itself. Two renders of `Greeting` agree, and `FnA` against `FnB` do not.
- [Keys](#primer/react-keys): applied in a new place. A keyed component keeps its nodes through insertions, removals and reorders, the way a keyed element does.

## Source material

- Rodrigo Pombo, [Step VII: Function Components](https://pomb.us/build-your-own-react/#step-vii-function-components)
- React documentation: [Your first component](https://react.dev/learn/your-first-component) and [Passing props to a component](https://react.dev/learn/passing-props-to-a-component)

## Where this fits

Up to here a fiber was a node, and its children were the elements written under it. A function component breaks both. `render.js` has to call the function, and `commit.js` has to cope with fibers that have no node. Hooks in 10 and 11 hang off component fibers, and the todo app in 12 is made of them.

## The problem

Let a function be the `type` of an element. A scenario builds trees out of the catalog's components, renders and re-renders them, clicks a button now and then, and dumps the page. Your dumps and logs are compared with React's. In a few tests the sizes of your idle periods are compared with a formula.

### Input

The entry program, `node assignments/assignment_09_function_components.js <input-file> <output-file>`, is the same few lines as in 06 to 08: import `../harness/env.js` first, then import `Didact` from `src/didact/index.js`, then await `runScenarioFile` from `../harness/scenario.js` with the input path, the output path and `Didact`. The Boilerplate has it written, and a blank start leaves it to you. Scenarios use these lines:

| Line | What happens |
|---|---|
| `tree <name> <markup>` | Stores a tree under a name. A tag with a capital letter, as in `<Frame title=News>`, is a catalog component and gets its attributes as props, as strings. |
| `render <name>` | Calls `Didact.render` with the tree and the container. Nothing runs yet. |
| `flush` | Runs idle periods until the loop is idle. Outside the units tests, every `render` is followed by a `flush`. |
| `idle <k>` | Runs one idle period in which `timeRemaining()` allows `k` units, and prints `idle <units run>`. |
| `click #<id>` | Fires a bubbling `click` on the element with that id, then flushes. |
| `log` | Prints one `log <name>` line per handler call since the previous `log` line. |
| `dump` | Prints the page. |

Handlers are written `onClick=@name`, and calling one adds `name` to the log. `key="a"` and `key=a` mean the same.

### Output

A dump lists the nodes under the container, in document order, and leaves the container out.

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

`<tag>` is lower case. The props field shows `className`, `id`, `title` and (on inputs) `value` when they are off their defaults, sorted by name, with spaces, quotes and `%` percent-encoded. Neighbouring text nodes become one `text` line. Watch the `<label>`. Elements are named `a`, `b`, ... in the order dumps first show them, and a name sticks to its node. Same label in two dumps, same DOM node; a node your library threw away and built again comes back under a new one.

While the first render is still waiting for idle periods, a dump shows an empty container. Nothing is committed before the last unit. An `idle` line prints how many units its period ran, and `idle 0` once nothing is left.

### The components

`harness/catalog.js` has more of them, but the ones that need `useState` or `useEffect` wait for 10 and 11. The tests use these four.

| Component | Props | What it returns |
|---|---|---|
| `Greeting` | `name` | `<h1>` with the two text children `Hi ` and the name, which a dump shows as the single line `Hi Ann` |
| `Frame` | `title` and children | `<section>` that holds an `<h2>` with the title, followed by every child it was given |
| `FnA` | none | `<i>a</i>` |
| `FnB` | none | `<b>b</b>` |

Each returns a single element. `Frame` puts `props.children` into the new element's children as they are, whether elements, components or text.

### What the library does with a component

- A function used as `type` is a component. Call it with the element's `props` (the `children` array included) and take the one element it returns as the single child of the component's fiber.
- A component's fiber has no node, but it is still a unit of work. For the idle periods, the unit count of a tree is 1 for the container's root fiber, plus 1 for every element and every text node, plus 1 for every component.
- A node's parent in the page is the node of the nearest ancestor fiber that has one. A component at the top of the tree has the container as its parent.
- A component's own node is the first node below it, looking through any components it returns. That is the node to place, to move and to remove for the component.
- Types are compared as before, and for components the type is the function. The same function at the same position (or with the same key) keeps the old nodes and gets the new props. Another function, or an element with a tag, replaces them in place.
- A component that goes away takes its node out of the page, with everything below that node. Removal works the same whenever the component was mounted, including in the render right before.
- Keys on components follow the rules of 07 and 08. The `key` stays in the `props` object the function receives, as it does for elements, and the catalog's components ignore it.
- In the tests a component never returns `null`, `undefined` or an array.

## Requirements

The report is grouped by requirement, and a test counts toward one only.

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

The tree is one component at the top. The container's first child is the `section` that `Frame` returned, and in it come the `h2`, then everything written inside `Frame`: the `h1` of the `Greeting`, the `b` of `FnB`, the `em`, and the text `tail`, a node of its own at depth 1. A component has no node, so none of the three shows in the dump.

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

The second dump is what the test is about. The render that mounted `FnA` put the `i` in the page, and the very next render takes it out. If your commit keeps going into the removed fiber's children after taking the node out, the `i` goes back in, and the page holds a node that no tree describes.

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

Count the units. The root fiber, the `Greeting`, its `h1` and two text nodes make five, spread as 2, 2 and 1 over three periods. The page stays empty for the first two, and the commit lands in the third. A program that skipped the unit for the component would count four, and the periods would read 2, 2, 0.

## Constraints

At most 42 lines and 12 renders per scenario. Texts are short. Every `Greeting` gets a name. The 45 tests cover each requirement, two longer sessions and five seeded random runs (a fresh seed gives five new ones). Only the three units tests have `idle` lines. A case has a 10-second limit and needs a small fraction of it.

## Hints

<details><summary>Hint 1: where to start</summary>

Two places assume that a fiber has a node. One is the unit that creates it, the other the commit that appends, updates and removes it. In the first, a component needs the function called instead. In the second, `fiber.parent.dom` is null whenever the parent is a component, and `fiber.dom` is null for the component itself.
</details>

<details><summary>Hint 2: the approach</summary>

Split `performUnitOfWork` in two, the way Pombo does with `updateFunctionComponent` and `updateHostComponent`. One branch is for function components: it calls the function and passes its single result to `reconcileChildren`. The other is the branch you already have, which makes the node and reconciles the children from the props. The reconciler itself needs no change, since it only compares types.

In the commit, write one helper that finds the DOM parent by climbing `parent` until a fiber has a `dom`, and one that finds a fiber's own node by descending `child` until a fiber has a `dom`. Use them for placing and for removing. The node a component is placed before is the first later sibling whose node, found by descending, is already in the page, and that search may have to go up through components.
</details>

<details><summary>Hint 3: the traps</summary>

- Do not give a component fiber a DOM node, and do not call `updateDom` on it. Guard on `fiber.dom`.
- A component's props include the children. The function gets the whole props object.
- In the commit, a deleted fiber is only removed. If you go on to commit its children, they still carry the tags from the render that mounted them, so a component mounted by the render right before is put back into the page. A fiber that has been rendered once more is not affected, which is why this passes the easy tests.
- A component and its siblings put their nodes into one DOM parent, the first ancestor fiber that has a node. Climb through components to find it, and descend through them to find a node.
- When the node to insert before belongs to a sibling that is a component, take the first node below that component. The component has none of its own.
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

Commit code that keeps walking a removed fiber's children, as the post's does, fails R7 like this:

```
  R7  A component mounted in one render can be removed or replaced by ... .    1 / 8   FAILED
      x 09-R7-mount-then-remove  FnA is mounted and removed by the very next render
          unexpected extra output at line 11: `node 1 c i ""`
          likely cause: R7 - A component mounted in one render can be removed or replaced by the very next render, with or without a render in between
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle)
          reproduce: py -P tools/run_js.py build/bugs/09/stale-deletion 09 build/cases/09/09-R7-mount-then-remove.in build/cases/09/09-R7-mount-then-remove.out
```

## After you pass: compare with the author's code

[Pombo's Step VII](https://pomb.us/build-your-own-react/#step-vii-function-components) checks `fiber.type instanceof Function` in `performUnitOfWork` and calls `updateFunctionComponent` or `updateHostComponent`. The first calls `fiber.type(fiber.props)` and hands the result to `reconcileChildren` as a one-element list. The second creates the node and reconciles `props.children`. In `commitWork` a loop climbs `fiber.parent` until it finds a fiber with a `dom`, and `commitDeletion` descends `fiber.child` until it finds one. The workbook splits his single file: `performUnitOfWork` and the two update functions sit in `render.js`, the commit in `commit.js`. Hint 4 gives the climb and the descent helpers of their own, `parentDom` and `ownDom`, where his `commitWork` has the climb inline and `commitDeletion` takes the parent node as an argument.

His deletion leaves a node behind when the component was mounted by the render right before. In the post's `commitWork` a deleted fiber is removed, and then its `child` and `sibling` are walked like those of any other fiber. The children of a component mounted one render ago still carry `PLACEMENT`, and their climb for a DOM parent now passes through the component to the live parent, so `appendChild` puts the node back. For a plain element the same walk only appends into a node that was detached a moment ago, which hides the problem. After one more render the tags read `UPDATE` and it is gone, and the post's own examples, `App` and `Counter`, never remove a component. Swapping `FnA` for `FnB` is hit the same way: the new node is appended at the end of the parent, where the old one stood in the middle. R7 asks for removal and replacement in the very next render, with and without a render in between.

A component that returns `null` renders nothing in his code. Removing it later throws inside `commitDeletion`. The tests never return `null` from a component, so that case, like arrays and fragments, stays outside the workbook. The page for 10 says what that exception does to his work loop. [React today](docs/react-today.md) collects the other places where React 19 and the post differ.
