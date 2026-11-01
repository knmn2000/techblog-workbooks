# 01 · Create elements

**Difficulty:** Easy · **Assignment** 1 of 12 · **Check:** `.\check 01`

**Tags**
- *Language:* [ES modules](#primer/js-modules) · [objects, spread and destructuring](#primer/js-objects) · [rest parameters and spread arguments](#primer/js-rest-spread) · [typeof](#primer/js-typeof) · [array methods](#primer/js-arrays) · [throw, try and catch](#primer/js-errors) · [async and await](#primer/js-async-await)
- *Library:* [the harness and scenario files](#primer/workbook-harness) · [process.argv and exit codes](#primer/node-process)
- *Concepts:* [elements and what JSX turns into](#primer/react-elements) · [React 19 against the posts](#primer/react-today)

## Read in the blog first

You can pass with this page alone. If you would rather start from Pombo's text, read [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) and stop where it turns to naming the library. The animated code in that step is the author's solution, so keep it for after you pass. The short review step before it ([Step Zero](https://pomb.us/build-your-own-react/#step-zero-review)) shows what a JSX tag turns into, which helps if JSX is new to you.

## Learning material

- [ES modules: import and export](#primer/js-modules): your file exports its functions by name, and the entry program imports them.
- [Objects, spread and destructuring](#primer/js-objects): an element is a plain object, and its props start as a copy of the ones you receive.
- [Rest parameters and spread arguments](#primer/js-rest-spread): the children arrive as however many arguments follow `props`.
- [typeof and the types you meet](#primer/js-typeof): `typeof` separates a string or a number from an element.
- [Array methods](#primer/js-arrays): the list of children goes in and a different list comes out.
- [throw, try, catch and finally](#primer/js-errors): until you write the function, the starter throws `not implemented: ...`, and the checker reports that as unfinished work instead of a crash.
- [async, await and top-level await](#primer/js-async-await): the entry program waits for the harness before it exits.
- [Install and check Node.js 26](#primer/node-install): the checker starts your entry program with `node`.
- [process.argv, exit codes and node --check](#primer/node-process): the entry program reads its input path and output path from `process.argv`.
- [The checker](#primer/workbook-check): the commands at the end of this page.
- [The harness and scenario files](#primer/workbook-harness): the three scenario lines described under Input.
- [Where the expected output comes from](#primer/workbook-oracle): for this assignment, a model written from the rules below and compared with `React.createElement` where the two agree.
- [py -P and Python 3.11](#primer/python-launcher): the checker is a Python program.
- [Elements, and what JSX turns into](#primer/react-elements): what the function produces and why the app code will call it by hand.
- [React 19 against the posts](#primer/react-today): the places where the real React departs from the posts, used in the last section.

## Source material

- Rodrigo Pombo, [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) and the review before it, [Step Zero](https://pomb.us/build-your-own-react/#step-zero-review)
- Wim Jongeneel, the part of [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=2.1%20The%20HTML%20syntax%20tree) on the HTML syntax tree, where his own element constructor appears
- React documentation: [createElement](https://react.dev/reference/react/createElement) and [Writing markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- MDN: [rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters) and [spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)

## Where this fits

Didact starts with the object that the rest of the library passes around. The DOM code, the fiber tree and the hooks all read `{ type, props }`, so whatever shape you settle on is the shape they get. Assignments 02 to 08 build their elements with the harness's own copy of this function, which keeps a slip in your file from spoiling them; assignment 09 is where the catalog's function components call yours.

## The problem

Write `createElement`, the function that a JSX tag compiles to. A scenario calls it with arguments written in the input file, and your program prints the objects it gets back.

### Input

The checker runs `node assignments/assignment_01_create_element.js <input-file> <output-file>`. The harness reads the input file, calls your `createElement` as each line says, and writes the output file. The lines are:

| Line | What the harness does |
|---|---|
| `call <type> <props> [child ...]` | Calls `createElement(type, props, ...children)` and prints the result. `<type>` is a bare word or a JSON string. `<props>` is a JSON object, `null`, or `@name`, an object defined by a `props` line. A child is a JSON string, a JSON number, or `$k`, the element that the k-th `call` returned (counting from 1). |
| `props <name> <json>` | Stores a props object under `<name>` for later `@name` arguments. Prints nothing. |
| `show <name>` | Prints the stored object as it is now. |

An `@name` argument hands your function the stored object itself, not a copy, and every `@name` of the same name is the same object.

The entry program, `assignments/assignment_01_create_element.js`, is short: it imports your `createElement` and the harness's `runScenarioFile` (from `../harness/scenario.js`), and ends with `await runScenarioFile(process.argv[2], process.argv[3], { createElement })`. The two arguments are the input path and the output path that the checker passes. The Boilerplate comes with this file finished. From scratch, write it before anything else.

Your file `src/didact/createElement.js` exports two functions:

| Export | Meaning |
|---|---|
| `createElement(type, props, ...children)` | The one the scenario calls. |
| `createTextElement(text)` | Returns the text element for one string or number: type `"TEXT_ELEMENT"`, props `{ nodeValue: text, children: [] }`, with `nodeValue` exactly as passed, so a number stays a number. The tests call only `createElement`; a text element shows up in the children it lands in. |

### Output

`call` prints one line, `element <k> <json>`, where `k` counts the calls so far, starting at 1. `show` prints `props <name> <json>`. The JSON is compact and written the way the harness writes it, so your code does not print it:

- keys come out sorted by name at every level, which hides the order in which you build the object;
- a space inside a string prints as `\u0020`, and a character outside ASCII as a `\uXXXX` escape;
- a number prints as JavaScript prints it, so the input `4.0` comes out as `4`.

```
element 1 {"props":{"children":[],"id":"a"},"type":"div"}
props p {"id":"a"}
```

### What an element is

An element is an object with two fields, `type` and `props`. `type` is the first argument as it came. `props` is a new object, not the one you received. It holds every key of the props you received, each with its value, plus `children`.

`children` is a new array on every call, with one entry per child argument in the order given:

| Child argument | Entry in `children` |
|---|---|
| a string, including `""` | `{"type":"TEXT_ELEMENT","props":{"nodeValue":<the string>,"children":[]}}` |
| a number, including `0` | the same, with the number as `nodeValue` |
| an element | that element, unchanged |

A number keeps its type: the child `42` has `nodeValue` 42, and the child `"42"` has `nodeValue` `"42"`. With no children the array is empty. One child still gives an array of one.

A `children` key in the props you receive has no effect. The array built from the child arguments replaces it, also when there are no child arguments and the result is `[]`.

Props of `null` act like an empty object. Your function leaves the object it received, and everything inside it, as it found them. `key` is an ordinary prop: it stays in `props` with the value it had, and it does not appear anywhere else on the element.

Children that are `null`, booleans or arrays, and an `undefined` child, are out of scope. No test passes them, so whatever your function does with them is fine.

## Requirements

- **R1** An element has the fields `type` and `props`, and no others. `type` is the first argument, and `props` carries every key and value of the props that were given.
- **R2** `props.children` is an array holding the children in order: empty for none, one entry for one child. A `children` key in the given props is replaced by it.
- **R3** A string or number child becomes a text element whose `nodeValue` is the value as given, so a number stays a number and `0` and `""` count.
- **R4** An element given as a child sits in `children` unchanged, at the position where it was passed.
- **R5** Props of `null` act like `{}`.
- **R6** The props you were given are not modified by the call, however often the object is reused.
- **R7** `key` stays in `props` as an ordinary prop.
- **E2E** Several `call` lines that build a tree from the leaves up, the way an app does.

## Examples

### Example 1: text, an element, text (test `01-R4-interleaved`)

input:
```
call b null "bold"
call p null "a " $1 " b"
```
output:
```
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"bold"},"type":"TEXT_ELEMENT"}]},"type":"b"}
element 2 {"props":{"children":[{"props":{"children":[],"nodeValue":"a\u0020"},"type":"TEXT_ELEMENT"},{"props":{"children":[{"props":{"children":[],"nodeValue":"bold"},"type":"TEXT_ELEMENT"}]},"type":"b"},{"props":{"children":[],"nodeValue":"\u0020b"},"type":"TEXT_ELEMENT"}]},"type":"p"}
```

`$1` is the element the first line returned. In the second call it is the middle child, and it appears in the output as line 1 printed it, between two text elements whose spaces the harness writes as `\u0020`. The strings `"a "` and `" b"` keep their spaces; do not trim a text.

### Example 2: a number is not a string (test `01-R3-numeric-string`)

input:
```
call p null "42" 42 "4.0" 4.0 "-7" -7
```
output:
```
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"42"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":42},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"4.0"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":4},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"-7"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":-7},"type":"TEXT_ELEMENT"}]},"type":"p"}
```

Six children, three pairs. In each pair the string keeps its quotes in the output and the number does not. The pair `"4.0"` and `4.0` is the odd one: the string stays `"4.0"`, while the number comes back as `4` because that is how JavaScript prints it. Nothing in your code needs to know that.

### Example 3: one props object, three elements (test `01-R6-reuse`)

input:
```
props p {"className":"box","title":"t"}
call div @p "one"
call div @p "two" "three"
call div @p
show p
```
output:
```
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"one"},"type":"TEXT_ELEMENT"}],"className":"box","title":"t"},"type":"div"}
element 2 {"props":{"children":[{"props":{"children":[],"nodeValue":"two"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"three"},"type":"TEXT_ELEMENT"}],"className":"box","title":"t"},"type":"div"}
element 3 {"props":{"children":[],"className":"box","title":"t"},"type":"div"}
props p {"className":"box","title":"t"}
```

The `show` line carries this test. The harness prints `p` after three calls that were all handed the same object, and it must still hold only `className` and `title`. An implementation that stores `children` on the object it received prints `children` there.

## Constraints

Types are single words, props are JSON objects or `null`, and every number is finite and prints the same in JSON and in JavaScript. A string child may hold any characters, spaces and quotes included. No scenario has more than 16 lines. The 48 tests are the cases of each requirement, two longer scripted trees and nine seeded random ones (`-Fresh` gives nine new ones). A correct solution takes milliseconds, and each test is allowed 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Run the smallest scenario first: one line, `call div null`. Your output has to be a single object with two fields. Get that right, then add a child, then a text child, then a props object. Each step in that order is a case in the tests.
</details>

<details><summary>Hint 2: the approach</summary>

Build the result's `props` as a fresh object that begins as a copy of the given props and then gets its own `children` field, so a `children` key in the given props cannot survive. Turn the child arguments into a new array, element by element: an element stays itself, anything else goes through `createTextElement`. The copy matters in two places: it keeps the caller's object unchanged, and it makes `null` props the same thing as an empty object.
</details>

<details><summary>Hint 3: the traps</summary>

- A number child is not a string, and `0` is a child. Neither should be turned into text, filtered out as falsy, or dropped.
- The text element needs `children: []` of its own. A later assignment walks into every element's children and expects an array there.
- One child is an array of one. Do not unwrap it, even though React's own `createElement` does.
- The order in which you spread the given props and write `children` decides which one wins. `children` must come out of your code, not out of the caller's object.
- Assigning to the object you received feels like a shortcut and works until the same object is used twice. `show` is there to catch it.
- `key` is a normal prop here. Do not take it out, and do not give the element a third field.
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

[Pombo's version](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) is `createElement`, which returns `{ type, props }` with the given props spread first and `children` after them, and `createTextElement`, which builds the `TEXT_ELEMENT` node with `nodeValue` and an empty `children`. Whatever is not an object goes to `createTextElement`, so the post has the same two functions this page asks for. The post keeps all its code in one file under the name `Didact` and points JSX at `Didact.createElement` with a pragma comment. Here the two functions have a module of their own, and the app code calls `createElement` by hand, because the workbook has no build step.

The post tests `typeof child === "object"`, and values that the spec leaves out meet that test in two ways. `null` and arrays are objects, so they land in `children` as they are. `undefined` and the booleans are not objects, so they become text elements holding `undefined`, `false` or `true`. React renders nothing for `null`, `undefined` and the booleans, and it renders the items of an array. The tests pass none of them.

The post says that React itself neither wraps primitive children nor creates an empty array when there are none, and that Didact does both on purpose, to keep the later code simple. This assignment follows the post: `children` is `[]`, not missing, and a lone child sits in an array. (`React.createElement` stores a lone child as the child itself.) React also keeps `key` in a field of the element beside `props`; here it stays in `props`, because the reconciler of assignment 07 reads it there. [React today](docs/react-today.md) lists where React 19 departs from the posts; its row on keys is the closest to this.

[Jongeneel's `createElement`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=2.1%20The%20HTML%20syntax%20tree) returns another shape, `{ kind, tagname, props, childeren, key }` (`childeren` is his spelling), with the children in a field beside `props`. Three more of its choices matter to the tests. It runs `delete props.key` on the object it receives, and that object is also the `props` of the node, so the caller's props change and the key sits on the node instead of in `props`. It reads `props.key` without a guard, so `null` props throw. And it takes only nodes as children, with text going through a separate `createText` that turns its value into a string. R6 and R7, R5 and R3 catch them in that order.
