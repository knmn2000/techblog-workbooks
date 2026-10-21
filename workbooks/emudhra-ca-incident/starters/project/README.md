# pkiaudit

`pkiaudit` audits a small public-key infrastructure. It reads a file of trust anchors,
certificates, chains and known-compromised keys, then reports which keys are weak or bad, which
chains a verifier would trust, and which chains each signing key could break if it leaked.

You build it one assignment at a time in the workbook *Build a PKI auditor yourself*, which
starts from eMudhra's
[statement on a certificate security incident](https://emudhra.com/en/post/certificate-security-incident).

## Install and run

Needs Python 3.10 or newer, and nothing outside the standard library. Install the package in
editable mode, so your changes take effect without reinstalling:

```
pip install -e .
pkiaudit audit examples/sample.pki
```

To run it without installing, put `src/` on the import path:

```
PYTHONPATH=src python -m pkiaudit audit examples/sample.pki
```

In PowerShell, set the path with `$env:PYTHONPATH = "src"` first.

## How it's organised

| Where | What |
|---|---|
| `src/pkiaudit/ecc/` | Elliptic-curve maths: modular arithmetic, adding and multiplying points, the named curves, ECDSA signing and verifying, and key generation |
| `src/pkiaudit/asn1/` | Reading DER, the binary encoding certificates use |
| `src/pkiaudit/x509/` | Certificates: their fields, the hash of their public key, and checking their signatures |
| `src/pkiaudit/pki/` | Decisions about a whole PKI: validating chains, linting keys, checking a key ceremony, distrust, and the audit |
| `src/pkiaudit/attack/` | Recovering a private key that was generated too small |
| `src/pkiaudit/__main__.py` | The `pkiaudit audit` command |
| `examples/` | A sample PKI to audit |
| `assignments/` | One small program per step, each checking that step against test cases |
