// ---- Assignment 04: the work loop ----
// render() only schedules work. Whenever the browser is idle, workLoop() builds the tree of
// fibers one unit of work at a time, so it can stop when the browser has something else to do.
import { createDom } from './dom.js';
import { reconcileChildren } from './reconcile.js';
import { state } from './state.js';

// ---- Assignment 05: commit when the last unit is done ----
import { commitRoot } from './commit.js';

// ---- Assignment 04, until 06: schedule the work ----
export function render(element, container) {
  state.wipRoot = { dom: container, props: { children: [element] } };
  state.nextUnitOfWork = state.wipRoot;
}

// ---- Assignment 06: schedule the work against the tree on screen ----
export function render(element, container) {
  state.deletions = [];
  state.wipRoot = { dom: container, props: { children: [element] }, alternate: state.currentRoot };
  state.nextUnitOfWork = state.wipRoot;
}

// ---- Assignment 04, until 05: the loop ----
function workLoop(deadline) {
  try {
    let shouldYield = false;
    while (state.nextUnitOfWork && !shouldYield) {
      state.nextUnitOfWork = performUnitOfWork(state.nextUnitOfWork);
      shouldYield = deadline.timeRemaining() < 1;
    }
  } finally {
    requestIdleCallback(workLoop); // even after an error, or the loop would be dead for good
  }
}

// ---- Assignment 05: commit in the same period as the last unit ----
function workLoop(deadline) {
  try {
    let shouldYield = false;
    while (state.nextUnitOfWork && !shouldYield) {
      state.nextUnitOfWork = performUnitOfWork(state.nextUnitOfWork);
      shouldYield = deadline.timeRemaining() < 1;
    }
    if (!state.nextUnitOfWork && state.wipRoot) commitRoot();
  } finally {
    requestIdleCallback(workLoop);
  }
}

// ---- Assignment 04, until 05: one unit of work ----
// Makes the fiber's node, gives the fiber its children, and returns the fiber to do next.
function performUnitOfWork(fiber) {
  if (!fiber.dom) fiber.dom = createDom(fiber);
  if (fiber.parent) fiber.parent.dom.appendChild(fiber.dom);
  reconcileChildren(fiber, fiber.props.children);
  return nextFiber(fiber);
}

// ---- Assignment 05, until 09: one unit of work, without touching the page ----
function performUnitOfWork(fiber) {
  if (!fiber.dom) fiber.dom = createDom(fiber);
  reconcileChildren(fiber, fiber.props.children);
  return nextFiber(fiber);
}

// ---- Assignment 09: function components ----
function performUnitOfWork(fiber) {
  if (typeof fiber.type === 'function') updateFunctionComponent(fiber);
  else updateHostComponent(fiber);
  return nextFiber(fiber);
}

function updateHostComponent(fiber) {
  if (!fiber.dom) fiber.dom = createDom(fiber);
  reconcileChildren(fiber, fiber.props.children);
}

// ---- Assignment 09, until 10: a component's children are what it returns ----
function updateFunctionComponent(fiber) {
  reconcileChildren(fiber, [fiber.type(fiber.props)]);
}

// ---- Assignment 10: hooks belong to the fiber being rendered ----
function updateFunctionComponent(fiber) {
  state.wipFiber = fiber;
  state.hookIndex = 0;
  fiber.hooks = [];
  reconcileChildren(fiber, [fiber.type(fiber.props)]);
}

// ---- Assignment 04: which fiber is next ----
// Depth first: the child, else the sibling, else the nearest ancestor's sibling.
function nextFiber(fiber) {
  if (fiber.child) return fiber.child;
  for (let next = fiber; next; next = next.parent) {
    if (next.sibling) return next.sibling;
  }
  return null;
}

requestIdleCallback(workLoop);
