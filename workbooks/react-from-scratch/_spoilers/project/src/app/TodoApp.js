// Assignment 12: the todo list, written the way an application would write it on top of Didact.
import { createElement as h, useEffect, useState } from '../didact/index.js';

export function TodoApp() {
  const [items, setItems] = useState([]);
  const [draft, setDraft] = useState('');
  const [nextId, setNextId] = useState(1);
  const left = items.filter((item) => !item.done).length;

  useEffect(() => {
    document.title = `${left} left`;
  }, [left]);

  function addItem(event) {
    event.preventDefault();
    const text = draft.trim();
    if (text === '') return;
    // The newest item goes first, and an id is never used twice, even after removals.
    setItems((current) => [{ id: nextId, text, done: false }, ...current]);
    setNextId((id) => id + 1);
    setDraft(() => '');
  }

  function typeDraft(event) {
    const { value } = event.target;
    setDraft(() => value);
  }

  const toggleItem = (id) =>
    setItems((current) => current.map((item) => (item.id === id ? { ...item, done: !item.done } : item)));
  const removeItem = (id) => setItems((current) => current.filter((item) => item.id !== id));

  return h(
    'div',
    { id: 'todo' },
    h(
      'form',
      { id: 'todo-form', onSubmit: addItem },
      h('input', { id: 'todo-input', value: draft, onInput: typeDraft }),
      h('button', { id: 'todo-add' }, 'Add'),
    ),
    h(
      'ul',
      { id: 'todo-list' },
      ...items.map((item) => h(TodoItem, { key: item.id, item, onToggle: toggleItem, onRemove: removeItem })),
    ),
    h('p', { id: 'todo-count' }, left, ' left'),
  );
}

function TodoItem({ item, onToggle, onRemove }) {
  return h(
    'li',
    { id: `item-${item.id}` },
    h('button', { id: `toggle-${item.id}`, onClick: () => onToggle(item.id) }, item.done ? 'done' : 'todo'),
    h('span', { id: `label-${item.id}`, className: item.done ? 'done' : '' }, item.text),
    h('button', { id: `remove-${item.id}`, onClick: () => onRemove(item.id) }, 'x'),
  );
}
