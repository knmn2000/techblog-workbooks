# 19 · Decide what each client accepts

**Difficulty:** Medium · **Assignment** 19 of 19 · **Check:** `.\check 19`

**Tags**
- *Language:* parsing `key=value` words · sets · reading facts in input order
- *Library:* none needed
- *Concepts:* revocation checking (CRLs) · Certificate Transparency (SCTs) · root bundles · SPKI blocklists · which client each fix reaches

## Read in the blog first

This page is complete on its own. Scott Helme's post
["Eight bits of trust"](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/#:~:text=I%20tested%20this%20on%20my%20own%20machines),
section "Who's exposed today", describes a test he ran on his own machines against a local server.
He built a forged chain for a well-known site under one of the weak intermediates. With default
settings, curl verified it, Python completed the handshake and Node reported `authorized: true`,
on every Linux and macOS machine he tested. On Windows the chain passed unless he turned
revocation checking on. He also writes that Chrome, Firefox and Safari require Certificate
Transparency, and that most non-browser clients trust a CA bundle on disk and check neither
revocation nor CT by default. This assignment models those differences with four switches per
client and synthetic names. It makes no claim about what any named client does today.

## Source material

- Scott Helme, [Eight bits of trust: eMudhra's CA keys cracked in milliseconds](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/), sections "Who's exposed today" and "Why 'it cannot be contained'"
- OpenSSL, [verification options](https://docs.openssl.org/3.0/man1/openssl-verification-options/): `-crl_check` (the leaf only) and `-crl_check_all` (every certificate in the chain)
- RFC 6962, [Certificate Transparency](https://www.rfc-editor.org/rfc/rfc6962): signed certificate timestamps (SCTs), the proofs a log returns for a certificate
- `docs/what-we-know.md` in this workbook, section "Why the weakness is cheap to find"
- Assignment 15 (`problems/15-blocklist-distrust.md`): the SPKI blocklist and root distrust that this assignment applies per client

## Where this fits

You can do this assignment any time after assignment 15. There, one browser blocked keys by SPKI
hash and distrusted roots. Here the same chain goes to several clients, and each one has only some
of the mechanisms. Your new `pki/client_policy.py` calls your `check_chain` from `pki/trust.py`
for the first two checks and adds revocation and CT after it. No later assignment uses it.

## The problem

Write a program that reads a list of clients and a list of certificate chains, and says for each
chain and each client whether that client accepts the chain, and if not, why.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these kinds of lines:

| Line | Meaning |
|---|---|
| `client <name> revocation=<off\|leaf\|chain> blocklist=<yes\|no> ct=<required\|ignored> bundle=<updated\|stale>` | A client and its four switches. The four `key=value` words come in any order. Every `client` line comes before the first `chain` line. |
| `blocked-spki <hash>` | An SPKI hash on the browsers' blocklist, as in assignment 15. |
| `distrusted-root <root-id>` | A root that updated root bundles no longer hold, as in assignment 15. |
| `revoked <cert-name>` | The CA's revocation data (its CRL) lists this certificate as revoked. |
| `logged <cert-name>` | This certificate carries CT proofs (SCTs) from logs. |
| `chain <id>` | Starts a chain. Its `cert` lines come right after it. |
| `cert <role> <cert-name> <spki-hash> <root-id>` | One certificate of the current chain, leaf first. `role` is `leaf`, `intermediate` or `root`. `root-id` is `-` for a leaf or an intermediate. |

A `cert-name` names one certificate. A name that appears in two chains comes with the same role,
SPKI hash and root id both times, and it is the same certificate. A `revoked` or `logged` line may
name a certificate that no chain contains.

The four fact lines (`blocked-spki`, `distrusted-root`, `revoked` and `logged`) add to sets that
grow as the input goes on. Each one affects only the chains that start after it. A fact line that
comes right after a chain's last `cert` line does not affect that chain.

### Output

For each chain in input order, and within a chain for each client in the order the `client` lines
declare them, write one line:

```
verdict <chain-id> <client> accept
verdict <chain-id> <client> reject blocked-spki <role>
verdict <chain-id> <client> reject distrusted-root <root-id>
verdict <chain-id> <client> reject revoked <role>
verdict <chain-id> <client> reject missing-ct
```

An input with 3 chains and 4 clients has 12 lines: the 4 lines of the first chain, then the 4 of
the second, then the 4 of the third. Copy the ids and names from the input unchanged.

### What the switches mean

| Switch | Value | Meaning |
|---|---|---|
| `blocklist` | `yes` | The client holds the SPKI blocklist and applies every `blocked-spki` line. |
| | `no` | The client ignores `blocked-spki` lines. |
| `bundle` | `updated` | The client's root bundle no longer holds the roots named by `distrusted-root`. |
| | `stale` | The client's bundle still holds them, so root distrust never applies. |
| `revocation` | `off` | The client looks up no revocation data. |
| | `leaf` | The client looks up the leaf only, like OpenSSL's `-crl_check`. |
| | `chain` | The client looks up every certificate, leaf to root, like OpenSSL's `-crl_check_all`. |
| `ct` | `required` | The client rejects a chain whose leaf is not `logged`. |
| | `ignored` | The client never looks at CT. |

A certificate counts as revoked when a `revoked` line names it. A certificate that no `revoked`
line names counts as not revoked, including one the input says nothing about.

A log issues its proofs (SCTs) for the end-entity certificate, the leaf (RFC 6962, section 3.3),
so only the leaf's `logged` status matters. A logged intermediate or root does not stand in for an
unlogged leaf, and an unlogged intermediate or root does not stop a logged leaf.

### The order of the checks

For each chain and client, stop at the first rule that applies:

| Step | Applies when | Reason written |
|---|---|---|
| 1 | `blocklist=yes` and a certificate's SPKI hash is blocked. The first such certificate from the leaf decides. | `blocked-spki <role>` |
| 2 | `bundle=updated` and the chain's root id is distrusted. | `distrusted-root <root-id>` |
| 3 | `revocation` is `leaf` and the leaf is revoked, or `revocation` is `chain` and any certificate is revoked. The first revoked certificate from the leaf decides. | `revoked <role>` |
| 4 | `ct=required` and the leaf is not logged. | `missing-ct` |
| 5 | None of the above. | `accept` |

Steps 1 and 2 are assignment 15's `check_chain`, called with the blocked hashes only when
`blocklist=yes` (an empty set otherwise) and with the distrusted roots only when `bundle=updated`
(an empty set otherwise). Its `spki` block becomes `blocked-spki` and its `root` block becomes
`distrusted-root`, with the same role or root id.

The two switches of step 1 and step 2 are separate. A client with `blocklist=yes` and
`bundle=stale` rejects a chain with a blocked key and accepts a chain under a distrusted root.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** The output has one `verdict` line per chain and client, chains in input order and clients
  in declaration order. A fact line affects only chains that start after it. The program reads the
  four switches by their keys, in any order. Every client accepts a chain with nothing blocked,
  distrusted or revoked and a logged leaf.
- **R2** `blocked-spki` rejects only clients with `blocklist=yes`, naming the first blocked
  certificate from the leaf. `distrusted-root` rejects only clients with `bundle=updated`.
- **R3** `revocation=off` never rejects. `revocation=leaf` rejects only a revoked leaf.
  `revocation=chain` rejects any revoked certificate, the root included, and names the first one
  from the leaf.
- **R4** `ct=required` rejects with `missing-ct` when the leaf is not logged, whatever the logging
  of the other certificates. `ct=ignored` never rejects.
- **R5** The reasons follow the order of the checks: blocklist, root distrust, revocation, CT.
  Revocation and CT are independent: a client that checks both rejects a logged leaf under a
  revoked intermediate, and a client that checks only CT accepts it.

## Examples

### Example 1: one forged chain, five clients (test `19-E2E-forged-chain`)

```
input:   blocked-spki 67f7806d
         revoked int-weak
         client updated-browser revocation=off blocklist=yes ct=required bundle=updated
         client old-browser revocation=off blocklist=no ct=required bundle=stale
         client cli-tool revocation=off blocklist=no ct=ignored bundle=stale
         client os-revocation revocation=chain blocklist=no ct=ignored bundle=stale
         client os-leaf-only revocation=leaf blocklist=no ct=ignored bundle=stale
         chain forged-site
         cert leaf site-leaf cd23e974 -
         cert intermediate int-weak 67f7806d -
         cert root root-a b2b2fe86 root-a-id

output:  verdict forged-site updated-browser reject blocked-spki intermediate
         verdict forged-site old-browser reject missing-ct
         verdict forged-site cli-tool accept
         verdict forged-site os-revocation reject revoked intermediate
         verdict forged-site os-leaf-only accept
```

The intermediate's key is on the blocklist, and its CA revoked it. The leaf is the forgery: no CA
issued it, so no CRL lists it and no log holds it. Only `updated-browser` holds the blocklist.
`old-browser` has no blocklist and requires CT, so it stops at step 4. `cli-tool` has none of the
four mechanisms. `os-revocation` looks up the whole chain and finds the intermediate at step 3.
`os-leaf-only` looks up the leaf, which no CRL lists, and accepts.

### Example 2: revocation and CT stop different chains (test `19-R5-independent-mechanisms`)

```
input:   client ct-only revocation=off blocklist=no ct=required bundle=stale
         client rev-only revocation=chain blocklist=no ct=ignored bundle=stale
         revoked int-a
         logged leaf-a
         chain c-logged-revoked
         cert leaf leaf-a 8c77d137 -
         cert intermediate int-a f4b3aff2 -
         cert root root-a b2b2fe86 root-a-id
         chain c-unlogged-clean
         cert leaf leaf-b 265c6e9d -
         cert intermediate int-b 54f8c189 -
         cert root root-a b2b2fe86 root-a-id

output:  verdict c-logged-revoked ct-only accept
         verdict c-logged-revoked rev-only reject revoked intermediate
         verdict c-unlogged-clean ct-only reject missing-ct
         verdict c-unlogged-clean rev-only accept
```

The first chain has a logged leaf under a revoked intermediate. A log accepts a certificate whose
chain leads to a root the log trusts (RFC 6962, section 3.1), so a leaf signed with a recovered
key could be logged too. The second chain has an unlogged leaf and nothing revoked. Each client
stops one chain and passes the other:

| Chain | Leaf logged | Something revoked | `ct-only` | `rev-only` |
|---|---|---|---|---|
| `c-logged-revoked` | yes | the intermediate | accept | reject revoked intermediate |
| `c-unlogged-clean` | no | nothing | reject missing-ct | accept |

### Example 3: the order of the checks (test `19-R5-priority`)

```
input:   client all-on revocation=chain blocklist=yes ct=required bundle=updated
         client no-blocklist revocation=chain blocklist=no ct=required bundle=updated
         client no-bundle revocation=chain blocklist=no ct=required bundle=stale
         client ct-only revocation=off blocklist=no ct=required bundle=stale
         client none revocation=off blocklist=no ct=ignored bundle=stale
         blocked-spki 67f7806d
         distrusted-root root-a-id
         revoked int-weak
         chain forged-site
         cert leaf site-leaf cd23e974 -
         cert intermediate int-weak 67f7806d -
         cert root root-a b2b2fe86 root-a-id

output:  verdict forged-site all-on reject blocked-spki intermediate
         verdict forged-site no-blocklist reject distrusted-root root-a-id
         verdict forged-site no-bundle reject revoked intermediate
         verdict forged-site ct-only reject missing-ct
         verdict forged-site none accept
```

All four reasons hold for this chain. Each client has one mechanism fewer than the one above it,
so each stops at a later step, and `none` accepts.

## Constraints

- At most 6 clients and at most 6 chains. Every chain has one leaf, one or two intermediates and
  one root, leaf first.
- The input is well formed: every `client` line has the four switches with valid values, and a
  chain's `cert` lines come right after its `chain` line, with no other line between them.
- Each case has a 10-second limit. The program does no heavy work.
- There are 38 tests: 5 for R1, 8 for R2, 9 for R3, 5 for R4, 8 for R5 and 3 end-to-end cases
  (Example 1, six clients against three chains, and six random clients against six random
  chains). The random case changes with `-Fresh`.
- The expected answers come from two places. For the root bundle and revocation, the generator
  builds each chain as real certificates with one CRL per CA and runs `openssl verify`: with the
  root in the `-CAfile` or without it, and with no revocation flag, `-crl_check` or
  `-crl_check_all`. OpenSSL fails when a CA has no CRL, so every CA in those runs has one. For the
  SPKI blocklist and CT, the expected answers follow the rules above by hand, since no library
  applies a browser blocklist or checks SCTs on synthetic certificates. A second implementation,
  written as a ranked table of reasons, agrees with every expected line.

## Hints

<details><summary>Hint 1: where to start</summary>

A client is four switches, and each mechanism reads one of the four fact sets. Write one function
that takes a chain, its certificate names, one client and the facts, and returns the first reason
or None. The program loops over chains and clients and turns each result into a line.
</details>

<details><summary>Hint 2: the approach</summary>

For each client, build the two sets that `check_chain` takes: the blocked hashes if the client
holds the blocklist, else an empty set, and the distrusted roots if its bundle is updated, else an
empty set. If `check_chain` returns a block, translate it. Otherwise walk the certificates the
revocation switch covers (none, the leaf, or all of them) from the leaf and stop at the first
revoked name. Then test the leaf's name against the logged set if the client requires CT.

Decide a chain as soon as its `cert` lines end, before you read the next fact line. If your
assignment 15 program decided a chain only when the next `chain` line arrived, a fact line between
two chains would reach the earlier one.
</details>

<details><summary>Hint 3: the traps</summary>

- `blocklist` and `bundle` are separate switches. Passing both of 15's sets to every client
  rejects a distrusted root for a client with a stale bundle.
- The blocklist applies to every certificate in the chain, the intermediates and the root as well
  as the leaf.
- `leaf` means the leaf only. A leaf-only client accepts a chain whose intermediate is revoked.
- `chain` includes the root. A root can list itself on its own CRL.
- With two revoked certificates, report the one nearer the leaf.
- CT looks at the leaf only, in both directions: logged intermediates don't help an unlogged leaf,
  and unlogged intermediates don't hurt a logged one.
- A logged leaf is no reason to skip revocation. Revocation comes before CT for a client that has
  both.
- Read the switches by key. The order of the four words changes from line to line.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
decide(chain, names, client, facts):
    blocked = facts.blocked_spki if client.blocklist else set()
    distrusted = facts.distrusted_roots if client.bundle_updated else set()
    block = check_chain(chain, blocked, distrusted)        # your assignment 15 function
    if block: return ("blocked-spki" if block.mechanism == "spki" else "distrusted-root", block.what)
    count = 0 if client.revocation == "off" else 1 if client.revocation == "leaf" else len(chain)
    for i in 0 .. count - 1:                                # leaf first
        if names[i] in facts.revoked: return ("revoked", chain[i].role)
    if client.ct_required and names[0] not in facts.logged: return ("missing-ct",)
    return None                                             # accept

main:
    for each line:
        if it is a cert line: add it to the current chain
        else:
            if a chain is open: write its verdicts (one per client) and close it
            client line -> remember the client; fact line -> add to its set; chain line -> open a chain
    at the end, write the verdicts of the open chain
```
</details>

## Checking your solution

```
.\check 19                                   run every test
.\check 19 -Case 19-R5-priority              one test, showing its full input, expected output and your output
.\check 19 -Fresh                            a new set of tests (new random seed)
.\check 19 -Dispute <id> "why"               set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  The reasons run in the order blocklist, root distrust, revocation... .    5 / 8   FAILED
      x 19-R5-priority  blocked, distrusted, revoked and unlogged at once: each client has one mechan...
          line 3: expected `verdict forged-site no-bundle reject revoked intermediate`, got `verdict forged-site no-bundle reject missing-ct`
          likely cause: R5 - The reasons run in the order blocklist, root distrust, revocation, CT, and revocation and CT are independent of each other
          expected values from: openssl verify for the root bundle and revocation (-CAfile with or without the root; no flag, -crl_check or -crl_check_all, one CRL per CA); the page's rules by hand for the SPKI blocklist and CT; a second, table-driven implementation agrees on every line
          reproduce: py -P tools/run_py.py solutions 19 build/cases/19/19-R5-priority.in build/cases/19/19-R5-priority.out
```

## After you pass: what the switches leave out

The reference `pki/client_policy.py` calls `check_chain` for steps 1 and 2, then has one small
function for revocation, `first_revoked`, and one test for CT. The browser response in assignment
15 is the first row of Example 1: it protects a client that receives the blocklist and the updated
bundle, and none of the others. Example 2 shows why the other two mechanisms don't replace each
other. Revocation catches a forged leaf only through a revoked certificate above it, because no CA
revokes a leaf it never issued. CT catches an unlogged leaf and passes a logged one.

Real clients differ from the four switches in ways the model leaves out. Some look up revocation
through OCSP as well as CRLs, and some treat missing revocation data as a failure, as OpenSSL does
when a CA has no CRL. Revocation names certificates, while a blocklist names keys. After
cross-signing, each weak key appeared in two certificates (`docs/what-we-know.md`), and one SPKI
block covers both. The switches also leave out how a client builds its chain and
how often it refreshes its bundle, and they say nothing about whether Helme's forged leaf was
logged.
