# ======================================================================================
# Assignment 14: Check a key ceremony
# Problem: problems/14-ceremony-checker.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It replays the log of a key generation ceremony and follows each key from the step
#   that made it to the step that publishes it, so a reused label or a key that changed on
#   the way gets flagged. It needs none of your earlier modules, and no later assignment
#   uses it.
#
# Your job:
#   Write the ceremony state in `pki/ceremony.py`, which replays a key ceremony log one
#   step at a time: generate, wrap, unwrap, fingerprint and publish. Give every generate
#   step a new key identity, even when it reuses a label, and let wrap and unwrap pass the
#   identity a label names on to another label. A publish reports `ok`, `undefined`, or a
#   mismatch with the label the key was generated under (see Chains of custody).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
