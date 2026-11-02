# 01 · Create elements

**Difficulty:** Easy · **Assignment** 1 of 12 · **Check:** `.\check 01`

**Tags**
- *Language:* [ES modules](#primer/js-modules) · [objects, spread and destructuring](#primer/js-objects) · [rest parameters and spread arguments](#primer/js-rest-spread) · [typeof](#primer/js-typeof) · [array methods](#primer/js-arrays) · [throw, try and catch](#primer/js-errors) · [async and await](#primer/js-async-await)
- *Library:* [the harness and scenario files](#primer/workbook-harness) · [process.argv and exit codes](#primer/node-process)
- *Concepts:* [elements and what JSX turns into](#primer/react-elements) · [React 19 against the posts](#primer/react-today)

## Read in the blog first

You can pass with this page alone. If you would rather meet Pombo's version first, read [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) up to the point where he starts naming the library. His animated code is his solution, so save it for after you pass. [Step Zero](https://pomb.us/build-your-own-react/#step-zero-review), the short review before it, shows what a JSX tag compiles to and is worth a minute if JSX is new to you.

## Learning material

- [ES modules: import and export](#primer/js-modules): `createElement.js` exports its functions by name.
- [Objects, spread and destructuring](#primer/js-objects): an element is a plain object, and its props start as a copy of the props you receive.
- [Rest parameters and spread arguments](#primer/js-rest-spread): after `props`, `createElement` takes any number of children.
- [typeof and the types you meet](#primer/js-typeof): `typeof` tells a string or a number from an element.
- [Array methods](#primer/js-arrays): a list of children goes in and a list of elements comes out.
- [throw, try, catch and finally](#primer/js-errors): the Boilerplate's functions throw `not implemented: ...` until you replace them, which the checker reports as work not done yet.
- [async, await and top-level await](#primer/js-async-await): used in the three-line program that the checker runs.
- [Install and check Node.js 26](#primer/node-install): your code runs under `node`.
- [process.argv, exit codes and node --check](#primer/node-process): where that program reads the two file paths it is given.
- [The checker](#primer/workbook-check): the commands under Checking your solution.
- [The harness and scenario files](#primer/workbook-harness): the test files described near the end of this page.
- [Where the expected output comes from](#primer/workbook-oracle): for this assignment, a model written from the rules below and compared with `React.createElement` wherever the two agree.
- [py -P and Python 3.11](#primer/python-launcher): the checker is a Python program.
- [Elements, and what JSX turns into](#primer/react-elements): the object you build, and why app code here writes its calls out by hand.
- [React 19 against the posts](#primer/react-today): where real React differs from the posts. The last section of this page touches it.

## Source material

- Rodrigo Pombo, [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) and the review before it, [Step Zero](https://pomb.us/build-your-own-react/#step-zero-review)
- Wim Jongeneel, the part of [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=2.1%20The%20HTML%20syntax%20tree) on the HTML syntax tree, where his own element constructor appears
- React documentation: [createElement](https://react.dev/reference/react/createElement) and [Writing markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- MDN: [rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters) and [spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)

## Where this fits

Every later piece of Didact (the DOM code, the fibers, the hooks) passes elements around, and this is the function that makes them. Assignments 02 to 08 build their test elements with a copy of it that the harness carries, so a slip here stays contained. Your own `createElement` first gets called by other code in 09, when the test components use it.

## The problem

Write `createElement`, a function that describes one piece of a page as a plain object. It draws nothing. You call it, you get an object back, and later assignments turn objects like it into DOM nodes.

### What an element is

When you write JSX such as `<h1 id="title">Hello</h1>`, a build tool turns it into a function call:

```js
createElement("h1", { id: "title" }, "Hello")
```

That call returns an element: a plain object with two fields, `type` and `props`.

```js
{
  type: "h1",
  props: {
    id: "title",
    children: [
      {
        type: "TEXT_ELEMENT",
        props: { nodeValue: "Hello", children: [] },
      },
    ],
  },
}
```

`type` is the first argument, as it came in. `props` holds the props you passed (`id`) and one more entry, `children`, an array of everything that sat between the tags. The string `"Hello"` did not go into `children` as itself. It became a small element of its own, a text element, and the next sections explain why.

### What goes in

| Argument | Type | What it is | Example |
|---|---|---|---|
| `type` | string | the tag name | `"div"`, `"h1"`, `"button"` |
| `props` | object, or `null` | the attributes, as keys and values; `null` when there are none | `{ id: "title", className: "big" }` |
| `...children` | any number of strings, numbers and elements | what goes inside, in order | `"Hello"`, `42`, another element |

### What comes out

An element: `{ type, props }`, where `type` is a string and `props` is an object. `props` has every key and value you passed in, plus `children`, an array in which every entry is an element, never a bare string or number.

### Text elements, and why `createTextElement` exists

A child like `"Hello"` or `42` is not an object, so it has no `type` and no `props`. Later code walks over every element's `children` and reads `.type` and `.props` on each entry. It would have to stop and ask "is this a string or an element?" every time. So `createElement` removes the question once: a string or number child is wrapped in an element before it goes into `children`.

`createTextElement(text)` builds that wrapper, so you write it once:

```js
createTextElement("Hello")
// { type: "TEXT_ELEMENT", props: { nodeValue: "Hello", children: [] } }
```

`TEXT_ELEMENT` is just a made-up type name that marks "this is raw text, not a tag". The text sits in `nodeValue`, and `children` is an empty array so that code which walks into the children of every element can walk into this one too. A number stays a number: `createTextElement(42)` has `nodeValue: 42`.

`createElement` calls `createTextElement` for each child argument that is a string or a number. A child that is already an element goes into `children` as it is.

| Child argument | Entry in `children` |
|---|---|
| a string, including `""` | a text element with that string as `nodeValue` |
| a number, including `0` | a text element with that number as `nodeValue`, still a number |
| an element | the same element, unchanged |

For example, `createElement("p", null, "a ", createElement("b", null, "bold"), 42)` returns a `p` with three children:

```
p
 ├─ text element, nodeValue "a "
 ├─ the b element, which has one text child, "bold"
 └─ text element, nodeValue 42 (the number, not "42")
```

### The details that the tests check

- `children` is always an array: `[]` for no children, and an array of one for a single child.
- The result's `props` is a new object. The object you were given is never modified, not even when the same one is passed to several calls.
- If the props you were given already have a `children` key, it does not survive: the array built from the child arguments replaces it.
- `null` props behave like an empty object.
- `key` is an ordinary prop. It stays in `props` and appears nowhere else on the element.
- Children that are `null`, booleans, arrays or `undefined` are out of scope. No test passes them, so your function can do what it likes with them.

### How the checker calls your function

The tests do not call `createElement` from JavaScript themselves. Each test is a short text file of lines, and `assignments/assignment_01_create_element.js` gives that file and your `createElement` to the harness. The harness makes the calls the file lists and writes down what each one returned. You do not write any of that reading and printing. The Boilerplate gives you the program finished. If you start from scratch it is three lines: import your `createElement` from `../src/didact/createElement.js`, import `runScenarioFile` from `../harness/scenario.js`, and end with `await runScenarioFile(process.argv[2], process.argv[3], { createElement })`.

An input file has three kinds of line:

| Line | Meaning |
|---|---|
| `call <type> <props> [child ...]` | Call `createElement(type, props, ...children)` and record the result. `<props>` is a JSON object or `null`. A child is a JSON string, a JSON number, or `$k`, the element that the k-th `call` returned, counting from 1. |
| `props <name> <json>` | Store a props object under a name, so that later `call` lines can pass it as `@name`. |
| `show <name>` | Write down the stored object as it is now. |

So `call h1 {"id":"title"} "Hello"` means `createElement("h1", { id: "title" }, "Hello")`. The `props` and `show` lines exist for one test: they check that your function leaves the caller's object alone. `@name` passes the stored object itself, not a copy.

The output file has one line per `call`, `element <k> <json>`, where `k` is the call's number and `<json>` is the element it returned, and one line `props <name> <json>` per `show`. The JSON is written compactly, with three conventions that keep it the same whatever order you built your object in:

- Keys are sorted by name at every level.
- A space inside a string is written as `\u0020`, and a character outside ASCII as a `\uXXXX` escape.
- Numbers print the way JavaScript prints them, so the input `4.0` comes back as `4`.

Read an output line the way the example above reads: `{"props":{"children":[...],"id":"title"},"type":"h1"}` is the object `{ type: "h1", props: { children: [...], id: "title" } }` with its keys in alphabetical order. The examples below show each result both ways.

## Requirements

- **R1** An element has the fields `type` and `props` and no others. `type` is the first argument; `props` carries every key and value of the props that were given.
- **R2** `props.children` is an array holding the children in order: empty for none, one entry for one child. A `children` key in the given props is replaced by it.
- **R3** A string or number child becomes a text element whose `nodeValue` is the value as given, so a number stays a number and `0` and `""` count.
- **R4** An element given as a child sits in `children` unchanged, at the position where it was passed.
- **R5** Props of `null` act like `{}`.
- **R6** The call leaves the props you were given unmodified, however often the object is reused.
- **R7** `key` stays in `props` as an ordinary prop.
- **E2E** End to end: several `call` lines that build a tree from the leaves up, the way an app does.

## Examples

### Example 1: a heading with one piece of text (test `01-R2-one-text`)

```
input:
call h1 null "Title"

output:
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"Title"},"type":"TEXT_ELEMENT"}]},"type":"h1"}
```

That one call is `createElement("h1", null, "Title")`. The output line is the returned element, written compactly. Spread out, it reads:

```js
{
  type: "h1",
  props: {
    children: [
      {
        type: "TEXT_ELEMENT",
        props: { nodeValue: "Title", children: [] },
      },
    ],
  },
}
```

The props were `null`, so `props` holds only `children`. The string `"Title"` is one entry of that array, wrapped as a text element. Even a single child gives an array.

### Example 2: an element inside an element (test `01-R4-one-level`)

```
input:
call span null "x"
call div null $1

output:
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"x"},"type":"TEXT_ELEMENT"}]},"type":"span"}
element 2 {"props":{"children":[{"props":{"children":[{"props":{"children":[],"nodeValue":"x"},"type":"TEXT_ELEMENT"}]},"type":"span"}]},"type":"div"}
```

In JavaScript terms: `const span = createElement("span", null, "x")`, then `createElement("div", null, span)`. `$1` stands for whatever line 1 returned. The first output line is the `span` with its text. The second is the `div`, and its one child is the `span` element from line 1, exactly as line 1 printed it. Nothing was wrapped, because it already was an element:

```
div
 └─ span
     └─ text element, nodeValue "x"
```

### Example 3: one props object, three elements (test `01-R6-reuse`)

```
input:
props p {"className":"box","title":"t"}
call div @p "one"
call div @p "two" "three"
call div @p
show p

output:
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"one"},"type":"TEXT_ELEMENT"}],"className":"box","title":"t"},"type":"div"}
element 2 {"props":{"children":[{"props":{"children":[],"nodeValue":"two"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"three"},"type":"TEXT_ELEMENT"}],"className":"box","title":"t"},"type":"div"}
element 3 {"props":{"children":[],"className":"box","title":"t"},"type":"div"}
props p {"className":"box","title":"t"}
```

All three calls get the same object `p`. Each result has `className` and `title` copied in plus its own `children`, so the three elements share nothing. The last line is what the test is about: after three calls, `p` must still hold only `className` and `title`. An implementation that writes `children` onto the object it received shows up here.

## Constraints

Types are single words. Props are JSON objects or `null`. Number arguments are finite; they print the way JavaScript prints them, so `4.0` comes back as `4`. A string child can hold any characters, spaces and quotes included. A scenario runs to 16 lines at most. The 48 tests cover each requirement's cases, then two longer scripted trees and nine seeded random ones (`-Fresh` gives nine new ones). A correct solution needs milliseconds. Each test may run for 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Start with the smallest test there is, the single line `call div null`. The result is one object with two fields. Get that right, then add a child, then a text child, then a props object. The tests have a case for every one of those steps.
</details>

<details><summary>Hint 2: the approach</summary>

Make the result's `props` a fresh object: copy the given props into it, then give it its own `children` field, so that a `children` key from the caller cannot survive. Turn the child arguments into a new array one at a time. An element stays itself and anything else goes through `createTextElement`. The copy does two jobs: the caller's object stays as it was, and `null` props turn into the same thing as an empty object.
</details>

<details><summary>Hint 3: the traps</summary>

- Do not turn a number child into a string. `0` is a child too, and a falsy filter drops it.
- A text element needs `children: []` of its own. The render in 03 walks into the children of every element, text elements included, and expects an array each time.
- One child is still an array of one. React's own `createElement` unwraps it; yours must not.
- Whichever is written later wins: the spread of the given props or your own `children`. The `children` in the result has to come from your code.
- Assigning to the object you received feels like a shortcut, and it holds until a test reuses the object. `show` is there for that case.
- Here `key` is an ordinary prop: it stays in `props`, and the element gets no third field for it.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
createElement(type, props, ...children):
    resultProps = a new object with every key of props   (nothing, if props is null)
    resultProps.children = for each child in children:
                               if the child is an element: the child itself
                               otherwise: createTextElement(child)
    return an object with fields type and props = resultProps

createTextElement(text):
    return an element of type "TEXT_ELEMENT" whose props are nodeValue = text and children = []
```
</details>

## Checking your solution

```
.\check 01                          every test, grouped by requirement
.\check 01 -Case 01-R3-number       one test with its full input, the expected lines and yours
.\check 01 -Fresh                   nine new random trees, to try your code on scenarios you have not seen
.\check 01 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A `createElement` that spreads the given props after it has written `children` fails like this:

```
  R2  `props.children` is always an array of the children in order: emp... .    5 / 6   FAILED
      x 01-R2-children-key  a children key in the given props is replaced by the children array
          element[0]: expected (n=1, json={"props":{"children":[{"props":{"children":[],"nodeValue":"x"},"type":"TEXT_ELEMENT"}]},"type":"div"}), got (n=1, json={"props":{"children":"junk"},"type":"div"}) - differs in json
          likely cause: R2 - `props.children` is always an array of the children in order: empty for none, one entry for one child
          expected values from: independent dict model in tools/gen_p01.py, cross-checked with React 19.3.1 createElement
          reproduce: py -P tools/run_js.py build/bugs/01/props-after-children 01 build/cases/01/01-R2-children-key.in build/cases/01/01-R2-children-key.out
```

## After you pass: compare with the author's code

[Pombo's version](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) has the same two functions this page asks for. `createElement` returns `{ type, props }` with the given props spread first and `children` after them, and whatever is not an object goes to `createTextElement`, which builds the `TEXT_ELEMENT` node with `nodeValue` and an empty `children`. In the post it all lives in one file under the name `Didact`, and a pragma comment points JSX at `Didact.createElement`. Here the two functions get a module of their own, and the app code calls `createElement` by hand, since the workbook has no build step.

The post decides with `typeof child === "object"`, which splits the out-of-scope values in two. `null` and arrays are objects, so they land in `children` as they are. `undefined` and the booleans are not, so they become text elements holding `undefined`, `false` or `true`. React renders nothing for `null`, `undefined` and the booleans, and it renders the items of an array. No test passes any of them.

According to the post, React itself neither wraps primitive children nor creates an empty array when there are none, and Didact does both on purpose to keep the later code simple. This assignment follows the post: `children` is `[]` when empty and never missing, and a lone child sits in an array. (`React.createElement` stores a lone child as the child itself.) React also keeps `key` in a field of the element beside `props`, whereas here it stays in `props`, because the reconciler of assignment 07 reads it there. [React today](docs/react-today.md) lists where React 19 departs from the posts, and its row on keys is the one that bears on this.

[Jongeneel's `createElement`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=2.1%20The%20HTML%20syntax%20tree) returns a different shape, `{ kind, tagname, props, childeren, key }` (`childeren` is his spelling), with the children in a field beside `props`. Three of its choices matter to the tests. It runs `delete props.key` on the object it receives, which doubles as the `props` of the node. The caller's props change, and the key sits on the node instead of in `props`. It reads `props.key` without a guard, so `null` props throw. And it takes only nodes as children: text goes through a separate `createText` that turns its value into a string. R6 and R7 catch the first, R5 the second, R3 the third.
