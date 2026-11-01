# React and the ideas in the posts

The assignments rebuild React's core in the order the two posts tell it. Each entry here names one idea, so a problem page can link to it instead of explaining it again, and says where React 19 has moved on from the posts.

## Elements, and what JSX turns into
<!--
id: react-elements
also: JSX; createElement; React element; vnode; virtual node; TEXT_ELEMENT; props.children
code: \bcreateElement\b
-->
JSX is the HTML-looking syntax in React code, like `<h1 id="top">Hi</h1>`. A browser can't run it, so a build step rewrites each tag into a call, `createElement(type, props, ...children)`, before the program starts. Here there is no build step and no JSX. You write the calls by hand, and the `createElement` of assignment 01 (`createElement.js`) is the function that rewrite would have targeted.

What comes back is an element: a plain object describing one piece of UI, and nothing more. It holds a `type` (a tag name, or a function when the element is a [component](#primer/react-function-components)) and `props`, with the children inside `props.children` as an array. Text has no tag, so a string or number child gets wrapped in an element of type `"TEXT_ELEMENT"`, which gives every node in the tree the same shape.

```js
createElement("h1", { id: "top" }, "Hi")
// { type: "h1",
//   props: { id: "top",
//            children: [ { type: "TEXT_ELEMENT",
//                          props: { nodeValue: "Hi", children: [] } } ] } }
```

Elements are cheap to build, and that's the point. An app makes a whole new [tree of them](#primer/react-tree) on every update and leaves the library to work out what changed. Real React shapes them a little differently: `key` sits beside `props` instead of inside it, text children stay plain strings, and `null` and booleans are legal children. Didact keeps `key` in `props`, wraps its text, and leaves `null` and booleans out. [React 19 against the posts](#primer/react-today) collects the other differences.

Learn more:
- [createElement](https://react.dev/reference/react/createElement), the reference page for the real element object
- [Writing markup with JSX](https://react.dev/learn/writing-markup-with-jsx), react.dev
- [Build your own React](https://pomb.us/build-your-own-react/), Step I, Rodrigo Pombo

## Trees of elements, and the "virtual DOM"
<!--
id: react-tree
also: virtual DOM; VDOM; element tree; render tree; UI tree
-->
Elements nest. A `ul` element holds `li` elements in its `props.children`, each `li` holds a text element, and what you get is a tree of plain objects. The page is a tree too: the DOM, made of element nodes and text nodes ([the DOM tree](#primer/dom-tree)). The simplest render possible walks the first tree and builds one node of the second for each element, attached under its parent.

```
element tree                    DOM tree
{ type: "ul" }            ->    <ul>
  { type: "li" }          ->      <li>
    TEXT_ELEMENT "a"      ->        "a"   (a text node)
  { type: "li" }          ->      <li>
    TEXT_ELEMENT "b"      ->        "b"
```

"Virtual DOM" is the nickname for the first tree. React's old documentation describes it as an ideal picture of the UI kept in memory, which the library keeps in step with the real DOM. The name sounds grander than the thing, which is a pile of objects. What you get for it is cheap comparison: DOM nodes are heavy and writing to them can trigger layout, while a fresh tree of objects costs a few allocations. The library keeps the last tree, builds the next, compares the two and touches the DOM only where they differ. That comparison is [reconciliation](#primer/react-reconciliation).

One trap in the vocabulary: react.dev's "render tree" holds only components, without the HTML tags they produce. The trees here hold the tags too.

Assignment 03 writes the walk (`renderSync.js`), and the checker's `dump` prints the DOM it builds, one node per line. A third tree arrives in 04: the [fibers](#primer/react-fibers).

Learn more:
- [Understanding your UI as a tree](https://react.dev/learn/understanding-your-ui-as-a-tree), react.dev
- [Virtual DOM and internals](https://legacy.reactjs.org/docs/faq-internals.html), from React's earlier documentation
- [Build your own React](https://pomb.us/build-your-own-react/), Step II, Rodrigo Pombo

## Fibers
<!--
id: react-fibers
also: fiber; fiber tree; unit of work; alternate; wipRoot; currentRoot; React Fiber
-->
A fiber is the library's own object for one node of the tree, and it doubles as one unit of work. An element says what you asked for; a fiber also holds what the library knows about it: the element's `type` and `props`, its `dom` node once one exists, and three links, `parent`, `child` (the first child) and `sibling` (the next one). The children of a parent form a linked list, which lets a whole tree be walked with a loop instead of recursion.

That matters because a recursive walk keeps your place on the call stack, and a call stack can't be paused. With the links, the place to resume is one variable: the next fiber. The order is depth first. Take the child if there is one, otherwise the sibling, otherwise the sibling of the nearest ancestor that has one. For `section > (ul > (li, li), footer)` the walk visits the root, `section`, `ul`, the two `li` fibers, then `footer`. The root fiber stands for the container the app renders into.

React's real fibers carry far more (priorities, hook state, a `return` link where the posts write `parent`). The workbook adds fields as assignments need them: `alternate` and `effectTag` in 06, `hooks` in 10. Name yours as you like. The tests only look at the page that results.

In 04, `reconcile.js` creates a fiber's child fibers and `render.js` walks them, one per turn of the [work loop](#primer/react-work-loop).

Learn more:
- [Build your own React](https://pomb.us/build-your-own-react/), Step IV, Rodrigo Pombo
- [React Fiber Architecture](https://github.com/acdlite/react-fiber-architecture), Andrew Clark's write-up of what a fiber is and why React adopted them

## Units of work and the work loop
<!--
id: react-work-loop
also: concurrent mode; time slicing; workLoop; performUnitOfWork; shouldYield; yielding; scheduler; cooperative scheduling
-->
A page's JavaScript shares one thread with clicks, scrolling and painting. Render a big tree in one go and all of that waits. The remedy: cut the job into small units, do a few, and hand control back to the browser until it has a gap to spare.

The loop that does this receives a deadline from the browser ([`requestIdleCallback`](#primer/dom-idle-callback)). It performs one unit, asks `deadline.timeRemaining()` how much of the idle period is left, and carries on while at least a millisecond remains. When time runs out it stops and asks for the next callback, and the unfinished work waits in a variable. The same pattern, with addition standing in for rendering:

```js
const jobs = Array.from({ length: 5000 }, (_, i) => i);
let total = 0;

function sumSome(deadline) {
  while (jobs.length > 0 && deadline.timeRemaining() > 1) total += jobs.pop();
  if (jobs.length > 0) requestIdleCallback(sumSome);
}
requestIdleCallback(sumSome);
```

In Didact a unit is one [fiber](#primer/react-fibers). The tests play the browser: the harness calls your loop with a fake deadline whose `timeRemaining()` runs out after a number of calls the test picks, and counts them.

React itself dropped `requestIdleCallback` for a scheduler of its own, and only concurrent features such as transitions can pause a render; an ordinary update renders in one pass ([React 19 against the posts](#primer/react-today)). Didact keeps the interruptible loop because yielding is the idea worth building. The code is in `render.js` from assignment 04 (`workLoop`, `performUnitOfWork`).

Learn more:
- [Build your own React](https://pomb.us/build-your-own-react/), Step III, Rodrigo Pombo
- [requestIdleCallback](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback), MDN
- [React v18](https://react.dev/blog/2022/03/29/react-v18), the section on concurrent rendering

## The render phase and the commit phase
<!--
id: react-render-commit
also: render phase; commit phase; commitRoot; wipRoot; work in progress; two-phase rendering
-->
Cutting the job into [units](#primer/react-work-loop) leaves a problem: when the browser takes over, the tree is half built. If each unit attached its node to the page, a user would see half an interface, which is why the work has two phases.

The render phase works out what the screen should be. It builds fibers and creates DOM nodes with their props set, but leaves the page alone, which means it can pause, restart or be thrown away. Pombo calls the tree under construction `wipRoot`, for work in progress. The commit phase then applies the result to the page in one synchronous pass that nothing interrupts. Anything that needs the finished page waits for it, [effects](#primer/react-effects) among them.

```
unit 1    create <div>          page still shows the old UI
unit 2    create <h1>           page still shows the old UI
unit 3    create <p>            page still shows the old UI
commit    insert div, h1, p     page shows the new UI, all at once
```

"Render" in this sense means calling components and building the result. Putting pixels on the screen is the browser's paint, which the React docs place after the commit; they count three steps in all: trigger, render, commit.

Assignment 05 brings in `commit.js`, and `render.js` stops attaching nodes as it goes. The tests dump the container between idle periods, which catches anything that appears early.

Learn more:
- [Render and commit](https://react.dev/learn/render-and-commit), react.dev
- [Build your own React](https://pomb.us/build-your-own-react/), Step V, Rodrigo Pombo

## Reconciliation by type and position
<!--
id: react-reconciliation
also: reconcile; reconcileChildren; diffing; diff algorithm; alternate; effectTag; PLACEMENT; UPDATE; DELETION
-->
An update hands the library a new element tree while the page still shows the old one. Reconciliation decides, place by place, which existing DOM node carries on. React's rule is a heuristic, cheap enough to run on every update: compare an element's `type` with the old fiber at the same position among its siblings.

- Same type: keep the DOM node, update only the props that changed, then move on to the children.
- Different type: assume a different subtree. Build a new node, drop the old one, and put the new one where the old one stood.
- Leftovers on either side: an old child with no element left loses its node, and an element with no old child gets a new one.

An exact comparison of two trees is too slow (cubic), which is why React settles for betting that different types mean different trees. For the comparison, each new fiber keeps a link to its twin from the last render (`alternate`) and carries a tag telling the [commit](#primer/react-render-commit) what to do: `UPDATE`, `PLACEMENT` or `DELETION`.

```
before   <div><p>a</p><b>b</b><i>c</i></div>
after    <div><p>a</p><u>b</u><i>c</i></div>
```

The `p` and `i` keep their nodes. The `b` becomes a `u`, a new node that has to land between them. Position is the only identity so far, which is why inserting at the front of a list goes badly without [keys](#primer/react-keys), and why a component keeps its [state](#primer/react-state) while its position and type stay put.

Most of 06 happens in `reconcile.js`, with `render.js` and `state.js` holding on to the last committed tree and `commit.js` acting on the tags. 07 and 08 rework that same function.

Learn more:
- [Reconciliation](https://legacy.reactjs.org/docs/reconciliation.html), from React's earlier documentation, the clearest account of the diffing rules
- [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state), react.dev
- [Build your own React](https://pomb.us/build-your-own-react/), Step VI, Rodrigo Pombo

## Keys
<!--
id: react-keys
also: key prop; key; keyed children; list keys; stable identity; keyed reconciliation
-->
Without keys, position is identity. Put a new item at the front of a list and every item now sits where another used to, so each node is rewritten with its new neighbour's data and a fresh node is added at the end. A key fixes that. It's a label an element carries (`key: "milk"`) that lets the library recognise it from one render to the next, wherever it now stands. The same key means the same child, and its node stays, along with whatever the browser keeps on it, such as typed text and focus.

```
before   li key="a"   li key="b"
after    li key="z"   li key="a"   li key="b"
```

Here `a` and `b` keep their nodes, and `z` is the only new one, placed first.

Keys are unique among siblings and stay the same for the same item, so take an id from the data and skip array indexes and random numbers. A key that changes means a new element: the old node goes and a new one is built. Children without a key still match by position. In React `key` is not a prop, since `props` lacks it and a component never receives it; Didact keeps it as an ordinary prop, as assignment 01 specifies. Keys can be falsy, `""` for one, so ask whether an element has a key instead of testing the key for truthiness ([`===`, `Object.is`, truthy and falsy](#primer/js-equality)).

Wim Jongeneel's post matches children by key, but only while the keys both lists share stay in the same order. Moving them is [the next entry](#primer/react-moving-nodes). Assignment 07 covers the first part, in `reconcile.js`, and the todo list in 12 keys its items by id.

Learn more:
- [Rendering lists](https://react.dev/learn/rendering-lists), react.dev, on where keys come from
- [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state), react.dev, which shows a key resetting a component
- [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d), Wim Jongeneel, the section on diffing children

## Reordering without recreating
<!--
id: react-moving-nodes
also: reorder; move DOM nodes; swap; shuffle; insertBefore; list reordering; placement
-->
Same keys, new order. Rebuilding the nodes would produce the right page and lose typed text, focus and anything else the browser held on them, so a reorder keeps each node and moves it. The DOM supports this directly: `insertBefore` and `appendChild` with a node that already has a parent move it, with no copy ([tree editing](#primer/dom-tree-editing)).

Two jobs follow. Matching finds each new child's old twin by key, wherever it stood. Placing decides which nodes have to move and puts each one in front of the right neighbour. Moving every node is correct and wasteful. Turning `a b c d` into `b c d a` takes one move, of `a`, and a node already in order relative to the others can stay where it is.

A moved node is still the same node, and its props are still compared and updated. The harness's `ops` line counts moves separately from creations and removals, so a plain reordering has to show no creates and no removes. If an input in the moved item holds typed text, the text travels with it; compare a [controlled input](#primer/react-controlled-inputs), where the state would carry it instead.

Real React moves a node among its siblings only. Take a subtree to a different parent and it is destroyed and built again. Jongeneel's post stops earlier, by his own account: children whose keys come out of order are removed and inserted again. Assignment 08 follows React, in `reconcile.js` and `commit.js`.

Learn more:
- [Reconciliation](https://legacy.reactjs.org/docs/reconciliation.html), from React's earlier documentation, on keys and on what React can and can't express as a move
- [Node.insertBefore()](https://developer.mozilla.org/en-US/docs/Web/API/Node/insertBefore), MDN
- [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d), Wim Jongeneel, for what his version leaves out

## Function components
<!--
id: react-function-components
also: component; components; props; props.children; composition; function type; component fiber
-->
A component is a function that takes props and returns an element. To use one, pass the function itself as the `type`: `createElement(Badge, { label: "new" }, child)`. JSX spells that `<Badge label="new">`, and the capital letter is what tells it apart from a tag name.

Creating that element doesn't call the function. The library does, in the render phase, when it reaches the component's fiber: it calls the function with the element's `props`, `children` among them, and the element that comes back becomes the fiber's one child. A component fiber has no DOM node of its own. It exists in the tree and nowhere on the page.

```js
function Badge({ label, children }) {
  return createElement("span", { className: "badge" }, label, ...children);
}
// createElement(Badge, { label: "new" }, createElement("b", null, "!"))
//   fiber(Badge) -> fiber(span) -> fibers for "new" and b
```

No node means two consequences. The commit can no longer assume that a fiber's parent owns a DOM node, and removing a component has to remove whatever its output made. Swapping one component function for another at the same position follows the type rule of [reconciliation](#primer/react-reconciliation): different functions are different types. The workbook has no way to skip a component whose props are unchanged, so each render pass runs all of them again. A component is also where [state](#primer/react-state) lives.

In 09 this lands in `render.js` and `commit.js`. The tests get their components from the harness catalog (`Greeting`, `Frame`, `Counter` and others), and in 12 you write your own.

Learn more:
- [Your first component](https://react.dev/learn/your-first-component), react.dev
- [Passing props to a component](https://react.dev/learn/passing-props-to-a-component), including the `children` prop
- [Build your own React](https://pomb.us/build-your-own-react/), Step VII, Rodrigo Pombo

## `useState` and the rules of hooks
<!--
id: react-state
also: useState; hooks; hook; setState; setter; state; state variable; rules of hooks; hook index
code: \buseState\b
-->
A function component runs from the top on every render, so its local variables start over each time. `useState(initial)` gives it a memory. It returns `[value, setValue]`, and the library keeps the value somewhere that survives, on the component's [fiber](#primer/react-fibers). The next render calls `useState` again and gets the stored value back; `initial` counts only the first time.

`setValue` changes nothing on the spot. It records an update and asks for a new render, and the variable in the render that is running keeps its old value ([how updates pile up](#primer/react-batching)).

A call finds its slot by order: the first `useState` of a component gets the first slot, the second gets the second. That's where the rules of hooks come from. Call hooks at the top level of the component, outside conditions, loops and anything after an early return, which keeps every render making the same calls in the same order.

```js
function Clicks() {
  const [count, setCount] = useState(0);      // slot 0
  const [last, setLast] = useState("never");  // slot 1
  const onClick = () => {
    setCount((n) => n + 1);
    setLast(() => "now");
  };
  return createElement("button", { onClick }, count, " / ", last);
}
```

In React the setter is the same function on every render, and an update sent through an old one still counts. Yours has to keep working after the component renders again. The workbook's setter takes an updater function, as React's does (React accepts a plain value too). State belongs to a position and a type: a parent re-rendering keeps it, and a different component in the same spot starts empty.

The file for 10 is `hooks.js`, with `state.js` and `render.js` telling it which component is running. The todo app in 12 keeps a [controlled input](#primer/react-controlled-inputs) in state.

Learn more:
- [useState](https://react.dev/reference/react/useState), react.dev
- [Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks), react.dev
- [Build your own React](https://pomb.us/build-your-own-react/), Step VIII, Rodrigo Pombo

## Several updates, one render
<!--
id: react-batching
also: batching; automatic batching; updater function; update queue; stale state; functional update
-->
A handler may call a [setter](#primer/react-state) more than once. React doesn't re-render after each call. It queues the updates, lets the handler finish, then renders once with all of them applied, oldest first. That is cheaper. The page never shows a state that sits between two of the calls.

The catch is that a render's `count` is a snapshot. Starting from 2, two calls of `setCount(count + 1)` both ask for 3, and the result is 3. Two updaters hand the first one's result to the second:

```js
setCount((n) => n + 1);   // 2 -> 3
setCount((n) => n * 5);   // 3 -> 15, and one render covers both
```

The workbook's setter takes functions for that reason. Each hook keeps a list of updaters that are waiting, and the next render of its component folds them into the state in order.

How much gets batched has grown. Before React 18, only updates inside React's own event handlers were batched; since 18 they are batched everywhere, timeouts and promises included. Pombo's design gets one render per burst because a setter only schedules the next render, and calls made before it runs share it. Jongeneel's `setState` re-renders on the spot, so three calls make three renders. The workbook follows React.

Assignment 10 puts it to the test: one of the catalog's counters calls its setter twice per click, and the page has to show both updates after a single flush.

Learn more:
- [Queueing a series of state updates](https://react.dev/learn/queueing-a-series-of-state-updates), react.dev
- [React v18](https://react.dev/blog/2022/03/29/react-v18), the section on automatic batching
- [useState](https://react.dev/reference/react/useState), the part on updating state from the previous state

## `useEffect`: after the DOM is updated
<!--
id: react-effects
also: useEffect; effect; side effect; cleanup; cleanup function; dependency array; deps; componentDidMount; componentDidUpdate; componentWillUnmount; lifecycle hooks
code: \buseEffect\b
-->
Rendering is a calculation: props and state in, elements out. Anything that reaches outside, such as starting a timer, subscribing to a feed or setting `document.title`, is a side effect, and `useEffect(effect, deps)` is where it goes. React calls `effect` after the [commit](#primer/react-render-commit), when the DOM already shows the new output. If `effect` returns a function, that is its cleanup. React calls it before the effect runs again and once more when the component goes away.

`deps` says when the effect is due. With an array, React compares each entry to the previous render's with `Object.is` and runs the effect again only when one differs. An empty array means once, after mounting. No array means after every render. A cleanup belongs to the render that produced it.

```js
function Ticker({ ms }) {
  useEffect(() => {
    const id = setInterval(() => console.log("tick"), ms);
    return () => clearInterval(id);
  }, [ms]);
  return createElement("p", null, `every ${ms} ms`);
}
```

When `ms` changes, the old interval is cleared before the new one starts. The order across components matters and the tests pin it: in one commit every cleanup that is due runs before any new effect, and on mounting a child's effect runs before its parent's.

React usually runs effects after the browser has painted, and Strict Mode in development adds an extra setup and cleanup. Didact runs them right after the commit and has no Strict Mode. Jongeneel's class components get the same moments from `componentDidMount`, `componentDidUpdate` and `componentWillUnmount`.

In 11, `hooks.js` remembers the effect and its deps and `commit.js` runs them once the DOM is updated. The catalog's logger components record what their effects do, and the todo app in 12 sets the page title from one.

Learn more:
- [useEffect](https://react.dev/reference/react/useEffect), react.dev
- [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects), react.dev
- [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d), Wim Jongeneel, the section on lifecycle hooks

## Controlled inputs
<!--
id: react-controlled-inputs
also: controlled component; uncontrolled; input value; onInput; onChange; form state; two-way binding
-->
A text input holds its own text in the browser. A controlled input hands that job to the app. The text lives in state, the element is rendered with its `value` taken from that state, and a handler stores the new text on each edit. The loop goes: keystroke, `input` event, the handler reading `event.target.value`, the setter, a re-render, `value` written back to the node. The state is the truth and the box shows it, so clearing a form is `setText(() => "")` with no DOM call at all.

```js
function Shout() {
  const [text, setText] = useState("");
  const onInput = (event) => {
    const typed = event.target.value;   // read it now: the updater runs in a later render
    setText(() => typed.toUpperCase());
  };
  return createElement("input", { value: text, onInput });
}
```

Whatever the user types, this box shows capitals, because the state decides.

React's `onChange` fires on every keystroke, like the browser's `input` event. The DOM's own `change` event waits until the field loses focus, and the harness dispatches `input`, which is why the todo app uses `onInput`. React also restores a controlled `value` that no handler accepted. Didact leaves whatever was typed, so keeping the state in step is your job. Inside a form, a submit reloads the page unless the handler calls `event.preventDefault()` ([inputs and the `submit` event](#primer/dom-form-inputs)).

The form in `TodoApp.js` (assignment 12) is where it matters. The checker's `type` command sets a field's `value` and dispatches `input`, the way a user's typing would, and `submit` fires the form's submit event.

Learn more:
- [`<input>`](https://react.dev/reference/react-dom/components/input), react.dev, the section on controlling an input with state
- [The input event](https://developer.mozilla.org/en-US/docs/Web/API/Element/input_event), MDN

## React 19 against the posts
<!--
id: react-today
also: React 19; React 19.3; ReactDOM.render; createRoot; requestIdleCallback; scheduler; differences from the posts; what changed since 2019
-->
Pombo follows React 16.8 (2019) and Jongeneel wrote in 2021. The workbook checks your code against React 19.3.1, and where they disagree, React 19 wins. The architecture survived: a tree of fibers, a render pass followed by a commit, children matched by type and key, hook state on the fiber. You build that part. What moved:

- React 19 dropped `ReactDOM.render`. `createRoot(container).render(element)` replaces it, and your `render(element, container)` stands in for `root.render`.
- React no longer schedules with `requestIdleCallback`, and only concurrent features such as transitions can pause a render.
- Updates have been batched everywhere since 18.
- Effects usually run after the paint, with every cleanup of a commit ahead of any new effect.
- Setters are one stable function per hook, and old ones keep working.
- On the DOM side, React sets attributes for most props, handles `style` objects and `value` specially, and listens on the root. Didact assigns properties and listens on each node, and the tests use only props where both read the same.
- Pombo has no keys, Jongeneel can't reorder, and React moves nodes.

```js
ReactDOM.render(element, container);        // the 2019 post, removed in React 19
createRoot(container).render(element);      // React 19, from "react-dom/client"
```

React 19 also removed `ReactDOM.hydrate`, `unmountComponentAtNode`, `findDOMNode`, string refs, legacy context, and `propTypes` and `defaultProps` on function components. 19.3's own additions, such as View Transitions, are outside this workbook. The full table is in `docs/react-today.md`, which assignment pages link wherever a test follows React against a post. Details sit in [work loop](#primer/react-work-loop), [batching](#primer/react-batching), [effects](#primer/react-effects) and [elements](#primer/react-elements).

Learn more:
- [React 19 upgrade guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide), the removed APIs and their replacements
- [createRoot](https://react.dev/reference/react-dom/client/createRoot), react.dev
- [React v18](https://react.dev/blog/2022/03/29/react-v18), where batching and `createRoot` arrived
