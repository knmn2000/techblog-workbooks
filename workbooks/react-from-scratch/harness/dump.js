// dump.js - turns a DOM tree into lines of text that tests compare.
//
// It reads nothing but standard DOM properties (nodeType, childNodes, tagName, nodeValue, className,
// id, title, value, disabled), so it works on minidom nodes and on jsdom nodes alike. The
// self-test and the React oracle rely on that.
//
// Line formats (fields are separated by single spaces):
//   node <depth> <label> <tag> "<props>"
//   text <depth> "<text>"

/**
 * Returns label(node). An element gets the next label (a, b, ... z, aa, ab, ...) the first time the
 * labeler sees it, and keeps it for as long as this labeler lives. Two dumps that print the same
 * label show the same DOM node, so labels are how a test checks that a node was kept, not rebuilt.
 */
export function makeLabeler() {
  const labels = new WeakMap();
  let count = 0;
  return function label(node) {
    let name = labels.get(node);
    if (name === undefined) {
      name = labelFor(count++);
      labels.set(node, name);
    }
    return name;
  };
}

/** 0 -> a, 25 -> z, 26 -> aa, 27 -> ab, ... (bijective base 26). */
function labelFor(index) {
  let name = "";
  for (let n = index + 1; n > 0; n = Math.floor((n - 1) / 26)) {
    name = String.fromCharCode(97 + ((n - 1) % 26)) + name;
  }
  return name;
}

const PROP_TAGS = {
  disabled: ["button", "input", "textarea"],
  value: ["input", "textarea"],
};

/** The `name=value` list of a node's non-default props, sorted by name. */
function describeProps(node, tag) {
  const found = [];
  const add = (name, value) => {
    if (value === true) {
      found.push(`${name}=true`);
      return;
    }
    const text = String(value);
    found.push(`${name}=${/[\s"%]/.test(text) ? encodeURIComponent(text) : text}`);
  };

  const isSet = (value) => value !== undefined && value !== null && String(value) !== "";
  if (isSet(node.className)) add("className", node.className);
  if (PROP_TAGS.disabled.includes(tag) && node.disabled) add("disabled", true);
  if (isSet(node.id)) add("id", node.id);
  if (isSet(node.title)) add("title", node.title);
  if (PROP_TAGS.value.includes(tag) && isSet(node.value)) add("value", node.value);
  return found.join(" "); // pushed in alphabetical order of the names
}

/** Text is percent-encoded only for the double quote, the percent sign and line breaks. */
export function encodeText(text) {
  return String(text).replace(/%/g, "%25").replace(/"/g, "%22").replace(/\r/g, "%0D").replace(/\n/g, "%0A");
}

function dumpChildren(parent, depth, label, lines) {
  const kids = parent.childNodes;
  let run = ""; // adjacent text nodes are merged into one text line
  const endRun = () => {
    if (run !== "") lines.push(`text ${depth} "${encodeText(run)}"`);
    run = "";
  };
  for (let i = 0; i < kids.length; i++) {
    const kid = kids[i];
    if (kid.nodeType === 3) {
      run += kid.nodeValue;
    } else if (kid.nodeType === 1) {
      endRun();
      dumpElement(kid, depth, label, lines);
    }
    // other node types (comments) are ignored
  }
  endRun();
}

function dumpElement(element, depth, label, lines) {
  const tag = element.tagName.toLowerCase();
  lines.push(`node ${depth} ${label(element)} ${tag} "${describeProps(element, tag)}"`);
  dumpChildren(element, depth + 1, label, lines);
}

/** The lines for the children of `container` (the container itself is not printed), at depth 0. */
export function dumpTree(container, label) {
  const lines = [];
  dumpChildren(container, 0, label, lines);
  return lines;
}

/** The lines for one node (and everything below it), at depth 0. */
export function dumpNode(node, label) {
  const lines = [];
  if (node.nodeType === 1) {
    dumpElement(node, 0, label, lines);
  } else if (node.nodeType === 3 && node.nodeValue !== "") {
    lines.push(`text 0 "${encodeText(node.nodeValue)}"`);
  }
  return lines;
}
