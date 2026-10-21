# 05 · Read DER

**Difficulty:** Medium · **Checkpoint** 5 of 16 · **Check:** `./check.sh 05`

**Tags**
- *Language:* bit manipulation · hex strings · recursion
- *Library:* none needed
- *Concepts:* ASN.1 · DER (Distinguished Encoding Rules) · tag-length-value encoding

## Read in the blog first

This checkpoint is prerequisite material, not drawn from eMudhra's post: every certificate in
this workbook is a DER-encoded byte string, and checkpoints 06 to 09 all start by walking that
encoding the way this one does. Read ITU-T X.690, section 8 ("Basic encoding rules"), in
particular 8.1 (the tag-length-value structure), 8.3 (INTEGER), 8.6 (BIT STRING) and 8.19
(OBJECT IDENTIFIER) - the Source material section below links the document. This page is
complete on its own after that.

## Where this fits

Nothing earlier in this workbook reads bytes this way. Every certificate checkpoint from here on
(06 reads certificate fields, 07 hashes a certificate's public key, 08 checks a signature, 09
validates a whole chain) starts by walking a certificate's bytes exactly as you will here. Get
the walk right once, and the rest of the DER details in the workbook stop being a format problem.

## The problem

Write a program that reads one or more DER-encoded byte strings and, for each one, prints every
node it contains: every tag-length-value (TLV) structure, in the order it appears in the file,
with its nesting depth, so the shape of the encoding is visible from the output alone.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p05_der_reader.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p05_der_reader.py` over it, or pick Boilerplate in the
book's editor. The boilerplate reads the input and writes the output; you fill in
`der_to_lines()`.

### The tag-length-value structure

Every DER-encoded value is three parts back to back: a **tag** (what kind of value this is), a
**length** (how many bytes of content follow), and the **content** itself (which, for a
constructed value, is itself a sequence of complete tag-length-value nodes).

**The tag** is the first byte (every tag used in this checkpoint fits in one byte; DER also has a
multi-byte "high tag number" form for tag numbers 31 and above, which does not appear in this
workbook and is out of scope here). Its bits mean:

| Bits | Meaning |
|---|---|
| 8-7 | tag class: `00` universal, `01` application, `10` context-specific, `11` private |
| 6 | `0` primitive (the content is the actual value), `1` constructed (the content is more TLV nodes) |
| 5-1 | tag number |

**Universal** tags are ASN.1's built-in types and always mean the same thing. This checkpoint
needs these tag numbers:

| Tag number | Type | Always |
|---|---|---|
| 1 | BOOLEAN | primitive |
| 2 | INTEGER | primitive |
| 3 | BIT STRING | primitive (this checkpoint never nests one) |
| 4 | OCTET STRING | primitive |
| 5 | NULL | primitive |
| 6 | OBJECT IDENTIFIER | primitive |
| 16 | SEQUENCE | constructed |
| 17 | SET | constructed |
| 23 | UTCTime | primitive |
| 24 | GeneralizedTime | primitive |

A **context-specific** tag ([0], [1], [2], [3], ...) means something different in each structure
that uses it - a certificate uses [0] for its version field and [3] for its extensions, both
wrapping another value (so both are constructed in this workbook). The tag number is still bits
5-1 of the same byte; only the class bits differ from universal.

**The length** follows the tag byte, in one of two forms:

- **Short form**: if the length byte's high bit is 0, the rest of that byte (0-127) is the
  length, and that's the whole length field (one byte).
- **Long form**: if the length byte's high bit is 1, the low 7 bits say how many more bytes
  follow, and those bytes, read as one big-endian number, are the length. For example `0x81 0xC8`
  means "1 more byte follows: 0xC8", so the length is 200. `0x82 0x01 0x2C` means "2 more bytes:
  0x01 0x2C", so the length is 300.

(DER also has an indefinite-length form, `0x80` with no length at all, ended by two zero bytes.
It is illegal in DER - every length here is definite - so you don't need to handle it; if you see
it, something upstream of you produced BER, not DER.)

**The content** is exactly that many bytes. For a primitive node, those bytes are the value,
decoded by type (below). For a constructed node, those bytes are more complete TLV nodes, one
after another, each one level deeper than its parent.

### Decoding each type's content

- **BOOLEAN**: one content byte. DER's canonical form is `0x00` for false and `0xFF` for true;
  print `true` or `false`.
- **NULL**: zero content bytes. Print `null`.
- **OCTET STRING**: the content bytes themselves. Print them as lowercase hex.
- **BIT STRING**: the **first** content byte is the number of unused bits (0-7) in the *last*
  byte of what follows; the rest of the content is the actual bit data. A BIT STRING with 0
  unused bits and payload `0xF0` means all 8 bits of that one byte are used. Print
  `<unused-bits>:<hex of the rest>`, e.g. `0:f0`.
- **OBJECT IDENTIFIER**: a sequence of "arcs" (numbers), base-128 encoded. The *first* two arcs
  are combined into one encoded value, `40 * arc1 + arc2` (arc1 is 0, 1 or 2); every other arc is
  encoded on its own. Each encoded value is one or more bytes: 7 bits of the value per byte, most
  significant group first, with the top bit of every byte but the last one of that value set to 1
  (meaning "more bytes follow for this value"). To decode: read bytes, accumulating 7 bits at a
  time into the current value, until you hit a byte whose top bit is 0 - that ends the value.
  The very first decoded value `v` splits back into `arc1, arc2` as: `v < 40` means `arc1 = 0,
  arc2 = v`; `v < 80` means `arc1 = 1, arc2 = v - 40`; otherwise `arc1 = 2, arc2 = v - 80`. Print
  the dotted form, e.g. `1.2.840.10045.2.1`.

  Worked example: bytes `2a 86 48 ce 3d 04 03 03`. `0x2a = 42`, which is `40*1 + 2`, so the first
  two arcs are `1, 2`. Next byte `0x86 = 1000_0110`: top bit set, so more bytes follow; value so
  far (low 7 bits) is `0000110 = 6`. Next byte `0x48 = 0100_1000`: top bit clear, so this ends the
  value: shift the running value left 7 and OR in `1001000 = 72`, giving `6*128 + 72 = 840`. Then
  `0xce 0x3d` the same way give `10045`, and the lone bytes `0x04`, `0x03`, `0x03` each give `4`,
  `3`, `3`. Full OID: `1.2.840.10045.4.3.3`.
- **UTCTime / GeneralizedTime**: print the content bytes as ASCII text, unchanged (this isn't a
  date-parsing checkpoint - just show the raw string, e.g. `251020120000Z`).
- **INTEGER**: the content bytes are the value in two's complement, most significant byte first.
  If the top bit of the first byte is 1, the value is negative: subtract `2^(8 * number of
  bytes)` from the unsigned reading of those bytes. A positive value whose own top bit would
  otherwise be set gets an extra `0x00` byte in front so it can't be mistaken for a negative one
  - that pad byte is not a sign marker to strip, it's part of making the encoding correct. Print
  the decimal value (this checkpoint's decoded integers always fit in a normal integer type; your
  language may need a big-integer type for the larger ones, since DER places no size limit on an
  INTEGER's content).

  Worked example: content `00 80` is two bytes, top byte `0x00`, so this is positive:
  `0x0080 = 128`. Content `80` alone (one byte, top bit set) is negative: unsigned reading is
  `128`, minus `2^8 = 256`, giving `-128`.
- **Any other type** (for example PrintableString or UTF8String, tag numbers you may see in real
  certificates but that this checkpoint does not ask you to decode, or a context-specific tag
  used for *implicit* tagging rather than wrapping another TLV) is printed as hex, the same as
  OCTET STRING.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains one kind of line:

| Line | Meaning |
|---|---|
| `der <hex>` | DER bytes, as lowercase hex with no spaces. May hold more than one complete top-level TLV node back to back (not wrapped in anything) - walk all of them. |

### Output

For every TLV node encountered, across all `der` lines, in the order each one starts (a
depth-first, document-order walk: a constructed node's own line comes before its children's
lines, and a node's children come before its next sibling), write one line:

```
node <depth> <class> <primitive-or-constructed> <tag> <length> <value>
```

- `<depth>`: `0` for a top-level node, `1` for its direct children, and so on.
- `<class>`: `universal`, `application`, `context` or `private`.
- `<primitive-or-constructed>`: the literal word `primitive` or `constructed`.
- `<tag>`: the tag number, in decimal.
- `<length>`: the number of content bytes, in decimal (not counting the tag or length field).
- `<value>`: decoded per the rules above for a primitive node, or the three characters `...` for
  a constructed node (its children are the lines that follow, so it carries no value of its own).

The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** BOOLEAN, NULL, OCTET STRING and BIT STRING decode correctly, including a BIT STRING's
  unused-bits byte, and multiple top-level nodes in one input are all walked, in order.
- **R2** INTEGER is two's complement: a value whose encoding needs a leading `0x00` pad byte
  still decodes to the right positive number, and a genuinely negative value decodes correctly
  too.
- **R3** OBJECT IDENTIFIER decodes its base-128 arcs to dotted notation, including arcs (or the
  combined first value) that need more than one byte.
- **R4** SEQUENCE, SET and context-specific tags are constructed: their content is more TLV
  nodes, each one depth deeper than its parent, continuing correctly through several levels.
- **R5** Both length forms work: short form, and long form with one or more length bytes,
  including the two lengths (127 and 128) right at the boundary between them.

## Examples

### Example 1: a BIT STRING with unused bits (test `05-R1-bit-string-unused`)

```
input:   der 030205a0

output:  node 0 universal primitive 3 2 5:a0
```

Tag byte `0x03`: class bits `00` (universal), constructed bit `0` (primitive), tag number `3`
(BIT STRING). Length byte `0x02`: short form, 2 content bytes. Content `03 a0`: first byte `0x03`
is the unused-bit count; the rest, `a0`, is the bit data. Output value: `5:a0`.

### Example 2: INTEGER needing a pad byte, next to one that doesn't (test `05-R2-int-side-by-side`)

```
input:   der 02020080020180

output:  node 0 universal primitive 2 2 128
         node 0 universal primitive 2 1 -128
```

The first value: tag `02` (INTEGER), length `02`, content `00 80`. The leading `00` says this is
positive: `0x0080 = 128`. The second value: tag `02`, length `01`, content `80` alone. Its top bit
is set and there's no pad byte, so it's negative: `0x80 = 128` unsigned, minus `256`, giving
`-128`. Two different one-byte-vs-two-byte encodings, two different numbers.

### Example 3: nesting with a context-specific tag (test `05-R4-context-explicit`)

```
input:   der a003020102

output:  node 0 context constructed 0 3 ...
         node 1 universal primitive 2 1 2
```

Tag byte `0xa0` is `1010_0000`: class bits `10` (context-specific), constructed bit `1`, tag
number `0`. This is exactly how a certificate wraps its version field: `[0]` constructed,
containing one INTEGER. The outer node's value is `...` because its content is itself a TLV node
(the INTEGER `2`), which appears as the next line, one level deeper.

## Constraints

- Every `der` line holds complete, well-formed DER: no truncated nodes, no indefinite length, no
  tag number of 31 or above.
- Depths in the test data go no deeper than 4.
- There are 47 tests: 9 for R1 (plus two multi-top-level-node cases), 13 for R2, 8 for R3, 8 for
  R4 (plus two random mixes), 6 for R5, and 3 end-to-end cases that combine several node types
  and several levels of nesting in one structure shaped like a slice of a real certificate. Part
  of the set is random and changes with `-Fresh`.

## Source material

- ITU-T X.690, [Information technology - ASN.1 encoding rules: BER, CER and DER](https://www.itu.int/rec/T-REC-X.690), section 8 (the encoding this checkpoint reads)
- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 4.1 (where checkpoint 06 uses this TLV structure to read a real certificate)

## Hints

<details><summary>Hint 1: where to start</summary>

Write one function that reads a single TLV node starting at some byte offset and returns the
node (its tag info, length and content) plus the offset just past it. Everything else - the
depth-first walk, the value formatting - is built around calling that function.
</details>

<details><summary>Hint 2: the approach</summary>

The tag byte alone tells you the class, whether it's constructed, and the tag number - all with
simple bit masking (`>> 6`, `& 0x20`, `& 0x1F`). The length byte tells you whether to read 1 byte
(short form) or N more bytes (long form) for the actual length. Once you have the content bytes,
a primitive node's value comes from decoding those bytes by type; a constructed node's "value" is
just the next TLV node, recursively, starting at the beginning of its content and continuing
until you've consumed exactly its length.
</details>

<details><summary>Hint 3: the traps</summary>

- An INTEGER's leading `0x00` byte is not junk to strip - it's what makes a value with a high bit
  set read as positive instead of negative. Only remove it if you're re-encoding (you're not,
  here); for decoding, just apply the two's-complement rule to the bytes as given.
- An OBJECT IDENTIFIER's first encoded value can itself be more than one byte if `40*arc1 + arc2`
  is large (this isn't just for every *other* arc - the combined first value follows the exact
  same base-128 rule as the rest).
- A constructed node's children are each one depth deeper than their parent, not all at depth 0
  or all at the same depth as each other's siblings two levels up.
- The length's long form can take one, two, or more bytes; the short/long boundary is 128 (a
  length of 127 is short form, 128 is the first one needing long form).
- A context-specific tag's number lives in the same five low bits as a universal tag's - only the
  two class bits differ. Don't assume tag number 0 means BOOLEAN just because that's universal
  tag 1 and context tag 0 looks similar in the byte.
- Multiple top-level nodes can appear back to back in one `der` line, with no wrapper around
  them. Keep reading until you run out of bytes, not just once.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
read_tlv(data, i, depth):
    first = data[i]
    cls = (first >> 6) & 0b11
    constructed = (first & 0x20) != 0
    tag = first & 0x1F

    length_byte = data[i+1]
    if high bit of length_byte is 0:
        length = length_byte
        content_start = i + 2
    else:
        n = length_byte & 0x7F
        length = big-endian value of the next n bytes
        content_start = i + 2 + n

    content = data[content_start : content_start + length]
    node = {cls, constructed, tag, length, content, depth, children: []}
    if constructed:
        k = content_start
        while k < content_start + length:
            child, k = read_tlv(data, k, depth + 1)
            node.children.append(child)
    return node, content_start + length

walk(node):
    print one line for node (value "..." if constructed, else decoded by type)
    for child in node.children:
        walk(child)
```
</details>

## Checking your solution

```
./check.sh 05                          run every test
./check.sh 05 -Case 05-R2-int-side-by-side   one test, showing its full input, expected output and your output
./check.sh 05 -Fresh                   a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 05 -Dispute <id> "why"      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  INTEGER is two's complement: a value needing a leading 0x00 pad b...    12 / 13  FAILED
      x 05-R2-int-neg-128  INTEGER -128 (negative, two's complement)
          node[0]: expected (depth=0, cls=universal, pc=primitive, tag=2, length=1, value=-128), got (depth=0, cls=universal, pc=primitive, tag=2, length=1, value=128) - differs in value
          likely cause: R2 - INTEGER is two's complement: a value needing a leading 0x00 pad byte is still read correctly, and so is a negative value
          expected values from: openssl asn1parse (OpenSSL 3.x): independently decodes tag class, constructed/primitive, depth and length from the same bytes
          reproduce: python3 -P tools/run_py.py solutions 05 build/cases/05/05-R2-int-neg-128.in build/cases/05/05-R2-int-neg-128.out
```

## After you pass: compare with the post

The post contains no code for this (it's prerequisite material, not drawn from the post), so
there is no author's version to compare. The reference solution is in `_spoilers/reference/`:
one small function, `read_tlv`, called recursively, plus a `format_value` function with one
branch per type.

**Something to look for:** the reference decodes an OBJECT IDENTIFIER's first value with the
general base-128 loop, not a special-cased single byte - look at how it handles an arc pair whose
combined value is itself large, and compare it with whatever you wrote for the "every other arc"
case.
