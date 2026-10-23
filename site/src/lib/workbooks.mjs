// Reads the workbook collection at build time and returns what the pages need. The site lives
// in the collection's repository (site/), so the workbooks are the folder next to it; set
// WORKBOOKS_DIR to build from another checkout.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

export const REPO_URL = 'https://github.com/knmn2000/techblog-workbooks';
export const REPO_NAME = 'techblog-workbooks';
// The skill that makes the workbooks, its install instructions, and its one-line install.
export const SKILL_URL = 'https://github.com/knmn2000/tech-blog-to-workbook';
export const SKILL_INSTALL_URL = `${SKILL_URL}#install`;
export const SKILL_INSTALL_CMD = 'npx skills add knmn2000/tech-blog-to-workbook --skill blog-to-leetcode';

function collectionDir() {
  const dir = path.resolve(process.env.WORKBOOKS_DIR ?? path.join(root, '..'));
  if (!fs.existsSync(path.join(dir, 'workbooks'))) throw new Error(`No workbooks/ folder in ${dir}. Set WORKBOOKS_DIR to the collection.`);
  return dir;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

// "**Difficulty:** Easy · **Assignment** 1 of 18 · ..." and the "*Concepts:* a · b · c" tag line.
function readProblem(file) {
  const md = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  const head = md.slice(0, 14).join('\n');
  const difficulty = /\*\*Difficulty:\*\*\s*(\w+)/.exec(head)?.[1] ?? 'Medium';
  // What the workbook calls one problem ("assignment", or "checkpoint" in older workbooks).
  const unit = /\*\*(\w+)\*\*\s+\d+\s+of\s+\d+/.exec(head)?.[1]?.toLowerCase() ?? null;
  const concepts = (/\*Concepts:\*\s*(.+)/.exec(head)?.[1] ?? '')
    .split('·')
    .map((s) => s.trim().replace(/`/g, ''))
    .filter(Boolean);
  return { difficulty, concepts, unit };
}

function guessLanguage(json) {
  if (json.project?.languageLabel) return json.project.languageLabel;
  const first = Object.values(json.checkpoints)[0];
  const ext = path.extname(first?.solution ?? '').toLowerCase();
  return { '.cpp': 'C++', '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.rs': 'Rust', '.go': 'Go' }[ext] ?? 'Any';
}

// The project the learner builds: every file, which assignment creates it and which ones add to it,
// grouped by folder. Empty for a workbook without a project layout.
function projectTree(json) {
  const spec = json.project;
  if (!spec) return null;
  const files = new Map();
  for (const [id, c] of Object.entries(json.checkpoints)) {
    for (const p of c.files ?? []) files.set(p, { path: p, owner: id, adds: [], purpose: spec.purposes?.[p] ?? '' });
  }
  for (const [id, c] of Object.entries(json.checkpoints)) {
    for (const p of c.extends ?? []) files.get(p)?.adds.push(id);
  }
  const folders = new Map();
  for (const f of files.values()) {
    const cut = f.path.lastIndexOf('/');
    const dir = cut < 0 ? '' : f.path.slice(0, cut + 1);
    if (!folders.has(dir)) folders.set(dir, []);
    folders.get(dir).push({ ...f, name: f.path.slice(cut + 1) });
  }
  const programs = Object.keys(json.checkpoints).length;
  return {
    dir: spec.dir ?? 'solutions',
    name: spec.name ?? '',
    run: spec.run ?? '',
    folders: [...folders.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([dir, list]) => ({ dir, files: list })),
    programs,
  };
}

export function loadWorkbooks() {
  const dir = collectionDir();
  const workbooksDir = path.join(dir, 'workbooks');
  const out = [];

  for (const slug of fs.readdirSync(workbooksDir).sort()) {
    const wdir = path.join(workbooksDir, slug);
    const jsonFile = path.join(wdir, 'workbook.json');
    if (!fs.statSync(wdir).isDirectory() || !fs.existsSync(jsonFile)) continue;

    let json;
    try {
      json = readJson(jsonFile);
      if (!json.book?.title || !json.checkpoints) throw new Error('missing book.title or checkpoints');
    } catch (e) {
      throw new Error(`workbooks/${slug}/workbook.json is not usable: ${e.message}`);
    }

    // A workbook whose book hasn't been built yet still gets a page, without links into the book.
    const bookFile = path.join(wdir, 'book', 'problem-book.html');
    const hasBook = fs.existsSync(bookFile);
    const site = json.site ?? {};

    const checkpoints = Object.entries(json.checkpoints)
      .sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }))
      .map(([id, c]) => {
        const problemFile = path.join(wdir, c.problem);
        // An assignment whose problem page isn't written yet has no difficulty; it shows as in progress.
        const meta = fs.existsSync(problemFile) ? readProblem(problemFile) : { difficulty: null, concepts: [], unit: null };
        return { id, title: c.title, ...meta };
      });
    const unit = checkpoints.find((c) => c.unit)?.unit ?? 'assignment';

    const counts = { Easy: 0, Medium: 0, Hard: 0 };
    for (const c of checkpoints) if (c.difficulty) counts[c.difficulty] = (counts[c.difficulty] ?? 0) + 1;

    const conceptCount = new Map();
    for (const c of checkpoints) for (const t of c.concepts) conceptCount.set(t, (conceptCount.get(t) ?? 0) + 1);

    out.push({
      slug,
      title: json.book.title,
      headline: json.book.headline ?? '',
      lede: json.book.lede ?? '',
      credits: json.book.credits ?? '',
      source: { url: json.book.sourceUrl, title: json.book.sourceTitle, author: json.book.author },
      language: site.language ?? guessLanguage(json),
      languageNote: site.languageNote ?? '',
      requires: site.requires ?? [],
      launch: site.launch ?? { windows: 'study.cmd', other: 'python3 -P tools/serve.py' },
      caveat: site.caveat ?? '',
      promptNote: site.promptNote ?? site.caveat ?? '',
      checkCommand: json.book.checkCommand ?? '.\\check {id}',
      project: projectTree(json),
      checkpoints,
      unit,
      units: unit[0].toUpperCase() + unit.slice(1) + 's',
      counts,
      topConcepts: [...conceptCount.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4).map(([t]) => t),
      hasBook,
      bookFile: hasBook ? bookFile : null,
    });
  }
  return out;
}
