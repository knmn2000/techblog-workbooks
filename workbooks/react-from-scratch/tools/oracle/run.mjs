// run.mjs - runs a scenario against REAL React 19 on jsdom and prints what the harness would print.
//
//   node tools/oracle/run.mjs [--todo] <scenario-file>
//
// From code:  import { runOracle } from "./run.mjs";   const lines = await runOracle(scenarioText);
//
// It reuses the harness: the scenario parser and command list (scenario.js), the tree markup, the
// component catalog (with lib = React) and the dump labeler. Only the backend differs: render() is
// root.render() inside act(), events are dispatched inside act(), and the DOM is a jsdom document.
//
// Commands React cannot answer print placeholders for the caller to replace: `idle <k>` prints
// `idle ?` and `ops ...` prints `ops ?`. `call`, `props`, `show`, `create` and `update` are not
// supported (they test the learner's own functions, not React).
//
// `<TodoApp/>` in a scenario (or --todo) registers todoApp.mjs as components.TodoApp.

import { readFileSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parseScenario, runCommands } from "../../harness/scenario.js";
import { makeHandlers } from "../../harness/markup.js";
import { makeCatalog } from "../../harness/catalog.js";

let loaded = null;

/** Loads jsdom and React once. The globals have to exist before react-dom is imported. */
async function load() {
  if (loaded) return loaded;
  process.env.NODE_ENV = "development"; // the production build of React has no act()
  const { JSDOM } = await import("jsdom");
  const dom = new JSDOM("<!doctype html><html><head></head><body></body></html>", { url: "http://localhost/" });
  globalThis.window = dom.window;
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  const savedDocument = globalThis.document;
  globalThis.document = dom.window.document; // react-dom reads it while it is imported
  let React, ReactDOMClient, TodoApp;
  try {
    React = (await import("react")).default;
    ReactDOMClient = await import("react-dom/client");
    ({ TodoApp } = await import("./todoApp.mjs"));
  } finally {
    globalThis.document = savedDocument;
  }
  loaded = { dom, window: dom.window, React, ReactDOMClient, act: React.act, TodoApp };
  return loaded;
}

/** The backend of scenario.js for React on jsdom. */
function makeReactBackend(env, extraComponents) {
  const { window, React, ReactDOMClient, act } = env;
  const document = window.document;

  // a clean page for every run
  document.head.replaceChildren();
  document.body.replaceChildren();
  const container = document.createElement("div");
  container.id = "root";
  document.body.appendChild(container);

  const entries = [];
  const record = (text) => entries.push(text);
  const catalog = makeCatalog(React, record);
  let root = null;

  return {
    document,
    container,
    h: React.createElement,
    handler: makeHandlers(record),

    component(name) {
      const found = Object.hasOwn(catalog, name) ? catalog[name] : extraComponents[name];
      if (typeof found !== "function") throw new Error(`unknown component "${name}"`);
      return found;
    },

    async render(element) {
      root ??= ReactDOMClient.createRoot(container);
      await act(async () => {
        root.render(element);
      });
    },

    flush() {}, // act() has already flushed everything

    async dispatch(node, type, { cancelable }) {
      const Ctor = type === "click" ? window.MouseEvent : window.Event;
      await act(async () => {
        node.dispatchEvent(new Ctor(type, { bubbles: true, cancelable }));
      });
    },

    // The native setter bypasses React's value tracking, like a user typing does.
    setValue(node, text) {
      Object.getOwnPropertyDescriptor(Object.getPrototypeOf(node), "value").set.call(node, text);
    },

    async poke() {
      await act(async () => {
        catalog.poke();
      });
    },

    takeLog: () => entries.splice(0),

    // Unmounts the tree at the end of a run (the cleanups it runs are not part of the output).
    async close() {
      if (root) await act(async () => root.unmount());
    },
  };
}

let queue = Promise.resolve();

/**
 * Runs scenario text against real React and returns the output lines.
 * options.todo: register TodoApp (default: when the text contains "<TodoApp").
 * options.warnings: an array that receives React's console.error output (otherwise it goes to stderr).
 * Calls are serialised, so it is safe to call it in parallel.
 */
export function runOracle(text, options = {}) {
  const result = queue.then(() => runOne(text, options));
  queue = result.catch(() => {});
  return result;
}

async function runOne(text, options) {
  const env = await load();
  const commands = parseScenario(text);
  const wantsTodo = options.todo ?? /<TodoApp\b/.test(text);
  const savedDocument = globalThis.document;
  const savedError = console.error;
  globalThis.document = env.window.document; // components and effects reach the page through this
  if (options.warnings) console.error = (...args) => options.warnings.push(args.join(" "));
  const backend = makeReactBackend(env, wantsTodo ? { TodoApp: env.TodoApp } : {});
  try {
    return await runCommands(commands, backend);
  } finally {
    try {
      await backend.close();
    } finally {
      console.error = savedError;
      globalThis.document = savedDocument;
    }
  }
}

/** Releases the jsdom window (lets a process end promptly). */
export async function closeOracle() {
  if (loaded) loaded.window.close();
  loaded = null;
}

async function main(args) {
  let todo;
  const files = [];
  for (const arg of args) {
    if (arg === "--todo") todo = true;
    else files.push(arg);
  }
  if (files.length !== 1) {
    console.error("usage: node run.mjs [--todo] <scenario-file>");
    process.exitCode = 2;
    return;
  }
  try {
    const lines = await runOracle(readFileSync(files[0], "utf8"), { todo });
    process.stdout.write(lines.map((line) => line + "\n").join(""));
  } catch (err) {
    const where = err?.scenarioLine ? `while running scenario line ${err.scenarioLine} (${err.scenarioText}):\n` : "";
    console.error(where + (err?.stack ?? String(err)));
    process.exitCode = 1;
  } finally {
    await closeOracle();
  }
}

const invokedDirectly =
  process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href.toLowerCase() === import.meta.url.toLowerCase();
if (invokedDirectly) await main(process.argv.slice(2));
