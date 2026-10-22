# ======================================================================================
# Assignment 19: Decide what each client accepts
# Problem: problems/19-client-policy.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module decides, for one certificate chain and one client, whether the client
#   accepts it. A client is four switches: whether it holds the SPKI blocklist, whether
#   its root bundle is updated, how much of the chain it checks for revocation and whether
#   it requires Certificate Transparency. It reuses your `check_chain` from assignment 15
#   for the blocklist and the root distrust, and no later assignment uses it.
#
# Your job:
#   Write `decide` in `pki/client_policy.py`: given a chain with its certificate names,
#   one client's four switches and the facts read so far, return why the client rejects
#   the chain, or None when it accepts it. Call your `check_chain` from assignment 15
#   first, with only the sets this client holds, then check revocation and Certificate
#   Transparency (see The order of the checks).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
