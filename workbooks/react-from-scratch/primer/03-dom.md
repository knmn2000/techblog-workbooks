# The DOM

The DOM is the browser's live model of a page, a tree of objects that scripts read and change, and it's what your library ends up drawing into. The tests run on a small DOM of the workbook's own, `harness/minidom.js`. For every call the assignments make it behaves like a browser, and like jsdom, where React runs to produce the expected outputs. Where it does less on purpose, the entry says so.

## The DOM tree: elements and text nodes
<!--
id: dom-tree
also: Document Object Model; DOM; node; element node; text node; nodeType; parentNode; childNodes; nextSibling; getElementById; container; root
code: \bdocument\.getElementById\s*\(
-->
To a script, a page is a tree of objects: the DOM. Each item is a node. Two kinds matter here. An element node stands for a tag such as `<div>` or `<button>`. A text node holds the characters between tags and has no tag, no props and no children. In `<p>Hi <b>you</b></p>` the `p` has two children, the text `"Hi "` and the `b`, and the `b` has one, the text `"you"`.

Nodes know their surroundings through `parentNode`, `childNodes`, `firstChild`, `lastChild`, `nextSibling` and `previousSibling`. `nodeType` is 1 for an element and 3 for a text node. To find an element already on the page, ask the document. `document.getElementById("box")` returns it, or `null`.

```js
// page: <div id="box"><p>Hi <b>you</b></p></div>
const p = document.getElementById("box").firstChild;
console.log(p.childNodes.length);          // 2
console.log(p.firstChild.nodeType);        // 3, the text "Hi "
console.log(p.lastChild.parentNode === p); // true
```

Making nodes starts in assignment 02, and in 03 you fill a container with a whole tree of them. Every test ends by dumping that tree: one `node` line per element with its depth, one `text` line per run of text (neighbouring text nodes print as one), and a label that stays with the same node across dumps. The container is a `<div id="root">` the harness puts in `body`. minidom has the reads above plus `contains`, `remove` and `getElementById`. It has no `querySelector` or `innerHTML`, and nothing in the workbook calls for either. A browser and jsdom answer the same reads the same way.

Learn more:
- [MDN: Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [MDN: Node](https://developer.mozilla.org/en-US/docs/Web/API/Node)
- [The DOM Standard](https://dom.spec.whatwg.org/)

## `createElement` and `createTextNode`
<!--
id: dom-create
also: document.createElement; document.createTextNode; make a node; new element; new text node; tagName; localName
code: \bdocument\.create(?:Element|TextNode)\s*\(
-->
`document.createElement("li")` makes an element node and `document.createTextNode("Buy milk")` makes a text node holding that string. Neither puts anything on the page. A new node has no parent and, if it's an element, no content, and it stays invisible until you attach it under a node on the page (see [appendChild and friends](#primer/dom-tree-editing)).

Tag names are case-insensitive in an HTML document: `createElement("LI")` makes the same element, whose `tagName` reads `"LI"` and whose `localName` reads `"li"`. The text you give `createTextNode` is plain text, so a `<` in it stays a character and isn't parsed as a tag.

```js
const li = document.createElement("li");
const label = document.createTextNode("Buy milk");
console.log(li.parentNode, li.childNodes.length); // null 0
li.appendChild(label);
console.log(li.textContent);                      // "Buy milk"
```

`createDom` in assignment 02 has to return an element node or a text node for each element it receives; the page names the type that marks a text element. Later renders call it once per node. The harness's `ops` command prints how many `create` calls happened, and from 06 on that count tells a node you kept from one you rebuilt. minidom's two functions follow the browser: `createElement` takes any tag string, an unknown one included, and `createTextNode` turns its argument into a string.

Learn more:
- [MDN: Document.createElement()](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement)
- [MDN: Document.createTextNode()](https://developer.mozilla.org/en-US/docs/Web/API/Document/createTextNode)

## Properties and attributes: `id`, `className`, `value`, `nodeValue`
<!--
id: dom-properties
also: attribute; property; IDL attribute; content attribute; setAttribute; getAttribute; className; class; nodeValue; textContent; data; title; disabled
-->
HTML source has attributes. The DOM has properties. A tag such as `<a id="home" class="nav" title="Home">` becomes an object, and a script changes it by plain assignment: `a.id = "x"`. Many properties mirror an attribute, some under another name. The attribute `class` is the property `className`, because `class` is a keyword in many languages that drive the DOM. `getAttribute` and `setAttribute` are a separate API for the markup side.

`id`, `className` and `title` stay in step with their attributes. `value` doesn't: an input's `value` property holds the text as it stands now, while its `value` attribute only supplies the starting text. A made-up property such as `a.foo = 1` is an ordinary JavaScript property and doesn't reach the markup.

Text nodes keep their characters in `nodeValue` (the same string is in `data`). On an element `nodeValue` is `null`, and assigning to it does nothing.

```js
const a = document.createElement("a");
a.className = "nav";
a.title = "Home";             // the tooltip, unrelated to document.title
const t = document.createTextNode("old");
t.nodeValue = "new";          // rewrites the text in place
```

An element's props land on a DOM node in assignment 02, and the page lists which names count. The dump prints `className`, `disabled`, `id`, `title` and `value`, each only for the tags where it means something, and `nodeValue` shows as a `text` line. Those are the prop lines a test can see. minidom gives the five a default (`""`, and `false` for `disabled`), accepts any other property you assign, and counts each assignment as a `write` in `ops`. It has no `setAttribute`, no `style` and no `innerHTML`, and no assignment calls for them. jsdom agrees on all five.

Learn more:
- [MDN: HTML attribute reference, content versus IDL attributes](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes)
- [MDN: Element.className](https://developer.mozilla.org/en-US/docs/Web/API/Element/className)
- [MDN: Node.nodeValue](https://developer.mozilla.org/en-US/docs/Web/API/Node/nodeValue)

## Listeners, event types and bubbling
<!--
id: dom-events
also: addEventListener; removeEventListener; event handler; event listener; click; bubbling; propagation; target; currentTarget; dispatchEvent; onclick
code: \.(?:add|remove)EventListener\s*\(
-->
Listeners are functions the browser calls when something happens to a node. `node.addEventListener("click", fn)` registers `fn` for events of type `"click"`, and `node.removeEventListener("click", fn)` takes it off again. Removal matches on type and on function identity. The function you remove has to be the object you added: two arrows with identical bodies are two functions. Adding one function twice for one type registers it once. Event types are lower-case words such as `"click"`, `"input"` and `"submit"`, with no `on` in front.

The listener receives an event object. `event.target` is the node where the event started; `event.currentTarget` is the node whose listener is running now. Most events then bubble: once the target's listeners have run, the same event goes to its parent's listeners, then the grandparent's, up to the top of the tree. One listener on a `<ul>` hears the clicks of every `<li>` and button below it.

```js
const list = document.createElement("ul");
const item = list.appendChild(document.createElement("li"));
list.addEventListener("click", (e) => console.log(e.target === item, e.currentTarget === list));
item.dispatchEvent(new Event("click", { bubbles: true })); // true true
```

Handlers get attached in assignment 02, whose page gives the rule for which props are handlers and which event type each becomes. The tests click a node by id and read what the handlers logged. From 06 the handlers change between renders, and `ops` prints the `addListener` and `removeListener` counts. minidom has `addEventListener` and nothing else. There are no `onclick` property handlers, so `node.onclick = fn` is an ordinary property that does nothing when a click arrives. `click` and `submit` events are cancelable and `input` is not. Browsers and jsdom agree on all of it.

Learn more:
- [MDN: EventTarget.addEventListener()](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN: EventTarget.removeEventListener()](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener)
- [MDN: Event bubbling](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Event_bubbling)

## `appendChild`, `insertBefore`, `removeChild`
<!--
id: dom-tree-editing
also: append; insert; remove; move a node; replaceChild; remove(); nextSibling; parentNode; reorder; placement; deletion
code: \.(?:appendChild|insertBefore|removeChild|replaceChild)\s*\(
-->
A freshly made node is nowhere. Three calls arrange nodes after that. `parent.appendChild(node)` makes `node` the last child of `parent`. `parent.insertBefore(node, ref)` puts it before `ref`, which has to be a child of `parent`; with `null` as `ref` it appends, and the call needs a second argument: you pass the `null` yourself. `parent.removeChild(node)` takes a child out and throws a `NotFoundError` when `node` isn't a child of `parent`, so removing the same node twice fails the second time.

A node has one place. Append or insert a node that already has a parent and it moves, with no removal first. Remove a node and its whole subtree goes with it; the descendants stay attached to it, and it can go back in later.

```js
const ul = document.createElement("ul");
const a = ul.appendChild(document.createElement("li"));
const b = ul.appendChild(document.createElement("li"));
ul.insertBefore(b, a);  // moves b: the order is now b, a
ul.removeChild(a);
ul.removeChild(a);      // throws NotFoundError
```

Assignment 03 attaches nodes to a parent for the first time; 05 does it for a whole finished tree in one pass. From 06 the tree changes after you draw it: nodes leave, new ones arrive, and in 07 the position of an arrival starts to matter. In 08 a node that exists has to change places. The harness counts an `insert` (a node that had no parent), a `move` (one that had) and a `remove`, which is how tests tell a reorder from a rebuild. minidom throws where a browser does, for a `removeChild` of a non-child and for an `insertBefore` whose reference isn't a child.

Learn more:
- [MDN: Node.appendChild()](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild)
- [MDN: Node.insertBefore()](https://developer.mozilla.org/en-US/docs/Web/API/Node/insertBefore)
- [MDN: Node.removeChild()](https://developer.mozilla.org/en-US/docs/Web/API/Node/removeChild)

## `requestIdleCallback` and `timeRemaining()`
<!--
id: dom-idle-callback
also: idle callback; IdleDeadline; deadline; cancelIdleCallback; background tasks; scheduler; idle period; didTimeout
code: \brequestIdleCallback\s*\(
-->
One thread runs layout, painting and your clicks, and a long script blocks all of it. `requestIdleCallback(fn)` asks the browser to call `fn` later, when the thread has nothing more urgent to do. It calls `fn` once, with a deadline object. `deadline.timeRemaining()` is the number of milliseconds left in this idle period, and it can drop to 0 at once if something urgent arrives. To keep going, `fn` has to register itself again before it returns, because the browser won't call it a second time.

```js
const jobs = [/* functions to run */];
function onIdle(deadline) {
  while (jobs.length > 0 && deadline.timeRemaining() > 0) jobs.shift()();
  if (jobs.length > 0) requestIdleCallback(onIdle); // ask for another period
}
requestIdleCallback(onIdle);
```

Only assignment 04 writes against it. `render.js` already registers the loop with a `requestIdleCallback(workLoop)` line at import time, and `workLoop` has to ask again every time it stops. Node has no such function, so `env.js` installs a stand-in that the tests drive, and you import it before your library; the entry programs do that first. The scenario command `idle k` runs one idle period in which `timeRemaining()` returns 1 until call number k, which returns 0 (a browser reports milliseconds). The test counts those calls, so read it once per unit of work. `flush` runs periods until one has no calls.

MDN marks the API as limited availability, and React's own scheduler doesn't use it. The posts use it because it shows the idea: work in slices, and hand the thread back when told.

Learn more:
- [MDN: Window.requestIdleCallback()](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestIdleCallback)
- [MDN: IdleDeadline.timeRemaining()](https://developer.mozilla.org/en-US/docs/Web/API/IdleDeadline/timeRemaining)
- [MDN: Background Tasks API](https://developer.mozilla.org/en-US/docs/Web/API/Background_Tasks_API)

## Inputs: `value`, the `input` and `submit` events
<!--
id: dom-form-inputs
also: input element; form; value; input event; submit event; preventDefault; event.target.value; typing; textarea; submit button
code: \.target\.value\b|\.preventDefault\s*\(
-->
An `<input>` keeps the text the user has typed in its `value` property. Typing fires an `input` event on that node after each change, and the event bubbles, so a parent can listen for it. Inside the listener, `event.target.value` is the text as it now stands. Assigning `input.value` from a script changes what the user sees. It fires nothing.

Pressing Enter in a form, or clicking its submit button (a `<button>` with no `type` is one), fires `submit` on the `<form>`, and then the browser's default action takes over: it navigates, which reloads the page. A listener that calls `event.preventDefault()` cancels that, and that's how a script-driven app takes over a form. The `input` event has no default action to cancel.

```js
const form = document.createElement("form");
const box = form.appendChild(document.createElement("input"));
form.addEventListener("submit", (e) => {
  e.preventDefault();
  console.log("add:", box.value);
});
```

Props don't see typed text. It lives on the node. Re-render a list and keep a node, and its text stays. Rebuild the node and the text is gone. That is what the `type` command in assignments 07 and 08 tests: it sets `value` on a node and dispatches `input`, and later dumps show whether the text followed its item. Assignment 12 uses all three pieces in the todo form, alongside the idea in [controlled inputs](#primer/react-controlled-inputs).

In minidom, `input` and `submit` are plain events the harness dispatches. Nothing turns keystrokes into `value`. A click on an enabled submit button inside a form makes the harness dispatch `submit`, unless a listener prevented the click. That rule lives in the harness, and minidom lets events reach disabled controls. The app relies on what browsers and jsdom also do.

Learn more:
- [MDN: the input event](https://developer.mozilla.org/en-US/docs/Web/API/Element/input_event)
- [MDN: the submit event](https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/submit_event)
- [MDN: Event.preventDefault()](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault)

## `document.title`
<!--
id: dom-document-title
also: page title; title element; tab title; window title; document.title
code: \bdocument\.title\b
-->
`document.title` is a string you can read and assign. The browser shows it in the tab and the window's title bar, and assigning to it also changes the text of the page's `<title>` element. A page without a `<title>` reads `""`. It hangs off `document`, so changing it leaves the node tree alone and a dump of the container looks the same before and after. Don't confuse it with an element's `title` property, which is the tooltip shown on hover.

```js
document.title = "3 left";
console.log(document.title);  // "3 left"
```

Assignment 12 uses it. The todo app keeps the title in step with a number it already tracks, from an effect (see [`useEffect`](#primer/react-effects)). The checker reads the title back, because `dump` prints a `title "..."` line after the tree whenever the title isn't empty. `index.html` starts with the title `didact`, so serve the folder (see [serving index.html](#primer/static-server)) and watch the tab change as you add and tick items. In minidom `document.title` is a plain string property that starts as `""`, with no `<title>` element behind it, which no assignment needs. Browsers and jsdom read and write it the same way.

Learn more:
- [MDN: Document.title](https://developer.mozilla.org/en-US/docs/Web/API/Document/title)
- [MDN: the title element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/title)
- [MDN: HTMLElement.title](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/title)
