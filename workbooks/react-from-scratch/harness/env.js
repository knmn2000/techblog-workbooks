// env.js - the test environment.
//
// Importing this module installs two globals:
//   document                              a minidom document with <div id="root"> inside <body>
//   requestIdleCallback / cancelIdleCallback   a scheduler that the tests control
//
// Import it BEFORE your library: a library may call requestIdleCallback while it is being imported.
//
// Exports: document, container (the #root div), stats(), resetStats(), idle(budget), flush().

import { createDocument } from "./minidom.js";

/**
 * Builds an independent environment. This module installs one of them as the global one; the
 * self-test builds extra ones so that its checks do not disturb each other.
 */
export function createEnv() {
  const { document, stats, resetStats, quiet } = createDocument();

  const container = quiet(() => {
    const root = document.createElement("div");
    root.id = "root";
    document.body.appendChild(root);
    return root;
  });
  resetStats();

  // ---- the controllable scheduler ----

  const pending = new Map(); // id -> callback, in registration order
  let nextId = 1;

  function requestIdleCallback(callback) {
    const id = nextId++;
    pending.set(id, callback);
    return id;
  }

  function cancelIdleCallback(id) {
    pending.delete(id);
  }

  /**
   * One idle period. Runs the callbacks that are registered right now (callbacks registered while it
   * runs wait for the next period). Each gets the same deadline object, whose timeRemaining():
   *   - counts its calls (across all callbacks of the period),
   *   - returns 1 while the call number is below `budget`, and 0 from call number `budget` on
   *     (always 1 when budget is Infinity).
   * Returns the number of timeRemaining() calls: the units of work done in the period.
   */
  function idle(budget) {
    let calls = 0;
    const deadline = {
      didTimeout: false,
      timeRemaining() {
        calls++;
        return calls >= budget ? 0 : 1;
      },
    };
    for (const id of [...pending.keys()]) {
      const callback = pending.get(id);
      if (!callback) continue; // cancelled by an earlier callback of this period
      pending.delete(id);
      callback(deadline);
    }
    return calls;
  }

  /** Runs unlimited idle periods until one reports no work. Does nothing when nothing is registered. */
  function flush() {
    if (pending.size === 0) return;
    for (let period = 0; period < 100000; period++) {
      if (idle(Infinity) === 0) return;
    }
    throw new Error("flush: the library is still doing work after 100000 idle periods");
  }

  return { document, container, stats, resetStats, quiet, idle, flush, requestIdleCallback, cancelIdleCallback };
}

export const env = createEnv();

globalThis.document = env.document;
globalThis.requestIdleCallback = env.requestIdleCallback;
globalThis.cancelIdleCallback = env.cancelIdleCallback;

export const { document, container, stats, resetStats, quiet, idle, flush } = env;
