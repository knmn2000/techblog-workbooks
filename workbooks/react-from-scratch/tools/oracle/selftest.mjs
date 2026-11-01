// selftest.mjs - checks the harness and the oracle themselves.
//
//   cd tools/oracle && node selftest.mjs        (needs Node 26 and `npm install` done in this folder)
//
// 1. minidom: child lists, move vs insert, listeners, bubbling, errors, write counting
// 2. dump, markup, scenario commands (with a tiny stub library), the catalog
// 3. the oracle: every command against real React 19 on jsdom
// 4. minidom against jsdom: the same random DOM operations on both, with the dumps compared

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

import { createDocument, MiniEvent, STAT_NAMES } from "../../harness/minidom.js";
import { createEnv } from "../../harness/env.js";
import { makeLabeler, dumpTree, dumpNode } from "../../harness/dump.js";
import { parseMarkup, buildElement, parseAttributes, makeHandlers, h } from "../../harness/markup.js";
import { parseScenario, runScenario, stableJson } from "../../harness/scenario.js";
import { makeCatalog } from "../../harness/catalog.js";
import { runOracle, closeOracle } from "./run.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const harnessDir = path.resolve(here, "../../harness");

const tests = [];
const test = (name, fn) => tests.push({ name, fn });

const eq = assert.deepEqual;

function throwsName(fn, name) {
  try {
    fn();
  } catch (err) {
    assert.equal(err.name, name, `expected ${name}, got ${err.name}: ${err.message}`);
    return err;
  }
  assert.fail(`expected ${name} to be thrown`);
}

/** A fresh minidom document with a few helpers. */
function fresh() {
  const world = createDocument();
  const { document } = world;
  const el = (tag, props = {}) => Object.assign(document.createElement(tag), props);
  const text = (value) => document.createTextNode(value);
  world.resetStats();
  return { ...world, el, text };
}

const kids = (node) => Array.from(node.childNodes);

// =============================================================================================
// 1. minidom
// =============================================================================================

test("minidom: node basics and defaults", () => {
  const { document, el, text } = fresh();
  const d = el("div");
  assert.equal(d.nodeType, 1);
  assert.equal(d.tagName, "DIV");
  assert.equal(d.localName, "div");
  assert.equal(el("Span").tagName, "SPAN");
  assert.equal(d.id, "");
  assert.equal(d.className, "");
  assert.equal(d.title, "");
  assert.equal(d.value, "");
  assert.equal(d.disabled, false);
  assert.equal(d.foo, undefined);
  assert.equal(d.parentNode, null);
  assert.equal(d.firstChild, null);
  assert.equal(d.lastChild, null);
  assert.equal(d.nextSibling, null);
  assert.equal(d.previousSibling, null);
  assert.equal(d.childNodes.length, 0);
  const t = text("hi");
  assert.equal(t.nodeType, 3);
  assert.equal(t.nodeValue, "hi");
  assert.equal(t.data, "hi");
  assert.equal(t.textContent, "hi");
  assert.equal(d.nodeValue, null);
  assert.equal(document.title, "");
  assert.equal(document.createTextNode(5).nodeValue, "5");
  assert.ok(d.ownerDocument === document);
});

test("minidom: appendChild and insertBefore build the child list; pointers follow", () => {
  const { el } = fresh();
  const p = el("div");
  const [a, b, c, d] = ["a", "b", "c", "d"].map((id) => el("span", { id }));
  p.appendChild(a);
  p.appendChild(c);
  p.insertBefore(b, c);
  p.insertBefore(d, null);
  eq(kids(p).map((n) => n.id), ["a", "b", "c", "d"]);
  assert.equal(p.firstChild, a);
  assert.equal(p.lastChild, d);
  assert.equal(a.previousSibling, null);
  assert.equal(a.nextSibling, b);
  assert.equal(c.previousSibling, b);
  assert.equal(d.nextSibling, null);
  assert.equal(b.parentNode, p);
  assert.equal(p.childNodes.length, 4); // live
  assert.equal(p.appendChild(el("i")).tagName, "I"); // returns the node
});

test("minidom: insert, move and remove are counted separately", () => {
  const { el, stats, resetStats } = fresh();
  const p = el("div");
  const q = el("div");
  const [a, b, c] = [el("a"), el("b"), el("i")];
  resetStats();
  p.appendChild(a);
  p.appendChild(b);
  p.insertBefore(c, a);
  eq(stats(), { create: 0, insert: 3, move: 0, remove: 0, write: 0, addListener: 0, removeListener: 0 });
  p.appendChild(c); // moves within the parent
  q.insertBefore(a, null); // moves to another parent
  eq(kids(p), [b, c]);
  eq(kids(q), [a]);
  eq(stats(), { create: 0, insert: 3, move: 2, remove: 0, write: 0, addListener: 0, removeListener: 0 });
  p.removeChild(b);
  a.remove();
  eq(stats(), { create: 0, insert: 3, move: 2, remove: 2, write: 0, addListener: 0, removeListener: 0 });
  eq(Object.keys(stats()), STAT_NAMES);
  a.remove(); // no parent: nothing happens, nothing is counted
  assert.equal(stats().remove, 2);
});

test("minidom: create counts createElement and createTextNode; stats() returns a copy", () => {
  const { document, stats, resetStats } = fresh();
  document.createElement("div");
  document.createTextNode("x");
  const copy = stats();
  assert.equal(copy.create, 2);
  copy.create = 99;
  assert.equal(stats().create, 2);
  resetStats();
  assert.equal(stats().create, 0);
});

test("minidom: removeChild of a non-child throws NotFoundError and counts nothing", () => {
  const { el, stats } = fresh();
  const p = el("div");
  const q = el("div");
  const a = el("span");
  const stranger = el("b");
  q.appendChild(a);
  const before = stats();
  throwsName(() => p.removeChild(a), "NotFoundError");
  throwsName(() => p.removeChild(stranger), "NotFoundError");
  eq(stats(), before);
  assert.equal(a.parentNode, q);
  assert.throws(() => p.removeChild("x"), TypeError);
});

test("minidom: insertBefore with a reference that is not a child throws and changes nothing", () => {
  const { el, stats } = fresh();
  const p = el("div");
  const a = el("a");
  const b = el("b");
  const stranger = el("i");
  p.appendChild(a);
  const before = stats();
  throwsName(() => p.insertBefore(b, stranger), "NotFoundError");
  eq(stats(), before);
  eq(kids(p), [a]);
  assert.equal(b.parentNode, null);
  assert.throws(() => p.insertBefore(b), TypeError); // the second argument is required
});

test("minidom: inserting a node before itself, and hierarchy errors", () => {
  const { el, text, stats, resetStats } = fresh();
  const p = el("div");
  const [a, b] = [el("a"), el("b")];
  p.appendChild(a);
  p.appendChild(b);
  resetStats();
  p.insertBefore(a, a);
  eq(kids(p), [a, b]);
  assert.equal(stats().move, 1);
  const inner = el("section");
  p.appendChild(inner);
  throwsName(() => inner.appendChild(p), "HierarchyRequestError");
  throwsName(() => p.appendChild(p), "HierarchyRequestError");
  throwsName(() => text("t").appendChild(el("b")), "HierarchyRequestError");
  assert.throws(() => p.appendChild("not a node"), TypeError);
});

test("minidom: replaceChild", () => {
  const { el, stats, resetStats } = fresh();
  const p = el("div");
  const [a, b, c] = [el("a"), el("b"), el("i")];
  p.appendChild(a);
  p.appendChild(b);
  resetStats();
  assert.equal(p.replaceChild(c, a), a);
  eq(kids(p), [c, b]);
  assert.equal(a.parentNode, null);
  eq(stats(), { create: 0, insert: 1, move: 0, remove: 1, write: 0, addListener: 0, removeListener: 0 });
  p.replaceChild(b, c); // b is already a child: it moves
  eq(kids(p), [b]);
  throwsName(() => p.replaceChild(el("u"), el("s")), "NotFoundError");
  assert.equal(p.replaceChild(b, b), b);
  eq(kids(p), [b]);
});

test("minidom: contains", () => {
  const { el } = fresh();
  const [p, q, r] = [el("div"), el("div"), el("div")];
  p.appendChild(q);
  q.appendChild(r);
  assert.ok(p.contains(r) && p.contains(q) && p.contains(p));
  assert.ok(!r.contains(p));
  assert.ok(!p.contains(null));
});

test("minidom: property writes are counted, reads and bookkeeping are not", () => {
  const { el, text, stats, resetStats } = fresh();
  const d = el("div");
  const t = text("a");
  const p = el("div");
  resetStats();
  d.id = "x"; // 1
  d.className = "c"; // 2
  d.foo = { any: "thing" }; // 3 (expando)
  d.onclick = () => {}; // 4
  d.disabled = true; // 5
  t.nodeValue = "b"; // 6
  t.data = "c"; // 7
  t.textContent = "d"; // 8
  d.id = "x"; // 9: assigning the same value is still a write
  assert.equal(stats().write, 9);
  assert.equal(t.nodeValue, "d");
  // reads and the node operations are not writes
  void d.id;
  void d.childNodes;
  p.appendChild(d);
  p.appendChild(t);
  p.removeChild(t);
  d.addEventListener("click", () => {});
  assert.equal(stats().write, 9);
  eq(
    { id: d.id, className: d.className, foo: d.foo.any, disabled: d.disabled },
    { id: "x", className: "c", foo: "thing", disabled: true },
  );
});

test("minidom: quiet() work is not counted; read-only properties cannot be assigned", () => {
  const { el, stats, quiet, resetStats } = fresh();
  const d = el("div");
  resetStats();
  quiet(() => {
    d.value = "x";
    d.appendChild(el("p"));
  });
  eq(stats(), Object.fromEntries(STAT_NAMES.map((n) => [n, 0])));
  assert.equal(d.value, "x");
  assert.throws(() => {
    d.parentNode = null;
  }, TypeError);
  assert.throws(() => {
    d.tagName = "p";
  }, TypeError);
  assert.equal(stats().write, 0); // a refused assignment is not a write
});

test("minidom: textContent of an element and of a text node", () => {
  const { el, text, stats, resetStats } = fresh();
  const p = el("p");
  p.appendChild(text("a"));
  const b = el("b");
  b.appendChild(text("b"));
  p.appendChild(b);
  p.appendChild(text("c"));
  assert.equal(p.textContent, "abc");
  const old = p.firstChild;
  resetStats();
  p.textContent = "z";
  assert.equal(kids(p).length, 1);
  assert.equal(p.textContent, "z");
  assert.equal(old.parentNode, null);
  eq(stats(), { create: 0, insert: 0, move: 0, remove: 0, write: 1, addListener: 0, removeListener: 0 });
  p.textContent = "";
  assert.equal(kids(p).length, 0);
});

test("minidom: listeners match type and function identity", () => {
  const { el, stats, resetStats } = fresh();
  const d = el("div");
  const calls = [];
  const f = () => calls.push("f");
  const g = () => calls.push("g");
  resetStats();
  d.addEventListener("click", f);
  d.addEventListener("click", f); // the same function twice: registered once
  d.addEventListener("click", g);
  d.addEventListener("input", f);
  d.dispatchEvent(new MiniEvent("click"));
  eq(calls, ["f", "g"]);
  d.removeEventListener("click", () => calls.push("f")); // an equal-looking other function: no match
  d.dispatchEvent(new MiniEvent("click"));
  eq(calls, ["f", "g", "f", "g"]);
  d.removeEventListener("input", g); // wrong type for g: no match
  d.removeEventListener("click", f);
  d.dispatchEvent(new MiniEvent("click"));
  eq(calls, ["f", "g", "f", "g", "g"]);
  d.dispatchEvent(new MiniEvent("input"));
  eq(calls, ["f", "g", "f", "g", "g", "f"]);
  eq({ add: stats().addListener, remove: stats().removeListener }, { add: 4, remove: 3 });
});

test("minidom: events bubble target -> ancestors, in registration order", () => {
  const { el } = fresh();
  const [root, mid, leaf] = [el("div", { id: "root" }), el("div", { id: "mid" }), el("button", { id: "leaf" })];
  root.appendChild(mid);
  mid.appendChild(leaf);
  const order = [];
  const note = (name) =>
    function listener(ev) {
      order.push(`${name}:${ev.currentTarget.id}:${ev.target.id}:${this.id}`);
    };
  root.addEventListener("click", note("r1"));
  mid.addEventListener("click", note("m1"));
  leaf.addEventListener("click", note("l1"));
  leaf.addEventListener("click", note("l2"));
  root.addEventListener("click", note("r2"));
  leaf.dispatchEvent(new MiniEvent("click"));
  eq(order, ["l1:leaf:leaf:leaf", "l2:leaf:leaf:leaf", "m1:mid:leaf:mid", "r1:root:leaf:root", "r2:root:leaf:root"]);

  // the event object has the documented shape
  let seen;
  leaf.addEventListener("shape", (ev) => {
    seen = ev;
  });
  assert.equal(leaf.dispatchEvent(new MiniEvent("shape")), true);
  eq(
    { type: seen.type, bubbles: seen.bubbles, defaultPrevented: seen.defaultPrevented, target: seen.target === leaf },
    { type: "shape", bubbles: true, defaultPrevented: false, target: true },
  );
  assert.equal(seen.currentTarget, null); // reset after dispatch

  // a plain object is accepted as an event description
  order.length = 0;
  mid.dispatchEvent({ type: "click" });
  eq(order, ["m1:mid:mid:mid", "r1:root:mid:root", "r2:root:mid:root"]);

  // a non-bubbling event stays on its target
  order.length = 0;
  leaf.dispatchEvent(new MiniEvent("click", { bubbles: false }));
  eq(order, ["l1:leaf:leaf:leaf", "l2:leaf:leaf:leaf"]);
});

test("minidom: preventDefault only works on cancelable events; stopPropagation", () => {
  const { el } = fresh();
  const [p, c] = [el("div"), el("div")];
  p.appendChild(c);
  c.addEventListener("submit", (ev) => ev.preventDefault());
  assert.equal(c.dispatchEvent(new MiniEvent("submit", { cancelable: true })), false);
  assert.equal(c.dispatchEvent(new MiniEvent("submit")), true);
  const seen = [];
  c.addEventListener("x", (ev) => {
    ev.stopPropagation();
    seen.push("c1");
  });
  c.addEventListener("x", () => seen.push("c2")); // same node: still runs
  p.addEventListener("x", () => seen.push("p"));
  c.dispatchEvent(new MiniEvent("x"));
  eq(seen, ["c1", "c2"]);
});

test("minidom: listeners removed or added during a dispatch", () => {
  const { el } = fresh();
  const d = el("div");
  const seen = [];
  const second = () => seen.push("second");
  const late = () => seen.push("late");
  d.addEventListener("go", () => {
    seen.push("first");
    d.removeEventListener("go", second);
    d.addEventListener("go", late);
  });
  d.addEventListener("go", second);
  d.dispatchEvent(new MiniEvent("go"));
  eq(seen, ["first"]); // second was removed before its turn, late was added after the snapshot
  d.dispatchEvent(new MiniEvent("go"));
  eq(seen, ["first", "first", "late"]);
});

test("minidom: getElementById searches the live tree under body", () => {
  const { document, el } = fresh();
  assert.equal(document.getElementById("a"), null);
  const outside = el("div", { id: "a" });
  assert.equal(document.getElementById("a"), null); // not attached
  const box = el("div");
  const inner = el("p", { id: "a" });
  box.appendChild(inner);
  document.body.appendChild(box);
  assert.equal(document.getElementById("a"), inner);
  inner.id = "b";
  assert.equal(document.getElementById("a"), null);
  assert.equal(document.getElementById("b"), inner);
  box.removeChild(inner);
  assert.equal(document.getElementById("b"), null);
  assert.equal(document.getElementById(""), null);
  void outside;
});

// =============================================================================================
// 2a. env: the scheduler
// =============================================================================================

test("env: idle() passes a deadline and counts timeRemaining() calls", () => {
  const env = createEnv();
  const loop = (budgetSeen) => (deadline) => {
    assert.equal(deadline.didTimeout, false);
    let n = 0;
    while (n < 10) {
      n++;
      budgetSeen.push(deadline.timeRemaining());
      if (budgetSeen.at(-1) < 1) break;
    }
  };
  const seen = [];
  env.requestIdleCallback(loop(seen));
  assert.equal(env.idle(3), 3);
  eq(seen, [1, 1, 0]);
  assert.equal(env.idle(3), 0); // nothing registered any more
  seen.length = 0;
  env.requestIdleCallback((deadline) => {
    for (let i = 0; i < 5; i++) seen.push(deadline.timeRemaining());
  });
  assert.equal(env.idle(Infinity), 5);
  eq(seen, [1, 1, 1, 1, 1]);
  seen.length = 0;
  env.requestIdleCallback((deadline) => {
    for (let i = 0; i < 4; i++) seen.push(deadline.timeRemaining());
  });
  assert.equal(env.idle(1), 4);
  eq(seen, [0, 0, 0, 0]);
});

test("env: callbacks registered during a period wait for the next one; cancelIdleCallback works", () => {
  const env = createEnv();
  const log = [];
  env.requestIdleCallback((d) => {
    d.timeRemaining();
    log.push("a");
    env.requestIdleCallback((d2) => {
      d2.timeRemaining();
      log.push("c");
    });
  });
  const id = env.requestIdleCallback(() => log.push("b-cancelled"));
  env.requestIdleCallback((d) => {
    d.timeRemaining();
    log.push("d");
  });
  env.cancelIdleCallback(id);
  assert.equal(env.idle(Infinity), 2);
  eq(log, ["a", "d"]);
  assert.equal(env.idle(Infinity), 1);
  eq(log, ["a", "d", "c"]);
  // a callback that cancels a later one of the same period
  let later;
  env.requestIdleCallback(() => env.cancelIdleCallback(later));
  later = env.requestIdleCallback(() => log.push("never"));
  env.idle(Infinity);
  eq(log, ["a", "d", "c"]);
});

test("env: flush() repeats periods until one does no work, does nothing without callbacks, and has a cap", () => {
  const env = createEnv();
  env.flush(); // nothing registered
  let units = 5;
  const loop = (deadline) => {
    while (units > 0 && deadline.timeRemaining() >= 1) units--;
    env.requestIdleCallback(loop);
  };
  env.requestIdleCallback(loop);
  assert.equal(env.idle(2), 2);
  assert.ok(units > 0);
  env.flush();
  assert.equal(units, 0);
  // an endless worker: flush gives up
  const env2 = createEnv();
  const endless = (deadline) => {
    deadline.timeRemaining();
    env2.requestIdleCallback(endless);
  };
  env2.requestIdleCallback(endless);
  assert.throws(() => env2.flush(), /still doing work/);
});

test("env: the global environment installs document and the scheduler; container is #root", async () => {
  assert.equal(typeof globalThis.requestIdleCallback, "function");
  assert.equal(typeof globalThis.cancelIdleCallback, "function");
  const { document, container, stats } = await import("../../harness/env.js");
  assert.equal(globalThis.document, document);
  assert.equal(container.id, "root");
  assert.equal(container.tagName, "DIV");
  assert.equal(document.getElementById("root"), container);
  eq(stats(), Object.fromEntries(STAT_NAMES.map((n) => [n, 0])));
});

// =============================================================================================
// 2b. dump
// =============================================================================================

test("dump: labels are a..z, aa, ab, ... and stay stable; text nodes get none", () => {
  const { el, text } = fresh();
  const label = makeLabeler();
  const nodes = Array.from({ length: 30 }, () => el("i"));
  const labels = nodes.map((n) => label(n));
  assert.equal(labels[0], "a");
  assert.equal(labels[25], "z");
  assert.equal(labels[26], "aa");
  assert.equal(labels[27], "ab");
  assert.equal(labels[29], "ad");
  assert.equal(label(nodes[3]), "d");
  assert.equal(new Set(labels).size, 30);
  const other = makeLabeler();
  assert.equal(other(nodes[7]), "a"); // a separate labeler starts again
  void text;
  // 26 + 26*26 + 1: the 703rd label
  const l2 = makeLabeler();
  let last;
  for (let i = 0; i < 703; i++) last = l2({});
  assert.equal(last, "aaa");
});

test("dump: node and text lines, sorted props, defaults hidden", () => {
  const { el, text } = fresh();
  const root = el("div");
  const label = makeLabeler();
  root.appendChild(el("section", { id: "s", className: "big", title: "t" }));
  const button = el("button", { disabled: true, id: "b" });
  button.appendChild(text("go"));
  root.appendChild(button);
  root.appendChild(el("input", { value: "v", disabled: false }));
  root.appendChild(el("div", { disabled: true, value: "ignored" })); // only buttons/inputs/textareas show disabled, value
  root.appendChild(el("textarea", { value: "t" }));
  eq(dumpTree(root, label), [
    'node 0 a section "className=big id=s title=t"',
    'node 0 b button "disabled=true id=b"',
    'text 1 "go"',
    'node 0 c input "value=v"',
    'node 0 d div ""',
    'node 0 e textarea "value=t"',
  ]);
  // numbers are printed as text
  const n = el("p", { id: 5, title: 0 });
  eq(dumpNode(n, label), ['node 0 f p "id=5 title=0"']);
});

test("dump: percent-encoding of prop values and of text", () => {
  const { el, text } = fresh();
  const label = makeLabeler();
  const d = el("div", { className: "a b", id: 'say"hi"', title: "100%" });
  eq(dumpNode(d, label), ['node 0 a div "className=a%20b id=say%22hi%22 title=100%25"']);
  // the whole value is encoded when it needs encoding; otherwise it is printed as is
  const e = el("div", { id: "a/b?c&d", title: "x y/z" });
  eq(dumpNode(e, label), ['node 0 b div "id=a/b?c&d title=x%20y%2Fz"']);
  // text: only quote, percent and line breaks; spaces stay
  const p = el("p");
  p.appendChild(text('say "hi" 50% a/b + c\nnext'));
  eq(dumpNode(p, label), ["node 0 c p \"\"", 'text 1 "say %22hi%22 50%25 a/b + c%0Anext"']);
});

test("dump: adjacent text nodes are concatenated, empty text is skipped", () => {
  const { el, text } = fresh();
  const label = makeLabeler();
  const p = el("p");
  p.appendChild(text("Hi "));
  p.appendChild(text("there"));
  p.appendChild(text(""));
  const b = el("b");
  b.appendChild(text(""));
  p.appendChild(b);
  p.appendChild(text(""));
  p.appendChild(text("a"));
  p.appendChild(text("b"));
  eq(dumpNode(p, label), ['node 0 a p ""', 'text 1 "Hi there"', 'node 1 b b ""', 'text 1 "ab"']);
  // a lone text node
  eq(dumpNode(text("x y"), label), ['text 0 "x y"']);
  eq(dumpNode(text(""), label), []);
  // the container is not printed; its children start at depth 0
  const c = el("div");
  c.appendChild(text("1"));
  c.appendChild(text("2"));
  eq(dumpTree(c, label), ['text 0 "12"']);
});

// =============================================================================================
// 2c. markup
// =============================================================================================

test("markup: parseMarkup handles attributes, nesting, components and whitespace", () => {
  const tree = parseMarkup('<div id=a className="big one" title=\'say "x"\' disabled onClick=@go>hi <b>there</b> <Counter id=d start=5/> </div>');
  assert.equal(tree.tag, "div");
  eq(tree.attrs, { id: "a", className: "big one", title: 'say "x"', disabled: true, onClick: { handler: "go" } });
  assert.equal(tree.children.length, 3); // "hi ", <b>, <Counter/>; the lone spaces are dropped
  assert.equal(tree.children[0], "hi ");
  assert.equal(tree.children[1].tag, "b");
  assert.equal(tree.children[1].children[0], "there");
  assert.equal(tree.children[2].tag, "Counter");
  eq(tree.children[2].attrs, { id: "d", start: "5" });

  eq(parseMarkup("<p> a  b </p>").children, [" a  b "]); // inner and outer spaces kept
  eq(parseMarkup("<p> </p>").children, []);
  eq(parseMarkup("<br/>").children, []);
  eq(parseMarkup('<ul><li key="0">x</li><li key=1></li></ul>').children.map((c) => c.attrs.key), ["0", "1"]);
  // void elements need no closing tag, and may have one
  eq(parseMarkup("<div><input id=a><input id=b></input><br></div>").children.map((c) => c.tag), ["input", "input", "br"]);
  // "/" inside an unquoted value, and a self-closing slash right after it
  eq(parseMarkup("<a href=x/y/>").attrs, { href: "x/y" });
  eq(parseMarkup('<p title="a>b">q</p>').attrs, { title: "a>b" });
});

test("markup: errors", () => {
  assert.throws(() => parseMarkup("<div>"), /missing <\/div>/);
  assert.throws(() => parseMarkup("<div></span>"), /does not match/);
  assert.throws(() => parseMarkup("text"), /expected a tag/);
  assert.throws(() => parseMarkup("<a></a>x"), /unexpected text/);
  assert.throws(() => parseMarkup('<a b="c></a>'), /unterminated/);
});

test("markup: handlers are memoised per name and append the name to the log", () => {
  const log = [];
  const handler = makeHandlers((t) => log.push(t));
  assert.equal(handler("one"), handler("one"));
  assert.notEqual(handler("one"), handler("two"));
  handler("one")();
  handler("two")();
  handler("one")();
  eq(log, ["one", "two", "one"]);
});

test("markup: buildElement uses h, the component lookup and the handlers", () => {
  const log = [];
  const handler = makeHandlers((t) => log.push(t));
  const Comp = () => null;
  const tree = parseMarkup('<div id=a onClick=@one><Comp x=1/>hi<b onClick=@one></b></div>');
  const el = buildElement(tree, { h, component: (name) => (name === "Comp" ? Comp : assert.fail("unknown")), handler });
  assert.equal(el.type, "div");
  assert.equal(el.props.id, "a");
  assert.equal(el.props.onClick, el.props.children[2].props.onClick); // same function for the same name
  assert.equal(el.props.children[0].type, Comp);
  eq(el.props.children[0].props, { x: "1", children: [] });
  eq(el.props.children[1], { type: "TEXT_ELEMENT", props: { nodeValue: "hi", children: [] } });
  el.props.onClick();
  eq(log, ["one"]);
  // no attributes -> props null reaches h
  let got;
  buildElement(parseMarkup("<p>x</p>"), { h: (type, props, ...c) => ((got = props), { type, c }), component: null, handler });
  assert.equal(got, null);
});

test("markup: the canonical h builds the element format of assignment 01", () => {
  const props = { id: "a", key: "k" };
  const child = h("b", null);
  const el = h("div", props, "x", 3, child);
  eq(el, {
    type: "div",
    props: {
      id: "a",
      key: "k",
      children: [
        { type: "TEXT_ELEMENT", props: { nodeValue: "x", children: [] } },
        { type: "TEXT_ELEMENT", props: { nodeValue: 3, children: [] } },
        { type: "b", props: { children: [] } },
      ],
    },
  });
  assert.equal(el.props.children[2], child);
  eq(props, { id: "a", key: "k" }); // not modified
  eq(h("p", null), { type: "p", props: { children: [] } });
  eq(parseAttributes('a=1 b="x y" c d=@h'), { a: "1", b: "x y", c: true, d: { handler: "h" } });
});

// =============================================================================================
// 2d. scenario commands, with a tiny stub library
// =============================================================================================

/** A trivial library: one unit of work per node, a work loop on requestIdleCallback, no hooks. */
function makeStubLib(env) {
  const { document } = env;
  const queue = [];
  const events = [];

  function loop(deadline) {
    let go = true;
    while (queue.length > 0 && go) {
      queue.shift()();
      go = deadline.timeRemaining() >= 1;
    }
    env.requestIdleCallback(loop);
  }
  env.requestIdleCallback(loop);

  function createDom(element) {
    const dom = element.type === "TEXT_ELEMENT" ? document.createTextNode(element.props.nodeValue) : document.createElement(element.type);
    applyProps(dom, {}, element.props);
    return dom;
  }

  function applyProps(dom, prev, next) {
    for (const name of Object.keys(next)) {
      if (name === "children" || prev[name] === next[name]) continue;
      if (name.startsWith("on")) {
        if (prev[name]) dom.removeEventListener(name.slice(2).toLowerCase(), prev[name]);
        dom.addEventListener(name.slice(2).toLowerCase(), next[name]);
      } else {
        dom[name] = next[name];
      }
    }
    for (const name of Object.keys(prev)) {
      if (name === "children" || name in next) continue;
      if (name.startsWith("on")) dom.removeEventListener(name.slice(2).toLowerCase(), prev[name]);
      else dom[name] = "";
    }
  }

  function unit(element, parentDom) {
    return () => {
      if (typeof element.type === "function") {
        queue.unshift(unit(element.type(element.props), parentDom));
        return;
      }
      const dom = createDom(element);
      parentDom.appendChild(dom);
      queue.unshift(...element.props.children.map((child) => unit(child, dom)));
    };
  }

  let recording = false;
  return {
    events,
    createElement: h,
    createDom,
    updateDom: (dom, prev, next) => applyProps(dom, prev, next),
    render(element, container) {
      if (!recording) {
        recording = true;
        env.quiet(() => {
          for (const type of ["click", "input", "submit"]) {
            container.addEventListener(type, (ev) => events.push(`${type} ${ev.target.id} bubbles=${ev.bubbles} cancelable=${ev.cancelable}`));
          }
        });
      }
      queue.push(() => {}); // the root fiber
      queue.push(unit(element, container));
    },
    components: { Extra: () => h("u", null, "extra") },
  };
}

async function runStub(text, mutate) {
  const env = createEnv();
  const lib = makeStubLib(env);
  mutate?.(lib, env);
  const out = await runScenario(text, lib, { env });
  return { out, lib, env };
}

test("scenario: parseScenario skips blank lines and comments and keeps the rest of the line", () => {
  const cmds = parseScenario("# note\n\nrender  a \r\n  type #x  two  words \ndump\n");
  eq(cmds.map((c) => [c.no, c.name, c.rest]), [
    [3, "render", "a "],
    [4, "type", "#x  two  words "],
    [5, "dump", ""],
  ]);
});

test("scenario: stableJson", () => {
  assert.equal(stableJson({ b: [1, "a b", null, true], a: { z: 1, y: () => 1 }, u: undefined }), '{"a":{"y":"[fn]","z":1},"b":[1,"a\\u0020b",null,true]}');
  assert.equal(stableJson("caf\u00e9 \"q\""), '"caf\\u00e9\\u0020\\"q\\""');
  assert.equal(stableJson([undefined, () => 0]), '[null,"[fn]"]');
  const cyc = {};
  cyc.me = cyc;
  assert.throws(() => stableJson(cyc), /itself/);
});

test("scenario 01: call, props, show", async () => {
  const { out } = await runStub(
    [
      'call div null',
      'call div {"id":"a b","n":2} "hello world" 3 $1',
      'props p {"x":[1,2],"s":"a b"}',
      "call span @p",
      "show p",
      'call "weird type" {"a":{"b":1}} "x"',
    ].join("\n"),
    (lib) => {
      lib.createElement = (type, props, ...children) => ({ type, props: { ...props, children } }); // children as given
    },
  );
  eq(out, [
    'element 1 {"props":{"children":[]},"type":"div"}',
    'element 2 {"props":{"children":["hello\\u0020world",3,{"props":{"children":[]},"type":"div"}],"id":"a\\u0020b","n":2},"type":"div"}',
    'element 3 {"props":{"children":[],"s":"a\\u0020b","x":[1,2]},"type":"span"}',
    'props p {"s":"a\\u0020b","x":[1,2]}',
    'element 4 {"props":{"a":{"b":1},"children":["x"]},"type":"weird\\u0020type"}',
  ]);
});

test("scenario 01: show reveals a library that modifies its props argument", async () => {
  const { out } = await runStub('props p {"id":"a"}\ncall div @p "x"\nshow p', (lib) => {
    lib.createElement = (type, props, ...children) => {
      props.children = children; // the bug that `show` is there to catch
      return { type, props };
    };
  });
  assert.equal(out[1], 'props p {"children":["x"],"id":"a"}');
});

test("scenario 02: create, update, click, dump, ops, log", async () => {
  const { out } = await runStub(
    [
      'create div id=a title="x y" onClick=@h',
      "dump",
      "ops",
      "click #a",
      "log",
      'update id=a title=z onClick=@h2 className=k',
      "dump",
      "click #a",
      "click a",
      "log",
      "ops write addListener removeListener",
      "create text nodeValue=hi",
      "dump",
    ].join("\n"),
  );
  eq(out, [
    "dump 1",
    'node 0 a div "id=a title=x%20y"',
    "ops 1 0 0 0 2 1 0",
    "log h",
    "dump 2",
    'node 0 a div "className=k id=a title=z"',
    "log h2",
    "log h2",
    "ops 2 1 1",
    "dump 3",
    'text 0 "hi"',
  ]);
});

test("scenario 03: tree, render, flush, dump, click, log", async () => {
  const { out } = await runStub(
    [
      "tree t <div id=a className=x>hi <button id=b onClick=@go>go</button></div>",
      "render t",
      "dump",
      "flush",
      "dump",
      "click #b",
      "click #b",
      "log",
      "log",
      "click #a",
    ].join("\n"),
  );
  eq(out, [
    "dump 1",
    "dump 2",
    'node 0 a div "className=x id=a"',
    'text 1 "hi "',
    'node 1 b button "id=b"',
    'text 2 "go"',
    "log go",
    "log go",
  ]);
});

test("scenario 04: idle counts units; a period ends when timeRemaining() reaches 0", async () => {
  // root + div + text + b + text = 5 units
  const { out } = await runStub(
    ["tree t <div id=a>hi<b>x</b></div>", "render t", "idle 2", "dump", "idle 2", "idle 5", "idle 1", "dump", "idle inf"].join("\n"),
  );
  eq(out, ["idle 2", "dump 1", "node 0 a div \"id=a\"", "idle 2", "idle 1", "idle 0", "dump 2", "node 0 a div \"id=a\"", 'text 1 "hi"', 'node 1 b b ""', 'text 2 "x"', "idle 0"]);
});

test("scenario: catalog components and lib.components are available to tree", async () => {
  const { out } = await runStub(
    [
      "tree t <Frame title=T><Greeting name=Ann/><FnA/><FnB/><Extra/></Frame>",
      "render t",
      "flush",
      "dump",
    ].join("\n"),
  );
  eq(out, [
    "dump 1",
    'node 0 a section ""',
    'node 1 b h2 ""',
    'text 2 "T"',
    'node 1 c h1 ""',
    'text 2 "Hi Ann"',
    'node 1 d i ""',
    'text 2 "a"',
    'node 1 e b ""',
    'text 2 "b"',
    'node 1 f u ""',
    'text 2 "extra"',
  ]);
  await assert.rejects(runStub("tree t <Nope/>\nrender t"), /unknown component "Nope"/);
});

test("scenario: type sets the value without counting a write, then dispatches a bubbling input event", async () => {
  const { out, lib } = await runStub(
    [
      "tree t <input id=i onInput=@typed/>",
      "render t",
      "flush",
      "ops write",
      "type #i hello  big world ",
      "dump",
      "log",
      "ops write",
      "type #i",
      "dump",
    ].join("\n"),
  );
  eq(out, [
    "ops 1",
    "dump 1",
    'node 0 a input "id=i value=hello%20%20big%20world%20"',
    "log typed",
    "ops 0",
    "dump 2",
    'node 0 a input "id=i"',
  ]);
  eq(lib.events, ["input i bubbles=true cancelable=false", "input i bubbles=true cancelable=false"]);
});

test("scenario: click and submit events bubble to the container and are cancelable", async () => {
  const { out, lib } = await runStub(
    ["tree t <div id=f onSubmit=@sent><button id=b onClick=@hit>x</button></div>", "render t", "flush", "submit #f", "click #b", "log"].join("\n"),
  );
  eq(out, ["log sent", "log hit"]); // a div is not a form: the click submits nothing
  eq(lib.events, ["submit f bubbles=true cancelable=true", "click b bubbles=true cancelable=true"]);
});

test("scenario: a click on an enabled submit button inside a form submits the form (the one default action)", async () => {
  const markup = "<form id=f onSubmit=@sent><button id=b>x</button><button id=c type=button>y</button><button id=d disabled>z</button><button id=e><span id=s>w</span></button></form>";
  const { out, lib } = await runStub(["tree t " + markup, "render t", "flush", "click #b", "log", "click #c", "click #d", "log", "click #s", "log"].join("\n"));
  eq(out, ["log sent", "log sent"]);
  eq(lib.events.filter((e) => e.startsWith("submit")), ["submit f bubbles=true cancelable=true", "submit f bubbles=true cancelable=true"]);
  // a click that a listener prevents does not submit
  const prevented = await runStub(["tree t " + markup, "render t", "flush", "click #b", "log"].join("\n"), (lib, env) => {
    const render = lib.render;
    lib.render = (el, container) => {
      render(el, container);
      env.quiet(() => container.addEventListener("click", (ev) => ev.preventDefault()));
    };
  });
  eq(prevented.out, []);
});

test("scenario: dump prints the title line (percent-encoded) when the title is not empty", async () => {
  const { out } = await runStub(["tree t <p>x</p>", "render t", "flush", "dump"].join("\n"), (lib, env) => {
    const render = lib.render;
    lib.render = (el, c) => {
      render(el, c);
      env.document.title = 'say "hi" 100%';
    };
  });
  eq(out, ["dump 1", 'node 0 a p ""', 'text 1 "x"', 'title "say %22hi%22 100%25"']);
});

test("scenario: ops names pick and order the counters; unknown names fail", async () => {
  const { out } = await runStub(["tree t <div id=a>hi<b>x</b></div>", "render t", "flush", "ops write create", "ops"].join("\n"));
  eq(out, ["ops 3 4", "ops 0 0 0 0 0 0 0"]); // writes: id=a and the nodeValue of two text nodes
  await assert.rejects(runStub("ops bogus"), /unknown statistic "bogus"/);
  const second = await runStub(["tree t <div id=a>hi<b>x</b></div>", "render t", "flush", "ops"].join("\n"));
  eq(second.out, ["ops 4 4 0 0 3 0 0"]);
});

test("scenario: errors in the scenario text carry the line, and learner errors pass through", async () => {
  await assert.rejects(runStub("dump\nfrobnicate x"), (err) => /unknown command "frobnicate"/.test(err.message) && err.scenarioLine === 2);
  await assert.rejects(runStub("render nope"), /unknown tree "nope"/);
  await assert.rejects(runStub("click #nothing"), /no element with id "nothing"/);
  await assert.rejects(runStub("call div"), /expected <type> <props>/);
  await assert.rejects(runStub("call div {bad}"), /not valid JSON/);
  await assert.rejects(runStub("call div null $3"), /no earlier call \$3/);
  await assert.rejects(runStub("poke"), /no Keeper has rendered/);
  await assert.rejects(runStub("tree t <div>\nrender t"), /missing <\/div>/);
  await assert.rejects(
    runStub("tree t <p>x</p>\nrender t", (lib) => {
      lib.render = () => {
        throw new Error("not implemented: render");
      };
    }),
    /^Error: not implemented: render/,
  );
});

test("scenario: runScenarioFile exit codes and output file (in a child process)", () => {
  const dir = mkdtempSync(path.join(os.tmpdir(), "oracle-selftest-"));
  try {
    const entry = path.join(dir, "entry.mjs");
    const url = (name) => pathToFileURL(path.join(harnessDir, name)).href;
    writeFileSync(
      entry,
      [
        `import ${JSON.stringify(url("env.js"))};`,
        `import { runScenarioFile } from ${JSON.stringify(url("scenario.js"))};`,
        'const mode = process.argv[4];',
        'const lib = { createElement(type, props, ...c) {',
        '  if (mode === "todo") throw new Error("not implemented: createElement");',
        '  if (mode === "boom") throw new Error("boom");',
        '  return { type, props: { ...props, children: c } };',
        '} };',
        'await runScenarioFile(process.argv[2], process.argv[3], lib);',
      ].join("\n"),
    );
    const input = path.join(dir, "in.txt");
    const output = path.join(dir, "out.txt");
    writeFileSync(input, "# c\ncall div null\ncall b null\n");
    const run = (mode) => spawnSync(process.execPath, [entry, input, output, mode], { encoding: "utf8" });

    let r = run("ok");
    assert.equal(r.status, 0, r.stderr);
    assert.equal(readFileSync(output, "utf8"), 'element 1 {"props":{"children":[]},"type":"div"}\nelement 2 {"props":{"children":[]},"type":"b"}\n');

    writeFileSync(output, "stale\n");
    r = run("todo");
    assert.equal(r.status, 99);
    assert.match(r.stderr, /^not implemented: createElement/);
    assert.ok(!existsSync(output), "no output file after an error");

    writeFileSync(output, "stale\n");
    r = run("boom");
    assert.equal(r.status, 1);
    assert.match(r.stderr, /scenario line 2/);
    assert.match(r.stderr, /Error: boom\n\s+at /);
    assert.ok(!existsSync(output));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("harness: importing the modules (not env.js) has no side effects on globals", () => {
  const files = ["minidom.js", "dump.js", "markup.js", "catalog.js", "scenario.js"].map((f) => pathToFileURL(path.join(harnessDir, f)).href);
  const code = `${JSON.stringify(files)}.reduce((p, f) => p.then(() => import(f)), Promise.resolve()).then(() => console.log(typeof document, typeof requestIdleCallback, typeof window))`;
  const r = spawnSync(process.execPath, ["-e", code], { encoding: "utf8" });
  assert.equal(r.status, 0, r.stderr);
  assert.equal(r.stdout.trim(), "undefined undefined undefined");
});

// =============================================================================================
// 2e. catalog (with a recording library that has no real hooks)
// =============================================================================================

test("catalog: Counter uses updater functions; counter d calls its setter twice per click", () => {
  const setterCalls = [];
  const lib = {
    createElement: h,
    useState: (initial) => [initial, (arg) => setterCalls.push(arg)],
    useEffect() {},
  };
  const catalog = makeCatalog(lib, () => {});
  const render = (props) => catalog.Counter(props);

  let el = render({});
  assert.equal(el.props.id, "c");
  const [button, span] = el.props.children;
  assert.equal(button.props.id, "c-inc");
  assert.equal(span.props.id, "c-count");
  eq(span.props.children, [{ type: "TEXT_ELEMENT", props: { nodeValue: 0, children: [] } }]); // a number child
  button.props.onClick();
  assert.equal(setterCalls.length, 1);
  assert.equal(typeof setterCalls[0], "function");
  assert.equal(setterCalls[0](10), 11);

  setterCalls.length = 0;
  el = render({ id: "d", start: "7" });
  assert.equal(el.props.children[1].props.children[0].props.nodeValue, 7);
  assert.equal(el.props.children[0].props.id, "d-inc");
  el.props.children[0].props.onClick();
  assert.equal(setterCalls.length, 2); // two queued updaters in one handler
  assert.ok(setterCalls.every((f) => typeof f === "function" && f(1) === 2));
});

test("catalog: Keeper stores only the first setter; poke calls it with n => n + 1", () => {
  const setters = [];
  const lib = {
    createElement: h,
    useState: (initial) => {
      const setter = (arg) => setters.push([setter, arg]);
      return [initial, setter];
    },
    useEffect() {},
  };
  const catalog = makeCatalog(lib, () => {});
  assert.throws(() => catalog.poke(), /no Keeper/);
  catalog.Keeper({});
  catalog.Keeper({}); // a second Keeper render creates another setter, which is not stored
  const first = setters.length;
  catalog.poke();
  assert.equal(setters.length, first + 1);
  assert.equal(setters.at(-1)[1](4), 5);
  assert.ok(!Object.keys(catalog).includes("poke"));
});

test("catalog: effect components log the documented texts", () => {
  const logged = [];
  const effects = [];
  const lib = {
    createElement: h,
    useState: (initial) => [initial, () => {}],
    useEffect: (fn, deps) => effects.push({ fn, deps }),
  };
  const catalog = makeCatalog(lib, (t) => logged.push(t));
  const run = () => {
    const { fn } = effects.at(-1);
    const cleanup = fn();
    cleanup();
  };
  catalog.Logger({ name: "x" });
  eq(effects.at(-1).deps, []);
  run();
  catalog.LoggerDeps({ name: "y", dep: "3" });
  eq(effects.at(-1).deps, ["3"]);
  run();
  catalog.LoggerEvery({ name: "z" });
  assert.equal(effects.at(-1).deps, undefined);
  run();
  const outer = catalog.Outer({ name: "o" });
  eq(effects.at(-1).deps, []);
  run();
  assert.equal(outer.props.children[0].type, catalog.Logger);
  eq(outer.props.children[0].props.name, "o.inner");
  eq(logged, ["mount x", "cleanup x", "run y 3", "clean y 3", "run z", "clean z", "mount o", "cleanup o"]);
});

// =============================================================================================
// 3. the oracle (real React 19.3.1 on jsdom)
// =============================================================================================

const oracle = async (lines, options = {}) => runOracle(Array.isArray(lines) ? lines.join("\n") : lines, options);

test("oracle: tree, render, dump (labels, props, text)", async () => {
  eq(await oracle(["tree t <div id=a className=x>hi <b>there</b></div>", "render t", "dump"]), [
    "dump 1",
    'node 0 a div "className=x id=a"',
    'text 1 "hi "',
    'node 1 b b ""',
    'text 2 "there"',
  ]);
});

test("oracle: React keeps the node for the same type at the same position and replaces on a type change", async () => {
  eq(
    await oracle([
      "tree a <div id=x>1</div>",
      "tree b <div id=y className=k>2</div>",
      "tree c <p id=z>3</p>",
      "render a",
      "dump",
      "render b",
      "dump",
      "render c",
      "dump",
    ]),
    [
      "dump 1", 'node 0 a div "id=x"', 'text 1 "1"',
      "dump 2", 'node 0 a div "className=k id=y"', 'text 1 "2"',
      "dump 3", 'node 0 b p "id=z"', 'text 1 "3"',
    ],
  );
});

test("oracle: click dispatches a bubbling event inside act; flush is a no-op; log drains", async () => {
  eq(
    await oracle([
      "tree t <div id=outer onClick=@outer><button id=btn onClick=@inner>x</button></div>",
      "render t",
      "flush",
      "click #btn",
      "click #outer",
      "log",
      "log",
      "click #btn",
      "log",
    ]),
    ["log inner", "log outer", "log outer", "log inner", "log outer"],
  );
});

test("oracle: Counter state, two counters, the double-setter counter d", async () => {
  const lines = await oracle([
    "tree t <div><Counter start=5/><Counter id=d/><Counter id=e/></div>",
    "render t",
    "click #c-inc",
    "click #d-inc",
    "click #d-inc",
    "click #e-inc",
    "dump",
  ]);
  const counts = lines.filter((_, i) => lines[i - 1]?.includes("-count")).map((l) => l);
  eq(counts, ['text 3 "6"', 'text 3 "4"', 'text 3 "1"']);
});

test("oracle: MultiCounter, Greeting, Frame with children", async () => {
  const lines = await oracle([
    "tree t <Frame title=T><Greeting name=Ann/><MultiCounter/></Frame>",
    "render t",
    "click #mc-b",
    "click #mc-b",
    "click #mc-a",
    "dump",
  ]);
  eq(lines, [
    "dump 1",
    'node 0 a section ""',
    'node 1 b h2 ""',
    'text 2 "T"',
    'node 1 c h1 ""',
    'text 2 "Hi Ann"',
    'node 1 d div "id=mc"',
    'node 2 e button "id=mc-a"',
    'text 3 "a"',
    'node 2 f button "id=mc-b"',
    'text 3 "b"',
    'node 2 g span "id=mc-av"',
    'text 3 "1"',
    'node 2 h span "id=mc-bv"',
    'text 3 "2"',
  ]);
});

test("oracle: Toggle changes its root tag and the new node stays live", async () => {
  eq(await oracle(["tree t <Toggle/>", "render t", "dump", "click #t-btn", "dump", "click #t-btn", "dump"]), [
    "dump 1", 'node 0 a div "id=t"', 'node 1 b button "id=t-btn"', 'text 2 "toggle"', 'node 1 c span "id=t-state"', 'text 2 "off"',
    "dump 2", 'node 0 d section "className=on id=t"', 'node 1 e button "id=t-btn"', 'text 2 "toggle"', 'node 1 f span "id=t-state"', 'text 2 "on"',
    "dump 3", 'node 0 g div "id=t"', 'node 1 h button "id=t-btn"', 'text 2 "toggle"', 'node 1 i span "id=t-state"', 'text 2 "off"',
  ]);
});

test("oracle: poke calls the first Keeper's setter", async () => {
  eq(await oracle(["tree t <Keeper/>", "render t", "poke", "poke", "dump"]), ["dump 1", 'node 0 a p "id=keeper"', 'text 1 "2"']);
  await assert.rejects(oracle("poke"), /no Keeper/);
});

test("oracle: type on an uncontrolled input; the value shows in dump", async () => {
  eq(await oracle(["tree t <div><input id=i/><input id=j/></div>", "render t", "type #i hello  world", "type #j x", "dump"]), [
    "dump 1",
    'node 0 a div ""',
    'node 1 b input "id=i value=hello%20%20world"',
    'node 1 c input "id=j value=x"',
  ]);
});

test("oracle: idle and ops print placeholders; call/props/show/create/update are refused", async () => {
  eq(await oracle(["tree t <p>x</p>", "render t", "idle 3", "ops", "ops create remove", "idle inf"]), ["idle ?", "ops ?", "ops ?", "idle ?"]);
  for (const line of ['call div null', 'props p {}', "show p", "create div", "update id=a"]) {
    await assert.rejects(oracle(line), /does not support it/, line);
  }
});

test("oracle: errors name the scenario line", async () => {
  await assert.rejects(oracle("dump\nbogus"), (err) => err.scenarioLine === 2 && /unknown command/.test(err.message));
  await assert.rejects(oracle("tree t <Nope/>\nrender t"), /unknown component/);
});

test("oracle: the todo app, typed into a controlled input and submitted", async () => {
  const warnings = [];
  const lines = await oracle(
    [
      "tree t <TodoApp/>",
      "render t",
      "dump",
      "type #todo-input buy milk",
      "submit #todo-form",
      "type #todo-input    ",
      "submit #todo-form",
      "type #todo-input write \"tests\" 100%",
      "submit #todo-form",
      "click #toggle-1",
      "dump",
      "click #remove-2",
      "dump",
    ],
    { warnings },
  );
  eq(warnings, []);
  eq(lines.slice(0, 11), [
    "dump 1",
    'node 0 a div "id=todo"',
    'node 1 b form "id=todo-form"',
    'node 2 c input "id=todo-input"',
    'node 2 d button "id=todo-add"',
    'text 3 "Add"',
    'node 1 e ul "id=todo-list"',
    'node 1 f p "id=todo-count"',
    'text 2 "0 left"',
    'title "0 left"',
    "dump 2",
  ]);
  // dump 2: item 2 (newest) first, item 1 done; one left; the input was cleared by the last add
  const second = lines.slice(10, lines.indexOf("dump 3"));
  eq(second.filter((l) => l.includes("li ")), ['node 2 g li "id=item-2"', 'node 2 k li "id=item-1"']);
  assert.ok(second.includes('text 4 "write %22tests%22 100%25"'));
  assert.ok(second.includes('node 3 m span "className=done id=label-1"'));
  assert.ok(second.includes('text 4 "done"'));
  assert.ok(second.includes('node 2 c input "id=todo-input"'));
  assert.ok(second.includes('text 2 "1 left"'));
  assert.equal(second.at(-1), 'title "1 left"');
  const third = lines.slice(lines.indexOf("dump 3"));
  eq(third.filter((l) => l.includes("li ")), ['node 2 k li "id=item-1"']);
  assert.equal(third.at(-1), 'title "0 left"');
});

test("oracle: clicking the Add button submits the form in jsdom, like the harness does", async () => {
  const typed = ["tree t <TodoApp/>", "render t", "type #todo-input x"];
  const viaClick = await oracle([...typed, "click #todo-add", "dump"]);
  const viaSubmit = await oracle([...typed, "submit #todo-form", "dump"]);
  eq(viaClick, viaSubmit);
  assert.ok(viaClick.includes('text 4 "x"'));
});

test("oracle: effect logs of Outer (nested) in mount and unmount", async () => {
  eq(await oracle(["tree o <Outer name=o/>", "tree p <p>x</p>", "render o", "log", "render p", "log"]), [
    "log mount o.inner",
    "log mount o",
    "log cleanup o",
    "log cleanup o.inner",
  ]);
});

test("oracle: calls may run in parallel and still give the sequential answers", async () => {
  const a = ["tree t <TodoApp/>", "render t", "type #todo-input a", "submit #todo-form", "dump"].join("\n");
  const b = ["tree t <Counter/>", "render t", "click #c-inc", "dump"].join("\n");
  const [ra, rb] = await Promise.all([runOracle(a), runOracle(b), runOracle(a)]);
  eq(ra, await runOracle(a));
  eq(rb, await runOracle(b));
  assert.equal(globalThis.document.getElementById("root").tagName, "DIV"); // the minidom global is back in place
});

// What React 19.3.1 does, pinned: _source/react-observed.md describes these. If a React upgrade changes
// one of them, this fails first.
const PINNED_EFFECTS = [
  ["mount: children before parents, siblings in order", ["tree t <Frame title=T><Outer name=o/><Outer name=p/></Frame>", "render t", "log"], ["mount o.inner", "mount o", "mount p.inner", "mount p"]],
  ["unmount: parents before children, siblings in order", ["tree t <div><Outer name=o/><Logger name=l/></div>", "tree u <p>x</p>", "render t", "log", "render u", "log"], ["mount o.inner", "mount o", "mount l", "cleanup o", "cleanup o.inner", "cleanup l"]],
  ["deps change: cleanup then run; same deps: nothing", ["tree a <LoggerDeps name=x dep=1/>", "tree b <LoggerDeps name=x dep=2/>", "render a", "render b", "render b", "log"], ["run x 1", "clean x 1", "run x 2"]],
  ["deps unchanged but other props changed: the effect does not run again", ["tree a <LoggerDeps name=a dep=1/>", "tree b <LoggerDeps name=b dep=1/>", "render a", "render b", "log"], ["run a 1"]],
  ["a cleanup is the one of the render that ran the effect (name a, though last rendered as b)", ["tree a <LoggerDeps name=a dep=1/>", "tree b <LoggerDeps name=b dep=1/>", "tree u <p>x</p>", "render a", "render b", "render u", "log"], ["run a 1", "clean a 1"]],
  ["every render: cleanup then run after each click", ["tree t <LoggerEvery name=e/>", "render t", "log", "click #e-btn", "log", "click #e-btn", "log"], ["run e", "clean e", "run e", "clean e", "run e"]],
  ["parent re-render with unchanged child deps: nothing logged", ["tree a <div><LoggerDeps name=x dep=1/></div>", "tree b <div className=k><LoggerDeps name=x dep=1/></div>", "render a", "log", "render b", "log"], ["run x 1"]],
  ["siblings, both deps change: all cleanups before any run", ["tree a <div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>", "tree b <div><LoggerDeps name=a dep=2/><LoggerDeps name=b dep=2/></div>", "render a", "log", "render b", "log"], ["run a 1", "run b 1", "clean a 1", "clean b 1", "run a 2", "run b 2"]],
  ["a replaced tree: cleanups of the old before the mounts of the new", ["tree a <div><Logger name=x/><LoggerDeps name=a dep=1/></div>", "tree b <section><LoggerDeps name=b dep=1/></section>", "render a", "log", "render b", "log"], ["mount x", "run a 1", "cleanup x", "clean a 1", "run b 1"]],
  ["a deletion inside a fiber is cleaned before that fiber's children", ["tree a <div><LoggerDeps name=a dep=1/><Logger name=x/></div>", "tree b <div><LoggerDeps name=a dep=2/></div>", "render a", "log", "render b", "log"], ["run a 1", "mount x", "cleanup x", "clean a 1", "run a 2"]],
  ["traversal order, not deletions first: an earlier update is cleaned before a deeper deletion", ["tree a <div><LoggerDeps name=a dep=1/><Frame title=A><Logger name=x/></Frame></div>", "tree b <div><LoggerDeps name=a dep=2/><Frame title=A></Frame></div>", "render a", "log", "render b", "log"], ["run a 1", "mount x", "clean a 1", "cleanup x", "run a 2"]],
  ["keyed reorder keeps component instances: no effect runs", ["tree a <div><LoggerDeps key=a name=a dep=1/><LoggerDeps key=b name=b dep=1/></div>", "tree b <div><LoggerDeps key=b name=b dep=1/><LoggerDeps key=a name=a dep=1/></div>", "render a", "log", "render b", "log"], ["run a 1", "run b 1"]],
  ["a component key change remounts", ["tree a <div><Logger key=a name=a/></div>", "tree b <div><Logger key=b name=b/></div>", "render a", "render b", "log"], ["mount a", "cleanup a", "mount b"]],
];

for (const [name, lines, expected] of PINNED_EFFECTS) {
  test("react 19.3.1 effects: " + name, async () => {
    const out = await oracle(lines);
    eq(out.map((l) => l.replace(/^log /, "")), expected);
  });
}

test("react 19.3.1 identity: same type keeps the node, a type change in the middle replaces only that node", async () => {
  const out = await oracle(["tree a <div><p>1</p><b>2</b><i>3</i></div>", "tree b <div><p>1</p><u>2</u><i>3</i></div>", "render a", "dump", "render b", "dump"]);
  eq(out.filter((l) => l.startsWith("node")).map((l) => l.split(" ").slice(2, 4).join(":")), ["a:div", "b:p", "c:b", "d:i", "a:div", "b:p", "e:u", "d:i"]);
});

test("react 19.3.1 identity: keyed insert at the front, keyed reverse (typed values follow), key change, unkeyed to keyed", async () => {
  const labelsOf = (out, which) => {
    const start = out.indexOf("dump " + which);
    const end = out.findIndex((l, i) => i > start && l.startsWith("dump "));
    return out.slice(start, end < 0 ? undefined : end).filter((l) => l.startsWith("node")).map((l) => l.split(" ").slice(2, 4).join(":") + (l.match(/value=(\w+)/)?.[0] ? ":" + l.match(/value=(\w+)/)[1] : ""));
  };
  let out = await oracle(["tree a <ul><li key=a>A</li><li key=b>B</li></ul>", "tree b <ul><li key=z>Z</li><li key=a>A</li><li key=b>B</li></ul>", "render a", "dump", "render b", "dump"]);
  eq(labelsOf(out, 1), ["a:ul", "b:li", "c:li"]);
  eq(labelsOf(out, 2), ["a:ul", "d:li", "b:li", "c:li"]);

  out = await oracle(["tree a <div><input key=a id=ia/><input key=b id=ib/><input key=c id=ic/></div>", "tree b <div><input key=c id=ic/><input key=b id=ib/><input key=a id=ia/></div>", "render a", "type #ia 1", "type #ib 2", "type #ic 3", "dump", "render b", "dump"]);
  eq(labelsOf(out, 1), ["a:div", "b:input:1", "c:input:2", "d:input:3"]);
  eq(labelsOf(out, 2), ["a:div", "d:input:3", "c:input:2", "b:input:1"]);

  out = await oracle(["tree a <ul><li key=0>A</li><li key=1>B</li></ul>", "tree b <ul><li key=1>B</li><li key=0>A</li></ul>", "tree c <ul><li key=2>B</li><li key=0>A</li></ul>", "tree d <ul><li>B</li><li>A</li></ul>", "render a", "dump", "render b", "dump", "render c", "dump", "render d", "dump"]);
  eq(labelsOf(out, 2), ["a:ul", "c:li", "b:li"]); // key="0" is a real key: both kept, swapped
  eq(labelsOf(out, 3), ["a:ul", "d:li", "b:li"]); // key 1 -> 2: a new node
  eq(labelsOf(out, 4), ["a:ul", "e:li", "f:li"]); // keyed -> unkeyed: both replaced
});

test("react 19.3.1 identity: Toggle and FnA/FnB replace their nodes; state sticks to the position", async () => {
  let out = await oracle(["tree a <Toggle/>", "render a", "dump", "click #t-btn", "dump", "click #t-btn", "dump"]);
  eq(out.filter((l) => /^node 0/.test(l)), ['node 0 a div "id=t"', 'node 0 d section "className=on id=t"', 'node 0 g div "id=t"']);
  out = await oracle(["tree a <div><FnA/></div>", "tree b <div><FnB/></div>", "render a", "dump", "render b", "dump"]);
  eq(out.filter((l) => l.startsWith("node")), ["node 0 a div \"\"", "node 1 b i \"\"", "node 0 a div \"\"", "node 1 c b \"\""]);
  out = await oracle(["tree a <div><Counter id=a start=1/><Counter id=b start=10/></div>", "tree b <div><Counter id=b start=10/><Counter id=a start=1/></div>", "render a", "click #a-inc", "render b", "dump"]);
  eq(out.filter((l) => l.startsWith("node 1") || /^text 3 "[0-9]+"/.test(l)), ['node 1 b div "id=b"', 'text 3 "2"', 'node 1 e div "id=a"', 'text 3 "10"']);
});

// =============================================================================================
// 4. minidom against jsdom
// =============================================================================================

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function minidomSide() {
  const { document } = createDocument();
  const container = document.createElement("div");
  document.body.appendChild(container);
  return { name: "minidom", document, container, nodes: [], label: makeLabeler(), makeEvent: (type, init) => new MiniEvent(type, init) };
}

function jsdomSide() {
  const { window } = new JSDOM("<!doctype html><body></body>");
  const { document } = window;
  const container = document.createElement("div");
  document.body.appendChild(container);
  return { name: "jsdom", document, container, nodes: [], label: makeLabeler(), makeEvent: (type, init) => new window.Event(type, init) };
}

function attempt(fn) {
  try {
    fn();
    return "ok";
  } catch (err) {
    return err.name;
  }
}

const TAGS = ["div", "span", "button", "input", "textarea", "p", "ul", "li"];
const STRINGS = ["a", "b c", 'q"q', "100%", "x/y", "", "0", "e f g"];
const IDS = ["a", "b", "c d", "x"];

function nodeAt(side, index) {
  return index === -1 ? side.container : side.nodes[index];
}

// A textarea's value is its text content in a browser (until it is assigned); minidom does not model that,
// so the sequences never put children into a textarea.
const isTextarea = (s, p) => nodeAt(s, p).tagName === "TEXTAREA";

const OPERATIONS = {
  createElement: (s, tag) => s.nodes.push(s.document.createElement(tag)),
  createText: (s, text) => s.nodes.push(s.document.createTextNode(text)),
  append: (s, p, c) => isTextarea(s, p) || nodeAt(s, p).appendChild(nodeAt(s, c)),
  insertBefore: (s, p, c, r) => isTextarea(s, p) || nodeAt(s, p).insertBefore(nodeAt(s, c), r === null ? null : nodeAt(s, r)),
  removeChild: (s, p, c) => nodeAt(s, p).removeChild(nodeAt(s, c)),
  replaceChild: (s, p, n, o) => isTextarea(s, p) || nodeAt(s, p).replaceChild(nodeAt(s, n), nodeAt(s, o)),
  remove: (s, c) => nodeAt(s, c).remove(),
  setId: (s, i, v) => {
    nodeAt(s, i).id = v;
  },
  setProp: (s, i, name, v) => {
    nodeAt(s, i)[name] = v;
  },
  setText: (s, i, how, v) => {
    if (how !== "textContent" || !isTextarea(s, i)) nodeAt(s, i)[how] = v;
  },
};

function randomStep(rng, count) {
  const pick = (list) => list[Math.floor(rng() * list.length)];
  const any = () => Math.floor(rng() * count); // any node
  const parent = () => (rng() < 0.3 ? -1 : any());
  const r = rng();
  if (count < 3 || r < 0.22) return ["createElement", pick(TAGS)];
  if (r < 0.32) return ["createText", pick(STRINGS)];
  if (r < 0.5) return ["append", parent(), any()];
  if (r < 0.66) return ["insertBefore", parent(), any(), rng() < 0.2 ? null : any()];
  if (r < 0.76) return ["removeChild", parent(), any()];
  if (r < 0.82) return ["replaceChild", parent(), any(), any()];
  if (r < 0.86) return ["remove", any()];
  if (r < 0.91) return ["setId", any(), pick(IDS)];
  if (r < 0.96) return ["setProp", any(), pick(["className", "title", "value", "disabled"]), rng() < 0.2 ? true : pick(STRINGS)];
  return ["setText", any(), pick(["nodeValue", "data", "textContent"]), pick(STRINGS)];
}

function snapshot(side) {
  const index = new Map(side.nodes.map((n, i) => [n, i]));
  index.set(side.container, -1);
  const rel = (n) => (n === null ? null : (index.get(n) ?? "foreign"));
  return {
    dump: dumpTree(side.container, side.label),
    relations: side.nodes.map((n) => [
      rel(n.parentNode),
      rel(n.previousSibling),
      rel(n.nextSibling),
      rel(n.firstChild),
      rel(n.lastChild),
      n.childNodes.length,
      n.nodeType,
    ]),
    text: side.container.textContent,
    byId: IDS.map((id) => rel(side.document.getElementById(id))),
    containsAll: side.nodes.map((n) => side.container.contains(n)),
  };
}

test("minidom vs jsdom: random DOM operation sequences give the same dumps, errors and relations", () => {
  let steps = 0;
  let errors = 0;
  for (let seed = 1; seed <= 150; seed++) {
    const rng = mulberry32(seed);
    const mini = minidomSide();
    const real = jsdomSide();
    const history = [];
    for (let step = 0; step < 70; step++) {
      const op = randomStep(rng, mini.nodes.length);
      history.push(op.join(","));
      const [name, ...args] = op;
      const a = attempt(() => OPERATIONS[name](mini, ...args));
      const b = attempt(() => OPERATIONS[name](real, ...args));
      const context = `seed ${seed} step ${step}: ${history.slice(-6).join(" | ")}`;
      assert.equal(a, b, `outcome differs (${a} vs ${b}) at ${context}`);
      if (a !== "ok") errors++;
      assert.deepEqual(snapshot(mini), snapshot(real), `state differs at ${context}`);
      steps++;
    }
  }
  assert.ok(errors > 100 && errors < steps / 2, `the sequences should include a fair share of errors, got ${errors} of ${steps}`);
});

test("minidom vs jsdom: listeners and events give the same call sequences", () => {
  let dispatches = 0;
  for (let seed = 1; seed <= 120; seed++) {
    const rng = mulberry32(1000 + seed);
    const pick = (list) => list[Math.floor(rng() * list.length)];
    const size = 6;
    // one script of steps, applied to both sides
    const parents = Array.from({ length: size - 1 }, (_, i) => Math.floor(rng() * (i + 1)));
    const script = Array.from({ length: 60 }, () => {
      const r = rng();
      return {
        kind: r < 0.35 ? "add" : r < 0.5 ? "remove" : "dispatch",
        node: Math.floor(rng() * size),
        type: pick(["click", "input"]),
        id: Math.floor(rng() * 4),
        init: { bubbles: rng() < 0.8, cancelable: rng() < 0.5 },
      };
    });
    const sides = [minidomSide(), jsdomSide()];
    for (const side of sides) {
      side.nodes.push(side.document.createElement("div"));
      parents.forEach((parent, i) => {
        side.nodes.push(side.document.createElement("div"));
        side.nodes[parent].appendChild(side.nodes[i + 1]);
      });
      side.container.appendChild(side.nodes[0]);
      side.log = [];
      const indexOf = (n) => (n === null ? "null" : side.nodes.indexOf(n));
      side.listeners = [0, 1, 2, 3].map(
        (id) =>
          function listener(ev) {
            side.log.push(`L${id} this=${indexOf(this)} cur=${indexOf(ev.currentTarget)} target=${indexOf(ev.target)} ${ev.type} prevented=${ev.defaultPrevented}`);
            if (id === 1) ev.preventDefault();
            if (id === 2) ev.stopPropagation();
            if (id === 3) ev.stopImmediatePropagation();
          },
      );
    }
    script.forEach((step, index) => {
      const outcomes = sides.map((side) => {
        const node = side.nodes[step.node];
        if (step.kind === "add") node.addEventListener(step.type, side.listeners[step.id]);
        else if (step.kind === "remove") node.removeEventListener(step.type, side.listeners[step.id]);
        else {
          side.log.length = 0;
          const returned = node.dispatchEvent(side.makeEvent(step.type, step.init));
          return `${returned}: ${side.log.join(" ; ")}`;
        }
        return step.kind;
      });
      if (step.kind === "dispatch") dispatches++;
      assert.equal(outcomes[0], outcomes[1], `seed ${seed} step ${index} (${JSON.stringify(step)})`);
    });
  }
  assert.ok(dispatches > 1000);
});

// =============================================================================================
// run
// =============================================================================================

let failed = 0;
for (const { name, fn } of tests) {
  try {
    await fn();
    console.log(`ok   ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL ${name}`);
    console.log(String(err?.stack ?? err).replace(/^/gm, "     "));
  }
}
await closeOracle();
console.log(`\n${tests.length - failed} of ${tests.length} checks passed`);
process.exitCode = failed ? 1 : 0;
