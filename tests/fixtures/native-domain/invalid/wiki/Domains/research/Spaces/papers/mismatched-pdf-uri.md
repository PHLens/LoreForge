---
citekey: mismatched-pdf-uri
title: "Mismatched PDF URI"
aliases:
  - Mismatched PDF URI
authors: "Ada Lovelace"
date: "2026"
category: "Example"
keywords: []
conference: "ExampleConf"
link: "https://example.com/mismatch"
create_date: "2026-01-01"
zotero_link: "zotero://open-pdf/0_EXPECTED"
zotero_folder: []
abstract: "Example abstract."
tags: []
$version: 1
$libraryID: 1
$itemKey: MISMATCH
---

# Mismatched PDF URI

[PDF](zotero://open-pdf/0_OTHER)

## Summary

### What's the problem?

The body opens a different Zotero attachment than frontmatter.

### How does this paper solved it?

It does not.

### What's the improvements?

None.

## Strengths

Focused invalid fixture.

## Weakness

Mismatched PDF target.

## Detailed Comments

The body PDF link must equal `zotero_link`.

## Ideas for improvement(How Can I do better)

Use the same open-pdf URI in frontmatter and body.

## Lessons learned

Validation must compare the two URI values.
