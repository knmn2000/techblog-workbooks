// scenario.js - reads a scenario file, runs its commands against a library, writes the result lines.
//
// A scenario is a list of commands, one per line (blank lines and lines starting with "#" are ignored).
// What each command does and prints is described in the assignment texts; the table of commands is
// COMMANDS below. Only the printed lines are compared by the checker.
//
// How it is organised (the React oracle in tools/oracle reuses all of this):
//   parseScenario(text)             -> [{no, name, rest, text}]
//   runCommands(commands, backend)  -> output lines; the command list lives here and talks only to a
//                                      `backend` object (see makeMinidomBackend for the members)
//   makeMinidomBackend(lib, env)    -> the backend that drives `lib` on the minidom environment
//   runScenario(text, lib, options) -> output lines (options.env, or options.backend for another backend)
//   runScenarioFile(in, out, lib)   -> the entry point of an assignment program

import { readFileSync, writeFileSync, rmSync } from "node:fs";
import { makeLabeler, dumpTree, dumpNode, encodeText } from "./dump.js";
import { parseMarkup, buildElement, parseAttributes, resolveHandlers, makeHandlers, h as canonicalH } from "./markup.js";
import { makeCatalog } from "./catalog.js";
import { MiniEvent, STAT_NAMES } from "./minidom.js";

// ---------------------------------------------------------------------------------------------
// parsing

export function parseScenario(text) {
  const commands = [];
  text.split(/\r?\n/).forEach((raw, index) => {
    const line = raw.trimStart();
    if (line.trim() === "" || line.startsWith("#")) return;
    const match = /^(\S+)(?:\s+([\s\S]*))?$/.exec(line);
    commands.push({ no: index + 1, name: match[1], rest: match[2] ?? "", text: raw });
  });
  return commands;
}

const isSpace = (ch) => ch === " " || ch === "\t";

/** Splits "word the rest of the line" into ["word", "the rest of the line"]. */
function splitWord(rest) {
  const match = /^(\S+)(?:\s+([\s\S]*))?$/.exec(rest.trim());
  return match ? [match[1], match[2] ?? ""] : ["", ""];
}

/**
 * Reads the next argument of a line from index `i`: a JSON string, a JSON object or array (which may
 * contain spaces), or a run of non-space characters. Returns [token, nextIndex], token null at the end.
 */
function readToken(s, i) {
  while (i < s.length && isSpace(s[i])) i++;
  if (i >= s.length) return [null, i];
  const start = i;
  if (s[i] === '"' || s[i] === "{" || s[i] === "[") {
    let depth = 0;
    for (; i < s.length; i++) {
      const ch = s[i];
      if (ch === '"') {
        for (i++; i < s.length && s[i] !== '"'; i++) if (s[i] === "\\") i++;
      } else if (ch === "{" || ch === "[") {
        depth++;
      } else if (ch === "}" || ch === "]") {
        depth--;
      }
      if (depth === 0) {
        i++;
        break;
      }
    }
  } else {
    while (i < s.length && !isSpace(s[i])) i++;
  }
  return [s.slice(start, i), i];
}

function parseJson(token, what) {
  try {
    return JSON.parse(token);
  } catch {
    throw new Error(`scenario: ${what} is not valid JSON: ${token}`);
  }
}

// ---------------------------------------------------------------------------------------------
// JSON output for `call` and `show`

function jsonString(text) {
  return JSON.stringify(text)
    .replace(/[^\x00-\x7e]/g, (ch) => "\\u" + ch.charCodeAt(0).toString(16).padStart(4, "0"))
    .replace(/ /g, "\\u0020");
}

/**
 * Compact JSON with sorted keys. A function prints as "[fn]", a space inside a string as   and a
 * character outside ASCII as a \u escape, so a result never contains a space or a non-ASCII character.
 * Like JSON.stringify, it leaves out properties whose value is undefined.
 */
export function stableJson(value, seen = new Set()) {
  if (typeof value === "function") return '"[fn]"';
  if (typeof value === "string") return jsonString(value);
  if (value === undefined || typeof value === "symbol") return "null";
  if (typeof value === "bigint") return jsonString(String(value));
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (seen.has(value)) throw new Error("scenario: cannot print a structure that contains itself");
  seen.add(value);
  let text;
  if (Array.isArray(value)) {
    text = "[" + value.map((item) => stableJson(item, seen)).join(",") + "]";
  } else {
    const parts = [];
    for (const key of Object.keys(value).sort()) {
      if (value[key] === undefined) continue;
      parts.push(jsonString(key) + ":" + stableJson(value[key], seen));
    }
    text = "{" + parts.join(",") + "}";
  }
  seen.delete(value);
  return text;
}

// ---------------------------------------------------------------------------------------------
// the commands

function need(member, command, what) {
  if (typeof member !== "function") throw new Error(`${command}: this runner does not support it (${what})`);
}

function findNode(ctx, idText) {
  const id = idText.startsWith("#") ? idText.slice(1) : idText;
  const found = ctx.backend.document.getElementById(id);
  if (found) return found;
  // A node made by `create` is not attached to the document; look at it directly.
  if (ctx.state.created && ctx.state.created.nodeType === 1 && ctx.state.created.id === id) return ctx.state.created;
  throw new Error(`no element with id "${id}"`);
}

function parseBudget(text) {
  if (/^(inf|infinity)$/i.test(text)) return Infinity;
  const n = Number(text);
  if (!Number.isInteger(n) || n < 0) throw new Error(`idle: the budget must be a whole number, got "${text}"`);
  return n;
}

export const COMMANDS = {
  // ---- 01: elements ----

  call(ctx, rest) {
    const { backend, state } = ctx;
    need(backend.createElement, "call", "it needs lib.createElement");
    let [typeToken, i] = readToken(rest, 0);
    let propsToken;
    [propsToken, i] = readToken(rest, i);
    if (typeToken === null || propsToken === null) throw new Error("call: expected <type> <props> [child ...]");
    const type = typeToken.startsWith('"') ? parseJson(typeToken, "the type") : typeToken;

    let props;
    if (propsToken.startsWith("@")) {
      const name = propsToken.slice(1);
      if (!state.propsDefs.has(name)) throw new Error(`call: no props named "${name}" (define it with the props command)`);
      props = state.propsDefs.get(name);
    } else {
      props = parseJson(propsToken, "the props");
    }

    const children = [];
    for (;;) {
      let token;
      [token, i] = readToken(rest, i);
      if (token === null) break;
      if (token.startsWith("$")) {
        const k = Number(token.slice(1));
        if (!Number.isInteger(k) || k < 1 || k > state.elements.length) throw new Error(`call: there is no earlier call ${token}`);
        children.push(state.elements[k - 1]);
      } else {
        children.push(parseJson(token, "a child"));
      }
    }

    const element = backend.createElement(type, props, ...children);
    state.elements.push(element);
    return [`element ${state.elements.length} ${stableJson(element)}`];
  },

  props(ctx, rest) {
    need(ctx.backend.createElement, "props", "it goes with call");
    const [name, json] = splitWord(rest);
    if (name === "" || json === "") throw new Error("props: expected <name> <json>");
    ctx.state.propsDefs.set(name, parseJson(json, "the props"));
  },

  show(ctx, rest) {
    need(ctx.backend.createElement, "show", "it goes with call");
    const [name] = splitWord(rest);
    if (!ctx.state.propsDefs.has(name)) throw new Error(`show: no props named "${name}"`);
    return [`props ${name} ${stableJson(ctx.state.propsDefs.get(name))}`];
  },

  // ---- 02: DOM nodes and props ----

  create(ctx, rest) {
    const { backend, state } = ctx;
    need(backend.createDom, "create", "it needs lib.createDom");
    const [kind, attrText] = splitWord(rest);
    if (kind === "") throw new Error("create: expected <tag|text> [prop ...]");
    const props = { ...resolveHandlers(parseAttributes(attrText), backend.handler), children: [] };
    state.prev = props;
    state.created = backend.createDom({ type: kind === "text" ? "TEXT_ELEMENT" : kind, props });
  },

  update(ctx, rest) {
    const { backend, state } = ctx;
    need(backend.updateDom, "update", "it needs lib.updateDom");
    if (!state.created) throw new Error("update: nothing was created yet (use create first)");
    const next = { ...resolveHandlers(parseAttributes(rest), backend.handler), children: [] };
    backend.updateDom(state.created, state.prev, next);
    state.prev = next;
  },

  // ---- 03 and later: trees ----

  tree(ctx, rest) {
    const [name, markup] = splitWord(rest);
    if (name === "" || markup === "") throw new Error("tree: expected <name> <markup>");
    ctx.state.trees.set(name, parseMarkup(markup));
  },

  async render(ctx, rest) {
    const { backend, state } = ctx;
    const [name] = splitWord(rest);
    const tree = state.trees.get(name);
    if (!tree) throw new Error(`render: unknown tree "${name}"`);
    const element = buildElement(tree, { h: backend.h, component: backend.component, handler: backend.handler });
    state.created = null;
    await backend.render(element);
  },

  idle(ctx, rest) {
    const budget = parseBudget(splitWord(rest)[0]);
    if (typeof ctx.backend.idle !== "function") return ["idle ?"];
    return [`idle ${ctx.backend.idle(budget)}`];
  },

  async flush(ctx) {
    await ctx.backend.flush();
  },

  // ---- events ----

  async click(ctx, rest) {
    const node = findNode(ctx, splitWord(rest)[0]);
    await ctx.backend.dispatch(node, "click", { cancelable: true });
    await ctx.backend.flush();
  },

  async type(ctx, rest) {
    const [id] = splitWord(rest);
    const node = findNode(ctx, id);
    const text = rest.slice(id.length + 1); // everything after the one space that follows the id
    ctx.backend.setValue(node, text);
    await ctx.backend.dispatch(node, "input", { cancelable: false });
    await ctx.backend.flush();
  },

  async submit(ctx, rest) {
    const node = findNode(ctx, splitWord(rest)[0]);
    await ctx.backend.dispatch(node, "submit", { cancelable: true });
    await ctx.backend.flush();
  },

  async poke(ctx) {
    await ctx.backend.poke();
    await ctx.backend.flush();
  },

  // ---- output ----

  dump(ctx) {
    const { backend, state } = ctx;
    state.dumps++;
    const lines = [`dump ${state.dumps}`];
    lines.push(...(state.created ? dumpNode(state.created, state.label) : dumpTree(backend.container, state.label)));
    const title = backend.document.title;
    if (title) lines.push(`title "${encodeText(title)}"`);
    return lines;
  },

  ops(ctx, rest) {
    if (typeof ctx.backend.ops !== "function") return ["ops ?"];
    const names = rest.split(/\s+/).filter(Boolean);
    return [`ops ${ctx.backend.ops(names).join(" ")}`];
  },

  log(ctx) {
    return ctx.backend.takeLog().map((entry) => `log ${entry}`);
  },
};

/**
 * Runs parsed commands against a backend and returns the output lines. The backend provides:
 *   document, container            where `dump` and `click` look (document.title, getElementById)
 *   h(type, props, ...children)    builds the elements of `tree` (canonical h, or React.createElement)
 *   component(name)                the function for a capitalised tag
 *   handler(name)                  the memoised @name handler (it logs `name`)
 *   render(element), flush()       draw an element into the container; run pending work (may be async)
 *   dispatch(node, type, {cancelable}), setValue(node, text), poke()   (may be async)
 *   takeLog()                      the log entries since the last call
 *   optional: idle(budget), ops(names), createElement, createDom, updateDom
 * A command whose backend member is missing prints a placeholder (`idle ?`, `ops ?`) or throws.
 */
export async function runCommands(commands, backend) {
  const state = {
    trees: new Map(),
    propsDefs: new Map(),
    elements: [],
    created: null,
    prev: null,
    dumps: 0,
    label: makeLabeler(),
  };
  const ctx = { backend, state };
  const out = [];
  for (const command of commands) {
    try {
      const run = COMMANDS[command.name];
      if (!Object.hasOwn(COMMANDS, command.name)) throw new Error(`unknown command "${command.name}"`);
      const lines = await run(ctx, command.rest);
      if (lines) out.push(...lines);
    } catch (err) {
      if (err !== null && typeof err === "object") {
        err.scenarioLine ??= command.no;
        err.scenarioText ??= command.text.trim();
      }
      throw err;
    }
  }
  return out;
}

// ---------------------------------------------------------------------------------------------
// the minidom backend

/** The activation behaviour of a click: the nearest button, if it is an enabled submit button in a form. */
function submitFromClick(target) {
  for (let node = target; node; node = node.parentNode) {
    if (node.nodeType !== 1 || node.tagName !== "BUTTON") continue;
    const kind = String(node.type ?? "").toLowerCase();
    if (node.disabled || (kind !== "" && kind !== "submit")) return;
    for (let form = node.parentNode; form; form = form.parentNode) {
      if (form.nodeType === 1 && form.tagName === "FORM") {
        form.dispatchEvent(new MiniEvent("submit", { bubbles: true, cancelable: true }));
        return;
      }
    }
    return;
  }
}

/**
 * The backend that runs `lib` on the minidom environment. `env` is the object exported by env.js
 * (loaded here when not given, so the importing program does not have to).
 */
export async function makeMinidomBackend(lib, env) {
  env ??= (await import("./env.js")).env;
  env.resetStats();

  const entries = [];
  const record = (text) => entries.push(text);
  const catalog = makeCatalog(lib, record);
  const method = (name) => (typeof lib[name] === "function" ? lib[name].bind(lib) : undefined);

  return {
    document: env.document,
    container: env.container,
    h: canonicalH,
    handler: makeHandlers(record),

    component(name) {
      const found = Object.hasOwn(catalog, name) ? catalog[name] : lib.components?.[name];
      if (typeof found !== "function") throw new Error(`unknown component "${name}"`);
      return found;
    },

    createElement: method("createElement"),
    createDom: method("createDom"),
    updateDom: method("updateDom"),

    render(element) {
      if (typeof lib.render !== "function") throw new Error("render: the library has no render function");
      lib.render(element, env.container);
    },
    flush: () => env.flush(),
    idle: (budget) => env.idle(budget),

    ops(names) {
      const wanted = names.length > 0 ? names : STAT_NAMES;
      for (const name of wanted) if (!STAT_NAMES.includes(name)) throw new Error(`ops: unknown statistic "${name}"`);
      const stats = env.stats();
      env.resetStats();
      return wanted.map((name) => stats[name]);
    },

    // One default action is emulated, because a browser (and jsdom, which the oracle uses) has it: a click
    // that is not prevented, on a submit button inside a form, submits the form (a cancelable, bubbling
    // submit event on the form). Nothing else has a default action.
    dispatch(node, type, { cancelable }) {
      const notPrevented = node.dispatchEvent(new MiniEvent(type, { bubbles: true, cancelable }));
      if (type === "click" && notPrevented) submitFromClick(node);
    },

    // The harness's own write: it must not be counted as one of the learner's writes.
    setValue(node, text) {
      env.quiet(() => {
        node.value = text;
      });
    },

    poke: () => catalog.poke(),
    takeLog: () => entries.splice(0),
  };
}

// ---------------------------------------------------------------------------------------------
// entry points

/** Runs scenario text against `lib` and returns the output lines. */
export async function runScenario(text, lib, options = {}) {
  const backend = options.backend ?? (await makeMinidomBackend(lib, options.env));
  return runCommands(parseScenario(text), backend);
}

/**
 * The entry point of an assignment program: reads the scenario file, runs it, writes the output file
 * (UTF-8, "\n" line ends). On an error no output file is left. An error whose message starts with
 * "not implemented" prints the message and sets exit code 99; any other error prints the message and
 * the stack and sets exit code 1. Returns the exit code.
 */
export async function runScenarioFile(inputPath, outputPath, lib, options = {}) {
  try {
    const lines = await runScenario(readFileSync(inputPath, "utf8"), lib, options);
    writeFileSync(outputPath, lines.map((line) => line + "\n").join(""), "utf8");
    return 0;
  } catch (err) {
    rmSync(outputPath, { force: true });
    const message = err instanceof Error ? err.message : String(err);
    if (message.startsWith("not implemented")) {
      console.error(message);
      process.exitCode = 99;
      return 99;
    }
    const where = err?.scenarioLine ? `while running scenario line ${err.scenarioLine} (${err.scenarioText}):\n` : "";
    console.error(where + (err instanceof Error && err.stack ? err.stack : message));
    process.exitCode = 1;
    return 1;
  }
}
