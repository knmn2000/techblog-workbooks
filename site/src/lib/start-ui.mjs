// The "run it locally" UI (git clone / AI prompt), as plain HTML + CSS + JS strings, so the same
// markup serves the workbook page sidebar and the dialog injected into the published problem book.
import { gitCommands, aiPrompt } from './start.mjs';

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function launchText(w) {
  return [
    '# Windows',
    w.launch.windows ?? 'study.cmd',
    ...(w.launch.mac ? ['# macOS', w.launch.mac] : []),
    `# ${w.launch.mac ? 'Linux' : 'macOS and Linux'}`,
    w.launch.other ?? 'python3 -P tools/serve.py',
  ].join('\n');
}

export function term(label, body) {
  return `<div class="wbs-term" data-term><div class="wbs-term-head"><span>${esc(label)}</span><button class="wbs-copy" type="button">Copy</button></div>${body}</div>`;
}

// `first` picks which tab comes first and is open: 'git' or 'ai'. `sourceUrl` adds a View source link by the heading.
export function startPanelHtml(w, { id = '', prefix = 'p', heading = 'Solve it on your machine', lead = true, first = 'git', sourceUrl = '' } = {}) {
  const git = gitCommands(w);
  const needs = w.requires.length ? `<div class="wbs-needs"><span class="wbs-k">Needs</span>${w.requires.map((r) => `<span class="wbs-chip">${esc(r)}</span>`).join('')}</div>` : '';
  const order = first === 'ai' ? ['ai', 'git'] : ['git', 'ai'];
  const labels = { git: 'Git clone', ai: 'Ask your AI' };
  const tabs = order.map((t) => `<button role="tab" aria-selected="${t === order[0]}" data-tab="${t}" type="button">${labels[t]}</button>`).join('\n    ');
  const panes = {
    git: `<div class="wbs-pane" data-pane="git"${order[0] === 'git' ? '' : ' hidden'}>
    <ol class="wbs-steps">
      <li>
        <h3>Get the files</h3>
        <div class="wbs-modes" role="radiogroup" aria-label="What to clone">
          <label><input type="radio" name="wbs-mode-${esc(prefix)}" value="single" checked> Only this workbook</label>
          <label><input type="radio" name="wbs-mode-${esc(prefix)}" value="full"> Whole collection</label>
        </div>
        ${term('bash', `<pre data-code="single">${esc(git.single)}</pre><pre data-code="full" hidden>${esc(git.full)}</pre>`)}
      </li>
      <li>
        <h3>Start the problem book</h3>
        <p class="wbs-note">Run the command for your system from the workbook folder. The book opens in your browser with Run and Submit working.</p>
        ${term('shell', `<pre>${esc(launchText(w))}</pre>`)}
      </li>
    </ol>
  </div>`,
    ai: `<div class="wbs-pane" data-pane="ai"${order[0] === 'ai' ? '' : ' hidden'}>
    <p class="wbs-note">Paste this into any coding assistant, such as Codex, Cursor, Gemini CLI, GitHub Copilot or Claude Code. It clones the workbook, checks the tools it needs (asking before installing anything), sets up your project and starts the book. The prompt tells it not to solve anything for you.</p>
    ${term('prompt', `<pre class="wbs-wrap">${esc(aiPrompt(w))}</pre>`)}
  </div>`,
  };
  const src = sourceUrl ? `<a class="wbs-src" href="${esc(sourceUrl)}">View source</a>` : '';
  return `<section class="wbs-start"${id ? ` id="${esc(id)}"` : ''}>
  ${heading || src ? `<div class="wbs-hrow">${heading ? `<h2 class="wbs-h">${esc(heading)}</h2>` : ''}${src}</div>` : ''}
  ${lead ? `<p class="wbs-lead">Your code runs on your machine against the workbook's checker. Choose how to set it up.</p>` : ''}
  <div class="wbs-tabs" role="tablist">
    ${tabs}
  </div>
  ${order.map((t) => panes[t]).join('\n  ')}
  ${needs}
  ${w.caveat ? `<p class="wbs-caveat">${esc(w.caveat)}</p>` : ''}
</section>`;
}

export const startPanelCss = `
.wbs-start { color: var(--text, #262626); font: 14px/1.55 var(--font-ui, system-ui, sans-serif); }
.wbs-start * { box-sizing: border-box; }
.wbs-hrow { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 0 8px; }
.wbs-h { font-size: 16px; margin: 0; letter-spacing: -0.01em; }
.wbs-src { font: 600 12px/1 var(--font-ui, system-ui, sans-serif); color: var(--text-2, #595959); border: 1px solid var(--line-strong, #d4d4d8); border-radius: 6px; padding: 6px 10px; white-space: nowrap; text-decoration: none; }
.wbs-src:hover { background: var(--fill, #f2f3f5); color: var(--text, #262626); text-decoration: none; }
.wbs-lead, .wbs-note { color: var(--text-2, #595959); margin: 0 0 12px; font-size: 13px; }
.wbs-tabs { display: flex; gap: 2px; border-bottom: 1px solid var(--line, #e7e7e7); margin-bottom: 14px; }
.wbs-tabs button { font: inherit; font-weight: 600; font-size: 13px; background: none; border: 0; border-bottom: 2px solid transparent; color: var(--text-2, #595959); padding: 6px 10px; cursor: pointer; margin-bottom: -1px; white-space: nowrap; }
.wbs-tabs button:hover { color: var(--text, #262626); }
.wbs-tabs button[aria-selected="true"] { color: var(--text, #262626); border-bottom-color: var(--brand, #ffa116); }
.wbs-steps { list-style: none; counter-reset: wbs; margin: 0; padding: 0; display: grid; gap: 16px; }
.wbs-steps li { counter-increment: wbs; position: relative; padding-left: 30px; min-width: 0; }
.wbs-steps li::before { content: counter(wbs); position: absolute; left: 0; top: 0; width: 20px; height: 20px; border-radius: 50%; background: var(--fill, #f2f3f5); color: var(--text-2, #595959); font-size: 11px; font-weight: 600; display: grid; place-items: center; }
.wbs-steps h3 { font-size: 13px; margin: 1px 0 6px; }
.wbs-modes { display: flex; flex-wrap: wrap; gap: 4px 14px; margin-bottom: 8px; font-size: 13px; }
.wbs-modes label { cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.wbs-modes input { accent-color: var(--brand, #ffa116); margin: 0; }
.wbs-term { background: #17181b; border: 1px solid #34363c; border-radius: 8px; overflow: hidden; min-width: 0; }
.wbs-term-head { display: flex; align-items: center; justify-content: space-between; background: #202226; border-bottom: 1px solid #34363c; padding: 3px 4px 3px 12px; color: #8b8f98; font: 500 11px var(--font-mono, ui-monospace, monospace); }
.wbs-copy { font: 600 11px var(--font-ui, system-ui, sans-serif); color: #e6e7ea; background: transparent; border: 1px solid #3c3f46; border-radius: 5px; padding: 2px 9px; cursor: pointer; }
.wbs-copy:hover { background: #34363c; }
.wbs-term pre { margin: 0; padding: 11px 13px; white-space: pre-wrap; overflow-wrap: anywhere; color: #e6e7ea; font: 400 12px/1.65 var(--font-mono, ui-monospace, monospace); }
.wbs-term pre[hidden] { display: none; }
.wbs-term pre.wbs-wrap { max-height: 230px; overflow-y: auto; }
.wbs-needs { display: flex; flex-wrap: wrap; align-items: center; gap: 5px; margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--line, #e7e7e7); }
.wbs-k { font-size: 11px; font-weight: 600; color: var(--text-3, #8c8c8c); margin-right: 4px; }
.wbs-chip { background: var(--fill, #f2f3f5); color: var(--text-2, #595959); border-radius: 999px; padding: 0 8px; font-size: 11.5px; line-height: 19px; }
.wbs-caveat { color: var(--text-2, #595959); font-size: 12px; margin: 10px 0 0; padding: 7px 10px; background: var(--fill, #f2f3f5); border-radius: 7px; }
.wbs-start :focus-visible { outline: 2px solid var(--brand, #ffa116); outline-offset: 2px; }
`;

export const startPanelJs = `
(function () {
  function init(root) {
    if (root.dataset.wbsInit) return;
    root.dataset.wbsInit = '1';
    var tabs = [].slice.call(root.querySelectorAll('[data-tab]')), panes = [].slice.call(root.querySelectorAll('[data-pane]'));
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (x) { x.setAttribute('aria-selected', String(x === t)); });
        panes.forEach(function (p) { p.hidden = p.dataset.pane !== t.dataset.tab; });
      });
    });
    [].slice.call(root.querySelectorAll('input[type=radio]')).forEach(function (r) {
      r.addEventListener('change', function () {
        [].slice.call(root.querySelectorAll('[data-code=single],[data-code=full]')).forEach(function (p) { p.hidden = p.dataset.code !== r.value; });
      });
    });
    [].slice.call(root.querySelectorAll('[data-term]')).forEach(function (term) {
      var b = term.querySelector('.wbs-copy');
      b.addEventListener('click', function () {
        var text = term.querySelector('pre:not([hidden])').textContent;
        var done = function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1600); };
        function fallback() {
          var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
          try { document.execCommand('copy'); done(); } catch (e) {} ta.remove();
        }
        if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback); else fallback();
      });
    });
  }
  [].slice.call(document.querySelectorAll('.wbs-start')).forEach(init);
})();
`;
