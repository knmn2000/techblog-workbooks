# JavaScript

The slice of the language the starters and assignments lean on, roughly in the order you hit it. It's recent JavaScript on Node.js 26, with no build step and no JSX.

## ES modules: `import` and `export`
<!--
id: js-modules
also: import; export; module; require; CommonJS; default export; named export; type module; package.json
code: ^\s*(import|export)\b
-->
A module is a file with a scope of its own. Nothing in it is visible elsewhere unless the file says `export`, and nothing from another file is visible until this one says `import`. An import picks a named export by name. A file may also have one default export, and the importer can call that anything it likes.

```js
// shapes.js
export const sides = 4;
export function area(w, h) { return w * h; }
export default function describe() { return 'a rectangle'; }

// main.js
import describe, { area, sides as n } from './shapes.js';
import './setup.js'; // runs the file, takes nothing from it
```

Three details catch people who come from other languages. The specifier is a file path. A relative one needs its extension: `'./shapes.js'`, not `'./shapes'`. Your project's `package.json` contains `"type": "module"`, which tells Node to read its `.js` files as modules. And a module runs once, the first time anything imports it, so import order matters when a file does something as it loads.

Every assignment program opens with imports, and every file you write in `src/didact/` exports something another one imports. `index.js` (assignment 04) ends with a default export of the `Didact` object plus a list of named ones. `TodoApp.js` (12) renames on import with `createElement as h`.

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
Elements, props, fibers and the library's shared state are all plain JavaScript objects: bags of named properties, written `{ name: value }`. Three bits of syntax keep the code around them short.

Shorthand first. When a variable already has the property's name, `{ render }` means `{ render: render }`. Spread, `{ ...a, x: 1 }`, builds a new object from the own properties of `a` and then `x`. If a name repeats, the later property wins, and the copy is shallow, so nested objects stay shared with the original. Destructuring runs the other way, pulling properties out into variables, either in a declaration (`const { id, text } = item`) or right in a parameter list.

```js
const base = { id: 7, tags: ['a'], done: false };
const next = { ...base, done: true };   // a new object; base is untouched
const { id, done } = next;              // id is 7, done is true
base.tags === next.tags;                // true: tags is shared, not copied
```

The entry programs hand your functions to the harness as `{ createElement }` or `{ createDom, updateDom }`, and the one for assignment 12 spreads the whole `Didact` object into a larger one. The copying half bites sooner, in 01: any time an assignment wants a new object built from another, with the other left unchanged, you are choosing how to copy.

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
Three dots, two jobs. Which one you get depends on where they sit.

In a parameter list, `...name` collects the remaining arguments into a real array. It has to come last, and when no extra arguments arrive the array is empty. At a call site, `f(...list)` does the reverse: the elements of `list` go in as separate arguments.

```js
function tag(name, ...kids) { return { name, kids }; }

tag('ul', 'a', 'b');        // kids: ['a', 'b']
tag('ul');                  // kids: [], still an array
const more = ['x', 'y'];
tag('ul', ...more, 'z');    // kids: ['x', 'y', 'z']
```

JSX is why it comes up. A tag with children, `<ul>{a}{b}</ul>`, compiles to a call that gets the children as extra arguments, so `createElement(type, props, ...children)` has to take any number of them. The Boilerplate of assignment 01 already has that signature; deciding what to do with the array is the assignment. Spread comes back in 12, where the app has its children in a list and the call wants them one by one.

Learn more:
- [MDN: Rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters)
- [MDN: Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)

## `typeof` and the types you meet
<!--
id: js-typeof
also: type check; typeof null; primitive types; Array.isArray; is a string; is a number; dynamic typing
code: \btypeof\b
-->
JavaScript has no type declarations. Values carry their type; variables don't. You will meet number (integers and fractions alike), string, boolean, `undefined`, `null`, function and object, with object covering plain objects, arrays and elements. `typeof x` returns the type's name as a string.

```js
typeof 'hi'          // 'string'
typeof 3.5           // 'number'
typeof {}            // 'object'
typeof [1, 2]        // 'object': arrays have no type name of their own
typeof (() => 1)     // 'function'
typeof undefined     // 'undefined'
typeof null          // 'object': a leftover of the first implementation, kept for compatibility
```

Two edges to remember. A check for "some object" lets `null` through, so test `=== null` separately, and reach for `Array.isArray(x)` when you need an array. In its favour, `typeof` doesn't throw on a name that was never declared.

Assignment 01 hands `createElement` children of several kinds in one list: strings, numbers and objects that are already elements. Telling them apart is your job, and `typeof` is one candidate. By 09 an element's `type` is no longer always a string.

Learn more:
- [MDN: typeof](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/typeof)
- [MDN: Grammar and types](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types)

## Array methods: map, filter, forEach, find, includes, slice
<!--
id: js-arrays
also: list; array; push; pop; splice; indexOf; some; every; reduce; length; Array.from
code: \.(map|filter|forEach|find|findIndex|includes|slice|splice|push|pop|shift|unshift|some|every|reduce|concat|indexOf)\(
-->
An array is an ordered list indexed from 0, with a `length`. Most of its methods take a function and call it once per element.

```js
const nums = [3, 8, 12];
nums.map((n) => n * 2);               // [6, 16, 24], a new array of the results
nums.filter((n) => n > 5);            // [8, 12], the elements the function accepted
nums.find((n) => n > 5);              // 8, the first one it accepted (or undefined)
nums.includes(8);                     // true, no function needed
nums.slice(1);                        // [8, 12], a copy from index 1 on
nums.forEach((n) => console.log(n));  // returns undefined: it exists for the side effect
```

`map`, `filter` and `slice` leave the array alone; `push`, `pop` and `splice` change it in place. When a library keeps an old tree around to compare with a new one, that difference decides whether the comparison still works.

Most assignments will have you reaching for these, even though the Boilerplate calls none of them. An element's children are an array from 01 on (`props.children`), and a lot of the work is turning one list into another: children into DOM nodes (03) or fibers (04), a list of data into a list of elements (12).

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
`throw` stops the current function and unwinds the call stack until some `catch` takes the error. If nothing does, the program prints a stack trace and exits with code 1. Any value can be thrown, but use `new Error('message')`, which records where it happened. A `finally` block runs whether the `try` block finished, threw or returned.

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

Every function you write in this workbook starts as a stub that throws `new Error('not implemented: ...')`, and the harness gives that message a meaning. An error whose text starts with `not implemented` ends the program with exit code 99, which the checker reports as "Not implemented yet" instead of a failure. Any other uncaught error becomes a Runtime Error, with its message beside it. If a test dies that way, read the stack trace from the top: the first line that names one of your files is where it happened.

You'll find the stubs in every Boilerplate file, from `createElement.js` in 01 on, and replacing them is the work. Exit codes get their own entry: [exit codes and `node --check`](#primer/node-process).

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
Reading a file, waiting on a timer or making a network request takes time, and JavaScript doesn't stop the world to wait. Such an operation returns a promise, an object standing for a result that arrives later. `await promise` pauses the surrounding function until the promise settles, then hands you the value, or throws if the operation failed. A function that uses `await` must be declared `async`, and calling it returns a promise of its own.

In an ES module, `await` also works at the top level of the file, outside any function. The module then counts as unfinished until the promise settles.

```js
import { readFile } from 'node:fs/promises';

const text = await readFile('notes.txt', 'utf8');   // top level: no async function around it
console.log(text.length);
```

You won't write `async` or `await` in your own files. Each program in `assignments/` boils down to one line of it, `await runScenarioFile(...)`, which reads the scenario, runs it against your library and writes the output file before the program ends. The library itself is synchronous and waits through scheduled callbacks, which is the subject of [requestIdleCallback](#primer/dom-idle-callback). One trap for the curious: a top-level `await` on a promise that can never settle ends Node with status 13.

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

An arrow function with an expression after `=>` returns that expression. With a `{ block }` body it needs an explicit `return`. To return an object literal, wrap it in parentheses, `() => ({ ok: true })`, or the parser takes the braces for a block. Arrows are the usual shape for callbacks, which is why you see them throughout array code.

A closure is a function that keeps access to the variables around where it was written, even after the outer code has finished running.

```js
function makeCounter() {
  let n = 0;
  return () => ++n;
}
const a = makeCounter();
const b = makeCounter();
a(); a(); b();   // 1, 2, 1: each counter has its own n
```

Handlers and setters are closures. A click handler written inside a component carries the values from the render that made it, and a setter handed out on a component's first render has to keep working on every render after; much of assignment 10 turns on that. The scenario files in the tests lean on closures from 02 on: each `onClick=@name` handler is a function that appends to a log, one function per name.

Learn more:
- [MDN: Arrow functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)

## `Object.keys`, `Object.entries`, `Object.hasOwn` and `in`
<!--
id: js-object-keys
also: iterate object; for in; property names; own property; has key; hasOwnProperty; Object.values; enumerate properties
code: \bObject\.(keys|entries|values|hasOwn|fromEntries)\b|\bfor\s*\(\s*(const|let|var)\s+\w+\s+in\b|\(\s*!?\s*(\w+|'[^']*'|"[^"]*")\s+in\s+\w+\s*\)
-->
`updateDom` in assignment 02 gets two props objects. It needs the names in each, and a way to ask whether one has a name the other lacks.

Going through an object's properties starts with their names. `Object.keys(obj)` returns an array of the object's own property names, `Object.values(obj)` the values, and `Object.entries(obj)` an array of `[name, value]` pairs, which pairs well with destructuring in a `for...of`. Own means set on the object itself rather than inherited.

Asking whether a name is present can be done two ways, and they reach differently. `'k' in obj` is true for own and inherited properties alike (`'toString' in {}` is true). `Object.hasOwn(obj, 'k')` is true for own ones only. Neither matches `obj.k !== undefined`, because a property can exist and hold `undefined`.

```js
const props = { id: 'x', title: undefined };
Object.keys(props);               // ['id', 'title']
Object.entries(props);            // [['id', 'x'], ['title', undefined]]
'title' in props;                 // true
props.title !== undefined;        // false: present, but its value is undefined
Object.hasOwn(props, 'id');       // true
```

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
`===` compares two values without converting either, so `1 === '1'` is false. `==` converts first and gives results such as `0 == ''` being true; leave it alone, with one exception below. Objects and functions compare by identity: two separate `{}` are not `===` to each other, and a function equals only itself, whatever its body.

A variant, `Object.is(a, b)`, is `===` with two corrections: `Object.is(NaN, NaN)` is true and `Object.is(0, -0)` is false. React compares a hook's dependency list with it, entry by entry. That matters in assignment 11.

Truthiness decides what `if (x)`, `x && y` and `x || y` do. The falsy values are `false`, `0`, `-0`, `0n`, `''`, `null`, `undefined` and `NaN`. Everything else is truthy, `'0'`, `[]` and `{}` included. That's a trap whenever a falsy value is also a legitimate one:

```js
const label = '';
label || 'untitled';     // 'untitled', although '' was a valid value
label ?? 'untitled';     // '': only null and undefined count as missing
label === undefined;     // false
```

If the question is whether something is there, ask it in those words, with `=== undefined` or `== null` (the one use of `==` worth knowing: it is true for `null` and `undefined` and for nothing else), and keep truthiness for when you want it. `??` has an [entry of its own](#primer/js-optional-chaining). Comparing old and new props in 02, deciding what counts as a key in 07 and comparing dependency lists in 11 all come down to these rules.

Learn more:
- [MDN: Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Equality_comparisons_and_sameness)
- [MDN: Falsy](https://developer.mozilla.org/en-US/docs/Glossary/Falsy)

## `for`, `for...of` and `while`
<!--
id: js-loops
also: loop; iterate; for each; do while; break; continue; for in; index loop; linked list traversal
code: \b(for|while)\s*\(|\bdo\s*\{
-->
The counting loop has three parts in its parentheses: setup, condition, step. `while (cond)` has only the condition and may run zero times. `for (const x of list)` visits the values of an array, a string, a `Map` or a `Set`. A plain object isn't iterable, so feed it through `Object.entries` first. Its lookalike `for (const k in obj)` visits property names, inherited ones too, and is best left alone. `break` leaves the loop, `continue` jumps to the next round.

```js
for (let i = 0; i < 3; i++) console.log(i);         // 0 1 2
for (const word of ['a', 'b']) console.log(word);   // a b
let n = 10;
while (n > 1) n = Math.floor(n / 2);                // repeats until the condition fails
```

Loops also walk structures with no index. Following `next` links until the chain ends is `for (let node = head; node; node = node.next)`: the setup picks a start, the step moves along a link, and the condition is the link itself.

The Boilerplate has no loops. Several assignments need them. Assignment 03 walks a tree whose children sit in arrays. 04 works "until there is none left or the time is up", which a counting loop doesn't fit. 05 visits every piece of a finished tree.

Learn more:
- [MDN: Loops and iteration](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration)
- [MDN: for...of](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of)

## Optional chaining `?.` and `??`
<!--
id: js-optional-chaining
also: null check; nullish coalescing; safe navigation; elvis operator; default value; ??=; undefined property
code: \?\.(?=[\w\[(])|\?\?
-->
A property read on `undefined` or `null` throws a TypeError. `a?.b` reads `b` only when `a` is neither; otherwise it gives `undefined` and skips the rest of the chain. It comes in three forms: `a?.b`, `a?.[key]` and `f?.()`. `a ?? b` gives `b` only when `a` is `null` or `undefined`, which differs from `a || b`, where `0` and the empty string fall through to `b` too. `a ??= b` assigns only if `a` is null or undefined.

```js
const user = { profile: null };
user.profile?.name;               // undefined, no error
user.profile?.name ?? 'anon';     // 'anon'

const score = 0;
score || 10;                      // 10, probably not what you meant
score ?? 10;                      // 0
```

Trees and linked structures have missing links. At the end of the work there is no next fiber (04), and from 06 on, when the library compares each render with the one before, the first render has nothing to compare with. A chain of lookups that can fall off the end is where `?.` pays off, and `??` supplies the value to use when it does.

Learn more:
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

## `Map` and `Set`
<!--
id: js-maps-sets
also: dictionary; hash map; hash table; unique values; lookup by key; Map.get; Set.has; groupBy
code: \bnew\s+(Map|Set|WeakMap|WeakSet)\b|\bMap\.groupBy\b
-->
Assignment 07 has to find children by key rather than by where they stand, in lists that can be long. A plain object works as a lookup table when the keys are strings, with two catches. It starts out with inherited names (`'constructor' in {}` is true), and it turns every key into a string, so `1` and `'1'` land on the same entry. `Map` has neither problem. Any value can be a key, keys compare like `===` (except that `NaN` equals `NaN`, and objects match by identity), insertion order is remembered, and there is a `size`. `Set` does the same for lone values and stores each one once.

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

A lookup by key doesn't scan. It costs about the same whatever the number of entries, while searching an array takes longer as the array grows.

Learn more:
- [MDN: Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [MDN: Set](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)

## String methods: `startsWith`, `slice`, `toLowerCase`
<!--
id: js-string-methods
also: substring; template literal; string; trim; split; uppercase; lowercase; prefix; case
code: \.(startsWith|endsWith|toLowerCase|toUpperCase|substring|substr|trim|trimStart|trimEnd|split|replace|replaceAll|padStart|padEnd|charAt)\(
-->
Strings start to carry meaning in assignment 02: a prop's name says whether it is an event handler, and the DOM spells the event's name another way. The page gives the rules; these methods are the usual tools for applying them.

Strings are immutable. Every method returns a new string and leaves the original alone. Indexes start at 0, and `s.length` counts UTF-16 units, so an emoji counts as two.

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

The older `substring` treats negative indexes as 0 and swaps its arguments when they come in the wrong order, which is why most people reach for `slice`.

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
A variable declared at the top of a module belongs to that module and lives as long as the program does. Every function in the file can read and change it, so `let count = 0` at the top is the simplest global state there is.

Sharing it with other files is where it gets fiddly. After `export let count = 0`, other modules can read `count` and see its current value, because an import is a live view of the exporter's variable. They can't assign to it. `count = 5` in the importing file throws `TypeError: Assignment to constant variable`. Only the module that declares a variable may reassign it.

That rules out a bare export for a value that several files must replace, such as which piece of work comes next. Export an object and let every file assign to its properties. The binding stays put while the properties change, and each file sees the change.

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

The `state.js` file is that object, created in assignment 04, where the Boilerplate gives you the empty `export const state = {}` and the page lists the fields. `render.js` and `commit.js` import it from 04 and 05 on, `hooks.js` from 10, and it picks up more fields as the library grows.

Learn more:
- [MDN: import (live bindings)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import)
- [MDN: export](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export)
