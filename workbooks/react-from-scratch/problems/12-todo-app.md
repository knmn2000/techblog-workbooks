# 12 · The todo app

**Difficulty:** Medium · **Assignment** 12 of 12 · **Check:** `.\check 12`

**Tags**
- *Language:* [ES modules](#primer/js-modules) · [array methods](#primer/js-arrays) · [arrow functions and closures](#primer/js-functions-closures) · [string methods](#primer/js-string-methods)
- *Library:* [inputs, the input and submit events](#primer/dom-form-inputs) · [document.title](#primer/dom-document-title) · [serving index.html locally](#primer/static-server)
- *Concepts:* [controlled inputs](#primer/react-controlled-inputs) · [keys](#primer/react-keys) · [useState and the rules of hooks](#primer/react-state) · [useEffect: after the DOM is updated](#primer/react-effects) · [function components](#primer/react-function-components)

## Read in the blog first

Jongeneel's article builds a [todo application](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application) on his library in section 6, the one before the conclusion: a controlled form component and a list component that contains it. Read the first paragraph and stop before the listings. The app you write is another one. Items can be removed, there is a count and a page title, ids never repeat, new items go in front, and the components are functions with hooks rather than classes. His code sketches the idea. It is not a model to follow. Nothing below depends on having read it.

## Learning material

- [Controlled inputs](#primer/react-controlled-inputs): the input displays the draft held in state, and typing updates that state.
- [document.title](#primer/dom-document-title): the title is the one piece of the page that sits outside the tree, which makes it an effect's job.
- [Serving index.html locally](#primer/static-server): `src/main.js` is the one file here that needs a browser, and a browser needs a server for module imports.
- [Inputs, the input and submit events](#primer/dom-form-inputs): the scenario lines `type` and `submit` dispatch these events.
- [Keys](#primer/react-keys): each item's key is its id, and the tests check which nodes stay put.
- [useEffect: after the DOM is updated](#primer/react-effects) and [useState and the rules of hooks](#primer/react-state): this time they are called from application code instead of a catalog component.

## Source material

- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application), section 6, the sample application
- React documentation: [Reacting to input with state](https://react.dev/learn/reacting-to-input-with-state), [Updating arrays in state](https://react.dev/learn/updating-arrays-in-state) and the [input](https://react.dev/reference/react-dom/components/input) component

## Where this fits

After eleven assignments of library code, this is the first program that uses it: `TodoApp` imports `createElement`, `useState` and `useEffect` from your library the way an application imports them from React, and never sees a fiber or a commit. There is a second file, `src/main.js`. The checker cannot run it, because it needs a browser. More at the end.

## The problem

Write a todo list as a function component on your own `Didact`. Scenarios render `<TodoApp/>`, type into its input, submit its form, click its buttons and dump the page. What your program prints is held against the output of the same app written in React.

### Input

`node assignments/assignment_12_todo_app.js <input-file> <output-file>` starts the entry program. It imports `../harness/env.js` first, then `Didact` from `../src/didact/index.js` and the named export `TodoApp` from `../src/app/TodoApp.js`. Its last line is `await runScenarioFile(process.argv[2], process.argv[3], { ...Didact, components: { TodoApp } })`, and the `components` entry is how `<TodoApp/>` in a scenario finds your function. The Boilerplate comes with the program written; starting blank, you write it. Scenario lines:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Names a tree. `tree t <TodoApp/>` is the usual one; the markup may also hold plain elements around it. |
| `render <name>` | Schedules the render with `Didact.render(tree, container)`. None of the work runs yet. |
| `flush` | Runs idle periods until nothing is left, effects included. |
| `type #<id> <text>` | Sets the element's `value` to the rest of the line, everything after the one space that follows the id, dispatches a bubbling `input` event, then flushes. `type #<id>` alone types the empty string. |
| `submit #<id>` | Dispatches a bubbling, cancelable `submit` event, then flushes. |
| `click #<id>` | A bubbling `click` and a flush. A click on `#todo-add` that your handler does not cancel also submits the form, as in a browser. |
| `dump` | Prints the page. |

### Output

`dump` prints a header with a running number, the page below the container (one `node` line per element, one `text` line per run of text), and a `title` line when `document.title` is not empty:

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
title "<document.title>"
```

A `node` line has the tag in lower case and the props that differ from their defaults (`className`, `id`, and an input's `value`), sorted by name. In a prop, a value containing a space, a double quote or a percent sign is percent-encoded: `value=buy%20milk`. A `text` line encodes only `"` and `%` (`%22`, `%25`), so spaces in a text stay as they are. Labels work as in the earlier dumps. A letter given to an element at its first appearance in a dump stays with it, which makes one letter one DOM node. The tests read that to tell which nodes your app keeps and which it rebuilds.

### The page

The root of your app produces this tree, with one `li` for each item, the newest first:

```
<div id="todo">
  <form id="todo-form">
    <input id="todo-input" value={draft}/>
    <button id="todo-add">Add</button>
  </form>
  <ul id="todo-list">
    <li id="item-{id}">
      <button id="toggle-{id}">todo or done</button>
      <span id="label-{id}" className="done or empty">{text}</span>
      <button id="remove-{id}">x</button>
    </li>
  </ul>
  <p id="todo-count">{n} left</p>
</div>
```

`<TodoApp/>` takes no props. For an empty list the dump runs from the first `div` down to `text 2 "0 left"` and ends with `title "0 left"`.

### The behaviour

`TodoApp` is a function component without props, exported by name from `src/app/TodoApp.js` (`export function TodoApp`), and imports what it needs from `../didact/index.js`. The primer's examples rename `createElement` to `h` on import. That is a habit and nothing more. The app's state is the list of items, the draft in the input and the id the next item will get. Your `Didact`'s setters take an updater function, `setItems((current) => ...)`, and do not support a plain value: write `setDraft(() => value)`, never `setDraft(value)`. The rules:

- The input is controlled: its `value` prop is the draft, and its `onInput` handler stores `event.target.value` as the new draft.
- `onSubmit` on the form calls `event.preventDefault()`. When the draft is empty once leading and trailing spaces are cut off, nothing else happens: no item, no id used, and the draft stays as typed. Otherwise a new item goes at the front of the list with the trimmed text, not done, and an id, and the draft is emptied. After an add the input shows the empty draft.
- Ids count up from 1 in the order items are added. Once used, an id stays used, even after its item is removed.
- The toggle button flips its item between `todo` and `done`. Its text shows the current one, and the label's `className` is `done` while the item is done and empty otherwise.
- The remove button deletes its item and nothing else.
- The count paragraph holds the text `<n> left`, in as many text nodes as you like, where `n` is the number of items that are not done.
- After every step `document.title` reads `<n> left`. Set it from an effect with the dependency list `[n]`, where `n` is the count of items not done, so that it runs when the count changes. The tests see only the result, in the `title` line of the next dump.
- Each `li` is keyed by its item's id. Adding, toggling, removing and typing all leave the other items' nodes where they are, along with the input, the form and the list.

Case files lose trailing spaces on every line, which rules out a scenario typing a draft of only spaces, or one ending in a space. The tests type an empty draft for the empty case, and one types a draft with three leading spaces and expects the item text without them. Trim before the emptiness test anyway.

### The part the checker cannot see

`src/main.js` renders `<TodoApp/>` into the `#root` element of `index.html`, as an entry program does for the tests but into a real page. The checker never runs it. To see the app, serve the project folder and open `index.html`, either with the book's Run button or with `python -m http.server 8000 --directory solutions` from the workbook folder, then browse to `http://localhost:8000/`. The server is needed because a browser refuses module imports from a file URL. Nothing in `main.js` is tested: a typo there passes the checker and leaves you a blank page.

## Requirements

Tests are grouped in the report by these ids. A failure may also name a likely cause, the requirement the first wrong line points at.

- **R1** A fresh app renders the tree above with no items, the count `0 left` and the title `0 left`, also when it is a child of other elements.
- **R2** `type` stores what was typed as the draft, and the input's `value` shows it (an empty draft shows no `value`).
- **R3** Submitting a draft that is not empty after trimming (through the form or the Add button) adds one item at the front: trimmed text, the next id, a `todo` button, and the input is cleared.
- **R4** Submitting a draft that is empty adds nothing and uses no id.
- **R5** The toggle button flips its item between `todo` and `done`, with the class `done` on the label while it is done, and touches no other item.
- **R6** The remove button deletes its item and nothing else. Ids are never reused.
- **R7** The count paragraph reads `<n> left` where n is the number of items that are not done.
- **R8** `document.title` is `<n> left` after every step.
- **R9** The nodes of items that stay are the same nodes after an add, a toggle or a remove, and typing keeps the input node.
- **E2E** Long sessions: scripted ones, and seeded random ones with valid operations only.

## Examples

### Example 1: the first item (test `12-R3-add-one-item`)

```
input:   tree t <TodoApp/>
         render t
         flush
         type #todo-input buy milk
         submit #todo-form
         dump

output:  dump 1
         node 0 a div "id=todo"
         node 1 b form "id=todo-form"
         node 2 c input "id=todo-input"
         node 2 d button "id=todo-add"
         text 3 "Add"
         node 1 e ul "id=todo-list"
         node 2 f li "id=item-1"
         node 3 g button "id=toggle-1"
         text 4 "todo"
         node 3 h span "id=label-1"
         text 4 "buy milk"
         node 3 i button "id=remove-1"
         text 4 "x"
         node 1 j p "id=todo-count"
         text 2 "1 left"
         title "1 left"
```

No `value` on the input. The add emptied the draft, and after the `type` alone it would show `value=buy%20milk`. The title reads `1 left` because the effect ran inside the last flush, ahead of the dump.

### Example 2: ids are not recycled (test `12-R6-ids-never-reused`)

```
input:   tree t <TodoApp/>
         render t
         flush
         type #todo-input one
         submit #todo-form
         type #todo-input two
         submit #todo-form
         click #remove-2
         type #todo-input three
         submit #todo-form
         click #remove-1
         type #todo-input four
         submit #todo-form
         dump

output:  dump 1
         node 0 a div "id=todo"
         node 1 b form "id=todo-form"
         node 2 c input "id=todo-input"
         node 2 d button "id=todo-add"
         text 3 "Add"
         node 1 e ul "id=todo-list"
         node 2 f li "id=item-4"
         node 3 g button "id=toggle-4"
         text 4 "todo"
         node 3 h span "id=label-4"
         text 4 "four"
         node 3 i button "id=remove-4"
         text 4 "x"
         node 2 j li "id=item-3"
         node 3 k button "id=toggle-3"
         text 4 "todo"
         node 3 l span "id=label-3"
         text 4 "three"
         node 3 m button "id=remove-3"
         text 4 "x"
         node 1 n p "id=todo-count"
         text 2 "2 left"
         title "2 left"
```

Two items are left and their ids are 4 and 3. An id taken as the length of the list plus one would have handed out `item-2` to three different items along the way. A removed item's id is gone for good. That is why the next id is state of its own.

### Example 3: older items keep their nodes (test `12-R9-front-insert-keeps-nodes`)

```
input:   tree t <TodoApp/>
         render t
         flush
         type #todo-input one
         submit #todo-form
         dump
         type #todo-input two
         submit #todo-form
         dump
         type #todo-input three
         submit #todo-form
         dump

output:  dump 1
         node 0 a div "id=todo"
         node 1 b form "id=todo-form"
         node 2 c input "id=todo-input"
         node 2 d button "id=todo-add"
         text 3 "Add"
         node 1 e ul "id=todo-list"
         node 2 f li "id=item-1"
         node 3 g button "id=toggle-1"
         text 4 "todo"
         node 3 h span "id=label-1"
         text 4 "one"
         node 3 i button "id=remove-1"
         text 4 "x"
         node 1 j p "id=todo-count"
         text 2 "1 left"
         title "1 left"
         dump 2
         node 0 a div "id=todo"
         node 1 b form "id=todo-form"
         node 2 c input "id=todo-input"
         node 2 d button "id=todo-add"
         text 3 "Add"
         node 1 e ul "id=todo-list"
         node 2 k li "id=item-2"
         node 3 l button "id=toggle-2"
         text 4 "todo"
         node 3 m span "id=label-2"
         text 4 "two"
         node 3 n button "id=remove-2"
         text 4 "x"
         node 2 f li "id=item-1"
         node 3 g button "id=toggle-1"
         text 4 "todo"
         node 3 h span "id=label-1"
         text 4 "one"
         node 3 i button "id=remove-1"
         text 4 "x"
         node 1 j p "id=todo-count"
         text 2 "2 left"
         title "2 left"
         dump 3
         node 0 a div "id=todo"
         node 1 b form "id=todo-form"
         node 2 c input "id=todo-input"
         node 2 d button "id=todo-add"
         text 3 "Add"
         node 1 e ul "id=todo-list"
         node 2 o li "id=item-3"
         node 3 p button "id=toggle-3"
         text 4 "todo"
         node 3 q span "id=label-3"
         text 4 "three"
         node 3 r button "id=remove-3"
         text 4 "x"
         node 2 k li "id=item-2"
         node 3 l button "id=toggle-2"
         text 4 "todo"
         node 3 m span "id=label-2"
         text 4 "two"
         node 3 n button "id=remove-2"
         text 4 "x"
         node 2 f li "id=item-1"
         node 3 g button "id=toggle-1"
         text 4 "todo"
         node 3 h span "id=label-1"
         text 4 "one"
         node 3 i button "id=remove-1"
         text 4 "x"
         node 1 j p "id=todo-count"
         text 2 "3 left"
         title "3 left"
```

Dump 2 puts the new item first under fresh labels `k` to `n`, and item 1 follows with its old `f` to `i`. Dump 3 repeats the move: item 3 leads with `o` to `r`, and items 2 and 1 keep theirs. With ids as keys the list inserts one new node in front. The old ones stay as they are. Keyed by position, it would rewrite item 1's node into item 2 and add a new node at the end, and the labels would show it.

## Constraints

Expect 41 tests: the cases of each requirement, two scripted sessions (the long one has about 50 steps) and five seeded random ones, which `-Fresh` replaces. Sessions stay short: none has more than 78 scenario lines. Item texts are short, can hold spaces, double quotes and percent signs, and never end in a space. A correct app answers a test in a fraction of a second, and the limit is 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Start by listing what the page depends on. Items, draft and next id each change on their own schedule, and each gets its own `useState`. The count and the title are derived values and not state: compute them from the items on every render. Only the title needs an effect, being the one thing outside the tree.
</details>

<details><summary>Hint 2: the approach</summary>

`TodoApp` gets three `useState` calls, a `useEffect` on the count, and a return value that is the tree from the contract. If the list gets hard to read, pull one item out into a function component of its own. Handlers use the updater form of the setter, `setItems((current) => ...)`, which is what your `useState` supports. Pass an item's id to its handlers rather than its position, and give each item's element a `key` that is the id.
</details>

<details><summary>Hint 3: the traps</summary>

- Trim the draft before you test it for emptiness, and store the trimmed text.
- The new item goes in front of the others: build the next list as `[newItem, ...current]`.
- The new id comes from state of its own. The length of the list plus one repeats an id once anything has been removed.
- Clear the draft after an add, or the input keeps showing it.
- Key by id. With the index as key, an insert at the front looks like a change to every item, and the nodes are rewritten.
- The `key` belongs on the element that is a child of the `ul`. If items are function components, put it on the component's element.
- `className` is `done` or an empty string, and a dump reads a missing prop and a prop set to `""` the same way.
- The count paragraph shows how many items are not done. All items would be the wrong number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
TodoApp():
    [items, setItems] = useState([])
    [draft, setDraft] = useState("")
    [nextId, setNextId] = useState(1)
    left = number of items not done

    useEffect(set document.title to left + " left", [left])

    onSubmit(event):
        event.preventDefault()
        text = trim(draft)
        if text is empty: return
        setItems(current => [{ id: nextId, text, done: false }, ...current])
        setNextId(id => id + 1)
        setDraft(() => "")

    return the tree of the contract:
        input: value = draft, onInput = event => setDraft(() => event.target.value)
        each item: an li keyed by its id; toggle and remove buttons call setItems with that id
        p: left + " left"
```
</details>

## Checking your solution

```
.\check 12                          every test, one line per requirement
.\check 12 -Case 12-R6-ids-never-reused    a single test: its scenario, the expected dump and yours
.\check 12 -Fresh                   five new random sessions
.\check 12 -Dispute <id> "why"      set a test aside when you are sure it is wrong
```

Forget to clear the input after an add and you get this:

```
  R3  Submitting a non-empty draft adds an item at the front of the lis... .    0 / 5   FAILED
      x 12-R3-add-one-item  type buy milk and submit the form
          node[0]: expected (depth=2, label=c, tag=input, props="id=todo-input"), got (depth=2, label=c, tag=input, props="id=todo-input value=buy%20milk") - differs in props  (in `dump 1`)
          likely cause: R3 - Submitting a non-empty draft adds an item at the front of the list: the trimmed text, the next id counting from 1, a todo button, and the input is cleared
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3 running tools/oracle/todoApp.mjs; every dump also checked against a model of the app in the generator
          reproduce: py -P tools/run_js.py build/bugs/12/input-not-cleared 12 build/cases/12/12-R3-add-one-item.in build/cases/12/12-R3-add-one-item.out
```

## After you pass: compare with the author's code

Jongeneel's [`ToDoComponent` and `NewItemForm`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application) are class components with state objects. `NewItemForm` keeps the draft and calls the `addItem` prop on submit, and `ToDoComponent` keeps the items and renders the list. Items are `li` elements keyed by index, each with a button that flips its `done` flag, and event handlers are lower-case properties such as `onsubmit` and `oninput`.

His app departs from the spec in several places. A new item goes at the end, where yours goes first. He keys by index, so each item is matched by position, and a removal or a front insert would rewrite the nodes of the items after it, where the tests expect every item to keep its own. His app only appends and has no removal, which is why the index key does no harm there. Submitting an empty draft adds an item with an empty label, since nothing trims or checks the draft. There is no remove button, no count, no ids and no title, and the toggle button reads `-` for an open item where yours reads `todo`. The draft lives in the form component, and a submit makes two `setState` calls, one in `addItem` and one that clears the draft. Each renders at once, where your handler's three updates give one render. His `renderDOM` also swaps the `#root` element itself for the app, where your `render` fills it. The tests side with the spec on all of these points.

The "Events" row of [React today](docs/react-today.md) covers React 19 as well as the post: handlers are named `onSubmit`, `onInput` and `onClick` here, as in React, and your `updateDom` turns them into listeners.
