// ---- Assignment 04, until 06: the shared state ----
// Everything the work loop shares lives on this one object: a module cannot reassign a variable
// that another module imported, but any module can change a property of an object.
export const state = {
  nextUnitOfWork: null, // the fiber the work loop does next; null when there is no work
  wipRoot: null, // the root of the tree being built (work in progress)
};

// ---- Assignment 06, until 10: the last committed tree and the old fibers to remove ----
export const state = {
  nextUnitOfWork: null,
  wipRoot: null,
  currentRoot: null, // the root of the tree that is on screen
  deletions: [], // old fibers that have no counterpart in the tree being built
};

// ---- Assignment 10: the component being rendered ----
export const state = {
  nextUnitOfWork: null,
  wipRoot: null,
  currentRoot: null,
  deletions: [],
  wipFiber: null, // the function component being rendered: its hooks live on it
  hookIndex: 0, // which hook of that component the next useState or useEffect call is
};
