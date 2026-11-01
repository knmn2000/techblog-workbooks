# 12 · The todo app

**Difficulty:** Medium · **Assignment** 12 of 12 · **Check:** `.\check 12`

**Tags**
- *Language:* [ES modules](#primer/js-modules) · [array methods](#primer/js-arrays) · [arrow functions and closures](#primer/js-functions-closures) · [string methods](#primer/js-string-methods)
- *Library:* [inputs, the input and submit events](#primer/dom-form-inputs) · [document.title](#primer/dom-document-title) · [serving index.html locally](#primer/static-server)
- *Concepts:* [controlled inputs](#primer/react-controlled-inputs) · [keys](#primer/react-keys) · [useState and the rules of hooks](#primer/react-state) · [useEffect: after the DOM is updated](#primer/react-effects) · [function components](#primer/react-function-components)

## Read in the blog first

Jongeneel's article builds a [todo application](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application) on his library in section 6, just before the conclusion: a controlled form component and a list component that contains it. Read the section's first paragraph and stop before the listings. The app below is a different one: items can be removed, there is a count and a page title, ids never repeat, new items go to the front, and the components are functions with hooks instead of classes. His code is a picture of the idea and not a model to follow. This page is complete without the article.

## Learning material

- [Controlled inputs](#primer/react-controlled-inputs): the input shows the draft you keep in state, and typing updates that state.
- [document.title](#primer/dom-document-title): the page title is the one piece of the page outside the tree, which makes it a job for an effect.
- [Serving index.html locally](#primer/static-server): `src/main.js` is the only file here that needs a browser, and a browser needs a server for module imports.
- [Inputs, the input and submit events](#primer/dom-form-inputs): used in a new way. The scenarios `type` into the input and `submit` the form.
- [Keys](#primer/react-keys): used in a new way. A key is an item's id, and the tests look for the nodes that stay.
- [useEffect: after the DOM is updated](#primer/react-effects) and [useState and the rules of hooks](#primer/react-state): used in a new way, by application code and not by a catalog component.

## Source material

- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application), section 6, the sample application
- React documentation: [Reacting to input with state](https://react.dev/learn/reacting-to-input-with-state), [Updating arrays in state](https://react.dev/learn/updating-arrays-in-state) and the [input](https://react.dev/reference/react-dom/components/input) component

## Where this fits

Eleven assignments built a library, and this one is the first program that uses it. `TodoApp` imports `createElement`, `useState` and `useEffect` from your library the way an application imports them from React, and never touches fibers or commits. There is a second file, `src/main.js`, that the checker cannot run, because it needs a browser: see the end of the problem.

## The problem

Write the todo list as a function component on your own `Didact`. A scenario renders `<TodoApp/>`, types into its input, submits its form, clicks its buttons and dumps the page, and the checker compares what you print with what the same app written in React prints.

### Input

The checker runs `node assignments/assignment_12_todo_app.js <input-file> <output-file>`. The program imports `../harness/env.js` first, then `Didact` from `../src/didact/index.js` and the named export `TodoApp` from `../src/app/TodoApp.js`, and ends with `await runScenarioFile(process.argv[2], process.argv[3], { ...Didact, components: { TodoApp } })`. The `components` entry is how `<TodoApp/>` in a scenario finds your function. The Boilerplate has the program finished; from a blank start you write it yourself. The lines a scenario holds:

| Line | What the harness does |
|---|---|
| `tree <name> <markup>` | Names a tree. `tree t <TodoApp/>` is the usual one; the markup may also hold plain elements around it. |
| `render <name>` | `Didact.render(tree, container)`. It schedules the work and does none of it. |
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

A `node` line gives the tag in lower case and the props that differ from their defaults (`className`, `id`, `value` of an input) sorted by name. A value with a space, a double quote or a percent sign is percent-encoded in a prop: `value=buy%20milk`. In a `text` line only `"` and `%` are encoded (`%22`, `%25`), so a text with spaces reads as it is. The label is a letter given to an element the first time a dump shows it and kept in every later dump, so the same letter means the same DOM node. The tests use that to see which nodes your app keeps and which it rebuilds.

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

The `<TodoApp/>` element itself has no props. Its dump for an empty list is the first `div` down to `text 2 "0 left"`, followed by `title "0 left"`.

### The behaviour

`TodoApp` is a function component without props, exported by name from `src/app/TodoApp.js` (`export function TodoApp`). It imports what it needs from `../didact/index.js`; the primer's examples rename `createElement` to `h` on import, which is a habit and not a rule. The state of the app is the list of items, the draft in the input and the id the next item gets. Your `Didact`'s setters take an updater function, `setItems((current) => ...)`, and a plain value is not supported, so write `setDraft(() => value)` and not `setDraft(value)`. The rules:

- The input is controlled: its `value` prop is the draft, and its `onInput` handler stores `event.target.value` as the new draft.
- The form's `onSubmit` handler calls `event.preventDefault()`. If the draft with its leading and trailing spaces cut off is empty, nothing else happens: no item, no id used, and the draft stays as typed. Otherwise a new item is added at the front of the list, with that trimmed text, not done, and an id; then the draft is emptied. The input shows the empty draft after an add.
- Ids count from 1 in the order items are added. An id is never used again, not even after the item that had it is removed.
- The toggle button flips its item between `todo` and `done`: the button's text says which, and the label's `className` is `done` while the item is done and empty otherwise.
- The remove button deletes its item and nothing else.
- `n` in the count paragraph is the number of items that are not done. The paragraph holds the text `<n> left`, in however many text nodes you like.
- After every step `document.title` is `<n> left`. Set it from an effect whose dependency list is `[n]`, `n` being the count of items not done, so it runs when the count changes. The tests see only the result, in the `title` line of the next dump.
- Each `li` is keyed by its item's id. Adding, toggling, removing and typing leave the nodes of the other items, and the input, the form and the list, where they are.

A case file cuts trailing spaces off every line, so a scenario cannot type a draft that is only spaces, or one that ends in a space. The tests type an empty draft for the empty case, and one test types a draft that starts with three spaces and expects the item text without them. Trim before the emptiness test all the same.

### The part the checker cannot see

`src/main.js` renders `<TodoApp/>` into the `#root` element of `index.html`, the way an entry program renders it for the tests but into a real page. The checker never runs it. To see the app, serve the project folder and open `index.html`, with the book's Run button or with `python -m http.server 8000 --directory solutions` from the workbook folder, then browse to `http://localhost:8000/`. A browser needs the server because it refuses module imports from a file URL. Nothing about `main.js` is tested, so a typo there passes the checker, and the page stays blank.

## Requirements

The report groups the tests by these ids. A failure can also name a likely cause: the requirement that the first wrong line points at.

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

The input has no `value` in the dump: the draft was emptied by the add. Typing alone would have shown `value=buy%20milk`. The title says `1 left` because the effect ran inside the last flush, before the dump.

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

Two items exist at the end, yet the ids are 4 and 3. A counter that is the length of the list plus one would have given `item-3` twice at some point, and the id of a removed item is gone for good. That is why the next id is state of its own.

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

In the second dump the new item comes first, with the new labels `k` to `n`, and item 1 follows with its old labels `f` to `i`. The third dump does the same again: item 3 is first with labels `o` to `r`, and items 2 and 1 keep theirs. Keyed by id, your list inserts one node in front of the old ones. Keyed by position, it would rewrite item 1's node into item 2, put a new node at the end, and the labels would say so.

## Constraints

The 41 tests are the cases of each requirement, two scripted sessions (the long one has about 50 steps) and five seeded random ones, which `-Fresh` replaces. A session has at most 78 scenario lines. Item texts are short, may hold spaces, double quotes and percent signs, and never end in a space. A correct app answers each test in a fraction of a second, against a limit of 10.

## Hints

<details><summary>Hint 1: where to start</summary>

List what the page depends on. The items, the draft and the next id each change on their own schedule, so each of the three gets its own `useState`. Derived values (the count, the title) are not state: compute it from the items on each render. Only the title is an effect, because it is the one thing outside the tree.
</details>

<details><summary>Hint 2: the approach</summary>

Write `TodoApp` with three `useState` calls and a `useEffect` on the count, and let it return the tree in the contract. Pull one item out into a function component of its own if the list gets hard to read. Every handler uses the updater form of the setter, `setItems((current) => ...)`, which is what your `useState` supports. Pass an item's id through its handlers instead of its position, and give the element of each item a `key` that is the id.
</details>

<details><summary>Hint 3: the traps</summary>

- Trim the draft before you test it for emptiness, and store the trimmed text.
- The new item goes in front of the others: build the next list as `[newItem, ...current]`.
- Take the new id from state of its own. The length of the list plus one repeats an id once something has been removed.
- Clear the draft after an add, or the input keeps showing it.
- Key by id. A key that is the index makes every insert at the front look like a change to all items, and the nodes get rewritten.
- A `key` needs to sit on the element that is a child of the `ul`. If items are function components, put it on the component's element.
- `className` is `done` or an empty string. A prop left out and a prop set to `""` read the same in a dump.
- The count paragraph shows the number of items that are not done, not the number of items.
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

An app that forgets to clear the input after an add fails like this:

```
  R3  Submitting a non-empty draft adds an item at the front of the lis... .    0 / 5   FAILED
      x 12-R3-add-one-item  type buy milk and submit the form
          node[0]: expected (depth=2, label=c, tag=input, props="id=todo-input"), got (depth=2, label=c, tag=input, props="id=todo-input value=buy%20milk") - differs in props  (in `dump 1`)
          likely cause: R3 - Submitting a non-empty draft adds an item at the front of the list: the trimmed text, the next id counting from 1, a todo button, and the input is cleared
          expected values from: React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3 running tools/oracle/todoApp.mjs; every dump also checked against a model of the app in the generator
          reproduce: py -P tools/run_js.py build/bugs/12/input-not-cleared 12 build/cases/12/12-R3-add-one-item.in build/cases/12/12-R3-add-one-item.out
```

## After you pass: compare with the author's code

Jongeneel's [`ToDoComponent` and `NewItemForm`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=6.%20Building%20a%20sample%20application) are class components with state objects: `NewItemForm` keeps the draft and calls the `addItem` prop on submit, and `ToDoComponent` keeps the items and renders the list. The items are `li` elements keyed by their index, each with a button that flips its `done` flag, and event handlers are lower-case properties such as `onsubmit` and `oninput`.

His app differs from the spec above in these ways: a new item goes at the end, where yours goes first. Its key is the index, so every item is matched by its position, and a removal or a front insert would rewrite the nodes of the items after it where the tests expect each item to keep its own (his app only appends and has no removal, so the index key does no harm there). Submitting an empty draft adds an item with an empty label, since nothing trims or checks the draft. It has no remove button, no count, no ids and no title, and its toggle button reads `-` for an open item where yours reads `todo`. The draft lives in the form component, and a submit makes two `setState` calls, one in `addItem` and one that clears the draft, which each render at once where your handler's three updates give one render. His `renderDOM` also swaps the `#root` element itself for the app, where your `render` fills it. The tests take the other side on each of these points.

For React 19 as well as the post, [React today](docs/react-today.md) lists the "Events" row: handlers are named `onSubmit`, `onInput` and `onClick` here, as in React, and your `updateDom` turns them into listeners.
