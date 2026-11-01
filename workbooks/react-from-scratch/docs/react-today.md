# React today, and what the posts say

Each post describes the React of its day: Pombo's follows React 16.8 (2019), Jongeneel's is from 2021. The tests check your code against React 19.3.1 (react-dom 19.3.1 on jsdom 30.1.3, run on Node 26). Where React changed, React wins. Below are the places where that matters, so a post and a test disagreeing doesn't send you hunting for a bug in your own code.

The architecture hasn't moved. React still builds a tree of fibers, renders in one pass and commits in another, matches children by type and key, and keeps hook state on the fiber. That part you build.

## Where the posts and React 19 differ

| Topic | The posts | React 19.3 | What the workbook does |
|---|---|---|---|
| Mounting | Pombo calls `Didact.render(element, container)`; the 2021 article's world is `ReactDOM.render` | `ReactDOM.render` is gone. You call `createRoot(container).render(element)` from `react-dom/client` | Your `render(element, container)` plays the part of `root.render`. The oracle uses `createRoot` |
| Scheduling | The work loop runs on `requestIdleCallback` | React stopped using it years ago and has its own scheduler package. Pombo's post says as much | The loop stays on `requestIdleCallback`: yielding to the browser is the idea, and the harness can drive it by hand |
| When rendering is interruptible | Always: any render can stop after a unit of work | Only for concurrent features such as transitions. An ordinary update renders in one uninterrupted pass | Your loop is interruptible, as in the post. Nothing in the tests depends on React being so |
| Batching | `setState` queues an action and schedules a render from the root | Updates are batched everywhere since React 18, promises and timeouts included | Several updater calls before the next render give one render, applied in order |
| Effects | Not covered by Pombo; Jongeneel's mount and update hooks run in a `setTimeout`, his unmount hook runs at once | Passive effects normally run after the browser has painted. All the cleanups of a commit run before any new effect | Your effects run right after the commit has updated the DOM, in React's order. The tests flush React's effects with `act` first |
| Setter identity | Pombo's `setState` closes over the hook of the render that created it | One setter function serves every render, and an update sent through an old one still counts | The tests side with React: an update sent through a setter from an earlier render is not lost |
| Props on DOM nodes | Both posts assign DOM properties (`dom.className = ...`) | React DOM sets attributes for most props, handles `style` objects, and treats `value` and `checked` on inputs specially | Tests stick to props that are DOM properties and read the same either way: `id`, `className`, `title`, `value`, `disabled` |
| Events | A listener on every element, named by lowercasing `onClick` to `click` | Listeners sit on the root container and React dispatches its own synthetic events | Same observable result for clicks, input and submit |
| Updater argument | Pombo's setter takes a function | `setState` also takes a plain value | Your setter has to accept an updater function. Plain values aren't tested |
| Keys | Pombo leaves them out; Jongeneel matches by key but can't reorder | Keys identify children across renders, and reordering moves the DOM nodes | Assignments 7 and 8 follow React, reorders included |

## APIs the workbook doesn't teach because React 19 dropped or deprecated them

React 19 removed `ReactDOM.render`, `ReactDOM.hydrate`, `unmountComponentAtNode`, `findDOMNode`, string refs, legacy context, `propTypes` and `defaultProps` on function components, and the `react-dom/test-utils` version of `act` (it now comes from `react`). Class components still work. The old `componentWillReceiveProps` family is legacy. So Jongeneel's class `Component` and its lifecycle methods turn up here as `useEffect`. The ideas carry over (run after mounting, run again when inputs change, clean up on unmount) in the shape React code takes today.

Function components can take `ref` as an ordinary prop in React 19, so `forwardRef` is no longer needed. Refs, context, Suspense, transitions, `useReducer` and `useMemo` are outside this workbook.
