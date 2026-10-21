// The two ways to start a workbook: git commands, and a prompt to hand to an AI assistant.
import { REPO_URL, REPO_NAME } from './workbooks.mjs';

export function gitCommands(w) {
  const url = `${REPO_URL}.git`;
  return {
    single: [
      `git clone --depth 1 --filter=blob:none --sparse ${url}`,
      `cd ${REPO_NAME}`,
      `git sparse-checkout set workbooks/${w.slug}`,
      `cd workbooks/${w.slug}`,
    ].join('\n'),
    full: [`git clone ${url}`, `cd ${REPO_NAME}/workbooks/${w.slug}`].join('\n'),
  };
}

export function aiPrompt(w) {
  const git = gitCommands(w).single;
  const needs = w.requires.length ? w.requires.map((r) => `   - ${r}`).join('\n') : '   - whatever the workbook README lists under what it needs';
  const launchWin = w.launch.windows ?? 'study.cmd';
  const launchOther = w.launch.mac && w.launch.other ? `${w.launch.mac} on macOS, ${w.launch.other} on Linux` : (w.launch.other ?? 'python3 -P tools/serve.py');
  const first = w.checkpoints[0]?.id ?? '01';
  const project = w.project
    ? `\n4. Set up my project: run "py -P tools/project.py setup" on Windows ("python3 -P tools/project.py setup" elsewhere). It creates solutions/, the ${w.language} project I'll build one ${w.unit} at a time. If I'd rather use another language, the README says how.\n`
    : '\n';
  const n = w.project ? [5, 6] : [4, 5];
  return `I want to work through the "${w.title}" workbook (${REPO_URL}/tree/main/workbooks/${w.slug}). Please set it up on my machine so I can start solving it. Work step by step and tell me what you're doing.

1. Clone only this workbook:

${git}

2. Read the workbook's README.md in that folder; it is the source of truth for setup.

3. Detect my operating system, then check which of these I have installed and tell me what's missing:
${needs}
   For anything missing, show me the install command for my OS and ask before running it.
${project}
${n[0]}. Start the study server from the workbook folder and leave it running: on Windows run ${launchWin}; elsewhere run ${launchOther}. (Python 3 is "py" on Windows and "python3" elsewhere.) Then tell me the URL to open (usually http://127.0.0.1:8787).

${n[1]}. Confirm it works: run the checker for ${w.unit} ${first} (".\\check ${first}" in PowerShell, "python3 -P tools/check.py ${first}" elsewhere). The first run creates that ${w.unit}'s files; the second should say "Not implemented yet", because the starter code leaves the work to me. A setup or build error means something is wrong, so fix it.${w.promptNote ? `\n\nNote: ${w.promptNote}` : ''}

Ground rules: I want to solve the ${w.unit}s myself. Don't write solutions, and don't open or summarise anything in the _spoilers/ folder or the Editorial. Help only with setup, and with a problem only when I ask.`;
}
