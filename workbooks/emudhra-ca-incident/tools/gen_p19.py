"""Test cases for assignment 19 (decide what each client accepts).

Each verdict combines four mechanisms, and the expected value of each comes from its own source:

- Root bundle and revocation: `openssl verify`. The generator builds every chain of a case as real
  certificates with `cryptography`, signs one CRL per CA listing that CA's revoked certificates, and
  runs

      openssl verify -attime <t> -CAfile <bundle> -untrusted <intermediates> [-crl_check | -crl_check_all] -CRLfile <crls> <leaf>

  The bundle holds the chain's root, unless the client's bundle is `updated` and the root is
  distrusted (then it holds an unrelated root). No flag models `revocation=off`, `-crl_check`
  (the leaf only) models `leaf`, and `-crl_check_all` (every certificate) models `chain`. OpenSSL
  stops at its first error: error 20 or 2 (no trusted issuer) means `distrusted-root`, and error
  23 at depth d means `revoked <role of certificate d>`. Every CA has a CRL in every run, because
  OpenSSL fails when one is missing and the page's model counts missing data as "not revoked".
- SPKI blocklist and Certificate Transparency: the rules on the page, by hand. No library applies a
  browser's SPKI blocklist or checks SCTs on synthetic certificates.

The three are combined in the page's order (blocklist, then OpenSSL's verdict, then CT), and a
second implementation written as a table of every candidate reason, ranked, must agree on every
line before a case is written.

    python3 -P tools/gen_p19.py                                  # tests/19 (seed 1)
    python3 -P tools/gen_p19.py --seed 777 --out build/fresh/19  # what `check 19 -Fresh` runs
"""

import datetime
import hashlib
import itertools
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import wbcore  # noqa: E402

LIB = ("openssl verify for the root bundle and revocation (-CAfile with or without the root; no flag, "
       "-crl_check or -crl_check_all, one CRL per CA); the page's rules by hand for the SPKI blocklist "
       "and CT; a second, table-driven implementation agrees on every line")
CT_SOURCE = ("the page's CT rule by hand (no library checks CT proofs on synthetic certificates); "
             "openssl verify confirms no other mechanism fires; a second implementation agrees")
BLOCK_SOURCE = ("the page's blocklist rule by hand (assignment 15's order) and openssl verify for the "
                "root bundle (-CAfile with or without the root); a second implementation agrees")

REQUIREMENTS = [
    ("R1", "One verdict line per chain and client, chains in input order and clients in declaration order; "
           "a fact line affects only later chains; switches are read by key"),
    ("R2", "`blocked-spki` rejects only clients with blocklist=yes (first role from the leaf); "
           "`distrusted-root` rejects only clients with bundle=updated"),
    ("R3", "Revocation follows the switch: off never rejects, leaf looks up the leaf only, chain looks up "
           "every certificate and names the first revoked one from the leaf"),
    ("R4", "ct=required rejects with missing-ct when the leaf is not logged, whatever the other certificates; "
           "ct=ignored never rejects"),
    ("R5", "The reasons run in the order blocklist, root distrust, revocation, CT, and revocation and CT "
           "are independent of each other"),
    ("E2E", "Several clients and chains in one input, mixing every verdict"),
]
EXPLAIN = "_lines=R1"

ATTIME = int(datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc).timestamp())
NOT_BEFORE, NOT_AFTER = datetime.datetime(2026, 1, 1), datetime.datetime(2028, 1, 1)
SWITCH_ORDER = ("revocation", "blocklist", "ct", "bundle")
ROLES_OK = ("leaf", "intermediate", "root")


def spki_token(name: str) -> str:
    """The stand-in SPKI hash of a certificate, 8 hex digits derived from its name."""
    return hashlib.sha256(f"spki:{name}".encode()).hexdigest()[:8]


# ---- The OpenSSL oracle (root bundle and revocation) ------------------------------------------

def x509_name(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


class Pki:
    """Real certificates for every name a case uses. A name is one certificate: the same name in
    two chains is the same certificate, issued by the same CA."""

    def __init__(self):
        self.keys, self.certs, self.issuer_of, self.serial = {}, {}, {}, {}
        self.next_serial = 100
        self.spare_root = None

    def key(self, name):
        if name not in self.keys:
            self.keys[name] = ec.generate_private_key(ec.SECP256R1())
        return self.keys[name]

    def cert(self, name, issuer, ca):
        if name in self.certs:
            assert self.issuer_of[name] == issuer, f"{name} is issued by two different CAs"
            return self.certs[name]
        self.next_serial += 1
        b = (x509.CertificateBuilder().subject_name(x509_name(name)).issuer_name(x509_name(issuer))
             .public_key(self.key(name).public_key()).serial_number(self.next_serial)
             .not_valid_before(NOT_BEFORE).not_valid_after(NOT_AFTER)
             .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True))
        if ca:
            b = b.add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
        self.certs[name] = b.sign(self.key(issuer), hashes.SHA256())
        self.issuer_of[name], self.serial[name] = issuer, self.next_serial
        return self.certs[name]

    def build(self, names):
        """Certificates for one chain, leaf first: each issued by the next, the root by itself."""
        out = []
        for i, name in enumerate(names):
            issuer = names[i + 1] if i + 1 < len(names) else name
            out.append(self.cert(name, issuer, ca=i > 0))
        return out

    def crl(self, ca_name, revoked):
        """The CRL that `ca_name` signs, listing the certificates it issued that are revoked."""
        b = (x509.CertificateRevocationListBuilder().issuer_name(x509_name(ca_name))
             .last_update(NOT_BEFORE).next_update(NOT_AFTER))
        for name in sorted(revoked):
            if self.issuer_of.get(name) == ca_name:
                b = b.add_revoked_certificate(x509.RevokedCertificateBuilder().serial_number(self.serial[name])
                                              .revocation_date(NOT_BEFORE).build())
        return b.sign(self.key(ca_name), hashes.SHA256())

    def unrelated_root(self):
        if self.spare_root is None:
            self.spare_root = self.cert("unrelated-root-not-in-any-chain", "unrelated-root-not-in-any-chain", ca=True)
        return self.spare_root


def pem(*objs) -> bytes:
    return b"".join(o.public_bytes(Encoding.PEM) for o in objs)


def openssl_verdict(pki, chain, revocation, root_in_bundle, revoked):
    """OpenSSL's first error for a chain, as the page's reason: None (verified), ("distrusted-root",
    root id) or ("revoked", role)."""
    names = [c["name"] for c in chain]
    certs = pki.build(names)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "bundle.pem").write_bytes(pem(certs[-1] if root_in_bundle else pki.unrelated_root()))
        (d / "untrusted.pem").write_bytes(pem(*certs[1:-1]))
        (d / "crls.pem").write_bytes(pem(*(pki.crl(n, revoked) for n in names[1:])))
        (d / "leaf.pem").write_bytes(pem(certs[0]))
        args = ["openssl", "verify", "-attime", str(ATTIME), "-CAfile", str(d / "bundle.pem"),
                "-untrusted", str(d / "untrusted.pem")]
        if revocation != "off":
            args += ["-crl_check" if revocation == "leaf" else "-crl_check_all", "-CRLfile", str(d / "crls.pem")]
        proc = subprocess.run(args + [str(d / "leaf.pem")], capture_output=True, text=True)
    text = proc.stdout + proc.stderr
    errors = re.findall(r"error (\d+) at (\d+) depth lookup", text)
    if proc.returncode == 0 and not errors:
        assert text.strip().endswith("OK"), text
        return None
    assert errors, f"openssl verify failed without a numbered error: {text}"
    code, depth = int(errors[0][0]), int(errors[0][1])
    if code in (2, 20):
        assert not root_in_bundle, text
        return ("distrusted-root", chain[-1]["root_id"])
    assert code == 23, f"unexpected openssl error {code}: {text}"
    return ("revoked", chain[depth]["role"])


# ---- The rules by hand, and the second implementation -----------------------------------------

def by_hand(pki, chain, client, facts):
    """The page's order: blocklist by hand, then OpenSSL for bundle and revocation, then CT by hand."""
    if client["blocklist"] == "yes":
        for c in chain:
            if c["spki"] in facts["blocked-spki"]:
                return ("blocked-spki", c["role"])
    root_in_bundle = not (client["bundle"] == "updated" and chain[-1]["root_id"] in facts["distrusted-root"])
    found = openssl_verdict(pki, chain, client["revocation"], root_in_bundle, facts["revoked"])
    if found:
        return found
    if client["ct"] == "required" and chain[0]["name"] not in facts["logged"]:
        return ("missing-ct",)
    return None


def table(chain, client, facts):
    """Every reason that holds, ranked by (mechanism, position from the leaf); the smallest wins."""
    looked_up = {"off": set(), "leaf": {0}, "chain": set(range(len(chain)))}[client["revocation"]]
    candidates = []
    for pos, c in enumerate(chain):
        candidates += [((1, pos), ("blocked-spki", c["role"]))] * (client["blocklist"] == "yes" and c["spki"] in facts["blocked-spki"])
        candidates += [((2, pos), ("distrusted-root", c["root_id"]))] * (
            client["bundle"] == "updated" and c["role"] == "root" and c["root_id"] in facts["distrusted-root"])
        candidates += [((3, pos), ("revoked", c["role"]))] * (pos in looked_up and c["name"] in facts["revoked"])
    candidates += [((4, 0), ("missing-ct",))] * (client["ct"] == "required" and chain[0]["name"] not in facts["logged"])
    return min(candidates)[1] if candidates else None


def line(chain_id, client_name, reason):
    return f"verdict {chain_id} {client_name} " + ("accept" if reason is None else "reject " + " ".join(reason))


# ---- Building a case ---------------------------------------------------------------------------

class Case:
    """One test input: clients, facts and chains, in the order they're added."""

    def __init__(self, rng=None):
        self.lines, self.clients, self.expected = [], [], []
        self.facts = {k: set() for k in ("blocked-spki", "distrusted-root", "revoked", "logged")}
        self.registry = {}
        self.rng = rng

    def client(self, name, revocation, blocklist, ct, bundle, shuffle=False):
        sw = dict(revocation=revocation, blocklist=blocklist, ct=ct, bundle=bundle)
        assert not any(l.startswith("chain ") for l in self.lines), "clients come before the first chain"
        order = list(SWITCH_ORDER)
        if shuffle:
            self.rng.shuffle(order)
        self.clients.append((name, sw))
        self.lines.append(f"client {name} " + " ".join(f"{k}={sw[k]}" for k in order))

    def block(self, cert_name):
        self.fact("blocked-spki", spki_token(cert_name))

    def fact(self, kind, value):
        self.facts[kind].add(value)
        self.lines.append(f"{kind} {value}")

    def chain(self, chain_id, names, root_id, pki):
        """names: leaf, intermediates..., root. The root carries `root_id`."""
        assert len(names) >= 3
        chain = []
        for i, name in enumerate(names):
            role = "leaf" if i == 0 else "root" if i == len(names) - 1 else "intermediate"
            c = dict(name=name, role=role, spki=spki_token(name), root_id=root_id if role == "root" else "-")
            assert self.registry.setdefault(name, c) == c, f"{name} reappears with other fields"
            chain.append(c)
        self.lines.append(f"chain {chain_id}")
        self.lines += [f"cert {c['role']} {c['name']} {c['spki']} {c['root_id']}" for c in chain]
        facts = {k: set(v) for k, v in self.facts.items()}  # only facts declared so far
        for name, sw in self.clients:
            a, b = by_hand(pki, chain, sw, facts), table(chain, sw, facts)
            assert a == b, f"{chain_id}/{name}: the oracle says {a}, the second implementation {b}"
            self.expected.append(line(chain_id, name, a))


def main():
    args = wbcore.parse_args("19")
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, build, source=None):
        case, pki = Case(random.Random(f"{args.seed}:{case_id}")), Pki()
        build(case, pki)
        assert len(case.clients) <= 6 and sum(l.startswith("chain ") for l in case.lines) <= 6
        cases.add(case_id, req, title, case.lines, case.expected, source=source)

    # Standard chain shapes: the cert names are unique to each chain unless a test shares them.
    def std(case, pki, cid, tag, root="root-a", root_id="root-a-id", ints=1):
        names = [f"{tag}-leaf"] + [f"{tag}-int{i + 1}" if ints > 1 else f"{tag}-int" for i in range(ints)] + [root]
        case.chain(cid, names, root_id, pki)
        return names

    every_switch = [  # six clients that between them set every switch value
        ("strict", "chain", "yes", "required", "updated"),
        ("leaf-check", "leaf", "no", "required", "stale"),
        ("blocklist-only", "off", "yes", "ignored", "stale"),
        ("bundle-only", "off", "no", "ignored", "updated"),
        ("revocation-only", "chain", "no", "ignored", "stale"),
        ("bare", "off", "no", "ignored", "stale"),
    ]

    # ---- R1: lines, order, facts that come later, switches by key
    # The R1 cases give each verdict a single reason and log every certificate of a logged chain,
    # so a mistake in one mechanism, or in the order of the checks, fails an R2 to R5 case instead.
    def log_all(case, names):
        for name in names:
            case.fact("logged", name)

    def r1_clean(case, pki):
        for c in every_switch:
            case.client(*c)
        log_all(case, ("clean-leaf", "clean-int", "root-a"))
        std(case, pki, "clean", "clean")
    add("19-R1-clean-chain-six-clients", "R1", "a logged chain with nothing blocked, distrusted or revoked: six clients accept", r1_clean)

    def r1_later(case, pki):
        case.client("blocklist-only", "off", "yes", "ignored", "stale")
        case.client("bundle-only", "off", "no", "ignored", "updated")
        case.client("revocation-only", "chain", "no", "ignored", "stale")
        names = std(case, pki, "before", "shared")
        case.block("shared-int")
        case.fact("distrusted-root", "root-a-id")
        case.fact("revoked", "shared-leaf")
        case.chain("after", names, "root-a-id", pki)
    add("19-R1-facts-after-a-chain", "R1",
        "blocked-spki, distrusted-root and revoked lines come after chain `before` and before chain `after`, which has the same certificates",
        r1_later)

    def r1_logged_later(case, pki):
        case.client("ct-only", "off", "no", "required", "stale")
        names = std(case, pki, "before", "late")
        log_all(case, names)
        case.chain("after", names, "root-a-id", pki)
    add("19-R1-logged-after-a-chain", "R1",
        "the leaf's logged line comes after chain `before`: missing-ct there, accept for the same certificates afterwards",
        r1_logged_later, source=CT_SOURCE)

    def r1_shuffled(case, pki):
        for c in every_switch:
            case.client(*c, shuffle=True)
        case.block("mix-int")
        case.fact("distrusted-root", "root-m-id")
        log_all(case, ("mix-leaf", "mix-int", "root-a", "other-leaf", "other-int", "root-m"))
        std(case, pki, "blocked-key", "mix")
        std(case, pki, "distrusted", "other", root="root-m", root_id="root-m-id")
    add("19-R1-switches-in-any-order", "R1",
        "the four key=value words of each client come in a shuffled order; a blocked intermediate, then a distrusted root",
        r1_shuffled)

    def r1_two(case, pki):
        case.client("bare", "off", "no", "ignored", "stale")
        case.client("rev-only", "chain", "no", "ignored", "stale")
        case.client("ct-only", "off", "no", "required", "stale")
        case.fact("revoked", "first-int")
        std(case, pki, "first", "first")
        log_all(case, ("second-leaf", "second-int", "root-a"))
        std(case, pki, "second", "second")
    add("19-R1-two-chains-three-clients", "R1",
        "two chains and three clients: six lines, chain by chain, clients in declaration order", r1_two)

    # ---- R2: the blocklist and the bundle, each its own switch
    for role, target in (("leaf", "leaf"), ("intermediate", "int"), ("root", None)):
        def r2_role(case, pki, role=role, target=target):
            case.client("with-blocklist", "off", "yes", "ignored", "stale")
            case.client("without-blocklist", "off", "no", "ignored", "stale")
            case.client("bundle-updated", "off", "no", "ignored", "updated")
            case.block(f"b{role}-{target}" if target else "root-b")
            std(case, pki, "c1", f"b{role}", root="root-b", root_id="root-b-id")
        add(f"19-R2-blocked-{role}", "R2",
            f"the {role}'s SPKI hash is blocked: only the client with blocklist=yes rejects", r2_role, source=BLOCK_SOURCE)

    def r2_two_blocked(case, pki):
        case.client("with-blocklist", "chain", "yes", "ignored", "stale")
        case.block("two-int")
        case.block("two-leaf")
        std(case, pki, "c1", "two")
    add("19-R2-two-blocked-names-the-leaf", "R2",
        "the leaf and the intermediate are both blocked (intermediate's line first): the leaf is named", r2_two_blocked,
        source=BLOCK_SOURCE)

    def r2_long(case, pki):
        case.client("with-blocklist", "off", "yes", "ignored", "stale")
        case.client("without-blocklist", "off", "no", "ignored", "updated")
        case.block("long-int2")
        std(case, pki, "long", "long", ints=2)
    add("19-R2-blocked-second-intermediate", "R2",
        "a chain with two intermediates, the second one (next to the root) blocked", r2_long, source=BLOCK_SOURCE)

    def r2_distrust(case, pki):
        case.client("bundle-updated", "off", "no", "ignored", "updated")
        case.client("bundle-stale", "off", "no", "ignored", "stale")
        case.client("blocklist-stale", "chain", "yes", "ignored", "stale")
        case.fact("distrusted-root", "root-old-id")
        std(case, pki, "old-root", "dist", root="root-old", root_id="root-old-id")
        std(case, pki, "other-root", "fine", root="root-new", root_id="root-new-id")
    add("19-R2-distrusted-root-updated-vs-stale", "R2",
        "a distrusted root: an updated bundle rejects, a stale bundle accepts even with the blocklist; another root is unaffected",
        r2_distrust, source=BLOCK_SOURCE)

    def r2_mixed(case, pki):
        case.client("blocklist-stale", "off", "yes", "ignored", "stale")
        case.client("no-blocklist-updated", "off", "no", "ignored", "updated")
        case.client("both", "off", "yes", "ignored", "updated")
        case.client("neither", "off", "no", "ignored", "stale")
        case.block("keyed-int")
        case.fact("distrusted-root", "root-d-id")
        std(case, pki, "blocked-key", "keyed")
        std(case, pki, "distrusted", "rooted", root="root-d", root_id="root-d-id")
    add("19-R2-blocklist-and-bundle-are-separate", "R2",
        "one chain with a blocked key, one under a distrusted root, four clients with each mix of the two switches",
        r2_mixed, source=BLOCK_SOURCE)

    def r2_both(case, pki):
        case.client("both", "off", "yes", "ignored", "updated")
        case.client("bundle-only", "off", "no", "ignored", "updated")
        case.client("blocklist-only", "off", "yes", "ignored", "stale")
        case.client("neither", "off", "no", "ignored", "stale")
        case.block("both-int")
        case.fact("distrusted-root", "root-e-id")
        std(case, pki, "c1", "both", root="root-e", root_id="root-e-id")
    add("19-R2-blocked-key-under-distrusted-root", "R2",
        "the intermediate is blocked and the root distrusted: blocklist clients name the key, the others the root or nothing",
        r2_both, source=BLOCK_SOURCE)

    # ---- R3: revocation modes against OpenSSL
    rev_clients = [("rev-off", "off"), ("rev-leaf", "leaf"), ("rev-chain", "chain")]

    def r3(case_id, title, revoked, ints=1, extra=None):
        def build(case, pki):
            for name, mode in rev_clients:
                case.client(name, mode, "no", "ignored", "stale")
            if extra:
                extra(case, pki)
            for name in revoked:
                case.fact("revoked", name)
            std(case, pki, "c1", "r", root="r-root", root_id="r-root-id", ints=ints)
        add(case_id, "R3", title, build)

    r3("19-R3-revoked-leaf", "the leaf is revoked: leaf and chain modes reject", ["r-leaf"])
    r3("19-R3-revoked-intermediate", "the intermediate is revoked: only chain mode rejects", ["r-int"])
    r3("19-R3-revoked-root", "the root is revoked on its own CRL: only chain mode rejects", ["r-root"])
    r3("19-R3-revoked-leaf-and-intermediate", "leaf and intermediate revoked: both modes that look name the leaf",
       ["r-int", "r-leaf"])
    r3("19-R3-revoked-intermediate-and-root", "intermediate and root revoked: chain mode names the intermediate",
       ["r-root", "r-int"])
    r3("19-R3-all-three-revoked", "every certificate revoked: leaf for both modes that look", ["r-root", "r-int", "r-leaf"])
    r3("19-R3-revoked-second-intermediate", "two intermediates, the one next to the root revoked", ["r-int2"], ints=2)
    r3("19-R3-revoked-elsewhere", "revoked lines name certificates of no chain in the input: everyone accepts",
       ["other-leaf", "other-int"])

    def r3_shared(case, pki):
        for name, mode in rev_clients:
            case.client(name, mode, "no", "ignored", "stale")
        case.fact("revoked", "shared-ca")
        case.chain("site-1", ["site-1-leaf", "shared-ca", "s-root"], "s-root-id", pki)
        case.chain("site-2", ["site-2-leaf", "shared-ca", "s-root"], "s-root-id", pki)
    add("19-R3-revoked-intermediate-two-chains", "R3",
        "one revoked intermediate issued the leaves of two chains: chain mode rejects both", r3_shared)

    # ---- R4: Certificate Transparency looks at the leaf only
    ct_clients = [("ct-required", "off", "no", "required", "stale"), ("ct-ignored", "off", "no", "ignored", "stale")]

    def r4(case_id, title, logged):
        def build(case, pki):
            for c in ct_clients:
                case.client(*c)
            for name in logged:
                case.fact("logged", name)
            std(case, pki, "c1", "t")
        add(case_id, "R4", title, build, source=CT_SOURCE)

    r4("19-R4-unlogged-leaf", "nothing logged: ct=required rejects, ct=ignored accepts", [])
    r4("19-R4-logged-leaf", "the leaf is logged: both accept", ["t-leaf"])
    r4("19-R4-logged-leaf-unlogged-intermediate", "the leaf is logged and the intermediate and root are not: both accept",
       ["t-leaf"])
    r4("19-R4-logged-intermediate-and-root-only", "the intermediate and root are logged, the leaf is not: missing-ct",
       ["t-int", "t-root"])

    def r4_two(case, pki):
        for c in ct_clients:
            case.client(*c)
        case.fact("logged", "seen-leaf")
        std(case, pki, "seen", "seen")
        std(case, pki, "unseen", "unseen")
    add("19-R4-two-chains-one-logged", "R4", "two chains, only the first leaf logged", r4_two, source=CT_SOURCE)

    # ---- R5: the order of the reasons, and two independent mechanisms
    def priority(case, pki):
        case.client("all-on", "chain", "yes", "required", "updated")
        case.client("no-blocklist", "chain", "no", "required", "updated")
        case.client("no-bundle", "chain", "no", "required", "stale")
        case.client("ct-only", "off", "no", "required", "stale")
        case.client("none", "off", "no", "ignored", "stale")
        case.block("int-weak")
        case.fact("distrusted-root", "root-a-id")
        case.fact("revoked", "int-weak")
        case.chain("forged-site", ["site-leaf", "int-weak", "root-a"], "root-a-id", pki)
    add("19-R5-priority", "R5",
        "blocked, distrusted, revoked and unlogged at once: each client has one mechanism fewer than the one before",
        priority)

    def independent(case, pki):
        case.client("ct-only", "off", "no", "required", "stale")
        case.client("rev-only", "chain", "no", "ignored", "stale")
        case.fact("revoked", "int-a")
        case.fact("logged", "leaf-a")
        case.chain("c-logged-revoked", ["leaf-a", "int-a", "root-a"], "root-a-id", pki)
        case.chain("c-unlogged-clean", ["leaf-b", "int-b", "root-a"], "root-a-id", pki)
    add("19-R5-independent-mechanisms", "R5",
        "a logged chain with a revoked intermediate, and an unlogged chain with nothing revoked: each check passes the other's chain",
        independent)

    def four_combos(case, pki):
        case.client("rev-and-ct", "chain", "no", "required", "stale")
        case.client("ct-only", "off", "no", "required", "stale")
        case.client("rev-only", "chain", "no", "ignored", "stale")
        for cid, revoked, logged in (("revoked-logged", True, True), ("revoked-unlogged", True, False),
                                     ("clean-unlogged", False, False), ("clean-logged", False, True)):
            if revoked:
                case.fact("revoked", f"{cid}-int")
            if logged:
                case.fact("logged", f"{cid}-leaf")
            std(case, pki, cid, cid)
    add("19-R5-revoked-and-logged-combinations", "R5",
        "the four combinations of a revoked intermediate and a logged leaf, for a client with both checks and one with each",
        four_combos)

    def pair(case_id, title, setup, client):
        def build(case, pki):
            case.client("tested", *client)
            setup(case)
            std(case, pki, "c1", "p", root="p-root", root_id="p-root-id")
        add(case_id, "R5", title, build)

    pair("19-R5-blocklist-before-revocation", "a revoked leaf and a blocked intermediate: blocked-spki intermediate",
         lambda c: (c.fact("revoked", "p-leaf"), c.block("p-int")), ("chain", "yes", "ignored", "stale"))
    pair("19-R5-distrust-before-revocation", "a revoked leaf under a distrusted root: distrusted-root",
         lambda c: (c.fact("revoked", "p-leaf"), c.fact("distrusted-root", "p-root-id")), ("chain", "no", "ignored", "updated"))
    pair("19-R5-blocklist-before-distrust", "a blocked leaf under a distrusted root: blocked-spki leaf",
         lambda c: (c.fact("distrusted-root", "p-root-id"), c.block("p-leaf")), ("off", "yes", "ignored", "updated"))
    pair("19-R5-revocation-before-ct", "a revoked intermediate and an unlogged leaf: revoked intermediate",
         lambda c: c.fact("revoked", "p-int"), ("chain", "no", "required", "stale"))
    pair("19-R5-all-on-accepts-clean", "every switch on, the leaf logged and nothing else listed: accept",
         lambda c: c.fact("logged", "p-leaf"), ("chain", "yes", "required", "updated"))

    # ---- E2E
    def forged(case, pki):
        case.block("int-weak")
        case.fact("revoked", "int-weak")
        case.client("updated-browser", "off", "yes", "required", "updated")
        case.client("old-browser", "off", "no", "required", "stale")
        case.client("cli-tool", "off", "no", "ignored", "stale")
        case.client("os-revocation", "chain", "no", "ignored", "stale")
        case.client("os-leaf-only", "leaf", "no", "ignored", "stale")
        case.chain("forged-site", ["site-leaf", "int-weak", "root-a"], "root-a-id", pki)
    add("19-E2E-forged-chain", "E2E",
        "a forged leaf under a blocked and revoked intermediate, five clients with different mechanisms", forged)

    def mixed(case, pki):
        for c in (("full", "chain", "yes", "required", "updated"), ("browser-old", "off", "no", "required", "stale"),
                  ("os-strict", "chain", "no", "ignored", "updated"), ("os-leaf", "leaf", "no", "ignored", "stale"),
                  ("blocklist-only", "off", "yes", "ignored", "stale"), ("bare", "off", "no", "ignored", "stale")):
            case.client(*c)
        case.block("forged-int")
        case.fact("revoked", "forged-int")
        case.fact("logged", "legacy-leaf")
        case.fact("logged", "fine-leaf")
        std(case, pki, "forged", "forged", root="root-x", root_id="root-x-id")
        case.fact("revoked", "legacy-leaf")
        case.fact("distrusted-root", "root-y-id")
        std(case, pki, "legacy", "legacy", root="root-y", root_id="root-y-id")
        std(case, pki, "fine", "fine", root="root-x", root_id="root-x-id")
    add("19-E2E-six-clients-three-chains", "E2E",
        "six clients and three chains: a forged chain, a revoked leaf under a distrusted root, and a clean chain", mixed)

    def random_case(case, pki):
        combos = list(itertools.product(("off", "leaf", "chain"), ("yes", "no"), ("required", "ignored"), ("updated", "stale")))
        for k, sw in enumerate(rng.sample(combos, 6)):
            case.client(f"client-{k + 1}", *sw, shuffle=True)
        roots = [("root-p", "root-p-id"), ("root-q", "root-q-id")]
        for n in range(6):
            tag = f"s{args.seed}-c{n + 1}"
            root, root_id = rng.choice(roots)
            ints = rng.choice((1, 1, 2))
            names = [f"{tag}-leaf"] + [f"{tag}-int{i + 1}" for i in range(ints)]
            # facts before this chain, about its own certificates or its root
            if rng.random() < 0.3:
                case.block(rng.choice(names + [root]))
            if rng.random() < 0.2 and root_id not in case.facts["distrusted-root"]:
                case.fact("distrusted-root", root_id)
            for name in names + [root]:
                if rng.random() < 0.25 and name not in case.facts["revoked"]:
                    case.fact("revoked", name)
            if rng.random() < 0.6:
                case.fact("logged", f"{tag}-leaf")
            case.chain(f"chain-{n + 1}", names + [root], root_id, pki)
    add(f"19-E2E-random-s{args.seed}", "E2E", f"six random clients and six random chains (seed {args.seed})", random_case)

    cases.save()


if __name__ == "__main__":
    main()
