# The site

The collection's website: a list of every workbook, a page for each one (what you build, how to
start, and the git and AI-prompt setup), and a read-only copy of each workbook's problem book.
It's a static Astro site, and it lives here, next to `workbooks/`, so a change to a workbook and
the site that shows it go out in the same push.

## How it gets the workbooks

At build time `src/lib/workbooks.mjs` reads `../workbooks/*/workbook.json` (set `WORKBOOKS_DIR`
to build from another checkout). For each workbook it reads the book's title and lede, the
assignments, the planned project layout, and each problem page's difficulty and concept tags.
The `site` block of `workbook.json` holds what the site needs and the tools don't: the language
label, what to install, and how to start the study server on each system.

The published book is the workbook's own `book/problem-book.html`. `src/lib/book-inject.mjs`
turns on the book's hosted mode (`window.WORKBOOK_HOST`): the editor is read-only, and typing in
it, Run, Submit and the Run locally button all open the setup dialog. The book template draws all of that
itself, so a change to the template can't break the site.

## Local development

```
npm install
npm run dev        # http://127.0.0.1:4321/techblog-workbooks/
npm run build      # writes dist/
```

## Publishing

`.github/workflows/pages.yml` publishes to GitHub Pages on every push to `main`: it rebuilds each
workbook's book from its sources, builds the site, and deploys it to
`https://knmn2000.github.io/techblog-workbooks/`. Turn it on once in the repository's
**Settings > Pages > Build and deployment > Source: GitHub Actions**.

For a custom domain, add it on the same settings page, point a `CNAME` record at
`knmn2000.github.io`, and set `SITE_BASE: /` and `SITE_URL: https://<your-domain>` as environment
variables of the build step in the workflow.
