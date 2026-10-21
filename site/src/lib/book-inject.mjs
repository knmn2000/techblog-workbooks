// The published copy of a problem book can't run code. The book has a hosted mode for this: it
// reads window.WORKBOOK_HOST before its own script runs, makes the editor read-only, and sends
// typing in the editor, Run, Submit and its "Run locally" button to WORKBOOK_HOST.runLocally(). This file sets that up and adds
// the dialog runLocally() opens: the same "git clone / ask your AI" panel as the workbook page.
import { startPanelHtml, startPanelCss, startPanelJs } from './start-ui.mjs';
import { href } from './paths.mjs';

const css = `
${startPanelCss}
#wbs-modal { position: fixed; inset: 0; z-index: 2147483000; display: flex; align-items: center; justify-content: center; padding: 16px; background: rgba(10, 10, 14, 0.62); }
#wbs-modal[hidden] { display: none; }
.wbs-dialog { width: min(560px, 100%); max-height: calc(100vh - 32px); overflow: auto; background: var(--layer, #fff); color: var(--text, #262626); border: 1px solid var(--line-strong, #d4d4d8); border-radius: 14px; padding: 22px; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35); font: 14px/1.55 var(--font-ui, system-ui, sans-serif); position: relative; }
.wbs-dialog h2 { font-size: 18px; margin: 0 0 4px; letter-spacing: -0.01em; padding-right: 30px; }
.wbs-dialog .wbs-sub { color: var(--text-2, #595959); margin: 0 0 16px; font-size: 13px; }
.wbs-x { position: absolute; top: 12px; right: 12px; width: 30px; height: 30px; border: 0; border-radius: 6px; background: transparent; color: var(--text-2, #595959); font-size: 20px; line-height: 1; cursor: pointer; }
.wbs-x:hover { background: var(--fill, #f2f3f5); color: var(--text, #262626); }
.wbs-dialog:focus { outline: none; }
body.wbs-open { overflow: hidden; }
@media (prefers-reduced-motion: no-preference) { .wbs-dialog { animation: wbs-in 0.14s ease-out; } @keyframes wbs-in { from { opacity: 0; transform: translateY(6px); } } }
`;

export function injectIntoBook(html, w) {
  const host = { back: { href: href(`/w/${w.slug}/`), label: w.title } };
  const config = `<script>window.WORKBOOK_HOST = ${JSON.stringify(host).replace(/</g, '\\u003c')};</script>\n`;
  const marker = '<script type="application/json" id="book-data">';
  const at = html.indexOf(marker);
  if (at < 0) throw new Error(`${w.slug}: the book has no book-data script, so it can't be published`);
  html = html.slice(0, at) + config + html.slice(at);

  const modal = `<div id="wbs-modal" hidden>
  <div class="wbs-dialog" role="dialog" aria-modal="true" aria-labelledby="wbs-title" tabindex="-1">
    <button class="wbs-x" type="button" aria-label="Close">&times;</button>
    <h2 id="wbs-title">Run this workbook on your computer</h2>
    <p class="wbs-sub">This copy of the book can't run code. On your machine, Run and Submit build your project and check it against every test.</p>
    ${startPanelHtml(w, { prefix: 'modal', heading: '', lead: false, first: 'ai' })}
  </div>
</div>`;

  const opener = `
(function () {
  var modal = document.getElementById('wbs-modal'), dialog = modal.querySelector('.wbs-dialog'), last = null;
  function open() { last = document.activeElement; modal.hidden = false; document.body.classList.add('wbs-open'); dialog.focus(); }
  function close() { modal.hidden = true; document.body.classList.remove('wbs-open'); if (last && last.focus) try { last.focus(); } catch (e) {} }
  modal.querySelector('.wbs-x').addEventListener('click', close);
  modal.addEventListener('mousedown', function (e) { if (e.target === modal) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !modal.hidden) { e.preventDefault(); close(); } }, true);
  window.WORKBOOK_HOST.runLocally = open;
})();
`;

  const block = `<style>${css}</style>\n${modal}\n<script>${startPanelJs}</script>\n<script>${opener}</script>\n`;
  const i = html.lastIndexOf('</body>');
  return i >= 0 ? html.slice(0, i) + block + html.slice(i) : html + '\n' + block;
}
