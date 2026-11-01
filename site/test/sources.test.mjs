// npm test: how a workbook's posts are read from workbook.json (src/lib/sources.mjs), and that the
// two workbooks already in the collection still read as they did.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { normaliseSources } from '../src/lib/sources.mjs';

const pomb = { url: 'https://pomb.us/build-your-own-react/', title: 'Build your own React', author: 'Rodrigo Pombo' };
const wim = { url: 'https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d', title: 'Creating Our Own React From Scratch', author: 'Wim Jongeneel' };

test('a workbook with one post reads its sourceUrl, sourceTitle and author', () => {
  const book = { sourceUrl: 'https://example.com/post', sourceTitle: 'A post', author: 'Someone' };
  assert.deepEqual(normaliseSources(book), [{ url: 'https://example.com/post', title: 'A post', author: 'Someone' }]);
});

test('book.sources lists every post, in the order written', () => {
  assert.deepEqual(normaliseSources({ sources: [pomb, wim] }), [pomb, wim]);
});

test('book.sources wins over the old fields, which stay as a fallback for older tools', () => {
  const book = { sources: [pomb, wim], sourceUrl: pomb.url, sourceTitle: pomb.title, author: pomb.author };
  assert.deepEqual(normaliseSources(book), [pomb, wim]);
});

test('an empty or unusable list falls back to the old fields', () => {
  const old = { sourceUrl: 'https://example.com/post', sourceTitle: 'A post', author: 'Someone' };
  const expected = [{ url: old.sourceUrl, title: old.sourceTitle, author: old.author }];
  assert.deepEqual(normaliseSources({ ...old, sources: [] }), expected);
  assert.deepEqual(normaliseSources({ ...old, sources: 'nope' }), expected);
  assert.deepEqual(normaliseSources({ ...old, sources: [null, {}, { title: 'no link' }] }), expected);
});

test('an entry without a title shows its link, and one without an author shows none', () => {
  assert.deepEqual(normaliseSources({ sources: [{ url: ' https://example.com/a ' }] }),
    [{ url: 'https://example.com/a', title: 'https://example.com/a', author: '' }]);
});

test('entries without a link are skipped, the rest are kept', () => {
  assert.deepEqual(normaliseSources({ sources: [{ title: 'lost' }, wim] }), [wim]);
});

test('a book with neither form still gives one entry, so a page never has to guess', () => {
  const [only] = normaliseSources({});
  assert.deepEqual(Object.keys(only), ['url', 'title', 'author']);
  assert.equal(normaliseSources(undefined).length, 1);
});

test('the entries are copies: changing one does not change workbook.json data', () => {
  const book = { sources: [pomb] };
  normaliseSources(book)[0].title = 'changed';
  assert.equal(book.sources[0].title, 'Build your own React');
});

// The workbooks in this repository: every one reads to at least one post with a link and a title.
const workbooks = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../workbooks');
for (const slug of fs.existsSync(workbooks) ? fs.readdirSync(workbooks) : []) {
  const file = path.join(workbooks, slug, 'workbook.json');
  if (!fs.existsSync(file)) continue;
  test(`workbooks/${slug}/workbook.json names its posts`, () => {
    const book = JSON.parse(fs.readFileSync(file, 'utf8')).book;
    const sources = normaliseSources(book);
    assert.ok(sources.length >= 1);
    for (const s of sources) {
      assert.match(s.url, /^https:\/\//);
      assert.ok(s.title, `${slug}: a post has no title`);
      assert.ok(s.author, `${slug}: a post has no author`);
    }
    if (!Array.isArray(book.sources)) assert.equal(sources.length, 1); // the old form is one post
  });
}
