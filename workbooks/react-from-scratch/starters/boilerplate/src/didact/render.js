// ======================================================================================
// Assignment 04: Work in units: fibers
// Problem: problems/04-fibers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   `render` and the work loop: units of work that the browser can interrupt, one fiber at
//   a time. Later, assignments 05, 06, 09 and 10 add to this file.
//
// Your job:
//   Write `render`, `workLoop` and `performUnitOfWork`. `render` only schedules the work.
//   Each idle period runs fibers until `timeRemaining()` falls below 1, one fiber per unit
//   of work. The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import { createDom } from './dom.js'; // createDom (assignment 02): the DOM node of a fiber, made when its unit of work runs
import { reconcileChildren } from './reconcile.js'; // reconcileChildren: the child fibers of a fiber, made when its unit of work runs
import { state } from './state.js'; // state: the shared fields, e.g. the next unit of work

export function render(element, container) {
  // TODO: see "The modules" and Requirement R1 on the page.
  throw new Error('not implemented: render');
}

function workLoop(deadline) {
  // TODO: see "Reading the clock" and Requirements R3 and R5 on the page.
  throw new Error('not implemented: workLoop');
}

requestIdleCallback(workLoop); // the browser (here: the test harness) calls workLoop whenever it is idle

function performUnitOfWork(fiber) {
  // TODO: see "Units of work" and Requirements R2, R4 and R6 on the page.
  throw new Error('not implemented: performUnitOfWork');
}
