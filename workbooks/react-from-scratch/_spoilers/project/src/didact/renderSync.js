// Assignment 03: the first draft of render. The recursion cannot be interrupted halfway;
// assignment 04 replaces it with a work loop and nothing imports this file after that.
import { createDom } from './dom.js';

export function render(element, container) {
  const dom = createDom(element);
  element.props.children.forEach((child) => render(child, dom));
  container.appendChild(dom);
}
