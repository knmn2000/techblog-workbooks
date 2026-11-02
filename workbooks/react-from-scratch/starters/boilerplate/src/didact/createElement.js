// ======================================================================================
// Assignment 01: Create elements
// Problem: problems/01-create-element.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   What JSX compiles to: a plain `{ type, props }` object, with the children inside
//   `props`.
//
// Your job:
//   Write `createElement(type, props, ...children)`, which returns the element `{ type,
//   props }` with every child inside `props.children`, and `createTextElement(text)`,
//   which wraps a string or number as the text element that goes there. The Boilerplate
//   gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

// An element is a plain object that describes one piece of a page. For example,
//   createElement("h1", { id: "title" }, "Hello")
// returns
//   { type: "h1", props: { id: "title", children: [ <a text element holding "Hello"> ] } }

/**
 * @param {string} type  the tag name, such as "div" or "h1"
 * @param {object | null} props  the attributes as keys and values, or null for none
 * @param {...(string | number | object)} children  what goes inside: text, numbers and other elements
 * @returns {{ type: string, props: object }}  `props` has every given prop plus `children`, an array of elements
 */
export function createElement(type, props, ...children) {
  // TODO: see "What goes in", "What comes out" and "The details that the tests check" on the page.
  throw new Error('not implemented: createElement');
}

/**
 * @param {string | number} text  one string or number child
 * @returns {{ type: "TEXT_ELEMENT", props: { nodeValue: string | number, children: [] } }}
 */
export function createTextElement(text) {
  // TODO: see "Text elements, and why createTextElement exists" on the page.
  throw new Error('not implemented: createTextElement');
}
