// markup.js - a tiny one-line markup language for describing element trees in scenario files.
//
//   <div id="a" className=big disabled onClick=@one>text <b>nested</b></div>
//   <Counter id="d" start=5/>
//
// Rules:
//   - A tag that starts with a capital letter is a component, looked up by name (see buildElement).
//   - Attribute values are strings. Write them bare (id=a), "double quoted" or 'single quoted'; there are
//     no escapes, so use the other kind of quote for a value that contains one.
//   - A bare attribute (no "=") means true.
//   - A value that starts with "@" is a handler: @one stands for one function that appends "one" to the
//     log. The same name always gives the same function.
//   - Text between tags is kept as it is, with its inner spaces. Text that is only whitespace between
//     tags is dropped. There are no character entities.
//   - input, br, hr and img need no closing tag (a closing tag is allowed right after them).
//   - key="k" is an ordinary string attribute.

const VOID_TAGS = new Set(["input", "br", "hr", "img"]);

/** A handler placeholder in a parsed tree or attribute list. */
function handlerRef(name) {
  return { handler: name };
}

function isHandlerRef(value) {
  return typeof value === "object" && value !== null && typeof value.handler === "string";
}

function markupError(source, index, message) {
  return new Error(`markup: ${message} at position ${index} in: ${source}`);
}

// ---------------------------------------------------------------------------------------------
// attributes

function isSpace(ch) {
  return ch === " " || ch === "\t" || ch === "\n" || ch === "\r";
}

/**
 * Reads attributes starting at `p.i` until the end of the text or until `>` or `/>` (when `stopAtTag`).
 * Returns an object {name: string | true | {handler}}.
 */
function readAttributes(p, stopAtTag) {
  const attrs = {};
  const s = p.s;
  for (;;) {
    while (p.i < s.length && isSpace(s[p.i])) p.i++;
    if (p.i >= s.length) {
      if (stopAtTag) throw markupError(s, p.i, "the tag is not closed");
      return attrs;
    }
    if (stopAtTag && (s[p.i] === ">" || (s[p.i] === "/" && s[p.i + 1] === ">"))) return attrs;

    const start = p.i;
    while (p.i < s.length && !isSpace(s[p.i]) && s[p.i] !== "=" && s[p.i] !== ">" && !(s[p.i] === "/" && s[p.i + 1] === ">")) p.i++;
    const name = s.slice(start, p.i);
    if (name === "") throw markupError(s, p.i, "expected an attribute name");

    let value = true;
    if (s[p.i] === "=") {
      p.i++;
      const quote = s[p.i];
      if (quote === '"' || quote === "'") {
        const end = s.indexOf(quote, p.i + 1);
        if (end < 0) throw markupError(s, p.i, "unterminated quoted value");
        value = s.slice(p.i + 1, end);
        p.i = end + 1;
      } else {
        const from = p.i;
        while (p.i < s.length && !isSpace(s[p.i]) && s[p.i] !== ">" && !(s[p.i] === "/" && s[p.i + 1] === ">")) p.i++;
        value = s.slice(from, p.i);
      }
      if (value.startsWith("@")) value = handlerRef(value.slice(1));
    }
    attrs[name] = value;
  }
}

/** Parses `name=value flag name="a b" onClick=@h` into an object (handlers become {handler: name}). */
export function parseAttributes(text) {
  return readAttributes({ s: text, i: 0 }, false);
}

/** Replaces the handler placeholders of an attribute object by functions from `handler(name)`. */
export function resolveHandlers(attrs, handler) {
  const props = {};
  for (const [name, value] of Object.entries(attrs)) props[name] = isHandlerRef(value) ? handler(value.handler) : value;
  return props;
}

/**
 * Returns handler(name): a memoised function per name that calls record(name). `record` is where the
 * run's log lines go.
 */
export function makeHandlers(record) {
  const known = new Map();
  return function handler(name) {
    let fn = known.get(name);
    if (fn === undefined) {
      fn = () => record(name);
      known.set(name, fn);
    }
    return fn;
  };
}

// ---------------------------------------------------------------------------------------------
// trees

/**
 * Parses one element tree. The result is {tag, attrs, children} where attrs is as for parseAttributes
 * and children is a list of strings and nested trees.
 */
export function parseMarkup(source) {
  const p = { s: source, i: 0 };
  skipSpaces(p);
  if (source[p.i] !== "<") throw markupError(source, p.i, "expected a tag");
  const tree = readElement(p);
  skipSpaces(p);
  if (p.i < source.length) throw markupError(source, p.i, "unexpected text after the root element");
  return tree;
}

function skipSpaces(p) {
  while (p.i < p.s.length && isSpace(p.s[p.i])) p.i++;
}

function readElement(p) {
  const s = p.s;
  p.i++; // "<"
  const start = p.i;
  while (p.i < s.length && /[A-Za-z0-9_.:-]/.test(s[p.i])) p.i++;
  const tag = s.slice(start, p.i);
  if (!/^[A-Za-z]/.test(tag)) throw markupError(s, start, "expected a tag name");

  const attrs = readAttributes(p, true);
  if (s[p.i] === "/") {
    p.i += 2; // "/>"
    return { tag, attrs, children: [] };
  }
  p.i++; // ">"

  if (VOID_TAGS.has(tag)) {
    const close = `</${tag}>`;
    if (s.startsWith(close, p.i)) p.i += close.length;
    return { tag, attrs, children: [] };
  }

  const children = [];
  for (;;) {
    if (p.i >= s.length) throw markupError(s, p.i, `missing </${tag}>`);
    if (s.startsWith("</", p.i)) {
      const end = s.indexOf(">", p.i);
      if (end < 0) throw markupError(s, p.i, "unterminated closing tag");
      const name = s.slice(p.i + 2, end).trim();
      if (name !== tag) throw markupError(s, p.i, `</${name}> does not match <${tag}>`);
      p.i = end + 1;
      return { tag, attrs, children };
    }
    if (s[p.i] === "<") {
      children.push(readElement(p));
    } else {
      const next = s.indexOf("<", p.i);
      const text = s.slice(p.i, next < 0 ? s.length : next);
      p.i += text.length;
      if (text.trim() !== "") children.push(text);
    }
  }
}

/**
 * Builds an element from a parsed tree.
 *   h(type, props, ...children)  the builder to use (the harness's `h` below, or React.createElement)
 *   component(name)              returns the function for a capitalised tag
 *   handler(name)                returns the function for @name (see makeHandlers)
 * An element without attributes gets props null.
 */
export function buildElement(tree, { h, component, handler }) {
  const type = /^[A-Z]/.test(tree.tag) ? component(tree.tag) : tree.tag;
  const names = Object.keys(tree.attrs);
  const props = names.length === 0 ? null : resolveHandlers(tree.attrs, handler);
  const children = tree.children.map((child) => (typeof child === "string" ? child : buildElement(child, { h, component, handler })));
  return h(type, props, ...children);
}

/**
 * The harness's own element builder, so that assignments from 02 on do not depend on your
 * createElement. It returns the element format of assignment 01: {type, props: {..., children}},
 * where a string or number child becomes a TEXT_ELEMENT and an object child passes through.
 */
export function h(type, props, ...children) {
  return {
    type,
    props: {
      ...props,
      children: children.map((child) =>
        typeof child === "object" && child !== null
          ? child
          : { type: "TEXT_ELEMENT", props: { nodeValue: child, children: [] } },
      ),
    },
  };
}
