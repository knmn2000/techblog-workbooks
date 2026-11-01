// ---- Assignment 05: commit the finished tree in one pass ----
// The render phase builds fibers and DOM nodes but leaves the page alone; this applies the result.
import { state } from './state.js';

// ---- Assignment 06: update props of kept nodes ----
import { updateDom } from './dom.js';

// ---- Assignment 05, until 06: append every node ----
export function commitRoot() {
  commitWork(state.wipRoot.child);
  state.wipRoot = null;
}

function commitWork(fiber) {
  fiber.parent.dom.appendChild(fiber.dom);
  for (let child = fiber.child; child; child = child.sibling) commitWork(child);
}

// ---- Assignment 06, until 11: remove, place and update ----
export function commitRoot() {
  state.deletions.forEach(commitDeletion);
  commitWork(state.wipRoot);
  state.currentRoot = state.wipRoot;
  state.wipRoot = null;
}

// ---- Assignment 11: effects run after the commit ----
export function commitRoot() {
  const { deletions, wipRoot } = state;
  deletions.forEach(commitDeletion);
  commitWork(wipRoot);
  state.currentRoot = wipRoot;
  state.wipRoot = null;
  // An effect can start a new render, so the tree has to count as committed before they run.
  runEffects(deletions, wipRoot);
}

// ---- Assignment 06, until 08: act on the effect tags ----
function commitWork(fiber) {
  if (fiber.effectTag === 'PLACEMENT') {
    fiber.parent.dom.insertBefore(fiber.dom, nextStableDom(fiber));
  } else if (fiber.effectTag === 'UPDATE') {
    updateDom(fiber.dom, fiber.alternate.props, fiber.props);
  }
  // The fiber's old twin stays for now. The one before it is garbage: cut the link to it, or
  // every old tree would be kept alive by the one after it.
  if (fiber.alternate) fiber.alternate.alternate = null;
  for (let child = fiber.child; child; child = child.sibling) commitWork(child);
}

// ---- Assignment 08, until 09: move kept nodes ----
function commitWork(fiber) {
  // A new node is inserted. A kept node that has to move goes through the same call, and
  // still gets its props updated below.
  if (fiber.effectTag === 'PLACEMENT') fiber.parent.dom.insertBefore(fiber.dom, nextStableDom(fiber));
  if (fiber.alternate) updateDom(fiber.dom, fiber.alternate.props, fiber.props);
  if (fiber.alternate) fiber.alternate.alternate = null;
  for (let child = fiber.child; child; child = child.sibling) commitWork(child);
}

// ---- Assignment 06, until 09: remove a deleted node ----
// Each deleted fiber is on the list once, and only its own node is removed: its children went
// with it.
function commitDeletion(fiber) {
  fiber.parent.dom.removeChild(fiber.dom);
}

// ---- Assignment 09: fibers without a DOM node ----
function commitWork(fiber) {
  if (fiber.effectTag === 'PLACEMENT') place(fiber);
  if (fiber.dom && fiber.alternate) updateDom(fiber.dom, fiber.alternate.props, fiber.props);
  if (fiber.alternate) fiber.alternate.alternate = null;
  for (let child = fiber.child; child; child = child.sibling) commitWork(child);
}

function commitDeletion(fiber) {
  parentDom(fiber).removeChild(domOf(fiber));
}

// A new function component and its first node are both tagged, so the second call finds the node
// already where it belongs.
function place(fiber) {
  const parent = parentDom(fiber);
  const dom = domOf(fiber);
  const before = nextStableDom(fiber);
  if (dom.parentNode !== parent || dom.nextSibling !== before) parent.insertBefore(dom, before);
}

// A function component has no node: its DOM parent is the nearest ancestor that has one ...
function parentDom(fiber) {
  let parent = fiber.parent;
  while (!parent.dom) parent = parent.parent;
  return parent.dom;
}

// ... and its own node is the first one under it.
function domOf(fiber) {
  while (!fiber.dom) fiber = fiber.child;
  return fiber.dom;
}

// ---- Assignment 06, until 09: where a placed node goes ----
// A placed node goes in front of the first later sibling that is not being placed itself, because
// that one already stands where it belongs. With none, it goes last.
function nextStableDom(fiber) {
  for (let sibling = fiber.sibling; sibling; sibling = sibling.sibling) {
    if (sibling.effectTag !== 'PLACEMENT') return sibling.dom;
  }
  return null;
}

// ---- Assignment 09: where a placed node goes ----
function nextStableDom(fiber) {
  // A function component without siblings of its own shares its DOM parent's children with the
  // siblings of the component above it, so look there next.
  for (let node = fiber; node.parent; node = node.parent) {
    for (let sibling = node.sibling; sibling; sibling = sibling.sibling) {
      const dom = stableDom(sibling);
      if (dom) return dom;
    }
    if (node.parent.dom) return null;
  }
  return null;
}

function stableDom(fiber) {
  if (fiber.effectTag === 'PLACEMENT') return null;
  return fiber.dom ?? stableDom(fiber.child);
}

// ---- Assignment 11: run the effects ----
// React's order: every cleanup that is due, then every effect that is due.
function runEffects(deletions, root) {
  cleanUp(root, Map.groupBy(deletions, (fiber) => fiber.parent));
  for (const hook of [...dueHooks(root)]) {
    hook.cleanup = hook.effect();
    hook.deps = hook.nextDeps;
    hook.due = false;
  }
}

// Walks the new tree. At each fiber, the children it lost go first (a lost fiber before its own
// children), then its surviving children, then the fiber's own cleanups.
function cleanUp(fiber, lostChildren) {
  for (const lost of lostChildren.get(fiber.alternate) ?? []) {
    for (const gone of parentFirst(lost)) gone.hooks?.forEach(runCleanup);
  }
  for (let child = fiber.child; child; child = child.sibling) cleanUp(child, lostChildren);
  fiber.hooks?.filter((hook) => hook.due).forEach(runCleanup);
}

function runCleanup(hook) {
  if (!hook.cleanup) return;
  hook.cleanup();
  hook.cleanup = undefined;
}

function* parentFirst(fiber) {
  yield fiber;
  for (let child = fiber.child; child; child = child.sibling) yield* parentFirst(child);
}

// The effects that are due, children before parents.
function* dueHooks(fiber) {
  for (let child = fiber.child; child; child = child.sibling) yield* dueHooks(child);
  for (const hook of fiber.hooks ?? []) {
    if (hook.due) yield hook;
  }
}
