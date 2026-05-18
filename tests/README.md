# Tests

Run the native domain verification fixture:

```bash
python3 skills/loreforge-domain/scripts/validate_native_domain.py
python3 skills/loreforge-domain/scripts/validate_native_domain.py --fix /path/to/domain
python3 tests/test_loreforge_domain_footnote_convention.py
python3 tests/test_loreforge_domain_card_atlas_boundary.py
python3 tests/simulate_native_domain_operations.py
python3 tests/simulate_wiki_config_flow.py
python3 tests/simulate_loreforge_entrypoint_flow.py
```

These scripts check the minimum single-expert LoreForge domain contract used by
the `loreforge-domain` skill, check skill-level Markdown conventions, and
smoke-test query, ingest, and update boundaries on a temporary fixture copy.
They also smoke-test entrypoint routing, paper workflow delegation, config discovery, initialization, sync
backend setup for new and existing wikis, raw source packages under
`Shared/Raw/<source-id>/` with `origin.md` plus `manifest.md`, and source import
behavior. The native domain validator can also clean orphan footnote definitions
with `--fix`.
