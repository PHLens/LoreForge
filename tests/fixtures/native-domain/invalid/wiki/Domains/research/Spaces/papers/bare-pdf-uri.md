---
citekey: bare-pdf-uri
title: "Bare PDF URI"
aliases:
  - Bare PDF URI
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/bare"
create_date: "2026-01-01"
zotero_link: "zotero://open-pdf/0_BAREPDF"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: BAREPDF
---

# Bare PDF URI

zotero://open-pdf/0_BAREPDF

## Summary

### What's the problem?

The body has a bare Zotero PDF URI but no Markdown PDF link.

### How does this paper solved it?

It does not.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Missing Markdown PDF link.

## Detailed Comments

The frontmatter URI is valid, but the body link contract is not satisfied.

## Ideas for improvement(How Can I do better)

Use `[PDF](zotero://open-pdf/...)`.

## Lessons learned

Validation must require the Markdown PDF link shape.
