# 03 · Render a tree

**Difficulty:** Easy · **Assignment** 3 of 12 · **Check:** `.\check 03`

**Tags**
- *Language:* [loops](#primer/js-loops) · [ES modules](#primer/js-modules)
- *Library:* [the harness and scenario files](#primer/workbook-harness)
- *Concepts:* [appendChild, insertBefore and removeChild](#primer/dom-tree-editing) · [trees of elements](#primer/react-tree)

## Read in the blog first

Nothing here depends on the post. For Pombo's version, take the start of [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function), the paragraphs on creating a node from the element type and doing the same for each child. Stop before the one about props: `createDom` from assignment 02 already covers that. The opening of [Step III](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode) explains what is wrong with a recursion like this one, and it can wait for 04.

## Learning material

- [Loops: for, for...of and while](#primer/js-loops): an element can have any number of children, and every one needs a visit.
- [appendChild, insertBefore and removeChild](#primer/dom-tree-editing): appending puts a node into its parent's list of children, and the order of the appends becomes the order on the page.
- [Trees of elements, and the "virtual DOM"](#primer/react-tree): the children of an element are elements too, so a tree is elements inside elements, and handling it means doing one thing to the root and then the same thing to each child.
- [ES modules: import and export](#primer/js-modules): the new part is importing a file of your own, by a relative path that ends in `.js`.

## Source material

- Rodrigo Pombo, [Step II: The render Function](https://pomb.us/build-your-own-react/#step-ii-the-render-function) and the start of [Step III](https://pomb.us/build-your-own-react/#step-iii-concurrent-mode)
- MDN: [Node.appendChild](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
- React documentation: [createRoot](https://react.dev/reference/react-dom/client/createRoot), which is what `render` stands in for

## Where this fits

Elements exist (01) and a node can be given its props (02). This assignment walks a whole tree of them, with `createDom` from `src/didact/dom.js` doing the work on each node. It is a first draft: one recursive call that cannot stop halfway, and 04 swaps it for a loop. You write `src/didact/renderSync.js`. After 04 nothing imports it.

## The problem

Write `render(element, container)`. It receives an element tree and an empty DOM node, builds the nodes for the whole tree with your `createDom` from 02, and puts them under that node. A scenario renders a tree, dumps the container, and clicks things to find out whether the handlers made it.

### The module

`src/didact/renderSync.js` exports `render(element, container)`. It returns nothing, and when it returns the whole tree is in the container. Elements arrive as `{ type, props }` objects in the format of assignment 01: `props.children` is always an array, and a string child is already a text element.

### Input

For each test the checker launches `node assignments/assignment_03_first_render.js <input-file> <output-file>`. The entry program hands the harness one function. It imports `render` from your `renderSync.js` and `runScenarioFile` from `../harness/scenario.js`, then awaits `runScenarioFile(process.argv[2], process.argv[3], { render })`. The Boilerplate includes it finished, and a from-scratch start needs it before the first test. A scenario is made of these lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Parses one line of markup into a tree and stores it. Nothing is rendered yet. |
| `render <name>` | Builds the elements of the stored tree and calls `render(element, container)` with the page's empty container. |
| `flush` | Runs any scheduled work to the end. Your `render` schedules none, so here it does nothing, and every scenario has one after `render`. |
| `dump` | Prints the container's contents, as described under Output. |
| `click #<id>` | Dispatches a bubbling `click` on the element with that id, which has to be in the container. |
| `log` | Prints the handler calls recorded since the last `log`. |

The markup is one line of HTML-like text: `<tag name="value" other=value flag onClick=@hit>text <b>nested</b></tag>`. Values are strings; a bare name such as `disabled` means `true`. `@hit` is a handler, one function that records the word `hit` in the log whenever it runs, and one name always means one function. Text between tags keeps its inner spaces, but whitespace-only text is dropped before it reaches the tree. `input`, `br`, `hr` and `img` take no closing tag. The harness builds the elements with its own copy of `createElement`, so your assignment 01 is not involved.

### Output

`dump` prints `dump <n>`, where `n` counts the dumps, followed by one line for each element and each run of text in the container, parents before their children, in document order:

```
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

The container itself is left out, so its first child sits at depth 0 and every level below adds 1. An element gets the next free label (`a`, `b`, ..., `z`, `aa`, ...) the first time a dump shows it, which makes labels run in document order within a single dump. `<tag>` is lower case. `<props>` lists the values that differ from the default for `className`, `disabled` (on `button`, `input` and `textarea`), `id`, `title` and `value` (on `input` and `textarea`), sorted by name and joined with single spaces. A value with whitespace, a double quote or `%` is percent-encoded, and a boolean prints as `true`. Props outside that list, `lang` for example, do not show. A text line shows the node's text with `%`, double quotes and line breaks encoded, and spaces left alone. Neighbouring text nodes print as one line. An empty container prints only the `dump <n>` line. No `title` line appears in these scenarios, because `document.title` stays empty.

Each handler call is printed as `log <name>`, in order.

### What `render` builds

Every element becomes one node of its tag, and every text element one text node holding the text. A node's children are the nodes of the element's children, in the order the element lists them, and they sit inside that node, not beside it. The top element's node becomes the container's only child. Props and handlers reach each node the way `createDom` puts them there. A click on a node runs its handlers, then its parent's, and so on up through the container.

Each scenario calls `render` once, onto an empty container: nothing to update, replace or clear.

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

```
input:
tree t <div><h1></h1><h2></h2><section><h3></h3><h4></h4></section></div>
render t
flush
dump

output:
dump 1
node 0 a div ""
node 1 b h1 ""
node 1 c h2 ""
node 1 d section ""
node 2 e h3 ""
node 2 f h4 ""
```

The depth column carries the structure. `h1`, `h2` and `section` are all at depth 1, siblings under the `div`; `h3` and `h4` at depth 2 sit inside the `section`. An implementation that renders children into the container instead of into their parent prints everything at depth 0, with the `div` last.

### Example 2: text on both sides of an element (test `03-R4-text-element-text`)

```
input:
tree t <p>hello <b>big</b> world</p>
render t
flush
dump

output:
dump 1
node 0 a p ""
text 1 "hello "
node 1 b b ""
text 2 "big"
text 1 " world"
```

The `p` has three children: text, the `b`, more text. The two texts print on separate lines because the `b` is between them, and each keeps the space beside the element, which the quotes make visible. `big` is a level deeper, inside the `b`.

### Example 3: a click rises through the ancestors (test `03-R6-bubbling`)

```
input:
tree t <div id="outer" onClick=@outer><button id="inner" onClick=@inner></button></div>
render t
flush
click #inner
log
click #outer
log

output:
log inner
log outer
log outer
```

The first click lands on the button, so `inner` runs, and then the click goes on to the `div`, where `outer` runs: two lines for one click. The second click is on the `div` itself. The button is no ancestor of the `div`, so only `outer` runs. There is no `dump` in this scenario; it only checks what clicks do.

## Constraints

Scenarios run to 10 lines at most. Every tag is lower case, which makes each element a plain host element with a string type, and no component appears before assignment 09. A tree has at most about 200 nodes (elements and texts together) and none is deeper than 10 levels. The ids a scenario clicks are unique within their tree. The 46 tests are each requirement's cases, two scripted pages and seven seeded random trees (`-Fresh` gives seven new ones). A correct solution finishes in milliseconds, and a test gets 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Do the smallest tree first, a single element with no children. Then give it one child and see what changes. The child is an element too, so whatever worked on the first one works on the second.
</details>

<details><summary>Hint 2: the approach</summary>

`render` takes a node to put things under, and for the top element that node is the container. Make the node for the element, call `render` on each child with the new node as the container, then attach the new node to the container you were given. Recursion copes with any depth. Text elements need no special case, since `createDom` already knows what to do with them.
</details>

<details><summary>Hint 3: the traps</summary>

- Children go into their parent's node. Hand them the container of your own call and they land beside the parent.
- Appending in list order keeps the children's order. Put each node at the front of the container and the list comes out reversed.
- Visit every child. Stop after the first, or skip the text elements, and nodes vanish without an error.
- Let `createDom` set the props. Do it yourself and `id` and `className` work, but a handler such as `onClick` ends up as a property that nothing listens to.
- Every element has an array in `element.props.children`, text elements included.
- No need to clear the container or reuse nodes. Each scenario renders once, into an empty one.
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

Requirements build on one another. When several fail, start with the first.

## After you pass: compare with the author's code

[Pombo's `render`](https://pomb.us/build-your-own-react/#step-ii-the-render-function) makes a text node for a `TEXT_ELEMENT` and an ordinary node for anything else, assigns the props, calls itself on every child with the new node as the container, and appends the node to its own container last. Children are therefore attached to a node before the node is attached to its parent. Do it the other way round, parent first and filled afterwards, and you get the same page. That passes too.

The post assigns props with a loop of its own: every prop except `children` becomes a property (`key` included), and this loop is where the two versions differ. A handler such as `onClick` ends up as a property of that name, which no browser looks at, so no handler works in the post's Step II until the listeners arrive in Step VI. Here the props go through your `updateDom`, clicks work from the first render, and R6 tests for it. The post's Step III then says that a recursion like this one keeps the main thread busy until the tree is done, which is why 04 takes it apart.

Neither the post nor this page clears what is already in the container. React empties it on a first render, but the tests render into an empty container and the difference stays hidden. React's `root.render` also finishes later than your `render` does. The row on mounting in [React today](docs/react-today.md) says that your `render` plays the part of `root.render`.
