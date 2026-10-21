// Links inside the site. GitHub Pages serves it under a path (/techblog-workbooks/), so a link
// written as "/w/slug/" must become "/techblog-workbooks/w/slug/".
const base = import.meta.env.BASE_URL.replace(/\/$/, '');

export const href = (path) => base + (path.startsWith('/') ? path : '/' + path);
