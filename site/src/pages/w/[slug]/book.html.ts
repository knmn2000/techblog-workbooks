// Serves the workbook's prebuilt problem book, with the "run it locally" layer injected (see book-inject.mjs).
// Opened from a published site, the book can't run your code.
import fs from 'node:fs';
import { loadWorkbooks } from '../../../lib/workbooks.mjs';
import { injectIntoBook } from '../../../lib/book-inject.mjs';

export function getStaticPaths() {
  return loadWorkbooks().filter((w) => w.hasBook).map((w) => ({ params: { slug: w.slug }, props: { w } }));
}

export function GET({ props, site }: { props: { w: any }; site: URL }) {
  const html = injectIntoBook(fs.readFileSync(props.w.bookFile, 'utf8'), props.w, site);
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}
