// ---- Assignment 04, until 10: the Didact object ----
// What an app imports: the library's public face.
import { createElement } from './createElement.js';
import { render } from './render.js';

const Didact = { createElement, render };

export default Didact;
export { createElement, render };

// ---- Assignment 10, until 11: useState joins the library ----
import { createElement } from './createElement.js';
import { useState } from './hooks.js';
import { render } from './render.js';

const Didact = { createElement, render, useState };

export default Didact;
export { createElement, render, useState };

// ---- Assignment 11: useEffect joins the library ----
import { createElement } from './createElement.js';
import { useEffect, useState } from './hooks.js';
import { render } from './render.js';

const Didact = { createElement, render, useState, useEffect };

export default Didact;
export { createElement, render, useState, useEffect };
