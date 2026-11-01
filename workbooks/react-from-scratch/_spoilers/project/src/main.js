// Assignment 12: the finished program. index.html loads this file, which draws the todo app into #root.
import { createElement as h, render } from './didact/index.js';
import { TodoApp } from './app/TodoApp.js';

render(h(TodoApp, null), document.getElementById('root'));
