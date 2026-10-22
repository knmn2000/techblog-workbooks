import { defineConfig } from 'astro/config';

// The site is served from the custom domain https://workbooks.2mbproblems.com/, at the root.
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://workbooks.2mbproblems.com',
  base: process.env.SITE_BASE ?? '/',
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
