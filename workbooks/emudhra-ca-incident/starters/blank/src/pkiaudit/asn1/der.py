# ======================================================================================
# Assignment 05: Read DER
# Problem: problems/05-der-reader.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module reads DER, the tag-length-value encoding that holds every certificate in
#   the project, into a tree of nodes, and decodes INTEGER, OBJECT IDENTIFIER and BIT
#   STRING values. Your `x509/certificate.py` (assignment 06), `x509/spki.py` (07) and
#   `x509/signature.py` (08) read certificates through it.
#
# Your job:
#   Write a DER reader in `asn1/der.py` that turns bytes into a tree of tag-length-value
#   nodes, each with its class, constructed bit, tag number, length, content bytes,
#   children and depth. Read both length forms, and have each node record where it starts
#   in the buffer and how many bytes it takes with its header, for assignments 07 and 08.
#   Add decoders for INTEGER, OBJECT IDENTIFIER and BIT STRING content, as "Decoding each
#   type's content" describes.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
