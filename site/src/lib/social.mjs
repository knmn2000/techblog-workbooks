// The Open Graph and Twitter tags that make a shared link show a title, a description and a card
// image on Twitter/X, WhatsApp, Slack, LinkedIn and the like. Crawlers need absolute URLs, so
// callers pass `url` and `image` already resolved against the site's origin.
export const OG_WIDTH = 1200;
export const OG_HEIGHT = 630;
export const SITE_NAME = 'Workbooks';

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function socialTags({ title, description, url, image }) {
  const tags = [
    ['property', 'og:type', 'website'],
    ['property', 'og:site_name', SITE_NAME],
    ['property', 'og:title', title],
    ['property', 'og:description', description],
    ['property', 'og:url', url],
    ['property', 'og:image', image],
    ['property', 'og:image:type', 'image/png'],
    ['property', 'og:image:width', OG_WIDTH],
    ['property', 'og:image:height', OG_HEIGHT],
    ['property', 'og:image:alt', title],
    ['name', 'twitter:card', 'summary_large_image'],
    ['name', 'twitter:image', image],
    ['name', 'twitter:image:alt', title],
  ];
  return tags.map(([attr, key, value]) => `<meta ${attr}="${key}" content="${esc(value)}" />`).join('\n  ');
}
