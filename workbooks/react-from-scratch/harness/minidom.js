// minidom.js - a small DOM for the workbook harness.
//
// It implements just the part of the browser DOM that the assignments use, and it behaves like a
// browser where that matters for correctness: removeChild of a node that is not a child throws,
// insertBefore with a reference that is not a child throws, appendChild of a node that already has a
// parent moves it, listeners are matched by event type and function identity, and events bubble
// from the target up through its ancestors.
//
// On top of that it counts what your code does to the DOM (see STAT_NAMES), so a test can tell
// "rebuilt the whole list" from "moved one node".
//
// How the counting works: every node is wrapped in a Proxy whose `set` trap counts one `write` for
// each property assignment made from outside (`el.id = "a"`, `el.onclick = f`, `text.nodeValue = "x"`,
// `el.anything = 1`). The node's own bookkeeping (parent, children, listeners) lives in a hidden record
// that is read and written directly, never through the proxy, so it is never counted.
//
// Not implemented on purpose: attributes (setAttribute), style, innerHTML, default actions (a click on
// a submit button does not submit the form), and "on<type>" handler properties (events reach only the
// listeners added with addEventListener).

const INTERNAL = Symbol("minidom.internal");
const INSPECT = Symbol.for("nodejs.util.inspect.custom");

export const ELEMENT_NODE = 1;
export const TEXT_NODE = 3;

/** The counters of `stats()`, in the order that `ops` prints them. */
export const STAT_NAMES = ["create", "insert", "move", "remove", "write", "addListener", "removeListener"];

// ---------------------------------------------------------------------------------------------
// helpers

function domError(name, message) {
  return new DOMException(message, name);
}

/** The hidden record of a node; throws a TypeError when `node` is not a minidom node. */
function rec(node) {
  const r = node?.[INTERNAL];
  if (r === undefined) throw new TypeError("minidom: expected a minidom node");
  return r;
}

function asNode(value, method, position) {
  if (value?.[INTERNAL] === undefined) {
    throw new TypeError(`Failed to execute '${method}' on 'Node': parameter ${position} is not of type 'Node'.`);
  }
  return value;
}

/** True when `ancestor` is `node` or one of its ancestors. */
function isInclusiveAncestor(ancestor, node) {
  for (let n = node; n; n = rec(n).parent) if (n === ancestor) return true;
  return false;
}

function siblingOf(node, offset) {
  const parent = rec(node).parent;
  if (!parent) return null;
  const list = rec(parent).children;
  return list[list.indexOf(node) + offset] ?? null;
}

/** Takes `node` out of its parent's child list (no statistics). */
function unlink(node) {
  const r = rec(node);
  const list = rec(r.parent).children;
  list.splice(list.indexOf(node), 1);
  r.parent = null;
}

function requireContainer(parent, method) {
  if (rec(parent).nodeType !== ELEMENT_NODE) {
    throw domError("HierarchyRequestError", `Failed to execute '${method}' on 'Node': This node type does not support this method.`);
  }
}

function insertNode(parent, node, before, method) {
  requireContainer(parent, method);
  asNode(node, method, 1);
  if (isInclusiveAncestor(node, parent)) {
    throw domError("HierarchyRequestError", `Failed to execute '${method}' on 'Node': The new child element contains the parent.`);
  }
  let ref = before ?? null;
  if (ref !== null) {
    asNode(ref, method, 2);
    if (rec(ref).parent !== parent) {
      throw domError("NotFoundError", `Failed to execute '${method}' on 'Node': The node before which the new node is to be inserted is not a child of this node.`);
    }
    if (ref === node) ref = siblingOf(node, +1); // inserting a node before itself keeps its place
  }
  const p = rec(parent);
  const n = rec(node);
  const moved = n.parent !== null;
  if (moved) unlink(node);
  const at = ref === null ? p.children.length : p.children.indexOf(ref);
  p.children.splice(at, 0, node);
  n.parent = parent;
  p.world.count(moved ? "move" : "insert");
  return node;
}

function removeNode(parent, child, method) {
  asNode(child, method, 1);
  if (rec(child).parent !== parent) {
    throw domError("NotFoundError", `Failed to execute '${method}' on 'Node': The node to be removed is not a child of this node.`);
  }
  unlink(child);
  rec(parent).world.count("remove");
  return child;
}

function collectText(node) {
  let text = "";
  for (const child of rec(node).children) {
    const r = rec(child);
    text += r.nodeType === TEXT_NODE ? r.value : collectText(child);
  }
  return text;
}

// ---------------------------------------------------------------------------------------------
// events

export class MiniEvent {
  constructor(type, init = {}) {
    this.type = String(type);
    this.target = null;
    this.currentTarget = null;
    this.bubbles = init.bubbles ?? true;
    this.cancelable = init.cancelable ?? false;
    this.defaultPrevented = false;
    this.cancelBubble = false;
    this.immediateStopped = false;
  }

  preventDefault() {
    if (this.cancelable) this.defaultPrevented = true;
  }

  stopPropagation() {
    this.cancelBubble = true;
  }

  stopImmediatePropagation() {
    this.cancelBubble = true;
    this.immediateStopped = true;
  }
}

// ---------------------------------------------------------------------------------------------
// nodes
//
// Constructors of the node classes must not assign to `this` after `super()`: `this` is the proxy by
// then, and an assignment would be counted as a write. Everything goes into the record instead.

export class MiniNode {
  constructor(world, nodeType, extra) {
    const r = { world, nodeType, parent: null, children: [], listeners: new Map(), self: null, ...extra };
    Object.defineProperty(this, INTERNAL, { value: r });
    r.self = new Proxy(this, world.handler);
    return r.self;
  }

  get nodeType() { return rec(this).nodeType; }
  get parentNode() { return rec(this).parent; }
  get parentElement() { return rec(this).parent; } // a parent is always an element here
  get childNodes() { return rec(this).children; } // live; do not modify it, use the methods below
  get firstChild() { return rec(this).children[0] ?? null; }
  get lastChild() { const list = rec(this).children; return list[list.length - 1] ?? null; }
  get nextSibling() { return siblingOf(rec(this).self, +1); }
  get previousSibling() { return siblingOf(rec(this).self, -1); }
  get ownerDocument() { return rec(this).world.document; }
  get nodeValue() { return null; }
  set nodeValue(_) {} // like a browser: assigning nodeValue on an element does nothing

  appendChild(node) {
    return insertNode(rec(this).self, node, null, "appendChild");
  }

  insertBefore(node, ref) {
    if (arguments.length < 2) {
      throw new TypeError("Failed to execute 'insertBefore' on 'Node': 2 arguments required, but only " + arguments.length + " present.");
    }
    return insertNode(rec(this).self, node, ref, "insertBefore");
  }

  removeChild(child) {
    return removeNode(rec(this).self, child, "removeChild");
  }

  replaceChild(node, old) {
    const self = rec(this).self;
    requireContainer(self, "replaceChild");
    asNode(node, "replaceChild", 1);
    asNode(old, "replaceChild", 2);
    if (isInclusiveAncestor(node, self)) {
      throw domError("HierarchyRequestError", "Failed to execute 'replaceChild' on 'Node': The new child element contains the parent.");
    }
    if (rec(old).parent !== self) {
      throw domError("NotFoundError", "Failed to execute 'replaceChild' on 'Node': The node to be replaced is not a child of this node.");
    }
    if (node === old) return old;
    let after = siblingOf(old, +1);
    if (after === node) after = siblingOf(node, +1);
    removeNode(self, old, "replaceChild");
    insertNode(self, node, after, "replaceChild");
    return old;
  }

  /** Removes this node from its parent (does nothing, and counts nothing, without a parent). */
  remove() {
    const r = rec(this);
    if (r.parent) removeNode(r.parent, r.self, "remove");
  }

  /** True for this node itself and for every descendant. */
  contains(other) {
    if (other === null || other === undefined) return false;
    asNode(other, "contains", 1);
    return isInclusiveAncestor(rec(this).self, other);
  }

  addEventListener(type, fn) {
    const r = rec(this);
    r.world.count("addListener");
    if (typeof fn !== "function") return; // like a browser: null and other non-callables are ignored
    const list = r.listeners.get(String(type)) ?? [];
    if (!list.includes(fn)) list.push(fn); // adding the same function twice has no effect
    r.listeners.set(String(type), list);
  }

  /** Matches on type and function identity; removing something that is not registered does nothing. */
  removeEventListener(type, fn) {
    const r = rec(this);
    r.world.count("removeListener");
    const list = r.listeners.get(String(type));
    const at = list ? list.indexOf(fn) : -1;
    if (at >= 0) list.splice(at, 1);
  }

  /**
   * Runs the listeners of the target, then of each ancestor (the event bubbles). Returns false when a
   * listener called preventDefault() on a cancelable event.
   */
  dispatchEvent(event) {
    const ev = event instanceof MiniEvent ? event : new MiniEvent(event?.type, event ?? {});
    const target = rec(this).self;
    ev.target = target;
    for (let node = target; node; node = rec(node).parent) {
      ev.currentTarget = node;
      const registered = rec(node).listeners.get(ev.type);
      if (registered) {
        for (const fn of [...registered]) {
          if (registered.includes(fn)) fn.call(node, ev); // skip listeners removed by an earlier listener
          if (ev.immediateStopped) break;
        }
      }
      if (!ev.bubbles || ev.cancelBubble) break;
    }
    ev.currentTarget = null;
    return !ev.defaultPrevented;
  }

  [INSPECT]() {
    return `[minidom ${rec(this).nodeType === TEXT_NODE ? "text" : "element"}]`;
  }
}

export class MiniText extends MiniNode {
  constructor(world, value) {
    super(world, TEXT_NODE, { value });
  }

  get nodeName() { return "#text"; }
  get nodeValue() { return rec(this).value; }
  set nodeValue(v) { rec(this).value = v === null ? "" : String(v); }
  get data() { return rec(this).value; }
  set data(v) { rec(this).value = v === null ? "" : String(v); }
  get textContent() { return rec(this).value; }
  set textContent(v) { rec(this).value = v === null ? "" : String(v); }
  get length() { return rec(this).value.length; }

  [INSPECT]() {
    return `[minidom text ${JSON.stringify(rec(this).value)}]`;
  }
}

export class MiniElement extends MiniNode {
  constructor(world, tag) {
    super(world, ELEMENT_NODE, { tag });
  }

  get tagName() { return rec(this).tag.toUpperCase(); }
  get localName() { return rec(this).tag.toLowerCase(); }
  get nodeName() { return rec(this).tag.toUpperCase(); }

  get textContent() { return collectText(rec(this).self); }

  /** Replaces all children with one text node (nothing for ""). Not counted: it is the DOM's own work. */
  set textContent(v) {
    const r = rec(this);
    for (const child of r.children) rec(child).parent = null;
    r.children.length = 0;
    const text = v === null || v === undefined ? "" : String(v);
    if (text !== "") {
      const node = new MiniText(r.world, text);
      rec(node).parent = r.self;
      r.children.push(node);
    }
  }

  [INSPECT]() {
    const own = Object.entries(this).map(([k, v]) => `${k}=${typeof v === "function" ? "[fn]" : JSON.stringify(v)}`);
    return `[minidom <${rec(this).tag.toLowerCase()}${own.length ? " " + own.join(" ") : ""}>]`;
  }
}

// Defaults that read like a browser's. They live on the prototype, so an assignment creates an own
// property on the node and a node that was never assigned reports the default.
Object.assign(MiniElement.prototype, { id: "", className: "", title: "", value: "", disabled: false });

// ---------------------------------------------------------------------------------------------
// the document

/**
 * Creates a document. Returns `{document, stats, resetStats, quiet}`:
 *   stats()       a fresh copy of the counters (see STAT_NAMES)
 *   resetStats()  sets every counter to zero
 *   quiet(fn)     runs fn without counting anything; the harness uses it for its own DOM work
 */
export function createDocument() {
  const counters = Object.fromEntries(STAT_NAMES.map((name) => [name, 0]));
  let paused = 0;

  const world = {
    document: null,
    count(name) {
      if (!paused) counters[name]++;
    },
    handler: {
      // Every assignment from outside code passes through here; internal bookkeeping never does.
      set(target, key, value) {
        if (typeof key === "symbol") return Reflect.set(target, key, value);
        if (!Reflect.set(target, key, value)) {
          throw new TypeError(`minidom: cannot assign to the read-only property "${key}"`);
        }
        world.count("write");
        return true;
      },
    },
  };

  const document = {
    nodeType: 9,
    nodeName: "#document",
    title: "",
    body: null,

    createElement(tag) {
      world.count("create");
      return new MiniElement(world, String(tag));
    },

    createTextNode(text) {
      world.count("create");
      return new MiniText(world, String(text));
    },

    /** Searches the live tree under `body`, in document order. */
    getElementById(id) {
      id = String(id);
      if (id === "") return null;
      const search = (node) => {
        if (rec(node).nodeType !== ELEMENT_NODE) return null;
        if (node.id === id) return node;
        for (const child of rec(node).children) {
          const found = search(child);
          if (found) return found;
        }
        return null;
      };
      return search(document.body);
    },
  };
  world.document = document;
  document.body = new MiniElement(world, "body");

  return {
    document,
    stats: () => ({ ...counters }),
    resetStats() {
      for (const name of STAT_NAMES) counters[name] = 0;
    },
    quiet(fn) {
      paused++;
      try {
        return fn();
      } finally {
        paused--;
      }
    },
  };
}
