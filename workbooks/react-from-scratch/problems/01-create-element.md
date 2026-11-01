# 01 · Create elements

**Difficulty:** Easy · **Assignment** 1 of 12 · **Check:** `.\check 01`

**Tags**
- *Language:* [ES modules](#primer/js-modules) · [objects, spread and destructuring](#primer/js-objects) · [rest parameters and spread arguments](#primer/js-rest-spread) · [typeof](#primer/js-typeof) · [array methods](#primer/js-arrays) · [throw, try and catch](#primer/js-errors) · [async and await](#primer/js-async-await)
- *Library:* [the harness and scenario files](#primer/workbook-harness) · [process.argv and exit codes](#primer/node-process)
- *Concepts:* [elements and what JSX turns into](#primer/react-elements) · [React 19 against the posts](#primer/react-today)

## Read in the blog first

You can pass with this page alone. If you would rather meet Pombo's version first, read [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) up to the point where he starts naming the library. His animated code is his solution, so save it for after you pass. [Step Zero](https://pomb.us/build-your-own-react/#step-zero-review), the short review before it, shows what a JSX tag compiles to and is worth a minute if JSX is new to you.

## Learning material

- [ES modules: import and export](#primer/js-modules): `createElement.js` exports by name, and the entry program imports from it.
- [Objects, spread and destructuring](#primer/js-objects): an element is a plain object, and its props begin as a copy of the props you receive.
- [Rest parameters and spread arguments](#primer/js-rest-spread): after `props` come any number of arguments, and the children are those.
- [typeof and the types you meet](#primer/js-typeof): `typeof` is how you tell a string or a number from an element.
- [Array methods](#primer/js-arrays): children in, a different list of children out.
- [throw, try, catch and finally](#primer/js-errors): the starter throws `not implemented: ...` until you replace it, and the checker treats that as work not done yet, not as a crash.
- [async, await and top-level await](#primer/js-async-await): the entry program awaits the harness before it exits.
- [Install and check Node.js 26](#primer/node-install): your entry program runs under `node`.
- [process.argv, exit codes and node --check](#primer/node-process): `process.argv` is where the input path and the output path show up in the entry program.
- [The checker](#primer/workbook-check): the commands listed under Checking your solution.
- [The harness and scenario files](#primer/workbook-harness): `call`, `props` and `show`, the three kinds of scenario line.
- [Where the expected output comes from](#primer/workbook-oracle): here, a model written from the rules below and checked against `React.createElement` wherever the two agree.
- [py -P and Python 3.11](#primer/python-launcher): what you need to run the checker, which is a Python program.
- [Elements, and what JSX turns into](#primer/react-elements): the shape `createElement` returns, and why the app code writes its calls out by hand.
- [React 19 against the posts](#primer/react-today): where real React differs from the posts. You meet it again in the last section here.

## Source material

- Rodrigo Pombo, [Step I: The createElement Function](https://pomb.us/build-your-own-react/#step-i-the-createelement-function) and the review before it, [Step Zero](https://pomb.us/build-your-own-react/#step-zero-review)
- Wim Jongeneel, the part of [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=2.1%20The%20HTML%20syntax%20tree) on the HTML syntax tree, where his own element constructor appears
- React documentation: [createElement](https://react.dev/reference/react/createElement) and [Writing markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- MDN: [rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters) and [spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)

## Where this fits

Didact starts with the object everything else passes around: the DOM code, the fibers and the hooks all read `{ type, props }`. A slip in your version stays contained, because assignments 02 to 08 build their elements with the harness's copy of this function. Your `createElement` is first called by other code in 09, when the catalog's function components use it.

## The problem

Write `createElement`, the function a JSX tag compiles to. A scenario file says how to call it, and your program prints what comes back.

### Input

`node assignments/assignment_01_create_element.js <input-file> <output-file>` is the command line behind each test. The harness reads the input, makes the calls each line asks for, and writes the output. A scenario has three kinds of line:

| Line | What the harness does |
|---|---|
| `call <type> <props> [child ...]` | Calls `createElement(type, props, ...children)` and prints the result. `<type>` is a bare word or a JSON string. `<props>` is a JSON object, `null`, or `@name`, an object defined by a `props` line. A child is a JSON string, a JSON number, or `$k`, the element that the k-th `call` returned (counting from 1). |
| `props <name> <json>` | Stores a props object under `<name>` for later `@name` arguments. Prints nothing. |
| `show <name>` | Prints the stored object as it is now. |

`@name` passes the stored object itself. Nothing is copied, and every use of one name is the same object.

The entry program, `assignments/assignment_01_create_element.js`, is short. It imports your `createElement` and the harness's `runScenarioFile` (from `../harness/scenario.js`) and ends with `await runScenarioFile(process.argv[2], process.argv[3], { createElement })`, passing along the input and output paths from the command line. The Boilerplate gives it to you finished. Starting from scratch, write it first, because nothing runs without it.

`src/didact/createElement.js` exports two functions:

| Export | Meaning |
|---|---|
| `createElement(type, props, ...children)` | The one the scenario calls. |
| `createTextElement(text)` | Returns the text element for one string or number: type `"TEXT_ELEMENT"`, props `{ nodeValue: text, children: [] }`, with `nodeValue` as passed, so a number stays a number. The tests call only `createElement`; a text element shows up in the children it lands in. |

### Output

`call` prints one line, `element <k> <json>`, where `k` counts the calls so far, starting at 1. `show` prints `props <name> <json>`. Your code prints nothing itself. The harness writes the JSON, compact, with a few conventions:

- Keys are sorted by name at every level, which hides the order you built the object in.
- A space inside a string prints as `\u0020`, and a character outside ASCII as a `\uXXXX` escape.
- Numbers print the way JavaScript prints them, which turns the input `4.0` into `4`.

```
element 1 {"props":{"children":[],"id":"a"},"type":"div"}
props p {"id":"a"}
```

### What an element is

An element is an object with two fields, `type` and `props`. `type` is the first argument, untouched. `props` is a fresh object, never the one passed in, holding every key and value of the props you received, plus `children`.

Every call also builds a fresh `children` array, one entry per child argument, in the order given:

| Child argument | Entry in `children` |
|---|---|
| a string, including `""` | `{"type":"TEXT_ELEMENT","props":{"nodeValue":<the string>,"children":[]}}` |
| a number, including `0` | the same, with the number as `nodeValue` |
| an element | that element, unchanged |

A number keeps its type: the child `42` gives `nodeValue` 42, and the child `"42"` gives `nodeValue` `"42"`. No children means an empty array, and one child still means an array of one.

A `children` key in the props you receive counts for nothing. The array built from the child arguments replaces it, even when there are no child arguments and the result is `[]`.

Props of `null` act like an empty object. The object you receive, and everything inside it, comes out of your function as it went in. `key` is an ordinary prop: it stays in `props` with its value and shows up nowhere else on the element.

Children that are `null`, booleans, arrays or `undefined` are out of scope. No test passes them, so your function can do what it likes with them.

## Requirements

- **R1** An element has the fields `type` and `props` and no others. `type` is the first argument; `props` carries every key and value of the props that were given.
- **R2** `props.children` is an array holding the children in order: empty for none, one entry for one child. A `children` key in the given props is replaced by it.
- **R3** A string or number child becomes a text element whose `nodeValue` is the value as given, so a number stays a number and `0` and `""` count.
- **R4** An element given as a child sits in `children` unchanged, at the position where it was passed.
- **R5** Props of `null` act like `{}`.
- **R6** The call leaves the props you were given unmodified, however often the object is reused.
- **R7** `key` stays in `props` as an ordinary prop.
- **E2E** Several `call` lines that build a tree from the leaves up, the way an app does.

## Examples

### Example 1: text, an element, text (test `01-R4-interleaved`)

```
input:
call b null "bold"
call p null "a " $1 " b"

output:
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"bold"},"type":"TEXT_ELEMENT"}]},"type":"b"}
element 2 {"props":{"children":[{"props":{"children":[],"nodeValue":"a\u0020"},"type":"TEXT_ELEMENT"},{"props":{"children":[{"props":{"children":[],"nodeValue":"bold"},"type":"TEXT_ELEMENT"}]},"type":"b"},{"props":{"children":[],"nodeValue":"\u0020b"},"type":"TEXT_ELEMENT"}]},"type":"p"}
```

`$1` stands for whatever line 1 returned. In the second call it is the middle child, and it shows up in the output as line 1 printed it, between two text elements whose spaces the harness writes as `\u0020`. `"a "` and `" b"` keep those spaces. Don't trim.

### Example 2: a number is not a string (test `01-R3-numeric-string`)

```
input:
call p null "42" 42 "4.0" 4.0 "-7" -7

output:
element 1 {"props":{"children":[{"props":{"children":[],"nodeValue":"42"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":42},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"4.0"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":4},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":"-7"},"type":"TEXT_ELEMENT"},{"props":{"children":[],"nodeValue":-7},"type":"TEXT_ELEMENT"}]},"type":"p"}
```

Six children, three pairs, and in every pair the string keeps its quotes in the output while the number loses them. `"4.0"` and `4.0` is the odd pair: the string stays `"4.0"`, and the number comes back as `4` because that is how JavaScript prints it. Your code receives a number.

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

The `show` line is what this test is about. After three calls that all got the same object, `p` must still hold only `className` and `title`. An implementation that writes `children` onto the object it received shows it here.

## Constraints

Types are single words. Props are JSON objects or `null`. Numbers are finite and print the same in JSON and in JavaScript. A string child can hold any characters, spaces and quotes included. A scenario runs to 16 lines at most. The 48 tests cover each requirement's cases, then two longer scripted trees and nine seeded random ones (`-Fresh` gives nine new ones). A correct solution needs milliseconds. Each test may run for 10 seconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Start with the smallest scenario there is, the single line `call div null`. The output is one object with two fields. Get that right, then add a child, then a text child, then a props object. The tests have a case for every one of those steps.
</details>

<details><summary>Hint 2: the approach</summary>

Make the result's `props` a fresh object: copy the given props into it, then give it its own `children` field, so that a `children` key from the caller cannot survive. Turn the child arguments into a new array one at a time. An element stays itself and anything else goes through `createTextElement`. The copy does two jobs: the caller's object stays as it was, and `null` props turn into the same thing as an empty object.
</details>

<details><summary>Hint 3: the traps</summary>

- Do not turn a number child into a string. `0` is a child too, and a falsy filter drops it.
- A text element needs `children: []` of its own. The render in 03 walks into the children of every element, text elements included, and expects an array each time.
- One child is still an array of one. React's own `createElement` unwraps it; yours must not.
- Whichever is written later wins: the spread of the given props or your own `children`. The `children` in the result has to come from your code.
- Assigning to the object you received feels like a shortcut, and it holds until a scenario reuses the object. `show` is there for that case.
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
