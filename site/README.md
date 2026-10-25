# The site

The collection's website. A list of the workbooks, a page for each (what you build, how to start,
the git and AI-prompt setup), and a read-only copy of each workbook's problem book. It's a static
Astro site that sits next to `workbooks/`, so a workbook change and the page that shows it ship in
the same push.

## How it gets the workbooks

At build time `src/lib/workbooks.mjs` reads `../workbooks/*/workbook.json`; set `WORKBOOKS_DIR` to
build from a different checkout. From each one it takes the book's title and lede, the
assignments, the planned project layout, and every problem page's difficulty and concept tags.
Whatever the site needs and the tools don't lives in the `site` block of `workbook.json`: the
language label, what to install, how to start the study server on each system, and two optional
notes, `caveat` for the setup panel and `promptNote` for the AI prompt.

The published book is the workbook's own `book/problem-book.html`. `src/lib/book-inject.mjs`
switches on the book's hosted mode (`window.WORKBOOK_HOST`), which makes the editor read-only.
Typing in it, Run, Submit and the Run locally button all open the setup dialog instead. The book
template draws that dialog itself, so a template change can't break the site.

## Local development

```
npm install
npm run dev        # http://127.0.0.1:4321/
npm run build      # writes dist/
```

## Publishing

Every push to `main` runs `.github/workflows/pages.yml`, which rebuilds each workbook's book from
its sources, builds the site and deploys it to GitHub Pages at
`https://workbooks.2mbproblems.com/`. Turn it on once in the repository's settings: under
Settings > Pages > Build and deployment, set Source to GitHub Actions.

The custom domain goes on the same settings page, with a `CNAME` record pointing at
`knmn2000.github.io`. The workflow's build step sets `SITE_BASE: /` and
`SITE_URL: https://workbooks.2mbproblems.com`.
