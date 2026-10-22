// The home page's social card, at /og.png; the default card for any page without its own.
import { loadWorkbooks } from '../lib/workbooks.mjs';
import { homeCard } from '../lib/og.mjs';

export async function GET({ site }: { site: URL }) {
  return new Response(await homeCard(loadWorkbooks(), site.host), { headers: { 'Content-Type': 'image/png' } });
}
