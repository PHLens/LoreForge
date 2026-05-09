---
name: loreforge-check
description: Internal LoreForge workflow for linting, auditing, and structural checks across LoreForge raw packages and native domains. Use when asked to lint, audit, validate, or review a wiki/domain.
user-invocable: false
version: 0.1.0
---

# LoreForge Check

Run a findings-first check on a LoreForge wiki or domain. This workflow
verifies raw package integrity, domain structure, links, provenance, and review
signals. It may use the validator bundled with `loreforge-domain`.

Always:

- resolve wiki/domain with `loreforge-config`
- inspect raw package integrity before domain provenance checks
- keep findings concrete with file paths
- separate blocking integrity issues from style or maintenance issues

## Checks

1. **Raw package integrity**
   - Flat capture-only files under `Shared/Raw/` are allowed.
   - For normalized `Shared/Raw/<source-id>/` packages, check that
     `origin.md` and `manifest.md` exist together.
   - Verify `content_hash` when present.
   - Verify local artifact pointers and `compiled_pages`.

2. **Native domain contract**
   - Prefer:

     ```bash
     python3 skills/loreforge-domain/scripts/validate_native_domain.py <domain-path>
     python3 skills/loreforge-domain/scripts/validate_native_domain.py --fix <domain-path>
     ```

   - `--fix` may remove orphan footnote definitions. Missing definitions still
     require manual repair.

3. **Links and provenance**
   - Broken `[[wikilinks]]`
   - Footnote markers without definitions
   - Footnote definitions without markers
   - Provenance pointing to non-existent raw manifests or domain source notes

4. **Domain quality**
   - Missing or stale index entries
   - Orphan pages with no inbound links
   - Pages over 200 lines
   - Tags not listed in `SCHEMA.md`
   - Pages with more than 3 tags
   - `confidence: low`, `contested: true`, or contradiction markers

5. **Log maintenance**
   - Newest-first order
   - More than 500 entries should trigger log rotation guidance

## Reporting

Report findings by severity:

1. Blocking data integrity or broken links
2. Domain boundary violations
3. Missing index/log/frontmatter
4. Provenance and confidence risks
5. Style and maintenance issues

If the user asked for a write-capable lint pass, insert a newest-first
`log.md` entry summarizing the check. Otherwise keep the check read-only.
