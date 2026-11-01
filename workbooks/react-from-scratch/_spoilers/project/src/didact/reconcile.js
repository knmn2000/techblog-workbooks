// ---- Assignment 04, until 06: a fiber for every child ----
// Turns the elements under a fiber into its child fibers, linked by child and sibling.
export function reconcileChildren(wipFiber, elements) {
  const fibers = elements.map((element) => ({
    type: element.type,
    props: element.props,
    dom: null,
    parent: wipFiber,
  }));
  wipFiber.child = fibers[0] ?? null;
  fibers.forEach((fiber, index) => {
    fiber.sibling = fibers[index + 1] ?? null;
  });
}

// ---- Assignment 06: compare with the previous tree ----
import { state } from './state.js';

function link(wipFiber, fibers) {
  wipFiber.child = fibers[0] ?? null;
  fibers.forEach((fiber, index) => {
    fiber.sibling = fibers[index + 1] ?? null;
  });
}

// The fiber for an element, given the old fiber it is compared with. The same type keeps the old
// DOM node (UPDATE). Otherwise the element gets a node of its own (PLACEMENT) and the old fiber goes.
function makeFiber(parent, element, oldFiber) {
  if (oldFiber?.type === element.type) {
    return {
      type: oldFiber.type,
      props: element.props,
      dom: oldFiber.dom,
      parent,
      alternate: oldFiber,
      effectTag: 'UPDATE',
    };
  }
  if (oldFiber) deleteFiber(oldFiber);
  return { type: element.type, props: element.props, dom: null, parent, alternate: null, effectTag: 'PLACEMENT' };
}

// The old fiber is only put on a list: the tree on screen is never changed by a render that may
// still be thrown away.
function deleteFiber(oldFiber) {
  state.deletions.push(oldFiber);
}

// ---- Assignment 06, until 07: compare by position ----
export function reconcileChildren(wipFiber, elements) {
  let oldFiber = wipFiber.alternate?.child;
  const fibers = elements.map((element) => {
    const fiber = makeFiber(wipFiber, element, oldFiber);
    oldFiber = oldFiber?.sibling;
    return fiber;
  });
  // The old children that the new list is too short for.
  for (; oldFiber; oldFiber = oldFiber.sibling) deleteFiber(oldFiber);
  link(wipFiber, fibers);
}

// ---- Assignment 07, until 08: match by key, if the keys stay in order ----
export function reconcileChildren(wipFiber, elements) {
  let oldFiber = wipFiber.alternate?.child;
  const fibers = elements.map((element) => {
    const match = findMatch(oldFiber, element);
    if (match) {
      // The old children passed over on the way to the match are not in the new list.
      for (; oldFiber !== match; oldFiber = oldFiber.sibling) deleteFiber(oldFiber);
      oldFiber = match.sibling;
    }
    return makeFiber(wipFiber, element, match);
  });
  for (; oldFiber; oldFiber = oldFiber.sibling) deleteFiber(oldFiber);
  link(wipFiber, fibers);
}

const keyOf = (item) => (item.props.key == null ? null : String(item.props.key));

// The old child an element continues. With a key: the first old child from `from` on that has the
// same key. Without one: the old child at `from`, if it has no key either (match by position).
function findMatch(from, element) {
  const key = keyOf(element);
  if (key === null) return from && keyOf(from) === null ? from : null;
  for (let fiber = from; fiber; fiber = fiber.sibling) {
    if (keyOf(fiber) === key) return fiber;
  }
  return null;
}

// ---- Assignment 08: match keys anywhere, move what is out of order ----
export function reconcileChildren(wipFiber, elements) {
  const oldFibers = new Map();
  for (let fiber = wipFiber.alternate?.child; fiber; fiber = fiber.sibling) {
    oldFibers.set(slotOf(fiber.props.key, fiber.index), fiber);
  }

  // The old position of the kept child that stood furthest along in the old order so far.
  let lastKeptIndex = 0;
  const fibers = elements.map((element, index) => {
    const slot = slotOf(element.props.key, index);
    const fiber = makeFiber(wipFiber, element, oldFibers.get(slot));
    oldFibers.delete(slot);
    fiber.index = index;
    if (fiber.alternate) {
      // A kept child that stood before one already kept has been passed by it: its node has to move.
      if (fiber.alternate.index < lastKeptIndex) fiber.effectTag = 'PLACEMENT';
      else lastKeptIndex = fiber.alternate.index;
    }
    return fiber;
  });
  // Whatever no new child took over.
  oldFibers.forEach((oldFiber) => deleteFiber(oldFiber));
  link(wipFiber, fibers);
}

// How an old child is found again: by its key, or by its position if it has none.
const slotOf = (key, index) => (key == null ? index : String(key));
