// ======================================================================================
// Assignment 04: Work in units: fibers
// Problem: problems/04-fibers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The `Didact` object an app imports: `createElement` and `render`, then the hooks as
//   they arrive. Later, assignments 10 and 11 add to this file.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import { createElement } from './createElement.js'; // createElement (assignment 01): what an app calls to describe its UI
import { render } from './render.js'; // render (this assignment): what an app calls to draw it

const Didact = { createElement, render };

export default Didact;
export { createElement, render };
