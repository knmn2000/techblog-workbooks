// The posts a workbook is built on. A workbook made from one post names it in book.sourceUrl,
// book.sourceTitle and book.author. One made from several lists them in book.sources, as
// [{ url, title, author }]; the old fields then only matter to tools that don't know the list.

// Always at least one entry (the old fields when there is no usable list), in the order written.
export function normaliseSources(book = {}) {
  const listed = (Array.isArray(book.sources) ? book.sources : [])
    .filter((s) => s && typeof s.url === 'string' && s.url.trim())
    .map((s) => ({ url: s.url.trim(), title: s.title?.trim() || s.url.trim(), author: s.author?.trim() || '' }));
  if (listed.length) return listed;
  return [{ url: book.sourceUrl, title: book.sourceTitle, author: book.author }];
}
