---
citekey: bad-pdf-link
title: "Bad PDF Link"
aliases:
  - Bad PDF Link
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/bad-pdf-link"
create_date: "2026-01-01"
zotero_link: "zotero://select/library/items/BADPDF"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: BADPDF
---

# Bad PDF Link

[[bad-pdf-link - Bad PDF Link.pdf|PDF]]

zotero://select/library/items/BADPDF

## Summary

### What's the problem?

This note has paper metadata but no valid Zotero PDF jump link.

### How does this paper solved it?

It uses an invalid link shape.

### What's the improvements?

No improvement.

## Strengths

Focused invalid fixture.

## Weakness

Invalid PDF link.

## Detailed Comments

The body includes an old wiki-local PDF link and a bare Zotero URI, but no
`[PDF](zotero://open-pdf/...)` link.

## Ideas for improvement(How Can I do better)

Use the Zotero open-pdf URI.

## Lessons learned

PDF jump-link validation must check the body link shape.
