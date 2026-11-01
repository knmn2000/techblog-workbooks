// Assignment 01: an element is a plain { type, props } object, with the children inside props.

// What JSX compiles to. A string or number child has no element of its own, so it gets a text
// element; an object child is already an element and passes through.
export function createElement(type, props, ...children) {
  return {
    type,
    props: {
      ...props,
      children: children.map((child) => (typeof child === 'object' ? child : createTextElement(child))),
    },
  };
}

// The element for a piece of text: its content travels as the nodeValue prop.
export function createTextElement(text) {
  return { type: 'TEXT_ELEMENT', props: { nodeValue: text, children: [] } };
}
