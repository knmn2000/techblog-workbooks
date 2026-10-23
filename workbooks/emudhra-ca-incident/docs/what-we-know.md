# What we know and what we don't

Status as of October 24, 2026. The incident became public seven days ago and the facts are still moving. eMudhra says it has not confirmed the root cause and will publish it in full when its investigation ends. This page separates four kinds of statement: facts that independent sources report, eMudhra's own account (attributed and unverified), the HSM vendor's account, and speculation or points in dispute. When eMudhra publishes, the second and third sections will change, and assignments 12 and 14 may change with them.

## Established

These points come from Mozilla's staff and Chrome's root program in Bugzilla bug 2083449, from Google's post on Chrome's response, and from four outside reports (Scott Helme, Ryan Hurst, Cisco Talos and BleepingComputer). Where they overlap they agree, and each point below names its source.

### The keys

- Eight P-384 intermediate CA private keys were integers below 256. The values are 4, 56, 66, 115, 155, 156, 230 and 237. Dennis Jackson of Mozilla wrote "The 8 impacted keys all used integers less than 256" (Bugzilla comment 5), and Helme lists the same eight values.
- Six of the eight are TLS issuing CAs (DV, OV and EV, in two generations called G3B and G3C). Two are code-signing CAs (Helme, Talos).
- They come from a key generation ceremony on April 30, 2025 that produced 24 intermediates. All impacted keys are P-384 keys in series B and C. In comment 5, Jackson reported that the P-384 keys in series A and A-1 resisted recovery, and that he had not yet examined the RSA keys.
- The HSM mapping eMudhra posted puts series A on an Entrust nShield Connect XC and series B and C on a Utimaco Se-Series Gen2, so every weak key came from the Utimaco HSM (Hurst). Hurst ran cheap tests on the RSA keys from the same HSM and found nothing wrong with them. He adds that cheap tests prove nothing about how a key was generated.
- Sectigo cross-signed these keys under its AAA Certificate Services root in May 2025. Each key therefore appears in two certificates, 16 certificates for 8 keys (Helme; Wayne lists the eight cross-certificates in comment 2). A chain through a cross-certificate ends at AAA Certificate Services and never reaches eMudhra's root. Sectigo wrote that Chrome and Mozilla had already removed that root and that Microsoft and Apple still trusted it (comment 6), and it revoked the cross-certificates on October 19 (comment 13).

### How the keys were found

- CAs disclose every intermediate in CCADB, the database the browser root programs share, and these eight went in on May 10, 2025. On October 17, 2026, Wayne ran Google's [paranoid_crypto](https://github.com/google/paranoid_crypto) over the CA certificates in CCADB. Its test for EC private values that fit in 32 bits, public since June 2022, flagged the eight keys 27 minutes after he started (Hurst).
- Hurst repeated the search. He tested the EC key in each of the 10,313 CA certificates in CCADB for a private value below 65,536. After a one-time table build of under a minute, the scan took 0.3 seconds and returned the 16 certificates that carry the eight keys, with no false positives.
- Hurst cites Jackson's note that AI agents on Jackson's own machine recovered the keys on the first try when told the task was a capture-the-flag puzzle. eMudhra's statement says the researcher worked "reportedly with the help of AI-assisted tooling". This page found no source for that claim.

### Why the weakness is cheap to find

- Jackson says baby-step giant-step, or generating the first 256 P-384 keys, recovers the keys "near instantly". Helme computed 1G, 2G, 3G and so on until one matched the public key, at most 255 steps, and recovered the keys behind all 16 certificates in under a second.
- The public key for d = 4 is the point 4G, which lies on P-384 like any other point. Its encoding and curve membership check out. This follows from the arithmetic and none of the sources disputes it. Only recovering the private key, or testing the public key against small multiples of G, shows the weakness.
- Helme built a forged chain for `api.stripe.com` on a local test server. He reports that curl with default settings verified it, Python completed the handshake and Node reported `authorized: true`, with the same results on Linux and macOS. On Windows, the chain passed unless revocation checking was on.
- Helme also reports that most non-browser clients trust an on-disk CA bundle and do not check revocation or Certificate Transparency (CT) by default. He reports Chrome's observation that no TLS certificates chaining to these CAs appeared in CT logs, so browsers that require CT should not have accepted forgeries.

### The response

- On Saturday, October 17, a researcher who goes by Wayne reported the keys to Apple, Google, Microsoft, Mozilla and eMudhra (Helme; Bugzilla comment 2). Chrome blocked the intermediates that evening with a CRLSet update, and Mozilla blocked them a few hours later through OneCRL (Helme). Google's post puts the CRLSet update at 19:45 UTC and says it blocked the SPKI hashes of the affected intermediates, which covers every certificate that carries those keys. Wayne reports that CRLSet sequence 10843, fetched at 22:46 UTC, listed the six TLS keys as revoked (comment 2).
- Apple added protections on October 19 (BleepingComputer). Talos reports that Microsoft blocked the two code-signing certificates.
- eMudhra revoked all eight intermediates.
- Mozilla announced the emergency removal of trust in emSign ECC Root CA - G3, the root above these intermediates (Bugzilla comment 18). Chrome expects its root store change to land on October 27 (comment 30). Google's post says the removal is there to support consumers of the Chrome Root Store that do not consume CRLSet updates.
- Talos reports that Go released versions 1.27.3 and 1.26.10, which filter chains containing the SPKI hashes of the eight certificates, under CVE-2026-111943.
- Mozilla sent eMudhra written questions on October 20 and asked for a first answer within 24 hours. eMudhra asked for 24 more hours, and as of October 23 Mozilla had received no answer (comment 42). In comment 39, eMudhra wrote that social media and investor scrutiny had made meaningful analysis impossible so far. Chrome's root program replied that this scrutiny is no reason to delay the response (comment 41).
- On October 22, eMudhra announced that its board had decided to withdraw from the global SSL/TLS certificate business (eMudhra press release; The Register). The same day, Update 4 of its statement offered its customers Sectigo-issued certificates as an alternative.

### Exploitation

No public source reports evidence that anyone recovered or used the keys, and none shows that no one did. The keys existed from April 30, 2025 to October 17, 2026, about 17 months. Talos reported no malicious incidents involving the certificates as of October 21, 14:00 UTC. A forged certificate served only to clients that skip revocation and CT checks would leave no public trace, which is the gap Helme's report points at.

## What eMudhra says

Everything in this section is eMudhra's account, from its statement (updated October 22), its press release of October 22 and its comments in Bugzilla. No independent party has confirmed it.

- eMudhra says it generated the keys on Utimaco HSMs certified to FIPS 140-2 Level 3 (comments 10 and 11).
- Update 3 of its statement names the failed step: "The problem was a flaw in one step of the ceremony procedure, not the absence of HSMs. During the ceremony, a key wrap/unwrap step produced a second, weak set of keys alongside the original strong keys."
- In comment 11, eMudhra describes the cause in three pieces. First, "an approved deviation to our usual KGC to test a wrap/unwrap was introduced as these keys were meant for export for this instance". Second, "a flaw in the code resulted in the second pair of keys being created onboard which were weaker". Third, "these second pair of weaker keys were used by mistake to create the csr (because the key labels were similar)". It adds that a set of original ECC keys was "created onboard as expected".
- The same comment acknowledges human errors in more than one step, and eMudhra says it will re-verify all its ceremonies.
- On CRLs, eMudhra says "The CRL's were signed with the original private keys (which were supposed to be the correct keys with appropriate entropy)" and that "they were resigned with flawed keys".
- Its statement says one affected intermediate was in production, that it issued no end-entity certificates, and that the problem went undetected through two audit cycles. The Register quotes eMudhra saying the roots "have gone through independent audits for two years in a row".
- In comment 19, eMudhra estimates "about 30,000 certs that require migration and about 97% came via ACME". Chrome's root program (comment 30) counts about 30,800 unexpired precertificates in CT logs that chain to the root, and says two InCommon intermediates issued 99.9% of them.
- eMudhra says it has no evidence that anyone recovered or exploited the keys before disclosure.
- It says it has not confirmed the root cause and promises to publish it in full. Its press release repeats that it will deliver a full root-cause report while it leaves the TLS business.
- The press release says its G1 RSA roots will keep serving customers until they move, that it will replace their certificates free of cost through partners, and that revocation and certificate status services will run until every certificate it issued has expired or been replaced.

## What Utimaco says

Utimaco made the HSM that series B and C came from. It posted a statement on October 23, which is the vendor's account of its own product:

- Its HSMs generate EC private keys inside the module with approved random number generation, and give an application no way to request an EC private key with a value it chooses or with reduced entropy.
- It has found no defect in the HSM's random number generation or its onboard EC key generation.
- From what eMudhra has disclosed, it believes a scripting error created alternative keys and used them in place of the keys the HSM created. It says it is in contact with eMudhra about the script.

Neither eMudhra nor Utimaco has published the script.

## Speculation and disputed points

### Theories from public threads

Commenters on Hacker News (item 50166579) have offered several explanations: test keys used by accident, keys generated outside the HSM and imported, a truncation or indexing bug that kept one byte, an operator who misread the key range, and values typed by hand. None of these comes with evidence. One commenter countered that a truncation bug would give uniform random bytes, and that these values do not look uniform. Another argued that any single value, including 4, is as likely as any other, and others replied that eight keys all below 256 is implausible by chance.

### Standards-minded questions on Bugzilla

Thor Simon (comment 31) asks how a Level 3 HSM could produce such keys, and suggests either that the operators did not follow policy and loaded keys from outside, or that the HSM can be configured to produce them. Jacob Durham (comment 33) argues that a P-384 scalar below 256 implies supplied or imported key material, because an in-module generator would not produce one. Both are arguments from how generators behave, and neither is an established finding. Utimaco's statement (above) agrees with their premise for its own HSMs.

### Whether the CRL problem shares the cause

eMudhra's account links its invalid CRL signatures (Mozilla bug 1970728, June 2025) to the same key mix-up. Jackson cites an Internet Archive snapshot showing the six P-384 CRLs failing verification since May 23, 2025. He reports that eMudhra said it produced the faulty CRLs the same day it created the A-1 certificates, and writes that, if accurate, the mismatch has nothing to do with creating the A-1 series on May 29.

Ryan Hurst worked back from the signatures on the five distinct CRLs eMudhra attached to bug 1970728 to the public keys that could have made them. Each candidate verifies its signature, none has a small private value, and none matches the key in the CA's certificate or any key in the 10,313 CA certificates in CCADB. He concludes that in June 2025 each of these CAs had two keys on the HSM: a normal key that eMudhra's systems used, and the weak key the certificate named. eMudhra then re-signed the CRLs with the weak keys. Hurst's analysis supports the link between the two problems. Jackson's question about the dates is still open.

### Dates and counts that differ between sources

- Earlier versions of eMudhra's statement dated the report to October 18 and the revocation to October 19. Comment 35 pointed out that Mozilla's records give October 17 (the report reached Mozilla at 20:06 UTC) and October 18 (Jackson reports the revocation at 09:38 UTC). The statement now gives October 17 and October 18.
- eMudhra's statement says one intermediate was in production. The Register reports eMudhra saying most were not used in production. Wayne's comment 2 describes the CA that eMudhra names as the production one as live before eMudhra disabled it.
- Talos writes that the flaw "took the encryption from 384 bytes of entropy down to 3 – 8" and uses bits earlier in the same post. P-384 keys carry about 384 bits. The eight values need between 3 bits (the value 4) and 8 bits (the value 237), so the Talos figures read as bits, but the post does not say so.

### The audit question

Some commenters argue that CAs choose and pay their auditors, and that WebTrust does not require an auditor to attest that the HSM generated the keys. This page does not rely on those claims, and the WebTrust criteria and CA/Browser Forum Baseline Requirements text were not checked here. eMudhra's statement says the issue passed two audit cycles. Hurst reports that BDO's WebTrust report for June 2025 to May 2026 lists all eight intermediates in scope, names bug 1970728 as an Other Matter, says the auditor examined the disclosed root cause, and gives an unmodified opinion. The ceremony fell in the previous audit period, and Hurst could not find that report. Why the issue passed is an open question.

## Open questions

- Which key-creation call produced the second key pair, who approved the deviation, and whether an auditor observed the ceremony (Durham, comment 33).
- Where the weak scalars came from, given the argument, now shared by Utimaco, that an in-module generator would not produce them. Utimaco points at the ceremony script.
- The per-key records Durham requests under Baseline Requirements 6.1.1.1: the generation script, the ceremony report, the witness report or video, the HSM model and firmware, the CMVP certificate number, any custom firmware, and any imported or restored key material.
- Whether the RSA keys from the Utimaco HSM have the problem (Jackson, comment 5). Hurst's cheap tests found nothing.
- Whether the CRL signing failure and the weak keys share a cause, which Hurst's analysis supports, and how that fits Jackson's dates.
- eMudhra's answers to Mozilla's written questions of October 20, outstanding as of October 23 (comment 42).
- Chrome's twelve questions (comment 30), which include migration instructions, the ACME migration mechanism and metrics, Sectigo's notification, the replacement of series A, and why the second key pair was not caught after the 2025 CRL incident.
- Why CRL #11 for emSign Root TLS CA - G1, published October 14, 2026, carries a signature that verifies under no disclosed key (Wayne, comment 7).
- Whether anyone used the keys between April 30, 2025 and October 17, 2026.

## What this workbook teaches

The workbook teaches how to detect weak CA keys and what the response involves. It does not claim to explain how eMudhra's keys came to be weak.

| Assignment | What it covers | Relation to the incident |
|---|---|---|
| 01 to 09 | Modular arithmetic, elliptic curves, ECDSA, DER, certificates, SPKI hashes, chain validation | Background that every later assignment uses |
| 10 Find a weak private key | Recovering a private key below a bound by enumeration, for the key and its negation | Matches the established facts: values below 256, recovered in well under a second |
| 11 Sign with a weak key | What an attacker can do with a recovered CA key | Matches the established facts, and the forged-chain demonstration in Helme's report |
| 12 Generate and validate a key | Range and small-value checks on a private key before use, and rejection sampling | A model of correct generation and validation. The check flags values like the incident's; it makes no claim about how eMudhra's keys were generated |
| 13 Lint a public key | The check that finds a small private key before a CA trusts or publishes it | Matches the established facts: only trying to recover the key exposes it, and a test of this kind (paranoid_crypto) found the keys |
| 14 Check a key ceremony | Following a key's identity from generation to publication | A model of one possible failure shape, drawn from eMudhra's unconfirmed account and Utimaco's reading of it. It makes no claim about what happened |
| 15 Block and distrust | Blocking keys by SPKI hash and distrusting a root | Matches the established response by Mozilla, Chrome, Apple, Microsoft and Go |
| 16 Audit a PKI | Which chains break when a signing key leaks | The same question the response raised: which chains depend on each affected key |
| 17 Find a weak key in square-root time | Baby-step giant-step, which searches a bound of N in about the square root of N steps | Jackson names this method as one way to recover the keys |
| 18 Verify a revocation list's signature | Checking a CRL against its issuer's key, and halting the issuer when it fails | A detection practice. eMudhra ties its invalid CRL signatures to the same key mix-up, Hurst's analysis of the 2025 CRLs supports the link, and Jackson questions the dates |
| 19 Decide what each client accepts | Which clients still accept a chain, given their revocation, blocklist, bundle and CT settings | Matches Helme's report that several non-browser clients accepted a forged chain with default settings |

Assignments 12 and 14 teach concepts: how to draw and check a private key, and why a ceremony has to track which key each step produces. If eMudhra's published analysis describes a different failure, those two assignments still teach the same concepts as models, and their framing will change to match.

## Sources

Read on October 24, 2026.

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), updated October 22
- eMudhra, [eMudhra to Exit global SSL/TLS Certificate Business](https://emudhra.com/en/press-release/emudhra-to-exit-global-ssl-tls-certificate-business), press release, October 22
- Utimaco, [Compromised private keys in eMudhra certificates](https://utimaco.com/news/blog-posts/compromised-private-keys-emudhra-certificates), Kevin McKeogh, October 23
- Ryan Hurst, [The Private Key Was Four](https://unmitigatedrisk.com/2026/10/the-private-key-was-four/), October 22
- Google, [Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates](https://blog.google/security/protecting-chrome-and-android-users-from-compromised-emudhra-intermediate-ca-certificates/), Chrome and Android Security Teams, October 20
- Mozilla, [Bugzilla bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449), comments 0 to 42
- Mozilla, [Bugzilla bug 1970728](https://bugzilla.mozilla.org/show_bug.cgi?id=1970728), eMudhra invalid CRL signatures
- Scott Helme, [Eight bits of trust: eMudhra's CA keys cracked in milliseconds](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/)
- Cisco Talos, [Compromised intermediate certificates](https://blog.talosintelligence.com/compromised-intermediate-certificates/)
- The Register, [Certification authority eMudhra defends its laughably weak private keys](https://www.theregister.com/security/2026/10/22/certification-authority-emudhra-defends-its-laughably-weak-private-keys/5304647)
- BleepingComputer, [Mozilla, Google, Apple block compromised eMudhra CA certificates](https://www.bleepingcomputer.com/news/security/mozilla-google-apple-block-compromised-emudhra-ca-certificates/)
- Hacker News, [eMudhra intermediate CA compromise](https://news.ycombinator.com/item?id=50166579), commenter theories only
