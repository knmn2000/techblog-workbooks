// ---- Assignment 10: useState ----
// State lives in a hook object that every render of the component finds again by position,
// so it survives re-renders, and so does the setter that points at it.
import { render } from './render.js';
import { state } from './state.js';

// The hook at the current position of the component being rendered: the object its previous
// render left there, or a new one the first time.
function nextHook(create) {
  const hook = state.wipFiber.alternate?.hooks[state.hookIndex] ?? create();
  state.wipFiber.hooks.push(hook);
  state.hookIndex++;
  return hook;
}

export function useState(initial) {
  const hook = nextHook(() => {
    const hook = { state: initial, queue: [] };
    hook.setState = (update) => {
      hook.queue.push(update);
      rerender();
    };
    return hook;
  });
  // Apply what was queued since the last render, oldest first.
  for (const update of hook.queue.splice(0)) hook.state = update(hook.state);
  return [hook.state, hook.setState];
}

// Starts again from the root, with the element it was last asked to draw.
function rerender() {
  const root = state.wipRoot ?? state.currentRoot;
  render(root.props.children[0], root.dom);
}

// ---- Assignment 11: useEffect ----
// The hook keeps the latest effect and its dependencies; the commit decides whether it is due.
export function useEffect(effect, deps) {
  const hook = nextHook(() => ({ deps: undefined, cleanup: undefined }));
  hook.effect = effect;
  hook.nextDeps = deps;
  hook.due = depsChanged(hook.deps, deps);
}

// `prev` are the dependencies of the last run. Without a list, on either side, the effect runs every time.
function depsChanged(prev, next) {
  return !prev || !next || prev.length !== next.length || next.some((dep, i) => !Object.is(dep, prev[i]));
}
