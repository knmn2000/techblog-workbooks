// Draws the social card for a page at build time: satori lays the card out as SVG (the text becomes
// paths, so no font is needed to rasterize it) and sharp turns that into the PNG crawlers require.
import fs from 'node:fs';
import { createRequire } from 'node:module';
import satori from 'satori';
import sharp from 'sharp';
import { OG_WIDTH, OG_HEIGHT } from './social.mjs';

const require = createRequire(import.meta.url);
const readFont = (file) => fs.readFileSync(require.resolve(file));

let fonts;
function loadFonts() {
  fonts ??= [
    { name: 'Geist', weight: 400, data: readFont('@fontsource/geist/files/geist-latin-400-normal.woff') },
    { name: 'Geist', weight: 600, data: readFont('@fontsource/geist/files/geist-latin-600-normal.woff') },
    { name: 'Geist', weight: 700, data: readFont('@fontsource/geist/files/geist-latin-700-normal.woff') },
    { name: 'JetBrains Mono', weight: 500, data: readFont('@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff') },
  ];
  return fonts;
}

// Same palette as the site's dark theme.
const C = { bg: '#1a1a1a', layer: '#262626', line: '#383838', text: '#e8e8ea', dim: '#a9aaae', faint: '#75767a', brand: '#ffa116', Easy: '#00b8a3', Medium: '#ffc01e', Hard: '#ff375f' };
const MARK = `data:image/svg+xml,${encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='#ffa116'/><path d='M9 10h14M9 16h14M9 22h8' stroke='#fff' stroke-width='3' stroke-linecap='round'/></svg>")}`;

// satori takes element objects, not JSX.
const el = (type, style, children) => ({ type, props: { style, children } });
const row = (style, children) => el('div', { display: 'flex', ...style }, children);

const pill = (label, dot) =>
  row({ alignItems: 'center', gap: 10, padding: '10px 20px', borderRadius: 999, background: C.layer, border: `1px solid ${C.line}`, fontSize: 26, fontWeight: 600, color: C.text, whiteSpace: 'nowrap' }, [
    dot ? el('div', { display: 'flex', width: 12, height: 12, borderRadius: 999, background: dot }) : null,
    label,
  ].filter(Boolean));

function card({ title, headline, pills, domain }) {
  // Long titles step down a size so they stay within two or three lines.
  const size = title.length <= 26 ? 88 : title.length <= 48 ? 72 : 56;
  return row({ boxSizing: 'border-box', width: OG_WIDTH, height: OG_HEIGHT, flexDirection: 'column', justifyContent: 'space-between', padding: '56px 72px', background: C.bg, color: C.text, fontFamily: 'Geist', borderTop: `10px solid ${C.brand}` }, [
    row({ alignItems: 'center', justifyContent: 'space-between' }, [
      row({ alignItems: 'center', gap: 16 }, [
        { type: 'img', props: { src: MARK, width: 52, height: 52 } },
        el('div', { display: 'flex', fontSize: 34, fontWeight: 700, letterSpacing: '-0.01em' }, 'Workbooks'),
      ]),
      el('div', { display: 'flex', fontFamily: 'JetBrains Mono', fontWeight: 500, fontSize: 24, color: C.faint }, domain),
    ]),
    row({ flexDirection: 'column', gap: 24 }, [
      el('div', { display: 'flex', fontSize: size, fontWeight: 700, lineHeight: 1.05, letterSpacing: '-0.025em' }, title),
      headline ? el('div', { display: 'flex', fontSize: 38, fontWeight: 400, lineHeight: 1.25, color: C.dim }, headline) : null,
    ].filter(Boolean)),
    row({ gap: 14 }, pills),
  ]);
}

async function render(tree) {
  const svg = await satori(tree, { width: OG_WIDTH, height: OG_HEIGHT, fonts: loadFonts() });
  // A palette PNG keeps the card small (WhatsApp skips large preview images).
  return sharp(Buffer.from(svg)).png({ palette: true, compressionLevel: 9 }).toBuffer();
}

export function workbookCard(w, domain) {
  const done = w.checkpoints.length;
  const pills = [
    pill(w.language),
    pill(`${done} ${done === 1 ? w.unit : w.units.toLowerCase()}`),
    ...['Easy', 'Medium', 'Hard'].filter((d) => w.counts[d]).map((d) => pill(`${w.counts[d]} ${d}`, C[d])),
  ];
  return render(card({ title: w.title, headline: w.headline, pills, domain }));
}

export function homeCard(workbooks, domain) {
  const n = workbooks.length;
  return render(card({
    title: "Don't just read tech blogs. Learn by building.",
    headline: 'Each workbook splits a technical post into coding assignments that add up to one project.',
    pills: [pill(`${n} ${n === 1 ? 'workbook' : 'workbooks'}`), pill('Free and open source')],
    domain,
  }));
}
