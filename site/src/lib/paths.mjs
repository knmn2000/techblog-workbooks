// Links inside the site. If the site is ever served under a path (SITE_BASE), a link written as
// "/w/slug/" must become "<base>/w/slug/".
const base = import.meta.env.BASE_URL.replace(/\/$/, '');

export const href = (path) => base + (path.startsWith('/') ? path : '/' + path);
