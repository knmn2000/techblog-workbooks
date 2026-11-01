# JavaScript

The parts of the language that the starters and the assignments lean on, in the order you meet them. The code is recent JavaScript run by Node.js 26, with no build step and no JSX.

## ES modules: `import` and `export`
<!--
id: js-modules
also: import; export; module; require; CommonJS; default export; named export; type module; package.json
code: ^\s*(import|export)\b
-->
A module is a file with a scope of its own. Nothing in it is visible elsewhere unless the file says `export`, and nothing from another file is visible unless this one says `import`. An import picks a named export by its name. A file may also have one default export, which the importer can call anything.

```js
// shapes.js
export const sides = 4;
export function area(w, h) { return w * h; }
export default function describe() { return 'a rectangle'; }

// main.js
import describe, { area, sides as n } from './shapes.js';
import './setup.js'; // runs the file, takes nothing from it
```

Three details catch people who come from other languages. The specifier is a file path, and a relative one needs its extension: `'./shapes.js'`, not `'./shapes'`. Your project's `package.json` contains `"type": "module"`, which tells Node to read its `.js` files as modules. And a module runs once, the first time anything imports it, so the order of imports matters when a file does something as it loads.

Every assignment program starts with imports, and each file you write in `src/didact/` exports what later files import. `index.js` (assignment 04) ends with a default export of the `Didact` object plus a list of named ones, and `TodoApp.js` (12) renames on import with `createElement as h`.

Learn more:
- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [Node.js: ECMAScript modules](https://nodejs.org/api/esm.html)
- [MDN: import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import)

## Objects, spread and destructuring
<!--
id: js-objects
also: object literal; shorthand property; spread operator; destructuring; copy an object; Object.assign; dictionary; hash map; shallow copy
code: [(,=]\s*\{[^{}]*\}|\{\s*\.\.\.\w|\b(const|let|var)\s*\{[^}]*\}\s*=
-->
A JavaScript object is a bag of named properties, written `{ name: value }`. Elements, props, fibers and the shared state in this workbook are all plain objects, and three bits of syntax keep the code around them short.

Shorthand: when a variable already has the property's name, `{ render }` means `{ render: render }`. Spread: `{ ...a, x: 1 }` builds a new object that holds the own properties of `a` and then `x`. A later property overrides an earlier one with the same name, and the copy is shallow, so nested objects stay shared with the original. Destructuring goes the other way and pulls properties out into variables, either in a declaration, `const { id, text } = item`, or right in a parameter list.

```js
const base = { id: 7, tags: ['a'], done: false };
const next = { ...base, done: true };   // a new object; base is untouched
const { id, done } = next;              // id is 7, done is true
base.tags === next.tags;                // true: tags is shared, not copied
```

The entry programs hand your functions to the harness as `{ createElement }` or `{ createDom, updateDom }`, and the one in assignment 12 spreads the whole `Didact` object into a larger one. The copying half matters earlier, in 01: whenever an assignment must return a new object built from another and leave the other unchanged, you are choosing how to copy.

Learn more:
- [MDN: Object initializer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer)
- [MDN: Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)
- [MDN: Destructuring](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring)

## Rest parameters and spread arguments
<!--
id: js-rest-spread
also: ...args; variadic; varargs; spread operator; rest operator; arguments object; three dots
code: \(\s*(\w+\s*,\s*)*\.\.\.\w+\s*\)
-->
The same three dots do two jobs, depending on which side of a call they sit.

In a parameter list, `...name` collects every remaining argument into a real array. It has to come last, and the array is empty when no extra arguments arrive. At a call site, `f(...list)` does the reverse and passes the elements of `list` as separate arguments.

```js
function tag(name, ...kids) { return { name, kids }; }

tag('ul', 'a', 'b');        // kids: ['a', 'b']
tag('ul');                  // kids: [], still an array
const more = ['x', 'y'];
tag('ul', ...more, 'z');    // kids: ['x', 'y', 'z']
```

JSX is the reason this shows up. A tag with children, `<ul>{a}{b}</ul>`, compiles to a call that receives the children as extra arguments, so `createElement(type, props, ...children)` has to take any number of them. That signature is already in the Boilerplate of assignment 01; what to do with the array is the assignment. The spread half returns in 12, where an app has its children in a list and a call wants them one by one.

Learn more:
- [MDN: Rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters)
- [MDN: Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)

## `typeof` and the types you meet
<!--
id: js-typeof
also: type check; typeof null; primitive types; Array.isArray; is a string; is a number; dynamic typing
code: \btypeof\b
-->
JavaScript has no type declarations. Values carry their type, variables do not. The types you meet here are number (integers and fractions alike), string, boolean, `undefined`, `null`, function and object, where object covers plain objects, arrays and elements. `typeof x` hands back the name of the type as a string.

```js
typeof 'hi'          // 'string'
typeof 3.5           // 'number'
typeof {}            // 'object'
typeof [1, 2]        // 'object': arrays have no type name of their own
typeof (() => 1)     // 'function'
typeof undefined     // 'undefined'
typeof null          // 'object': a leftover of the first implementation, kept for compatibility
```

Two edges are worth remembering. A check for "some object" lets `null` through, so test for it with `=== null`, and use `Array.isArray(x)` when you need an array. On the plus side, `typeof` does not throw on a name that was not declared.

Assignment 01 hands `createElement` children of different kinds in a single list: strings, numbers and objects that are already elements. Telling them apart is yours to work out, and `typeof` is one of the candidates. In 09 an element's `type` stops being a string every time.

Learn more:
- [MDN: typeof](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/typeof)
- [MDN: Grammar and types](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types)

## Array methods: map, filter, forEach, find, includes, slice
<!--
id: js-arrays
also: list; array; push; pop; splice; indexOf; some; every; reduce; length; Array.from
code: \.(map|filter|forEach|find|findIndex|includes|slice|splice|push|pop|shift|unshift|some|every|reduce|concat|indexOf)\(
-->
An array is an ordered list, indexed from 0, with a `length`. Most of its methods take a function and call it once per element.

```js
const nums = [3, 8, 12];
nums.map((n) => n * 2);               // [6, 16, 24], a new array of the results
nums.filter((n) => n > 5);            // [8, 12], the elements the function accepted
nums.find((n) => n > 5);              // 8, the first one it accepted (or undefined)
nums.includes(8);                     // true, no function needed
nums.slice(1);                        // [8, 12], a copy from index 1 on
nums.forEach((n) => console.log(n));  // returns undefined: it exists for the side effect
```

`map`, `filter` and `slice` leave the array they are called on alone. `push`, `pop` and `splice` change it in place. If a library keeps an old tree around to compare with a new one, that difference decides whether the comparison still works.

You will reach for these in most assignments, though the Boilerplate calls none of them. An element's children are an array from 01 on (`props.children`), and a lot of the work is turning one list into another: children into DOM nodes (03), into fibers (04), a list of data into a list of elements (12).

Learn more:
- [MDN: Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Array.prototype.map()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map)
- [MDN: Indexed collections](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Indexed_collections)

## `throw`, `try`, `catch` and `finally`
<!--
id: js-errors
also: exception; raise; error handling; new Error; stack trace; not implemented; uncaught error; exit code 99
code: \bthrow\b|\btry\s*\{|\bcatch\b|\bfinally\b
-->
`throw` stops the current function and unwinds the call stack until some `catch` takes the error. If none does, the program prints a stack trace and exits with code 1. You can throw any value, but `new Error('message')` is the one to use because it records where it happened. A `finally` block runs whether the `try` block finished, threw or returned.

```js
function split(line) {
  if (line === '') throw new Error('empty line');
  return line.split(',');
}

try {
  split('');
} catch (err) {
  console.log(err.message);   // empty line
} finally {
  console.log('done');        // runs either way
}
```

Every function you write in this workbook starts as a stub that throws `new Error('not implemented: ...')`, and the harness gives that message a meaning. A thrown error whose text starts with `not implemented` ends the program with exit code 99, which the checker reports as "Not implemented yet" instead of a failure. Any other uncaught error becomes a Runtime Error, with the message next to it. If a test dies that way, read the stack trace from the top: the first line that names one of your files is where it happened.

The stubs sit in every Boilerplate file you create, from `createElement.js` in 01 on, and replacing one with real code is the job. Exit codes have an entry of their own, [exit codes and `node --check`](#primer/node-process).

Learn more:
- [MDN: throw](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/throw)
- [MDN: try...catch](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch)
- [MDN: Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error)

## `async`, `await` and top-level await
<!--
id: js-async-await
also: promise; Promise; then; asynchronous; top-level await; event loop; callback
code: \b(async|await)\b
-->
Reading a file, waiting on a timer or making a network request takes time, and JavaScript does not stop the world to wait. Such an operation returns a promise: an object standing for a result that arrives later. `await promise` pauses the surrounding function until the promise settles, then gives you the value, or throws if the operation failed. A function that uses `await` has to be declared `async`, and calling it returns a promise of its own.

In an ES module, `await` also works at the top level of the file, outside any function. The module then counts as unfinished until the promise settles.

```js
import { readFile } from 'node:fs/promises';

const text = await readFile('notes.txt', 'utf8');   // top level: no async function around it
console.log(text.length);
```

You will not write `async` or `await` in your own files. Each program in `assignments/` comes down to a single line of it, `await runScenarioFile(...)`, which reads the scenario, runs it against your library and writes the output file before the program ends. The library itself is synchronous and waits through scheduled callbacks, the subject of [requestIdleCallback](#primer/dom-idle-callback). One trap for the curious: a top-level `await` on a promise that cannot settle ends Node with status 13.

Learn more:
- [MDN: await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await)
- [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [Node.js: top-level await in ES modules](https://nodejs.org/api/esm.html)

## Arrow functions and closures
<!--
id: js-functions-closures
also: lambda; anonymous function; callback; fat arrow; =>; function expression; scope; lexical scope; handler
code: =>
-->
Two ways to write the same function:

```js
function add(a, b) { return a + b; }
const add2 = (a, b) => a + b;
```

An arrow function with an expression after `=>` returns that expression. With a `{ block }` body it needs an explicit `return`. To return an object literal, wrap it in parentheses, `() => ({ ok: true })`, or the parser reads the braces as a block. Arrow functions are the usual shape for callbacks, which is why you see them everywhere in array code.

A closure is a function that keeps access to the variables around the place where it was written, even after that outer code has finished running.

```js
function makeCounter() {
  let n = 0;
  return () => ++n;
}
const a = makeCounter();
const b = makeCounter();
a(); a(); b();   // 1, 2, 1: each counter has its own n
```

Handlers and setters are closures. A click handler written inside a component carries the values of the render that made it, and a setter handed out on a component's first render has to keep working on every later one; much of assignment 10 turns on that. The scenario files in the tests lean on the same thing from 02: their `onClick=@name` handlers are functions that append to a log, one function per name.

Learn more:
- [MDN: Arrow functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)

## `Object.keys`, `Object.entries`, `Object.hasOwn` and `in`
<!--
id: js-object-keys
also: iterate object; for in; property names; own property; has key; hasOwnProperty; Object.values; enumerate properties
code: \bObject\.(keys|entries|values|hasOwn|fromEntries)\b|\bfor\s*\(\s*(const|let|var)\s+\w+\s+in\b|\(\s*!?\s*(\w+|'[^']*'|"[^"]*")\s+in\s+\w+\s*\)
-->
To go through an object's properties you first need their names. `Object.keys(obj)` returns an array of the object's own property names, `Object.values(obj)` the values, and `Object.entries(obj)` an array of `[name, value]` pairs, which goes well with destructuring in a `for...of`. Own means set on the object itself, not inherited.

To ask whether a name is present there are two tests with different reach. `'k' in obj` is true for own and inherited properties alike (`'toString' in {}` is true). `Object.hasOwn(obj, 'k')` is true for own ones only. Both differ from `obj.k !== undefined`, because a property can exist and hold `undefined`.

```js
const props = { id: 'x', title: undefined };
Object.keys(props);               // ['id', 'title']
Object.entries(props);            // [['id', 'x'], ['title', undefined]]
'title' in props;                 // true
props.title !== undefined;        // false: present, but its value is undefined
Object.hasOwn(props, 'id');       // true
```

Assignment 02 is where this arrives. `updateDom` receives two props objects, so it needs the names in each and a way to ask whether one has a name the other lacks.

Learn more:
- [MDN: Object.keys()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/keys)
- [MDN: Object.hasOwn()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn)
- [MDN: the in operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/in)

## `===`, `Object.is`, truthy and falsy
<!--
id: js-equality
also: strict equality; loose equality; ==; !==; NaN; falsy values; truthiness; identity; null vs undefined; SameValue
code: [!=]==|\bObject\.is\s*\(|\s(==|!=)\s
-->
`===` compares two values without converting either: `1 === '1'` is false. `==` converts first and produces results like `0 == ''` being true, so leave it alone, with one exception below. Objects and functions compare by identity: two separate `{}` are not `===` to each other, and a function equals only itself, whatever its body.

`Object.is(a, b)` is `===` with two corrections: `Object.is(NaN, NaN)` is true, and `Object.is(0, -0)` is false. React compares a hook's dependency list with it, entry by entry, which matters in assignment 11.

Truthiness decides what `if (x)`, `x && y` and `x || y` do. The falsy values are `false`, `0`, `-0`, `0n`, `''`, `null`, `undefined` and `NaN`. Everything else is truthy, including `'0'`, `[]` and `{}`. That is a trap whenever a falsy value is also a legitimate one:

```js
const label = '';
label || 'untitled';     // 'untitled', although '' was a valid value
label ?? 'untitled';     // '': only null and undefined count as missing
label === undefined;     // false
```

If the question is whether something is there, ask it in those words, with `=== undefined` or `== null` (the one use of `==` worth knowing: it is true for `null` and `undefined` and for nothing else), and keep truthiness for the cases where you want it. The `??` operator has an [entry of its own](#primer/js-optional-chaining). Comparing old and new props in 02, deciding what counts as a key in 07 and comparing dependency lists in 11 all come down to the rules on this page.

Learn more:
- [MDN: Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Equality_comparisons_and_sameness)
- [MDN: Falsy](https://developer.mozilla.org/en-US/docs/Glossary/Falsy)

## `for`, `for...of` and `while`
<!--
id: js-loops
also: loop; iterate; for each; do while; break; continue; for in; index loop; linked list traversal
code: \b(for|while)\s*\(|\bdo\s*\{
-->
The counting loop has three parts in its parentheses: setup, condition, step. `while (cond)` has only the condition, and may run zero times. `for (const x of list)` visits the values of an array, a string, a `Map` or a `Set`; a plain object is not iterable, so feed it through `Object.entries` first. Its lookalike `for (const k in obj)` visits property names, inherited ones too, and is best left alone. `break` leaves the loop and `continue` jumps to the next round.

```js
for (let i = 0; i < 3; i++) console.log(i);         // 0 1 2
for (const word of ['a', 'b']) console.log(word);   // a b
let n = 10;
while (n > 1) n = Math.floor(n / 2);                // repeats until the condition fails
```

A loop also walks structures that have no index. Following a `next` link until the chain ends is `for (let node = head; node; node = node.next)`: the setup picks a start, the step moves along a link, and the condition is the link itself.

The Boilerplate has no loops, and several assignments need them. Assignment 03 walks a tree whose children sit in arrays. 04 does work "until there is none left or the time is up", which does not fit a counting loop. 05 visits every piece of a finished tree.

Learn more:
- [MDN: Loops and iteration](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration)
- [MDN: for...of](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of)

## Optional chaining `?.` and `??`
<!--
id: js-optional-chaining
also: null check; nullish coalescing; safe navigation; elvis operator; default value; ??=; undefined property
code: \?\.(?=[\w\[(])|\?\?
-->
Reading a property of `undefined` or `null` throws a TypeError. `a?.b` reads `b` only when `a` is neither, and otherwise gives `undefined` and skips the rest of the chain. It comes in three forms: `a?.b`, `a?.[key]` and `f?.()`. `a ?? b` gives `b` only when `a` is `null` or `undefined`. That differs from `a || b`, where `0` and the empty string fall through to `b` as well. `a ??= b` assigns only if `a` is null or undefined.

```js
const user = { profile: null };
user.profile?.name;               // undefined, no error
user.profile?.name ?? 'anon';     // 'anon'

const score = 0;
score || 10;                      // 10, probably not what you meant
score ?? 10;                      // 0
```

Trees and linked structures have missing links. At the end of the work there is no next fiber (04), and from 06 on, with the library comparing each render to the one before, the first render has nothing to compare with. A chain of lookups that can fall off the end is where `?.` earns its place, and `??` supplies the value to use when it does.

Learn more:
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

## `Map` and `Set`
<!--
id: js-maps-sets
also: dictionary; hash map; hash table; unique values; lookup by key; Map.get; Set.has; groupBy
code: \bnew\s+(Map|Set|WeakMap|WeakSet)\b|\bMap\.groupBy\b
-->
A plain object works as a lookup table when the keys are strings, with two catches. It starts out with inherited names (`'constructor' in {}` is true), and an object turns every key into a string, so `1` and `'1'` land on the same entry. `Map` has neither problem. It takes any value as a key, compares keys like `===` (except that `NaN` equals `NaN`, and objects match by identity), remembers insertion order and has a `size`. `Set` does the same for lone values and stores each one once.

```js
const seen = new Map();
seen.set('a', 1).set('b', 2);
seen.get('a');                    // 1
seen.get('z');                    // undefined
seen.has('b');                    // true
seen.delete('b');
for (const [key, value] of seen) console.log(key, value);   // a 1

const ids = new Set(['a', 'b', 'a']);
ids.size;                         // 2
ids.has('a');                     // true
```

A lookup by key does not scan: it costs about the same however many entries there are, where searching an array takes longer as the array grows.

Assignment 07 is where they enter the picture: you have to find children by their key rather than by where they stand, in lists that can be long.

Learn more:
- [MDN: Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [MDN: Set](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)

## String methods: `startsWith`, `slice`, `toLowerCase`
<!--
id: js-string-methods
also: substring; template literal; string; trim; split; uppercase; lowercase; prefix; case
code: \.(startsWith|endsWith|toLowerCase|toUpperCase|substring|substr|trim|trimStart|trimEnd|split|replace|replaceAll|padStart|padEnd|charAt)\(
-->
Strings are immutable: every method returns a new string and leaves the original as it was. Indexes start at 0, and `s.length` counts UTF-16 units, so an emoji counts as two.

```js
const file = 'Report.Final.PDF';
file.startsWith('Rep');                    // true, and case sensitive
file.toLowerCase();                        // 'report.final.pdf'
file.slice(7);                             // 'Final.PDF', from index 7 on
file.slice(0, 6);                          // 'Report': the end index is excluded
file.slice(-3);                            // 'PDF': a negative index counts from the end
file.toLowerCase().endsWith('.pdf');       // true
const msg = `${3} items`;                  // a template literal: backticks with ${} holes
```

`substring` is the older relative of `slice`. It treats negative indexes as 0 and swaps its arguments when they come in the wrong order, which is why most people reach for `slice` instead.

Assignment 02 is where strings start to carry meaning: a prop's name says whether it is an event handler, and the DOM spells the event's name in another way. The page gives the rules, and these methods are the usual tools for applying them.

Learn more:
- [MDN: String](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)
- [MDN: String.prototype.startsWith()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/startsWith)
- [MDN: String.prototype.slice()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/slice)

## Module-level state and why `state.js` is an object
<!--
id: js-global-state
also: global variable; shared state; singleton; live binding; let export; reassign import; mutable module state; Assignment to constant variable
code: \bexport\s+(const|let)\s+state\b|\bimport\s*\{[^}]*\bstate\b[^}]*\}\s*from
-->
A variable declared at the top of a module belongs to that module and lives as long as the program does. Every function in the file can read and change it, so a `let count = 0` at the top is the simplest global state there is.

Sharing it with other files needs a closer look. After `export let count = 0`, other modules can read `count` and see its current value, because an import is a live view of the exporter's variable. They cannot assign to it: `count = 5` in the importing file throws `TypeError: Assignment to constant variable`. Only the module that declares a variable may reassign it.

A value that several files must replace, such as which piece of work comes next, cannot be a bare export. Export an object instead and let every file assign to its properties. The binding stays put while the properties change, and each file sees the change.

```js
// counter.js
export const counter = { value: 0 };

// a.js
import { counter } from './counter.js';
counter.value++;

// b.js
import { counter } from './counter.js';
console.log(counter.value);   // sees the change from a.js
```

`state.js` is that object. You create it in assignment 04, where the Boilerplate gives the empty `export const state = {}` and the page lists the fields. `render.js` and `commit.js` import it from 04 and 05 on, `hooks.js` joins them in 10, and later assignments add fields to it as the library grows.

Learn more:
- [MDN: import (live bindings)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import)
- [MDN: export](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export)
