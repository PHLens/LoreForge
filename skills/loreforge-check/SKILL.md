---
name: loreforge-check
description: Internal LoreForge workflow for linting, auditing, and structural checks across LoreForge raw packages and native domains. Use when asked to lint, audit, validate, or review a wiki/domain.
user-invocable: false
version: 0.2.0
---

# LoreForge Check

Run a findings-first check on a LoreForge wiki or domain. This workflow
verifies raw package integrity, domain structure, links, provenance, and review
signals. It may use the shared Python `loreforge_validator` module through the
CLI or compatibility wrapper.

Always:

- resolve wiki/domain with `loreforge-config`
- inspect raw package integrity before domain provenance checks
- skip `90-Legacy/` and other legacy imports as validation targets
- keep findings concrete with file paths
- separate blocking integrity issues from style or maintenance issues

## Checks

1. **Raw package integrity**
   - `Shared/Raw/` entries should be source package directories.
   - Each `Shared/Raw/<source-id>/` package must include `origin.md` and
     `manifest.md` together.
   - Verify `content_hash` when present.
   - Verify local artifact pointers and `compiled_pages`.

2. **Zotero paper note format**
   - Validate existing notes at `Domains/research/Spaces/papers/<citekey>.md`.
   - Require Zotero paper-note frontmatter fields: `citekey`, `title`,
     `aliases`, `authors`, `date`, `category`, `keywords`, `conference`,
     `link`, `create_date`, `zotero_link`, `zotero_folder`, `abstract`,
     `tags`, `$version`, `$libraryID`, and `$itemKey`.
   - Require `zotero_link` to contain a `zotero://open-pdf/...` URI and require
     the paper body to include a Zotero PDF jump link such as
     `[PDF](zotero://open-pdf/...)`.
   - Require the paper reading template:
     `Summary` with `What's the problem?`, `How does this paper solved it?`,
     and `What's the improvements?`, followed by `Strengths`,
     `Weakness`, `Detailed Comments`, `Ideas for improvement(How Can I do
     better)`, and `Lessons learned`.
   - Do not require every Zotero item to have a note; only validate Markdown
     notes that already exist.

3. **Native domain contract**
   - Prefer:

     ```bash
     PYTHONPATH=lib python3 -m loreforge_validator <domain-path>
     PYTHONPATH=lib python3 -m loreforge_validator --fix <domain-path>
     ```

   - The compatibility wrapper remains valid for older workflows:

     ```bash
     python3 skills/loreforge-domain/scripts/validate_native_domain.py <domain-path>
     python3 skills/loreforge-domain/scripts/validate_native_domain.py --fix <domain-path>
     ```

   - `--fix` may remove orphan footnote definitions. Missing definitions still
     require manual repair.

4. **Links and provenance**
   - Broken `[[wikilinks]]`
   - Footnote markers without definitions
   - Footnote definitions without markers
   - Provenance pointing to non-existent raw manifests or domain source notes
   - Path-qualified links into `90-Legacy/` are ignored by validation because
     legacy imports are not active LoreForge pages.

5. **Domain quality**
   - Missing or stale index entries
   - Orphan pages with no inbound links
   - Pages over 200 lines
   - Tags not listed in `SCHEMA.md`
   - Pages with more than 3 tags
   - `confidence: low`, `contested: true`, or contradiction markers

6. **Log maintenance**
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
