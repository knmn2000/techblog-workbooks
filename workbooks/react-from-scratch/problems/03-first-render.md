# 03 · Render a tree

**Difficulty:** Easy · **Assignment** 3 of 12 · **Check:** `.\check 03`

**Tags**
- *Language:* [loops](#primer/js-loops) · [ES modules](#primer/js-modules)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [appendChild, insertBefore and removeChild](#primer/dom-tree-editing) · [trees of elements](#primer/react-tree)

## Read in the blog first

The page is complete without the post. For Pombo's version, read the start of [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function), the paragraphs about creating a node from the element type and doing the same for each child, and stop before the paragraph about the props, because `createDom` from assignment 02 already does that part. The opening of [Step III](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) explains what is wrong with a recursion like this one. You can leave it for assignment 04.

## Learning material

- [Loops: for, for...of and while](#primer/js-loops): an element has any number of children, and each has to be visited.
- [appendChild, insertBefore and removeChild](#primer/dom-tree-editing): a node joins a parent's list of children when you append it, and the order of the appends is the order on the page.
- [Trees of elements, and the "virtual DOM"](#primer/react-tree): the children of an element are elements, so a tree is handled by doing one thing to the root and then the same thing to each child.
- [ES modules: import and export](#primer/js-modules): used in a new way. This file imports from a module you wrote, with a relative path that ends in `.js`.

## Source material

- Rodrigo Pombo, [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function) and the start of [Step III](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode)
- MDN: [Node.appendChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
- React documentation: [createRoot](https://react.dev/reference/react-dom/client/createRoot), which is what `render` stands in for

## Where this fits

The two earlier files build an element and put props on one node. This one walks a whole tree of elements and uses both, with `createDom` from `src/didact/dom.js` doing the work on each node. It is a first draft: one recursive call that cannot stop halfway, which assignment 04 replaces with a loop. You write `src/didact/renderSync.js`, and nothing imports it after 04.

## The problem

Write `render(element, container)`. Given an element tree and an empty DOM node, it builds the nodes for the whole tree and puts them under that node, using the `createDom` you wrote in assignment 02. A scenario renders a tree, dumps the container, and clicks things to see whether the handlers arrived.

### The module

`src/didact/renderSync.js` exports `render(element, container)`. It returns nothing, and by the time it returns the whole tree is in the container. The elements it receives are `{ type, props }` objects in the format of assignment 01: `props.children` is always an array, and a string child is a text element.

### Input

The checker runs `node assignments/assignment_03_first_render.js <input-file> <output-file>`. The entry program gives the harness a single function: it imports `render` from your `renderSync.js` and `runScenarioFile` from `../harness/scenario.js`, then awaits `runScenarioFile(process.argv[2], process.argv[3], { render })`. The Boilerplate has it finished; if you started from scratch, put it in place before you test anything. The lines of a scenario are:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Parses one line of markup into a tree and stores it. Nothing is rendered yet. |
| `render <name>` | Builds the elements of the stored tree and calls `render(element, container)` with the page's empty container. |
| `flush` | Runs any scheduled work to the end. Your `render` schedules none, so here it does nothing, and every scenario has one after `render`. |
| `dump` | Prints the container's contents, as described under Output. |
| `click #<id>` | Dispatches a bubbling `click` on the element with that id, which has to be in the container. |
| `log` | Prints the handler calls recorded since the last `log`. |

The markup is one line of HTML-like text: `<tag name="value" other=value flag onClick=@hit>text <b>nested</b></tag>`. Values are strings, and a bare name such as `disabled` means `true`. `@hit` is a handler: it is one function that records the word `hit` in the log when it runs, and one name is one function. Text between tags keeps its inner spaces. A piece of text that is only whitespace is dropped, so it does not appear in a tree. `input`, `br`, `hr` and `img` need no closing tag. The harness builds the elements with its own copy of `createElement`, so the tree does not depend on your assignment 01.

### Output

`dump` prints `dump <n>`, where `n` counts the dumps, followed by one line for each element and each run of text in the container, parents before their children, in document order:

```
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

The container itself is not printed, so its first child has depth 0 and each level down adds 1. A label is the next free name (`a`, `b`, ..., `z`, `aa`, ...) the first time a dump shows an element, so in a single dump they run in document order. `<tag>` is lower case. `<props>` lists the values that differ from the default for `className`, `disabled` (on `button`, `input` and `textarea`), `id`, `title` and `value` (on `input` and `textarea`), sorted by name and joined with single spaces. A value with whitespace, a double quote or `%` is percent-encoded, and a boolean prints as `true`. Props that the dump does not list, `lang` for example, do not show. A text line shows the node's text with `%`, double quotes and line breaks encoded; spaces stay. Neighbouring text nodes print as one line. An empty container prints only the `dump <n>` line, and no `title` line appears in this assignment: `document.title` stays empty.

`log` prints `log <name>` for each handler call, in order.

### What `render` builds

Every element becomes one node of its tag, and every text element becomes one text node holding the text. A node's children are the nodes of the element's children, in the order the element lists them, and they are inside that node, not beside it. The top element's node becomes the container's only child. Props and handlers get onto each node the way `createDom` puts them there. A click on a node runs its handlers, then those of its parent, and so on up through the container.

Each scenario calls `render` once, onto an empty container, so there is nothing to update, replace or clear.

## Requirements

- **R1** An element without children becomes one node with the element's tag, and it is the only child of the container once `render` has returned. The container is empty before `render` runs.
- **R2** The nodes of an element's children are inside its node, at every depth.
- **R3** Siblings keep their order, and none is left out.
- **R4** A string child becomes a text node at its place among its siblings, with its spaces kept.
- **R5** The props of an element are set on its node.
- **R6** Handlers are attached: a click runs the handler of the node that was clicked and then those of its ancestors.
- **E2E** Whole pages and larger random trees.

## Examples

### Example 1: the last child has children (test `03-R3-last-is-deep`)

input:
```
tree t <div><h1></h1><h2></h2><section><h3></h3><h4></h4></section></div>
render t
flush
dump
```
output:
```
dump 1
node 0 a div ""
node 1 b h1 ""
node 1 c h2 ""
node 1 d section ""
node 2 e h3 ""
node 2 f h4 ""
```

The depth column carries the structure. `h1`, `h2` and `section` are all at depth 1, so they are siblings under the `div`, and `h3` and `h4` at depth 2 sit inside the `section`. An implementation that renders children into the container instead of into their parent prints every node at depth 0, with the `div` last.

### Example 2: text on both sides of an element (test `03-R4-text-element-text`)

input:
```
tree t <p>hello <b>big</b> world</p>
render t
flush
dump
```
output:
```
dump 1
node 0 a p ""
text 1 "hello "
node 1 b b ""
text 2 "big"
text 1 " world"
```

The `p` has three children: a text node, the `b`, and another text node. The two texts print as separate lines because the `b` sits between them, and each keeps the space next to the element, which the quotes make visible. The word `big` is one level deeper, inside the `b`.

### Example 3: a click rises through the ancestors (test `03-R6-bubbling`)

input:
```
tree t <div id="outer" onClick=@outer><button id="inner" onClick=@inner></button></div>
render t
flush
click #inner
log
click #outer
log
```
output:
```
log inner
log outer
log outer
```

The first click lands on the button, so `inner` runs first, and then the click goes on to the `div`, where `outer` runs. That is two lines for one click. The second click is on the `div` itself, and the button is not an ancestor, so only `outer` runs. The scenario has no `dump`: it only checks what clicks do.

## Constraints

Scenarios have at most 10 lines. Every tag is lower case, so each element is a plain host element with a string for its type, and no component appears before assignment 09. A tree has at most about 200 nodes, elements and texts together, and none is deeper than 10 levels. Ids that a scenario clicks are unique inside their tree. The 46 tests are the cases of each requirement, two scripted pages and seven seeded random trees (`-Fresh` gives seven new ones). A correct solution takes milliseconds, and each test is allowed 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Handle the smallest tree first: a single element with no children. Then ask what changes when it has one child. The child is an element too, so whatever you did for the first one is what you do for the second.
</details>

<details><summary>Hint 2: the approach</summary>

`render` takes a node to put things under, and for the top element that node is the container. Make the node for the element, then call `render` for each child, with the new node as its container, and then attach the new node to the container you were given. The recursion handles any depth. Text elements need no special case here, because `createDom` already knows what to make of them.
</details>

<details><summary>Hint 3: the traps</summary>

- A child goes into its parent's node. Pass the container of the call you are in, and the children land beside the parent instead.
- Keep the children's order. Appending in list order is enough, and putting each node at the front of the container turns the order around.
- Visit every child. Stopping after the first, or skipping the text elements, drops nodes without any error.
- Use `createDom` for props. Assigning props yourself makes `id` and `className` work, and a handler such as `onClick` then ends up as a property that nothing listens to.
- `element.props.children` is an array for every element, text elements included.
- Do not clear the container or reuse nodes: each scenario renders once, into an empty container.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
render(element, container):
    dom = createDom(element)
    for each child in element.props.children:
        render(child, dom)
    container.appendChild(dom)
```
</details>

## Checking your solution

```
.\check 03                          every test, grouped by requirement
.\check 03 -Case 03-R3-three-tags   one test with its full input, the expected dump and yours
.\check 03 -Fresh                   seven new random trees, to try your code on scenarios you have not seen
.\check 03 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A `render` that puts each node in front of the container's first child turns every list around, and fails like this:

```
  R3  Siblings keep their order and none is dropped ........................    1 / 7   FAILED
      x 03-R3-three-tags  h1, h2, h3 in a div
          node[0]: expected (depth=1, label=b, tag=h1, props=""), got (depth=1, label=b, tag=h3, props="") - differs in tag  (in `dump 1`)
          likely cause: R3 - Siblings keep their order and none is dropped
          expected values from: React 19.3.1 + react-dom 19.3.1 on jsdom 30.1.3 (tools/oracle)
          reproduce: py -P tools/run_js.py build/bugs/03/siblings-reversed 03 build/cases/03/03-R3-three-tags.in build/cases/03/03-R3-three-tags.out
```

The requirements build on each other, so when several fail, start with the first one in the list.

## After you pass: compare with the author's code

[Pombo's `render`](https://pomb.us/build-your-own-react/#step-ii-the-render-function) makes a text node for a `TEXT_ELEMENT` and an ordinary node otherwise, assigns the props, calls itself for every child with the new node as the container, and appends the node to its container last. Children are therefore attached to a node before the node is attached to its parent. Attaching the parent first and filling it afterwards gives the same page, and passes too.

The post assigns the props with a loop of its own, every prop that is not `children` as a property (`key` included), and that loop is the part that differs here. A handler such as `onClick` ends up as a property of that name, which no browser looks at, so in the post's Step II no handler works until the listeners arrive in Step VI. This assignment sends the props through your `updateDom`, so a click works from the first render on, and R6 tests that. The post's Step III then says that a recursion like this one keeps the main thread busy until the tree is done, which is why 04 takes it apart.

Neither the post nor this page clears what is already in the container, while React empties it on a first render, and the tests render into an empty container. A call to React's `root.render` also finishes later than your `render`. The row on mounting in [React today](docs/react-today.md) says that your `render` plays the part of `root.render`.
