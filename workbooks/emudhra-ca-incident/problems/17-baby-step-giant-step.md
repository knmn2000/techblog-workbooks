# 17 · Find a weak key in square-root time

**Difficulty:** Hard · **Assignment** 17 of 19 · **Check:** `.\check 17`

**Tags**
- *Language:* big integers · dictionaries · exact integer square roots (`math.isqrt`) · rounding up with `//`
- *Library:* none needed
- *Concepts:* baby-step giant-step · the negation of a point · time and memory trade-off · key space

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident)
says a researcher "was able to reverse-engineer" the weak keys and doesn't say how. In Mozilla's
[bug 2083449, comment 5](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449#c5), Dennis
Jackson of Mozilla wrote that the keys "can be recovered near instantly via the baby-step
giant-step discrete log algorithm or more simplistically by just generating the 'first' 256 P384
keys." Assignment 10 wrote the second method. In this assignment you write the first.

## Source material

- Mozilla, [Bugzilla bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449), comment 5 (Dennis Jackson, October 18, 2026): the keys are integers below 256, recoverable with baby-step giant-step or by generating the first 256 keys
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- D. Shanks, "Class number, a theory of factorization, and genera", *Proceedings of Symposia in Pure Mathematics* 20 (1971): the first description of baby-step giant-step
- A. Menezes, P. van Oorschot and S. Vanstone, [*Handbook of Applied Cryptography*](https://cacr.uwaterloo.ca/hac/), chapter 3, section 3.6.2: baby-step giant-step for discrete logarithms
- SECG, [SEC 2: Recommended Elliptic Curve Domain Parameters](https://www.secg.org/sec2-v2.pdf), for `secp256r1` and `secp384r1`

## Where this fits

You can do this any time after assignment 10. Your `attack/weak_key.py` from that assignment tries
`d = 1, 2, 3, ...` with one point addition each, so a bound of 2^28 costs 268,435,456 additions:
3.8 hours on P-256 with the project's arithmetic. The new `attack/bsgs.py` finds the same keys
with about 32,800 additions, in under 2 seconds. It uses `add_points` and `scalar_multiply` from
your `ecc/curve.py` (assignments 02 and 03) and the curves in your `ecc/curves.py`. No later
assignment depends on it.

## The problem

Write a program that reads public keys and finds, for each one, a small private value with
baby-step giant-step, in either sign. It also answers `plan` lines with the size of the table and
the number of steps a search of a given size needs.

### Weak keys come in pairs

A public key is `Q = d*G`. Its negation `-Q = (x, p - y)` is `(n - d)*G`, where `n` is the order
of `G`. The private key `n - d` is a 256-bit or 384-bit number, but anyone who knows `d` knows
`n - d`, so `-(d*G)` is as weak as `d*G`. This assignment writes a private value `e` with a sign:
`e = d` for `d*G` and `e = -d` for `-(d*G)`, the same notation as assignment 10. A key is weak
when `Q = e*G` for some `e` with `1 <= |e| <= N`, where `N` is the bound.

### The idea

Pick a table size `m`. Store the x coordinate of each of `1*G, 2*G, ..., m*G`, the baby steps.
Then take a giant point `P = Q - c*G` for some number `c`, the centre, and look up its x in the
table. Two different points share an x only when one is the negation of the other, so a hit on the x of
`j*G` means one of two things, and y tells you which:

| What you find | Then | So |
|---|---|---|
| `P` has the x and the y of `j*G` | `P = j*G` | `Q = (c + j)*G`, so `e = c + j` |
| `P` has the x of `j*G` and the other y | `P = -(j*G)` | `Q = (c - j)*G`, so `e = c - j` |
| `P` is the point at infinity | `Q = c*G` | `e = c` |

One giant point therefore tests the 2m + 1 values from `c - m` to `c + m`. Centres `0, 2m, 4m,
...` and `-2m, -4m, ...` cover every `e`, positive and negative, and moving from one centre to the
next costs one addition of `2m*G` or `-(2m*G)`.

The y comparison gives you both signs at no extra cost. A one-sided search that uses only the
same-y row of the table above needs centres `m` apart, about `N / m` of them, to cover `1 .. N`. With
both rows, each giant point covers twice as many values, and the same number of giant points
covers `-N .. N`.

### The search

Let `N` be the bound and `M` the table limit (no limit until a `table` line sets one).

| Name | Definition | In exact integers |
|---|---|---|
| `m`, the baby steps | `min(ceil(sqrt(N)), M)` | `math.isqrt(N - 1) + 1`, then the limit |
| `g`, the giant points of the down walk, Q included | `ceil((N + m) / (2m))`: the last centre, `2m*(g - 1)`, is within `m` of `N` | `(N + 3*m - 1) // (2*m)` |
| giant points in all | `2g - 1`: Q, then `g - 1` going down and `g - 1` going up | |

Floating point gives wrong answers here. `math.sqrt(2**54 - 1)` rounds up to `2**27`, so
`int(math.sqrt(N - 1)) + 1` is one too big at `N = 2^54`, and `(N + m) / (2*m)` loses its last
digits once the numbers pass 2^53.

For `N = 10`: `m = 4` and `g = 2`, so the centres are `-8`, `0` and `8`, and the three giant
points cover `-12 .. 12`.

### The baby steps

The table maps the x of `j*G` to `j` and the y of `j*G`, for `j = 1 .. m`. Start from `G` and add
`G` once per step. `j` starts at 1: `0*G` is the point at infinity, which has no x.

### The giant steps

1. Compute `S = (2m)*G` with `scalar_multiply`, and its negation `(Sx, p - Sy)`.
2. Walk down: start at `P = Q` (centre 0) and add `-S` each step, so the centres are `0, 2m, 4m,
   ...`, for `g` points.
3. Walk up: start at `P = Q + S` (centre `-2m`) and add `S` each step, so the centres are `-2m,
   -4m, ...`, for `g - 1` points. The down walk has already looked at `Q`.
4. At each point, apply the table under "The idea". A hit gives one `e`.
5. If `1 <= |e| <= N`, the key is weak with that `e`. Otherwise the key is not weak: the walk only
   reaches values less than `N + 2m` from 0, far below `n`, so the `e` it finds is the only candidate,
   and you can stop.
6. If neither walk hits, the key is not weak.

The last giant point on each side can reach past `N` (up to `12` for `N = 10`), so step 5's range
check is part of the answer.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains four kinds of lines:

| Line | Meaning |
|---|---|
| `bound <N>` | The bound for every `key` line after it, until the next `bound` line. A decimal integer from 1 to 268435456 (2^28). |
| `table <M>` | The most baby steps the search may store, for every `key` and `plan` line after it, until the next `table` line: a decimal integer of 1 or more, or `none` for no limit. Until the first `table` line there is no limit. |
| `key <label> <curve> <x> <y>` | A public key, as in assignment 10. `label` is a word with no spaces. `curve` is `P-256` or `P-384`. `x` and `y` are lowercase hexadecimal with no `0x` prefix. |
| `plan <label> <bits>` | Ask what a search with bound `N = 2^bits` costs under the table limit in effect. `bits` is an integer from 1 to 400. |

### Output

For each `key` or `plan` line, in input order, write one line:

```
weak <label> <e>                   Q = e*G with 1 <= |e| <= N; e in decimal, with a minus sign for -(d*G)
none <label>                       no such e
plan <label> baby <m> giant <t>    m baby steps and t = 2g - 1 giant points, for N = 2^bits
```

Copy `<label>` from the input unchanged. The checker ignores extra whitespace.

### What a search costs

These times come from the reference solution with the project's own arithmetic (51 microseconds
per point addition on P-256, 84 on P-384), for a key that isn't weak, so every giant point runs.
The scan columns multiply the bound by those per-addition costs.

| Bound | `m` | Giant points | P-256 | P-384 | Scan of every value, P-256 | P-384 |
|---|---|---|---|---|---|---|
| 2^20 | 1,024 | 1,025 | 0.11 s | 0.17 s | 53 s | 88 s |
| 2^24 | 4,096 | 4,097 | 0.45 s | 0.74 s | 14 min | 23 min |
| 2^26 | 8,192 | 8,193 | 0.92 s | 1.3 s | 57 min | 1.6 h |
| 2^28 | 16,384 | 16,385 | 1.7 s | 2.7 s | 3.8 h | 6.3 h |

The table holds `m` entries. A Python dictionary from a 256-bit x to `(j, y)` takes about 248
bytes per entry, so the table for bound 2^40 (2^20 entries) takes 260 MB, for 2^48 4.2 GB, and for
2^64 (2^32 entries) about 1.1 TB. A `table` limit below `sqrt(N)` saves memory and costs giant
points, which the `plan` lines let you compute.

A random key has a private value anywhere from 1 to `n`. Every such value is `e` or `n - e` for
some `e` up to `n / 2`, so the two-sided search needs `N` of about `n / 2`. On P-256 that takes
about 2^127.5 baby steps and 2^127.5 giant points, 4.8 x 10^38 additions: 1.5 x 10^19 years at
10^12 additions per second, with a table of 2^127.5 entries. On P-384 it takes 8.9 x 10^57
additions, or 2.8 x 10^38 years. The search works on the incident's keys because their values are below 256.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** One output line per `key` and `plan` line, in input order, in the formats above, each key
  searched on its own curve. A later `bound` or `table` line replaces the earlier one for the
  lines after it.
- **R2** A key `d*G` with `1 <= d <= N` gives `weak <label> <d>`. This includes `d = 1`, `d = m`
  and `m + 1`, `d` on a giant point's centre (where `Q - c*G` is the point at infinity), `d` at
  `c - m` and `c + m`, `d = N`, bounds of 1, 2 and 3, bounds that are not perfect squares, and
  tables limited to 1 and 7 entries.
- **R3** A key `-(d*G)` with `1 <= d <= N` gives `weak <label> -<d>`, at the same edges as R2.
- **R4** A key with no `e` in `-N .. N` gives `none`: `d = N + 1` and `-(N + 1)`, values the last
  giant points reach past the bound, and strong keys.
- **R5** Bounds up to 2^28 on P-256 and 2^26 on P-384 finish inside the time limit, where a scan
  of every value takes from 3.5 minutes (2^22 on P-256) to 3.8 hours (2^28 on P-256).
- **R6** A `plan` line gives `baby <m> giant <2g - 1>` from the formulas under "The search", in
  exact integers, with the `table` limit in effect.

## Examples

### Example 1: a key and its negation (test `17-R3-pair`)

```
input:   bound 1000000
         key k1 P-256 64ea16d4aab61131b07ef7674bf0db82a2d38731661af07802abf16fe95fec0e c57d9f0c6781d32915b513051c2c9215af1de8eff77b122b55f5a403a963fe31
         key k2 P-256 64ea16d4aab61131b07ef7674bf0db82a2d38731661af07802abf16fe95fec0e 3a8260f2987e2cd7ea4aecfae3d36dea50e217110884edd4aa0a5bfc569c01ce

output:  weak k1 654321
         weak k2 -654321
```

`N = 1,000,000`, so `m = 1000`, the centres are 2000 apart and `g = 501`. The two keys share x:

| Key | Walk | Giant point | Table hit | `e` |
|---|---|---|---|---|
| `k1 = 654321*G` | down, step 327 (centre 654000) | `Q - 654000*G = 321*G` | `j = 321`, same y | `654000 + 321 = 654321` |
| `k2 = -(654321*G)` | up, step 327 (centre -654000) | `Q + 654000*G = -(321*G)` | `j = 321`, other y | `-654000 - 321 = -654321` |

For `k2`, the down walk runs all 501 points without a hit before the up walk finds it. Assignment
10's loop would need 654,321 additions for either key; this search needs about 1,000 for the table
and at most 1,001 giant points.

### Example 2: past the bound (test `17-R4-past-the-bound`)

```
input:   bound 10
         key k11 P-256 3ed113b7883b4c590638379db0c21cda16742ed0255048bf433391d374bc21d1 9099209accc4c8a224c843afa4f4c68a090d04da5e9889dae2f8eefce82a3740
         key k12 P-256 741dd5bda817d95e4626537320e5d55179983028b2f82c99d500c5ee8624e3c4 0770b46a9c385fdc567383554887b1548eeb912c35ba5ca71995ff22cd4481d3
         key km11 P-256 3ed113b7883b4c590638379db0c21cda16742ed0255048bf433391d374bc21d1 6f66df64333b375edb37bc505b0b3975f6f2fb26a16776251d07110317d5c8bf
         key km12 P-256 741dd5bda817d95e4626537320e5d55179983028b2f82c99d500c5ee8624e3c4 f88f4b9463c7a024a98c7caab7784eab71146ed4ca45a358e66a00dd32bb7e2c
         key k10 P-256 cef66d6b2a3a993e591214d1ea223fb545ca6c471c48306e4c36069404c5723f 878662a229aaae906e123cdd9d3b4c10590ded29fe751eeeca34bbaa44af0773

output:  none k11
         none k12
         none km11
         none km12
         weak k10 10
```

`N = 10` gives `m = 4`, `g = 2` and centres `-8`, `0`, `8`. For `k11 = 11*G`, the down walk's
second point is `Q - 8*G = 3*G`, so `e = 8 + 3 = 11`, which is above 10: `none`. For `km11`, the up
walk's point `Q + 8*G = -(3*G)` gives `e = -8 - 3 = -11`: `none`. For `k10`, `Q - 8*G = 2*G`
gives `e = 10`: `weak`. A key `8*G` would make `Q - 8*G` the point at infinity, which gives
`e = 8`.

### Example 3: one key at two bounds, and three plans (test `17-E2E-bound-gap`)

```
input:   bound 4096
         key k1 P-256 e99290f9e5021fa60c36a801f04fe77a36de5b6d88b1ea166885527b6244985a c2d4c3b4ad3a2fbbbda807358c41058adead60ed001b91ea2fc0ebad61c708c8
         bound 4194304
         key k2 P-256 e99290f9e5021fa60c36a801f04fe77a36de5b6d88b1ea166885527b6244985a c2d4c3b4ad3a2fbbbda807358c41058adead60ed001b91ea2fc0ebad61c708c8
         table 1024
         plan p1 32
         table none
         plan p2 32
         plan p3 384

output:  none k1
         weak k2 3000000
         plan p1 baby 1024 giant 4194305
         plan p2 baby 65536 giant 65537
         plan p3 baby 6277101735386680763835789423207666416102355444464034512896 giant 6277101735386680763835789423207666416102355444464034512897
```

Both keys are `3000000*G`. With bound 4096 it is `none`. With bound 2^22, `m = 2048` and the
centres are 4096 apart; `3000000 = 732 * 4096 + 1728`, so the down walk finds `Q - 2998272*G =
1728*G` at its step 732. The plans show the trade for bound 2^32: a table of 1,024 entries needs
`2 * ceil((2^32 + 1024) / 2048) - 1 = 4,194,305` giant points, and a table of 65,536 entries needs
65,537. For 2^384, both numbers are about 2^192.

## Constraints

- Every line is a `bound`, `table`, `key` or `plan` line, with no blank lines. A `bound` line
  comes before the first `key` line.
- Every key is a valid point on its curve. Labels have no spaces. An input has at most 15 `key`
  lines and at most 12 `plan` lines.
- A bound is at most 2^28, and at most 2^26 in any input that has a P-384 key.
- Each case has a 10-second limit. The reference's slowest test takes 1.7 seconds, so a program
  three times slower than the reference passes. Several keys can share a bound, and building the
  table once per bound and curve saves time; a program that rebuilds it for every key still
  passes.
- The answer for a key doesn't depend on the table limit, which changes only the work. A program
  that ignores the limit in its search passes the key tests; the `plan` lines are where it shows.
  A program that honours the limit stays fast because the tests use small tables only with small
  bounds: with `table 1`, a search walks about `N / 2` giant points.
- There are 48 tests: 3 for R1, 15 for R2, 8 for R3, 7 for R4, 7 for R5, 4 for R6 and 4
  end-to-end. They cover both curves, the edges listed in R2 to R4, bounds up to 2^28 with strong
  keys, `plan` lines for `bits` from 1 to 400 with tables of 1, 1,000 and 2^40 entries, and the
  eight values reported for the incident. Part of the set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Write `e` as `c + t`, where `c` is a multiple of `2m` and `t` is between `-m` and `m`. You can
compute every `t*G` for `t` from 1 to `m` once, before you see any key: that's the table. The y
comparison gives you `-t`, and the point at infinity gives you `t = 0`. For each `c`, one point
addition takes you from `Q - c*G` to the next centre. Write `plan` first, because the search uses
the same two numbers.
</details>

<details><summary>Hint 2: the approach</summary>

Build a dictionary from the x of `j*G` to `(j, y)` for `j = 1 .. m`, adding `G` once per step.
Compute `S = (2m)*G` with your `scalar_multiply` and negate it by replacing y with `p - y`. Walk
from `Q` by adding `-S`, `g` points, then from `Q + S` by adding `S`, `g - 1` points. At each point,
look up x; on a hit, compare y to choose `c + j` or `c - j`, then check the range. Keep the tables
in a dictionary keyed by curve and `m`, so keys that share a bound share the table.
</details>

<details><summary>Hint 3: the traps</summary>

- Compare y on a hit. Matching x alone gives `c + j` where the answer is `c - j`, and turns
  `-(d*G)` into `d`.
- Walk both ways. A walk that only goes down from `Q` finds `-(d*G)` only for `d <= m`.
- `Q - c*G` can be the point at infinity (your `add_points` returns `None`). That means `e = c`;
  reading its x crashes.
- Round `m` and `g` up, in integers. Rounding `g` down misses the keys near the bound, and floating
  point breaks the `plan` lines for large `bits`.
- Check `1 <= |e| <= N` after a hit. The last giant points reach `2m*(g - 1) + m`, which can be up to `2m - 1` past `N`.
- The table holds `j = 1 .. m`, all `m` of them. With one entry missing, the values `c - m` and
  `c + m` fall through.
- Step by `2m*G`, the same `2m` your centres use.
- Keep one table per curve. A P-256 table finds nothing for a P-384 key.
- A `table` line changes `m` for the `plan` lines after it.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
plan(N, M):
    m = isqrt(N - 1) + 1
    if M is set: m = min(m, M)
    g = (N + 3*m - 1) // (2*m)
    return m, 2*g - 1

build_baby_table(curve, m):
    table = {}
    P = G
    for j from 1 to m:
        table[P.x] = (j, P.y)
        P = add(P, G)
    return table

find(curve, Q, N, table):
    m = size of table
    g = (N + 3*m - 1) // (2*m)
    S = scalar_multiply(2*m, G);  minusS = (S.x, p - S.y)
    for (step, sign, first) in [(minusS, +1, 0), (S, -1, 1)]:
        P = Q if first == 0 else add(Q, S)
        for k from first to g - 1:
            c = sign * 2*m*k
            if P is infinity:        e = c
            else if P.x in table:    (j, y) = table[P.x];  e = c + j if y == P.y else c - j
            else:                    e = none
            if e is not none:
                return e if 1 <= |e| <= N else none
            P = add(P, step)
    return none
```
</details>

## Checking your solution

```
.\check 17                          run every test
.\check 17 -Case 17-R3-pair         one test, showing its full input, expected output and your output
.\check 17 -Fresh                   a new set of tests (new random seed), to confirm on data you haven't seen
.\check 17 -Dispute <id> "why"      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this, here from a program that matches x and skips the y comparison:

```
  R2  A key d*G with d from 1 to the bound gives `weak <label> <d>`, in... .    5 / 15  FAILED
      x 17-R2-table-edge-p256  P-256, bound 1000 (m = 32): d = 31, 32 and 33 around the last baby step
          line 3: expected `weak k33 33`, got `weak k33 95`
          likely cause: R2 - A key d*G with d from 1 to the bound gives `weak <label> <d>`, including d at the edges of the table and of the giant steps
          expected values from: cryptography 41.0.7 (OpenSSL): each public key is computed from the chosen private value; plan lines from the page's formulas in exact integers
          reproduce: py -P tools/run_py.py solutions 17 build/cases/17/17-R2-table-edge-p256.in build/cases/17/17-R2-table-edge-p256.out
```

The down walk's second point is `33*G - 64*G = -(31*G)`. Its x matches `j = 31`, and without the
y comparison the program reports `64 + 31 = 95`.

## After you pass: compare with the post

The post contains no code, and it doesn't say which method the researcher used. Jackson's comment
names both methods. The eight reported values are all below 256, so a loop of 255 additions finds
each of them, and so does this search with `m = 16`. Your search also reaches bounds the loop
can't: 2^28 costs about 32,800 additions here, against 268,435,456 for the loop.

The reference `attack/bsgs.py` has three functions: `plan`, `build_baby_table` and
`find_private_key_bsgs`, which walks down and then up from `Q` and stops at the first hit. It
stores `(j, y)` for each x, about 248 bytes per entry for P-256 against 132 bytes for `j` alone.
Storing only `j` and computing `j*G` again on a hit is a correct alternative that uses about half
the memory. Another correct layout uses centres `2m + 1` apart, so that neighbouring giant points
don't overlap at `c + m`, and walks once from the most negative centre upwards.
