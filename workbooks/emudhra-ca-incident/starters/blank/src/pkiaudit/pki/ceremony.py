# ======================================================================================
# Assignment 14: Check a key ceremony
# Problem: problems/14-ceremony-checker.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It replays the log of a key generation ceremony and checks that each CSR carries the
#   public key the witnesses approved, identifying keys by fingerprint and never by label.
#   It flags labels that collide and deviations from the script. It needs none of your
#   earlier modules, and no later assignment uses it.
#
# Your job:
#   Write the ceremony state in `pki/ceremony.py`, which replays a key ceremony log one
#   step at a time: generate, approve, deviation, csr and publish. Identify each key by
#   its public-key fingerprint and never by its label, and let the priorities under Output
#   decide the line when several findings apply (see Identifying a key and Deviations).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
