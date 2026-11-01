# 07 · Match children by key

**Difficulty:** Medium · **Assignment** 7 of 12 · **Check:** `.\check 07`

**Tags**
- *Language:* [`Map` and `Set`](#primer/js-maps-sets) (optional) · [`===`, `Object.is`, truthy and falsy](#primer/js-equality)
- *Library:* [the harness and scenario files](#primer/workbook-harness) · [inputs: `value` and the `input` event](#primer/dom-form-inputs)
- *Concepts:* [keys](#primer/react-keys) · [reconciliation by type and position](#primer/react-reconciliation) · [fibers](#primer/react-fibers)

## Read in the blog first

You can do this page without the post. If you want the idea first, read the opening of section [3.2, Creating the diff for the children](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children) in [Jongeneel's article](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d). That means the prose and the first figure, which compares two lists of children by key. Stop where the code of `childsDiff` begins, because that is the author's answer to this assignment. A second figure, keys in a new order, closes the section; it belongs to 08. Pombo's [Step VI](https://pomb.us/build-your-own-react/#step-vi-reconciliation) points here in one sentence: React also uses keys, for a better reconciliation. His [epilogue](https://pomb.us/build-your-own-react/#epilogue) lists reconciliation by key among the features you can add.

## Learning material

- [Keys](#primer/react-keys): what a `key` prop promises, and why it has to be unique among siblings and not across the page.
- [`Map` and `Set`](#primer/js-maps-sets): a table from key to old fiber is one way to find a child's partner. Walking the old list is the other.
- [Inputs: `value` and the `input` event](#primer/dom-form-inputs): the scenarios type into inputs, and typed text lives only on the node. Rebuild the node and the text is gone.
- [Reconciliation by type and position](#primer/react-reconciliation): used here in a new way. Position still decides for children without a key, and a matched pair has to agree on type.
- [`===`, `Object.is`, truthy and falsy](#primer/js-equality): put to a new use. The empty string is a legal key, and it is falsy.

## Source material

- Wim Jongeneel, [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children), section 3.2 on the diff for the children, and the [repository](https://github.com/WimJongeneel/ts-reactive-rendering) behind it
- Rodrigo Pombo, [Step VI: Reconciliation](https://pomb.us/build-your-own-react/#step-vi-reconciliation)
- React documentation: [Rendering lists](https://react.dev/learn/rendering-lists) and [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)

## Where this fits

Position matching, as in 06, pairs a new child with whatever stood in its slot. Put one item in front of a list and it falls apart. Every old node takes its neighbour's text, and a spare node is tacked on at the end. A key tells the library which child is which. Only `reconcile.js` changes.

## The problem

Teach `reconcileChildren` to pair each new child with the old child that has the same key, wherever that old child stood. A scenario renders a list, renders an edited list and dumps the page. Every dump is compared with React's, and the checker also counts the DOM nodes your program built and removed.

### Input

The checker starts `node assignments/assignment_07_keys.js <input-file> <output-file>`. The program is short. Import `../harness/env.js` first: your library has to load after the fake page and the controllable idle callback exist. Import your `Didact` object from `src/didact/index.js`. End with `await runScenarioFile(process.argv[2], process.argv[3], Didact)`, where `runScenarioFile` comes from `../harness/scenario.js`. The Boilerplate has it written. From a blank start, those lines are yours. A scenario uses these lines:

| Line | What happens |
|---|---|
| `tree <name> <markup>` | Stores a tree of one root element under a name. `key="a"` is an attribute like the rest and lands in `props.key` as a string. |
| `render <name>` | Calls `Didact.render` with that tree and the container. No work runs yet. |
| `flush` | Runs idle periods until your work loop is idle. Each `render` here gets a `flush` before the next command. |
| `type #<id> <text>` | Sets the `value` of the element with that id to the rest of the line, fires a bubbling `input` event, then flushes. |
| `dump` | Prints the page. |
| `ops create remove` | Prints how many nodes the harness DOM created and how many `removeChild` calls it saw since the previous `ops` line (or since the start). |

Inputs in the markup have an id and no `value` attribute, so typed text is the only value they ever hold. Keys are unique among siblings. Two lists in one tree may reuse a key, though, and a key dropped from a list may return in a later render as a new child.

### Output

A `dump` opens with a counter line, then lists the container's content, parents before children. The container itself is not printed, so a root element sits at depth 0.

```
dump <n>
node <depth> <label> <tag> "<props>"
text <depth> "<text>"
```

The props field holds `className`, `id`, `title` and, on inputs, `value`, whenever they differ from their defaults. They are sorted by name and separated by spaces, and a value containing a space, a quote or `%` is percent-encoded. Neighbouring text nodes share one `text` line.

The tests read labels. Elements are named `a`, `b`, `c`, ... `z`, `aa`, ... in the order dumps first show them, and a node keeps its label in every later dump. The same label in two dumps is therefore the same DOM node, and a node you rebuild shows up under a new letter even when it looks identical.

An `ops` line is `ops <creates> <removes>`. A create is one `createElement` or `createTextNode` call on the harness DOM, so elements and text nodes both count. A remove is one `removeChild` call.

### How children are matched

These rules work on the children of one parent at a time, and again inside every matched pair.

| New child | It continues | Otherwise |
|---|---|---|
| has a key | the old child with that key, if its type is the same | a new node is built; an old child with that key but another type is removed |
| has no key | the old child at the same position, if that has no key either and the same type | a new node is built; an old child at that position of another type is removed |

- A key is `String(props.key)`. A child whose `props.key` is missing, `null` or `undefined` has none. Keys are compared as those strings, as they are. The empty string is a key and `"0"` is a key. `"1"` and `"01"` are two keys, and so are `"0"` and `""`. Duplicate keys among siblings are not tested, so what happens to them is up to you.
- A child that continues an old one keeps the old node. Its props and text are brought up to date as in 06, and its own children are matched by these same rules.
- A keyed child never continues an unkeyed one, and an unkeyed child never continues a keyed one. The tests switch whole lists from one kind to the other and do not mix both kinds in one list, so a mixed list is yours to define.
- A new node goes before the first later sibling that is already standing in the page, or last if there is none. Several new children in a row follow the same rule.
- An old child that no new child continues is removed, with one `removeChild` for the child's own node, whatever it holds.
- In this assignment the keys that two renders share come in the same order in both. A list that reorders its keys is assignment 08.

## Requirements

Each case targets one requirement. A failing run names the requirement most of its failures point to.

- **R1** Rendering a list again with the same keys in the same order keeps every node, and the changed props and text are written into the kept nodes.
- **R2** A new keyed child is built and placed where the new list has it: at the front, in the middle or at the end.
- **R3** A child whose key is still in the list keeps its node, and every node below it, while other children are added and removed around it, over several renders too.
- **R4** A child whose key is missing from the new list is removed, that one only: first, last, middle, several next to each other, or all.
- **R5** A key that is new, or a known key on a different tag, gives a new node in the place of the old child.
- **R6** An input keeps what was typed into it for as long as its key is in the list. A new input starts empty.
- **R7** Keys are compared as exact strings: `""` is a key, `"0"` is a key, and `"1"`, `"01"` and `"001"` are three keys.
- **R8** Children without a key match by position, and a keyed child never matches an unkeyed one.
- **R9** `ops create remove` counts a create for every element and text node of a new child and one remove for every removed child, and nothing for kept ones.
- **E2E** Longer sessions on lists between other elements, among them seeded random ones.

## Examples

### Example 1: a new item in front (test `07-R2-front`)

```
input:   tree t1 <ul><li key="a">item a</li><li key="b">item b</li></ul>
         render t1
         flush
         dump
         ops create remove
         tree t2 <ul><li key="z">item z</li><li key="a">item a</li><li key="b">item b</li></ul>
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
         ops 5 0
         dump 2
         node 0 a ul ""
         node 1 d li ""
         text 2 "item z"
         node 1 b li ""
         text 2 "item a"
         node 1 c li ""
         text 2 "item b"
         ops 2 0
```

The new `li` comes first and takes the new label `d`. The two old items keep `b` and `c`, text included. Nothing is rewritten. Position matching would have written `item z` into the first node and built a spare at the end. On the `ops` lines, the first says five creates: the `ul`, two `li`s and two texts. The second says two, the `li` and its text, and no removes.

### Example 2: the empty key (test `07-R7-empty-key-front-removal`)

```
input:   tree t1 <ul><li key="x">item x</li><li key="">item empty</li><li key="y">item y</li></ul>
         render t1
         flush
         dump
         ops create remove
         tree t2 <ul><li key="">item empty</li><li key="y">item y</li></ul>
         render t2
         flush
         dump
         ops create remove

output:  dump 1
         node 0 a ul ""
         node 1 b li ""
         text 2 "item x"
         node 1 c li ""
         text 2 "item empty"
         node 1 d li ""
         text 2 "item y"
         ops 7 0
         dump 2
         node 0 a ul ""
         node 1 c li ""
         text 2 "item empty"
         node 1 d li ""
         text 2 "item y"
         ops 0 1
```

Item `x` is gone. The other two keep `c` and `d`. Watch the middle child, whose key is `""`. A test written as `if (key)` takes it for a child without a key, goes looking for it by position, finds `x` there instead and rebuilds it.

### Example 3: typed text and a new key (test `07-R6-key-change-resets`)

```
input:   tree t1 <ul><li key="a"><input id="ia"/></li><li key="b"><input id="ib"/></li></ul>
         render t1
         flush
         dump
         ops create remove
         type #ia typed
         type #ib kept
         tree t2 <ul><li key="a2"><input id="ia"/></li><li key="b"><input id="ib"/></li></ul>
         render t2
         flush
         dump
         ops create remove

output:  dump 1
         node 0 a ul ""
         node 1 b li ""
         node 2 c input "id=ia"
         node 1 d li ""
         node 2 e input "id=ib"
         ops 5 0
         dump 2
         node 0 a ul ""
         node 1 f li ""
         node 2 g input "id=ia"
         node 1 d li ""
         node 2 e input "id=ib value=kept"
         ops 2 1
```

The first item's key changed from `a` to `a2`. That makes it a new child, even though its id is the one it had. Its `li` and `input` are new (`f` and `g`), the word `typed` went away with the old input, and the old `li` is removed. That is two creates and one remove. The remove counts once because the old `li` is one child, and the input inside leaves with it. The second item still has the key `b`, so `d` and `e` are the old nodes and the input still holds `kept`.

## Constraints

No scenario runs past 56 lines, 7 renders or 12 children in a list. Texts are single words, or two words for typed values. The 47 tests cover every requirement, two longer sessions and seven seeded random runs (a fresh seed gives seven new ones). Each case has a 10-second limit and takes a fraction of a second.

## Hints

<details><summary>Hint 1: where to start</summary>

In 06 the child at slot `i` is compared with the old fiber at slot `i`. With keys, the old child you want can stand several slots away. Write a function from the new element and the old children to its partner, and call it where 06 picks the old fiber at the same position.
</details>

<details><summary>Hint 2: the approach</summary>

Go through the new elements in order and find each one's partner among the old children: by key if it has one, by position if not. A partner of the same type gives a fiber that keeps the partner's DOM node and links back to it (an update). Otherwise the fiber gets a node of its own (a placement), and if a partner of another type turned up, queue that old fiber for removal. When the elements run out, queue every old child that no new child took. A table from key to old fiber makes the lookup a single step. Walking forward through the old list works as well, since in this assignment the keys that survive keep their order.
</details>

<details><summary>Hint 3: the traps</summary>

- The key `""` is falsy. Compare with `=== undefined` or `== null`, never with `if (key)`.
- Convert a key with `String` and keep it a string. Turning `"01"` into the number 1 merges it with `"1"`, and `""` and `"0"` both become 0.
- The next old child is not always the next one to match. Old children that the walk passes over without a partner are removed.
- Several new children in a row: the sibling after the first new node may be new too, with no place in the page yet. Insert before the first following sibling that is already in the page.
- Queue each removed fiber once, and remove only its own node. The nodes below it go with it.
- Same key on a different tag means the old child is removed and the new one is built. It does not keep the node.
- A child without a key gets a partner only when the old child at its position has no key either.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
reconcileChildren(wipFiber, elements):
    oldFibers = children of wipFiber.alternate, in order
    claimed = empty set
    for each element, at position i:
        key = element.props.key, or none if it has none
        partner = old fiber with that key        (key given)
                  old fiber at position i         (no key, and that fiber has no key)
        if partner exists and partner.type == element.type:
            fiber = update fiber, dom = partner.dom, alternate = partner
        else:
            fiber = placement fiber, new dom to be made
            if partner exists: queue partner for removal
        claimed.add(partner)
        add fiber to the new list
    for each old fiber not in claimed: queue for removal
    link the new list with child and sibling
```
</details>

## Checking your solution

```
.\check 07                          every test, grouped by requirement
.\check 07 -Case 07-R2-front        one test with its input, the expected output and yours
.\check 07 -Fresh                   seven new random sessions, to try your code on scenarios you haven't seen
.\check 07 -Dispute <id> "why"      set aside a test you are sure is wrong
```

A reconciler that appends every new node, which is what Jongeneel's code does with a new first item, fails like this:

```
  R2  A new keyed child is built and placed where the new list has it: ... .    1 / 7   FAILED
      x 07-R2-front  a keyed item is added in front of two others
          node[0]: expected (depth=1, label=d, tag=li, props=""), got (depth=1, label=b, tag=li, props="") - differs in label  (in `dump 2`)
          likely cause: R2 - A new keyed child is built and placed where the new list has it: at the front, in the middle or at the end
          expected values from: React 19.3.1 on jsdom 30.1.3 (tools/oracle); ops lines from a model of the matching rules in tools/gen_p07.py
          reproduce: py -P tools/run_js.py build/bugs/07/front-insert-appended 07 build/cases/07/07-R2-front.in build/cases/07/07-R2-front.out
```

## After you pass: compare with the author's code

[Jongeneel's children diff](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d#:~:text=3.2%20Creating%20the%20diff%20for%20the%20children) is `childsDiff`. It keeps two lists of what is left, `remainingOldChilds` and `remainingNewChilds`, and finds the first old child whose key also occurs in the new list. This page calls that child the pivot; the code only keeps its key, in `nextUpdateKey`. `removeUntilkey` queues a `remove` for every old child in front of the pivot, `insertUntilKey` queues an `insert` for every new child in front of the pivot's partner, and the pair itself gets the diff of its two nodes, an `update`, a `replace` or a `skip`. The loop goes round again on what is left, and the leftovers are removed, then inserted. `applyChildrenDiff` replays the resulting list of operations against the DOM with a running offset. The workbook has no such list. As in 06, `reconcileChildren` builds the new fibers and tags them, and the commit places them.

Replay that list and an item that belongs at position 0 ends up at the end whenever other children are still in the page. The code looks up the node before the item's position, finds none at index -1 and falls back to appending. The post's own second figure, `A, B, C` to `B, A, C`, leaves the list reading `A, B, B` when you run it. The loop `while (nextUpdateKey)` also ends early on a falsy key. The empty string is one. The post gives every text node that key by default. A text child is therefore removed and built again on every render, and a list whose first shared key is falsy goes through the removal and insertion sweep as a whole. A list of children without keys gets an empty operation list, so no change to it ever reaches the page. The TypeScript types require a key on `createElement`, which hides that. Here such children match by position, as in 06.

The post lets a key be a string or a number and compares keys as they are, with `indexOf` when it looks for the next pair and with `!=` when it sweeps, so `1` and `"1"` can come out as one key or as two. Here a key is `String(props.key)`. A key that is in both lists but reached in a different order is removed and inserted again, because the post says outright that it does not support reordering. Assignment 08 changes that, the way React does. Section 5.6 later makes `removeUntilkey` unmount a removed child that is itself a component, and nothing deeper: a component inside a removed element gets no unmount call. Components arrive in 09, and 11 checks the cleanup.

`createElement` in the post also deletes `key` from the props object it receives, which alters the caller's object. Here `key` stays an ordinary prop. The table in [React today](docs/react-today.md) shows where React 19 and the posts part ways, and its row on keys is the one that applies.
