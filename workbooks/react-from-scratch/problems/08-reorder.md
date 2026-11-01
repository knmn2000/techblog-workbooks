# 08 · Reorder keyed children

**Difficulty:** Hard · **Assignment** 8 of 12 · **Check:** `.\check 08`

**Tags**
- *Language:* [`Map` and `Set`](#primer/js-maps-sets) · [array methods](#primer/js-arrays)
- *Library:* [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing) · [inputs: `value` and the `input` event](#primer/dom-form-inputs)
- *Concepts:* [reordering without recreating](#primer/react-moving-nodes) · [keys](#primer/react-keys) · [fibers](#primer/react-fibers)

## Read in the blog first

Neither post has this step. Jongeneel's article states that its key matching cannot reorder: a key that shows up in a different order is removed and built again, and a stateful component loses its state with it. Pombo's [Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation) has an aside saying React detects children that change places, and his [epilogue](https://pomb.us/build-your-own-react/#epilogue) lists reconciliation by key among the features you can add. This assignment follows React instead, and the workbook, not a post, is its author. The page holds all you need, and [Rendering lists](https://react.dev/learn/rendering-lists) on react.dev shows the same behaviour from the user's side. If you read Jongeneel's [section 3.2, Creating the diff for the children](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children) first, the last figure of the section shows keys in a new order, which is the case here. The post builds its B again. Here B keeps its node.

## Learning material

- [Reordering without recreating](#primer/react-moving-nodes): how a node changes places without being thrown away, and why its typed text comes along.
- [`appendChild`, `insertBefore`, `removeChild`](#primer/dom-tree-editing): a new use for it. Inserting a node that already has a parent moves it.
- [Keys](#primer/react-keys): used in a new way. A key now finds its child wherever it stood.
- [`Map` and `Set`](#primer/js-maps-sets): a different use this time. With the keys out of order, walking the old list beside the new one stops working. A table from key to old fiber doesn't care about order.
- [Inputs: `value` and the `input` event](#primer/dom-form-inputs): put to new use. The tests type before a reorder and read the text afterwards.

## Source material

- React documentation: [Rendering lists](https://react.dev/learn/rendering-lists), [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children), section 3.2 on the diff for the children, for the case it leaves out
- MDN, [`Node.insertBefore`](https://developer.mozilla.org/en-US/docs/Web/API/Node/insertBefore), which says what happens to a node that is already in the document

## Where this fits

07 finds an old child by key only while the shared keys keep their order. Now any order goes. `reconcile.js` has to find a partner anywhere in the old list and notice which kept children ended up out of order. `commit.js` then puts those nodes where they now belong without building new ones.

## The problem

Let a keyed list change order. A scenario renders a list, then a permutation of it, often with items added and dropped in the same step. It types into inputs here and there and dumps the page. Each dump is compared with React's, and the checker counts the nodes your program built and removed.

### Input

Each scenario goes through `node assignments/assignment_08_reorder.js <input-file> <output-file>`. From a blank start that program is yours to write, in three steps: load `../harness/env.js` before anything else, import the default `Didact` export of `src/didact/index.js`, and `await` the harness function `runScenarioFile` (from `../harness/scenario.js`) with the two file names from `process.argv` and `Didact`. The Boilerplate comes with it done. These are the scenario lines this assignment relies on.

| Line | Effect |
|---|---|
| `tree <name> <markup>` | Remembers a one-root tree under a name. `key="a"` is a string attribute and arrives as `props.key`. |
| `render <name>` | Calls `Didact.render(tree, container)` and returns. Nothing is drawn yet. |
| `flush` | Runs idle periods until the loop has nothing left. A `render` is always followed by a `flush`. |
| `type #<id> <text>` | Writes the rest of the line into the `value` of the element with that id, fires a bubbling `input` event and flushes. |
| `dump` | Prints the container, as described next. |
| `ops create remove` | Prints the harness DOM's counters of `create` and `remove` since the last `ops` line or since the start. |

Inputs carry an id and no `value` attribute. Sibling keys are unique, though one tree may use the same key in two different lists. The keys of a later render can come in any order.

### Output

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

A dump prints the container's content from the top: one `node` line per element, one `text` line per run of text, a parent before its children, and the container itself left out. The props field lists `className`, `id`, `title` and (on inputs) `value` when they are off their defaults, sorted by name, with spaces, quotes and `%` percent-encoded.

A label is a node's identity across dumps. The first time a dump shows an element it takes the next unused name from `a`, `b`, ... `z`, `aa`, ..., and it keeps that name for the rest of the scenario. Equal labels in two dumps are one DOM node. A node moved to another place keeps its label, which is how the tests tell a move from a rebuild. Lines come in page order.

`ops <creates> <removes>` counts calls: `createElement` plus `createTextNode` for the first number, `removeChild` for the second. A move is neither, and the line leaves the move counter out.

### What has to be true after a render

- Every new child with a key continues the old child with the same key and the same type, wherever the old child stood. The old node is kept. A key is `String(props.key)` as in 07, and a missing, `null` or `undefined` key means no key.
- The children of every parent end up in the new list's order, a new child at its own place.
- A kept child gets its new props and text, whether or not its node moved. Its own children are matched by the same rules.
- A new child whose key no old child has, or whose key has an old child of another type, gets a new node. Old children that no new child continues are removed, one `removeChild` each for the child's own node.
- Children without a key are matched by position, as in 06. Swapping their texts changes the texts in the same nodes and never moves a node. The tests do not mix keyed and unkeyed children in one list.
- Keys are exact strings: `""`, `"0"`, `"1"` and `"01"` are four keys, and none of them is "no key".
- Which nodes you move, and how many, is up to you. Any set of moves that ends in the right order without building anything new passes, so a permutation of the same keys costs `ops 0 0`.

## Requirements

Each test is filed under one requirement, and the report tallies the passes for each.

- **R1** The same keys in a new order (swap, reverse, rotate) put the nodes in that order, and every node is a kept one.
- **R2** A reorder in the same render as new and removed keys: the kept children keep their nodes in the new order, new ones are built, missing ones are removed.
- **R3** An input keeps what was typed into it when its item moves, and typing into it afterwards still reaches it.
- **R4** A child that moves still receives its new props and text, including the removal of a prop.
- **R5** `ops create remove` is `0 0` for a pure reorder, and counts only the new children's nodes and the removed children otherwise.
- **R6** Lists inside items reorder on their own, and an item that moves takes its nested nodes along.
- **R7** The keys `""`, `"0"`, `"1"` and `"01"` move like any other key.
- **R8** Children without a key are matched by position, even when their texts come in another order.
- **R9** Long runs of reorders, insertions and removals.
- **E2E** Whole sessions on sortable rows and on a list between other elements.

## Examples

### Example 1: a shuffle with one new and one dropped item (test `08-R2-shuffle-insert-remove`)

```
input:   tree t1 <ul><li key="a">item a</li><li key="b">item b</li><li key="c">item c</li><li key="d">item d</li></ul>
         render t1
         flush
         dump
         ops create remove
         tree t2 <ul><li key="d">item d</li><li key="x">item x</li><li key="a">item a</li><li key="c">item c</li></ul>
         render t2
         flush
         dump
         ops create remove

output:  dump 1
         node 0 a ul ""
         node 1 b li ""
         text 2 "item a"
         node 1 c li ""
         text 2 "item b"
         node 1 d li ""
         text 2 "item c"
         node 1 e li ""
         text 2 "item d"
         ops 9 0
         dump 2
         node 0 a ul ""
         node 1 e li ""
         text 2 "item d"
         node 1 f li ""
         text 2 "item x"
         node 1 b li ""
         text 2 "item a"
         node 1 d li ""
         text 2 "item c"
         ops 2 1
```

Item `d` went from last to first, and `a` and `c` stayed behind it in their old order. In the second dump the labels `e`, `b` and `d` are the old `li`s of `d`, `a` and `c`. Item `x` is `f`, a new node. The node of item `b` is gone. The counters: one new `li` with its text is two creates, one dropped `li` is one remove. The three reordered items cost nothing.

### Example 2: two inputs trade places (test `08-R3-bare-inputs-swap`)

```
input:   tree t1 <div><input key="a" id="ia"/><input key="b" id="ib"/></div>
         render t1
         flush
         dump
         ops create remove
         type #ia left
         type #ib right
         dump
         tree t2 <div><input key="b" id="ib"/><input key="a" id="ia"/></div>
         render t2
         flush
         dump
         ops create remove
         type #ib right!
         dump

output:  dump 1
         node 0 a div ""
         node 1 b input "id=ia"
         node 1 c input "id=ib"
         ops 3 0
         dump 2
         node 0 a div ""
         node 1 b input "id=ia value=left"
         node 1 c input "id=ib value=right"
         dump 3
         node 0 a div ""
         node 1 c input "id=ib value=right"
         node 1 b input "id=ia value=left"
         ops 0 0
         dump 4
         node 0 a div ""
         node 1 c input "id=ib value=right!"
         node 1 b input "id=ia value=left"
```

Typed text lives on the nodes and nowhere in your library, so it travels with the node. `c` comes first in dump 3 and still reads `right`. The last `type` looks `ib` up in the page and writes to whichever node is first now. A library that built two new inputs would show the labels `d` and `e` in dump 3, both empty.

### Example 3: moved nodes still get their new props (test `08-R4-moved-props-change`)

```
input:   tree t1 <ul><li key="a" className="x" title="t">A</li><li key="b" id="bb">B</li><li key="c">C</li></ul>
         render t1
         flush
         dump
         ops create remove
         tree t2 <ul><li key="c" className="new">C</li><li key="b" title="now">B</li><li key="a" className="y">A</li></ul>
         render t2
         flush
         dump
         ops create remove

output:  dump 1
         node 0 a ul ""
         node 1 b li "className=x title=t"
         text 2 "A"
         node 1 c li "id=bb"
         text 2 "B"
         node 1 d li ""
         text 2 "C"
         ops 7 0
         dump 2
         node 0 a ul ""
         node 1 d li "className=new"
         text 2 "C"
         node 1 c li "title=now"
         text 2 "B"
         node 1 b li "className=y"
         text 2 "A"
         ops 0 0
```

Whether a node moved or stayed, its props changed too. `a` swaps `className=x title=t` for `className=y`, `b` loses its id and gains a title, `c` gains a class. A program that treats "moved" as the whole story for a node and skips the prop comparison prints the old props here.

## Constraints

No scenario goes past 74 lines, 11 renders or 10 children in a list. The 42 tests hold cases for each requirement, two longer sessions and seven seeded random runs: shuffles with inserts and removals, some with inputs and typing in between. A fresh seed gives seven new ones. Each case has a limit of 10 seconds, and a correct program needs a small fraction of that.

## Hints

<details><summary>Hint 1: where to start</summary>

In 07 you walked the old list in step with the new one. A reorder breaks that, because the partner of the next new child can lie before the old child you are looking at. Replace the walk with a lookup that doesn't care where the old child stood. Then there is the second job, getting the nodes into the new order. Treat it as a problem of its own.
</details>

<details><summary>Hint 2: the approach</summary>

Put the old children in a table by key. Go through the new elements in order and take each partner out of the table: same key and same type means a kept fiber that carries the old node, anything else means a new node. Whatever is left in the table is removed.

For the order, give every fiber its position in its list. Compare each kept child's old position with the highest old position among the kept children before it in the new list. If it is lower, a later child has passed it and its node has to move. If it is higher, the child stays. It becomes the new highest. The children that stay form an increasing run of old positions. Moving as few nodes as possible would mean keeping a longest such run in place; this rule keeps a run that is not always the longest, and the tests accept that.

In the commit, a moved node and a new node go through the same insertion: put it in front of the first later sibling that already stands in the right place, or at the end. Insertion of a node that has a parent moves it. Moved nodes still get their props updated.
</details>

<details><summary>Hint 3: the traps</summary>

- A moved fiber is a kept one. Give it the old node and the old fiber as its alternate, and tag it for placement as well.
- A new node and a moved node both go before the first later sibling that is already settled. A sibling that is new or moving itself is not settled yet, and it may not be in the page at all.
- Update a moved node's props too. The commit step for placement must not replace the update.
- Removed children are the ones left in the table. Do not remove a child that you matched and moved.
- Children without a key have nothing to look up, so match them by position. Reverse `<li>A</li><li>B</li><li>C</li>` and the result is three text updates, not a remove and an insert.
- The key `""` is falsy and `"0"` is not. Test whether a child has a key with `== null`, not with `if (key)`.
- Each fiber's old position has to survive from one render to the next, so store it on the fiber when you make it.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
reconcileChildren(wipFiber, elements):
    table = map from slot to old fiber, for each old child
            (slot = key, or position when the child has no key)
    highest = 0
    for each element, at position i:
        slot = key, or i if it has no key
        partner = table.get(slot); table.delete(slot)
        fiber = update fiber (old dom, alternate = partner)   if partner has the same type
                placement fiber (new dom)                       otherwise; if partner exists, queue it for removal
        fiber.index = i
        if fiber has a partner:
            if partner.index < highest: tag fiber for moving
            else: highest = partner.index
        add fiber to the new list
    queue every old fiber still in the table for removal
    link the new list

commitWork(fiber):
    if fiber is tagged for placement or moving:
        insert fiber.dom before the first later sibling that is not tagged
    if fiber has an alternate: updateDom(fiber.dom, alternate.props, props)
    commit the children
```
</details>

## Checking your solution

```
.\check 08                          every test, grouped by requirement
.\check 08 -Case 08-R4-moved-props-change   one test with its input, the expected dumps and yours
.\check 08 -Fresh                   seven new random sessions, to try your code on scenarios you haven't seen
.\check 08 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A reconciler that answers an out-of-place key by removing the old node and building a new one, which is what Jongeneel's does, fails like this:

```
  R1  Rendering the same keys in a new order puts the nodes in that ord... .    0 / 7   FAILED
      x 08-R1-swap-first-two  [a, b, c] becomes [b, a, c]
          node[0]: expected (depth=1, label=b, tag=li, props=""), got (depth=1, label=e, tag=li, props="") - differs in label  (in `dump 2`)
          likely cause: R1 - Rendering the same keys in a new order puts the nodes in that order and keeps every one of them
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle); ops lines from a model of the matching rules in tools/gen_p07.py
          reproduce: py -P tools/run_js.py build/bugs/08/reorder-as-remove-and-insert 08 build/cases/08/08-R1-swap-first-two.in build/cases/08/08-R1-swap-first-two.out
```

## After you pass: compare with the author's code

[Jongeneel's `childsDiff`](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children) has no operation for moving a node. Its vocabulary is update, replace, skip, remove and insert. A key that the new list reaches before the old list does is inserted as a brand new node, and its old node is removed when the walk gets there. His second figure, `A, B, C` to `B, A, C`, becomes insert B, update A, remove B, update C: one node built and one thrown away, and a stateful component in it would start over. The article calls this a simplified implementation and says reordering is not supported. Replayed by his `applyChildrenDiff`, the list also hits the front-insert problem described in 07, and the page ends up reading `A, B, B`. Here the same keys cost no node at all (R1, R5). Typed text survives (R3). His loop `while (nextUpdateKey)` also stops on a falsy key, which R7 asks about again with moves involved.

[Pombo's `reconcileChildren`](https://pomb.us/build-your-own-react/#step-vi-reconciliation) compares by position and ignores `key`, although an aside in the post says React also uses keys, which lets it detect children that change places. Position matching is still the rule for children without a key. R8 tests that. Reverse a list that has no keys and the nodes stay put while their texts change.

React keeps every key that is in both lists as the same node and moves only some of them: it remembers the highest old index among the children matched so far and moves a child whose old index is lower, which is the rule in Hint 2. The tests don't count moves, so a program that moves every kept child in turn passes as well. In [React today](docs/react-today.md), the row on keys says that reordering moves DOM nodes, which is what this assignment asks of you.
