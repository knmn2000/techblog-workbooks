// todoApp.mjs - the todo application of assignment 12, written with real React.
//
// The DOM it produces is the contract of the assignment (the learner's TodoApp must produce the same):
//
//   <div id="todo">
//     <form id="todo-form"><input id="todo-input" value={draft}/><button id="todo-add">Add</button></form>
//     <ul id="todo-list">  one <li id="item-N"> per item, newest first:
//        <li id="item-N" key=N>
//          <button id="toggle-N">todo|done</button>
//          <span id="label-N" className="done"|"">text</span>
//          <button id="remove-N">x</button>
//        </li>
//     </ul>
//     <p id="todo-count">{n} left</p>
//   </div>
//
// Behaviour: ids count from 1 in the order the items are added; a new item goes to the front of the
// list; submitting a draft that is empty after trimming adds nothing; adding clears the input; the
// stored text is the trimmed draft; n is the number of items that are not done; an effect that depends on
// [n] sets document.title to "<n> left".

import { createElement as h, useState, useEffect } from "react";

export function TodoApp() {
  const [items, setItems] = useState([]);
  const [draft, setDraft] = useState("");
  const [nextId, setNextId] = useState(1);

  const left = items.filter((item) => !item.done).length;

  useEffect(() => {
    document.title = `${left} left`;
  }, [left]);

  function onSubmit(event) {
    event.preventDefault();
    const text = draft.trim();
    if (text === "") return;
    setItems((current) => [{ id: nextId, text, done: false }, ...current]);
    setNextId((id) => id + 1);
    setDraft("");
  }

  const toggle = (id) => setItems((current) => current.map((item) => (item.id === id ? { ...item, done: !item.done } : item)));
  const remove = (id) => setItems((current) => current.filter((item) => item.id !== id));

  return h(
    "div",
    { id: "todo" },
    h(
      "form",
      { id: "todo-form", onSubmit },
      h("input", { id: "todo-input", value: draft, onInput: (event) => setDraft(event.target.value) }),
      h("button", { id: "todo-add" }, "Add"),
    ),
    h(
      "ul",
      { id: "todo-list" },
      items.map((item) =>
        h(
          "li",
          { id: `item-${item.id}`, key: item.id },
          h("button", { id: `toggle-${item.id}`, onClick: () => toggle(item.id) }, item.done ? "done" : "todo"),
          h("span", { id: `label-${item.id}`, className: item.done ? "done" : "" }, item.text),
          h("button", { id: `remove-${item.id}`, onClick: () => remove(item.id) }, "x"),
        ),
      ),
    ),
    h("p", { id: "todo-count" }, left, " left"),
  );
}
