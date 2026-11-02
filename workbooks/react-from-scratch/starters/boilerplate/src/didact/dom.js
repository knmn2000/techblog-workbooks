// ======================================================================================
// Assignment 02: DOM nodes and props
// Problem: problems/02-dom-props.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Two jobs on a single DOM node: build it from an element, and bring its properties and
//   listeners in line with new props.
//
// Your job:
//   Write `createDom(element)`, which builds the DOM node for an element, and
//   `updateDom(dom, prevProps, nextProps)`, which changes a node from one set of props to
//   the next and writes only what differs: new and changed properties are set, removed
//   ones are cleared, and a listener is swapped when its handler changed. The Boilerplate
//   gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

// createDom turns an element into a real DOM node, and updateDom keeps that node in step with new props.
// For example, with a button that has an id and a click handler:
//   const dom = createDom({ type: "button", props: { id: "b", onClick: handlerA, children: [] } })
//   updateDom(dom, { id: "b", onClick: handlerA }, { id: "c", onClick: handlerB })
// The update sets dom.id to "c", takes handlerA off the "click" event and puts handlerB on.

/**
 * @param {{ type: string, props: object }} element  an element from assignment 01; type "TEXT_ELEMENT" means a text node
 * @returns {Node}  a new DOM node (a text node or an element), not attached to anything
 */
export function createDom(element) {
  // TODO: see "What each prop becomes on a node" and Requirements R1 to R5 on the page.
  throw new Error('not implemented: createDom');
}

/**
 * @param {Node} dom  the node that currently shows prevProps
 * @param {object} prevProps  the props the node shows now
 * @param {object} nextProps  the props it should show; the node is changed to match, writing as little as possible
 * @returns {void}
 */
export function updateDom(dom, prevProps, nextProps) {
  // TODO: see "Writing as little as possible" and Requirements R2 and R4 to R9 on the page.
  throw new Error('not implemented: updateDom');
}
