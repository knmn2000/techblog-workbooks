import { defineConfig } from 'astro/config';

// GitHub Pages serves this repository's site at https://knmn2000.github.io/techblog-workbooks/,
// so every page lives under /techblog-workbooks/. With a custom domain, build with SITE_BASE=/ .
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://knmn2000.github.io',
  base: process.env.SITE_BASE ?? '/techblog-workbooks',
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
