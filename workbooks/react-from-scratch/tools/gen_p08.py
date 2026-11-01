"""Test cases for assignment 08 (reorder keyed children).

    py -P tools/gen_p08.py                                  # tests/08 (seed 1)
    py -P tools/gen_p08.py --seed 777 --out build/fresh/08  # what `.\\check 08 -Fresh` runs

Dump lines come from real React 19 on jsdom (tools/oracle), `ops create remove` lines from the model in
gen_p07.py (shared with this generator: the script builder, the model, the random lists). The model matches
children by key with a lookup table and ignores their order, which is exactly what a correct reorder
does: a permutation creates nothing and removes nothing. The `move` counter is not compared (a program
may move more nodes than React does and still be right).

Same rules as for 07: `flush` between renders, unique keys among siblings, lists that never mix keyed and
unkeyed children, uncontrolled inputs with ids. Unlike 07, the keys two renders share may change order.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbcore  # noqa: E402
from gen_p07 import (  # noqa: E402
    COMPARE, ODD_POOL, PLAIN_POOL, Book, Lists, Script, field_item, fields, keyed, li, plain, ul, word,
)
from reactgen import rng_for  # noqa: E402

REQUIREMENTS = [
    ("R1", "Rendering the same keys in a new order puts the nodes in that order and keeps every one of them"),
    ("R2", "A reorder together with new and removed keys: kept children keep their nodes, in the new order"),
    ("R3", "An input keeps what was typed into it when its item moves, and typing into it afterwards still works"),
    ("R4", "A child that moves still receives its new props and text"),
    ("R5", "`ops create remove` is 0 0 for a pure reorder, and counts only the new and removed children otherwise"),
    ("R6", "Lists inside items reorder on their own, and an item that moves takes its nested nodes along"),
    ("R7", "Keys such as \"\", \"0\", \"1\" and \"01\" move like any other key"),
    ("R8", "Children without a key still match by position, even when their texts are reordered"),
    ("R9", "Long runs of reorders, insertions and removals"),
    ("E2E", "Whole sessions on sortable lists"),
]
EXPLAIN = "ops=R5"


def groups(spec):
    """Outer items that each hold a keyed inner list; spec is [(key, [inner keys])]."""
    items = []
    for key, inner in spec:
        rows = "".join(li(i, f"{key}.{i}") for i in inner)
        items.append(f'<li key="{key}"><b>{key}</b><ol>{rows}</ol></li>')
    return ul(*items)


def row(key, name, input_id):
    return f'<li key="{key}"><input id="{input_id}"/><span>{name}</span></li>'


def hand_made(book):
    names = lambda *keys: [word(k) for k in keys]  # noqa: E731

    # R1 -------------------------------------------------------------------------------------------
    book.add("08-R1-swap-first-two", "R1", "[a, b, c] becomes [b, a, c]",
             Script().step(keyed("a", "b", "c")).step(keyed("b", "a", "c")), kept=names("a", "b", "c"))
    book.add("08-R1-swap-ends", "R1", "[a, b, c, d] becomes [d, b, c, a]",
             Script().step(keyed("a", "b", "c", "d")).step(keyed("d", "b", "c", "a")), kept=names("a", "b", "c", "d"))
    book.add("08-R1-reverse-three", "R1", "[a, b, c] becomes [c, b, a]",
             Script().step(keyed("a", "b", "c")).step(keyed("c", "b", "a")), kept=names("a", "b", "c"))
    book.add("08-R1-reverse-six", "R1", "six items in reverse order",
             Script().step(keyed(*"abcdef")).step(keyed(*"fedcba")), kept=names(*"abcdef"))
    book.add("08-R1-rotate-left", "R1", "[a, b, c, d, e] becomes [b, c, d, e, a]",
             Script().step(keyed(*"abcde")).step(keyed(*"bcdea")), kept=names(*"abcde"))
    book.add("08-R1-rotate-right", "R1", "[a, b, c, d, e] becomes [e, a, b, c, d]",
             Script().step(keyed(*"abcde")).step(keyed(*"eabcd")), kept=names(*"abcde"))
    book.add("08-R1-swap-and-back", "R1", "two items swap, swap again, and a third render changes nothing",
             Script().step(keyed("a", "b")).step(keyed("b", "a")).step(keyed("a", "b")).step(keyed("a", "b")),
             kept=names("a", "b"))

    # R2 -------------------------------------------------------------------------------------------
    book.add("08-R2-reorder-and-insert", "R2", "[a, b, c] becomes [c, x, a, b]",
             Script().step(keyed("a", "b", "c")).step(keyed("c", "x", "a", "b")),
             kept=names("a", "b", "c"), fresh=names("x"))
    book.add("08-R2-reorder-and-remove", "R2", "[a, b, c, d] becomes [d, b, a]: c is gone",
             Script().step(keyed("a", "b", "c", "d")).step(keyed("d", "b", "a")),
             kept=names("a", "b", "d"), gone=names("c"))
    book.add("08-R2-shuffle-insert-remove", "R2", "[a, b, c, d] becomes [d, x, a, c]: one new, one gone, three moved around",
             Script().step(keyed("a", "b", "c", "d")).step(keyed("d", "x", "a", "c")),
             kept=names("a", "c", "d"), fresh=names("x"), gone=names("b"))
    book.add("08-R2-keeps-a-and-b", "R2", "[a, b, c] becomes [b, x, a]",
             Script().step(keyed("a", "b", "c")).step(keyed("b", "x", "a")),
             kept=names("a", "b"), fresh=names("x"), gone=names("c"))
    book.add("08-R2-everything-at-once", "R2", "five items become [e, y, c, x, a]: two new, two gone, three reordered",
             Script().step(keyed(*"abcde")).step(keyed("e", "y", "c", "x", "a")),
             kept=names("a", "c", "e"), fresh=names("x", "y"), gone=names("b", "d"))

    # R3 -------------------------------------------------------------------------------------------
    book.add("08-R3-reverse-inputs", "R3", "three inputs with text are reversed, then text is typed into the first one",
             Script().step(fields(("a", "ia"), ("b", "ib"), ("c", "ic"))).type("ia", "one").type("ib", "two words").type("ic", "three").dump()
                     .step(fields(("c", "ic"), ("b", "ib"), ("a", "ia"))).type("ia", "one more").dump(),
             kept=["ia", "ib", "ic"], between=(1, 2))
    book.add("08-R3-rotate-inputs", "R3", "four inputs with text rotate by one, twice",
             Script().step(fields(("a", "ia"), ("b", "ib"), ("c", "ic"), ("d", "id"))).type("ia", "A").type("ib", "B").type("ic", "C").type("id", "D").dump()
                     .step(fields(("b", "ib"), ("c", "ic"), ("d", "id"), ("a", "ia")))
                     .step(fields(("c", "ic"), ("d", "id"), ("a", "ia"), ("b", "ib"))),
             kept=["ib", "ic", "id", "ia"])
    book.add("08-R3-shuffle-with-edits", "R3", "inputs with text are shuffled while one is removed and one is added",
             Script().step(fields(("a", "ia"), ("b", "ib"), ("c", "ic"), ("d", "id"))).type("ia", "aa").type("ib", "bb").type("ic", "cc").type("id", "dd").dump()
                     .step(fields(("d", "id"), ("n", "in"), ("a", "ia"), ("c", "ic"))).type("in", "new").dump(),
             kept=["ia", "ic", "id"], fresh=["in"], gone=["ib"], between=(1, 2))
    book.add("08-R3-bare-inputs-swap", "R3", "two inputs directly under a div swap places",
             Script().step('<div><input key="a" id="ia"/><input key="b" id="ib"/></div>').type("ia", "left").type("ib", "right").dump()
                     .step('<div><input key="b" id="ib"/><input key="a" id="ia"/></div>').type("ib", "right!").dump(),
             kept=["ia", "ib"], between=(1, 2))

    # R4 -------------------------------------------------------------------------------------------
    book.add("08-R4-moved-text-changes", "R4", "[a, b, c] becomes [c, a, b] and every text changes",
             Script().step(ul(li("a", "alpha"), li("b", "beta"), li("c", "gamma")))
                     .step(ul(li("c", "GAMMA"), li("a", "ALPHA"), li("b", "BETA"))))
    book.add("08-R4-moved-props-change", "R4", "a reversed list whose props change: set, change and remove",
             Script().step(ul(li("a", "A", ' className="x" title="t"'), li("b", "B", ' id="bb"'), li("c", "C")))
                     .step(ul(li("c", "C", ' className="new"'), li("b", "B", ' title="now"'), li("a", "A", ' className="y"'))))
    book.add("08-R4-moved-nested-change", "R4", "two items swap and the nested content of each changes",
             Script().step(ul('<li key="a"><b>one</b><i>x</i></li>', '<li key="b"><b>two</b><i>y</i></li>'))
                     .step(ul('<li key="b"><b>TWO</b><i>y</i><u>new</u></li>', '<li key="a"><b>one</b></li>')))

    # R5 -------------------------------------------------------------------------------------------
    book.add("08-R5-pure-reverse", "R5", "ops after the first render, after a reverse and after reversing back",
             Script().step(keyed(*"abcd")).step(keyed(*"dcba")).step(keyed(*"abcd")))
    book.add("08-R5-pure-rotate", "R5", "ops after a rotation of five items",
             Script().step(keyed(*"abcde")).step(keyed(*"cdeab")))
    book.add("08-R5-reorder-with-edits", "R5", "ops for [a, b, c, d] to [d, x, a]: one new item, two removed",
             Script().step(keyed(*"abcd")).step(keyed("d", "x", "a")))
    book.add("08-R5-nested-ops", "R5", "ops when an item with nested content moves, is removed and is added",
             Script().step(ul('<li key="a"><b>A</b><i>1</i></li>', '<li key="b"><b>B</b><i>2</i></li>'))
                     .step(ul('<li key="b"><b>B</b><i>2</i></li>', '<li key="a"><b>A</b><i>1</i></li>', '<li key="n"><span><i>n</i></span></li>'))
                     .step(ul('<li key="n"><span><i>n</i></span></li>', '<li key="a"><b>A</b><i>1</i></li>')))

    # R6 -------------------------------------------------------------------------------------------
    book.add("08-R6-outer-and-inner", "R6", "outer items swap while their inner lists are reversed",
             Script().step(groups([("p", ["a", "b", "c"]), ("q", ["a", "b"])]))
                     .step(groups([("q", ["b", "a"]), ("p", ["c", "b", "a"])])),
             kept=["p", "q"])
    book.add("08-R6-inner-only", "R6", "only one inner list is reordered, the outer list is unchanged",
             Script().step(groups([("p", ["a", "b", "c"]), ("q", ["a", "b", "c"])]))
                     .step(groups([("p", ["a", "b", "c"]), ("q", ["c", "a", "b"])])),
             kept=["p", "q"])
    book.add("08-R6-moved-item-takes-its-list", "R6", "the last of three items moves to the front with an inner list that also changes",
             Script().step(groups([("p", ["a"]), ("q", ["a", "b"]), ("r", ["x", "y", "z"])]))
                     .step(groups([("r", ["z", "y", "x"]), ("p", ["b", "a"]), ("q", ["a", "b"])])),
             kept=["p", "q", "r"])

    # R7 -------------------------------------------------------------------------------------------
    book.add("08-R7-empty-key-moves", "R7", "the child with the empty key moves from the front to the back, and back",
             Script().step(keyed("", "a", "b")).step(keyed("a", "b", "")).step(keyed("", "a", "b")),
             kept=names("", "a", "b"))
    book.add("08-R7-zero-keys", "R7", "keys \"0\", \"1\" and \"2\" are rotated",
             Script().step(keyed("0", "1", "2")).step(keyed("2", "0", "1")),
             kept=names("0", "1", "2"))
    book.add("08-R7-look-alike-keys", "R7", "keys \"1\", \"01\" and \"001\" are reversed",
             Script().step(keyed("1", "01", "001")).step(keyed("001", "01", "1")),
             kept=names("1", "01", "001"))
    book.add("08-R7-empty-and-zero-swap", "R7", "\"\" and \"0\" swap while a new item joins and another leaves",
             Script().step(keyed("", "0", "a")).step(keyed("0", "n", "")),
             kept=names("", "0"), fresh=names("n"), gone=names("a"))

    # R8 -------------------------------------------------------------------------------------------
    book.add("08-R8-unkeyed-reversed", "R8", "no keys: three texts are reversed, the nodes stay where they are",
             Script().step(plain("A", "B", "C")).step(plain("C", "B", "A")))
    book.add("08-R8-unkeyed-inputs", "R8", "no keys: two inputs with text, the labels swap, the text stays with the position",
             Script().step(ul('<li><b>A</b><input id="p1"/></li>', '<li><b>B</b><input id="p2"/></li>')).type("p1", "typed first").type("p2", "typed second").dump()
                     .step(ul('<li><b>B</b><input id="p1"/></li>', '<li><b>A</b><input id="p2"/></li>')))
    book.add("08-R8-unkeyed-shuffle-shrink", "R8", "no keys: five items in a new order and fewer of them",
             Script().step(plain("e", "d", "c", "b", "a")).step(plain("b", "e", "a")))

    # E2E ------------------------------------------------------------------------------------------
    sort = Script()
    people = {"ann": "Ann", "bob": "Bob", "cy": "Cy", "dee": "Dee", "eve": "Eve"}

    def table(*order):
        return ul(*[row(k, people[k], f"r-{k}") for k in order])

    sort.step(table("ann", "bob", "cy", "dee"))
    for k, text in (("ann", "likes tea"), ("bob", "late"), ("cy", "ok"), ("dee", "away")):
        sort.type(f"r-{k}", text)
    sort.dump()
    sort.step(table("dee", "cy", "bob", "ann"))
    sort.step(table("dee", "cy", "ann"))
    sort.step(table("dee", "eve", "cy", "ann"))
    sort.type("r-eve", "new hire")
    sort.step(table("ann", "cy", "dee", "eve"))
    sort.step(table("eve", "dee", "cy", "ann"))
    book.add("08-E2E-sortable-rows", "E2E", "rows with an input each: sort descending, drop one, add one, sort both ways", sort)

    board = Script()
    board.step('<div><h2>board</h2><ul><li key="t1">write</li><li key="t2">test</li><li key="t3">ship</li></ul><p>3 tasks</p></div>')
    board.step('<div><h2>board</h2><ul><li key="t3">ship</li><li key="t1">write</li><li key="t2">test</li></ul><p>3 tasks</p></div>')
    board.step('<div><h2>board</h2><ul><li key="t2">test (done)</li><li key="t3">ship</li><li key="t4">review</li><li key="t1">write</li></ul><p>4 tasks</p></div>')
    board.step('<div><h2>board</h2><ul><li key="t4">review</li><li key="t2">test (done)</li></ul><p>2 tasks</p></div>')
    book.add("08-E2E-board", "E2E", "a list between a heading and a counter: reorders, additions and removals, siblings stay put", board)


# ---- Random cases ----------------------------------------------------------------------------------

class Shuffles(Lists):
    """Random lists where the keys two renders share may change their order."""

    def next(self):
        old = self.keys
        kept = [k for k in old if self.rng.random() < 0.8]
        if self.rng.random() < 0.85:
            self.rng.shuffle(kept)
        new = list(kept)
        banned = set(old)
        for _ in range(self.rng.choice([0, 0, 1, 1, 2])):
            key = self.fresh_key(banned | set(new))
            banned.add(key)
            new.insert(self.rng.randint(0, len(new)), key)
        self.keys = new
        return new


def random_shuffles(book, seed):
    plans = [("R2", "text", PLAIN_POOL, 0, "random shuffles with insertions and removals on text items"),
             ("R3", "input", PLAIN_POOL, 0, "random shuffles of keyed inputs, typing between renders"),
             ("R3", "input", PLAIN_POOL, 1, "random shuffles of keyed inputs, typing between renders"),
             ("R6", "nested", PLAIN_POOL, 0, "random shuffles of items with nested content"),
             ("R7", "text", ODD_POOL, 0, "random shuffles with the keys \"\", \"0\", \"00\", \"1\", \"01\" in play"),
             ("R9", "input", PLAIN_POOL, 0, "a long run of shuffles on inputs"),
             ("R9", "text", PLAIN_POOL, 1, "a long run of shuffles on text items")]
    for req, kind, pool, n, what in plans:
        rng = rng_for(seed, f"08-{req}-{kind}-{n}")
        lists = Shuffles(rng, pool, kind)
        script = Script()
        steps = rng.randint(4, 6) + (4 if req == "R9" else 0)
        lists.first()
        script.step(lists.markup())
        for _ in range(steps):
            if kind == "input":
                lists.type_somewhere(script)
            lists.next()
            script.step(lists.markup())
        book.add(f"08-{req}-random-s{seed}-{n}", req, f"{what} (seed {seed}, {steps + 1} renders)", script)


def main():
    args = wbcore.parse_args("08")
    book = Book()
    hand_made(book)
    random_shuffles(book, args.seed)
    book.save(args, requirements=REQUIREMENTS, compare=COMPARE, explain=EXPLAIN)


if __name__ == "__main__":
    main()
