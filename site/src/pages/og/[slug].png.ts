// One social card per workbook, at /og/<slug>.png (see lib/og.mjs).
import { loadWorkbooks } from '../../lib/workbooks.mjs';
import { workbookCard } from '../../lib/og.mjs';

export function getStaticPaths() {
  return loadWorkbooks().map((w) => ({ params: { slug: w.slug }, props: { w } }));
}

export async function GET({ props, site }: { props: { w: any }; site: URL }) {
  return new Response(await workbookCard(props.w, site.host), { headers: { 'Content-Type': 'image/png' } });
}
