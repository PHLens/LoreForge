# Tests

Run the native domain verification fixture:

```bash
python3 skills/loreforge-wiki/scripts/validate_native_domain.py
python3 skills/loreforge-wiki/scripts/validate_native_domain.py --fix /path/to/domain
python3 tests/simulate_native_domain_operations.py
python3 tests/simulate_wiki_config_flow.py
python3 tests/simulate_router_flow.py
```

These scripts check the minimum single-expert LoreForge domain contract used by
the `loreforge-wiki` skill and smoke-test capture, query, ingest, and update
boundaries on a temporary fixture copy. They also smoke-test wiki config
discovery, initialization, flat raw clip capture under `Shared/Raw/`, ingest
normalization into `Shared/Raw/<source-id>/origin.md` plus `manifest.md`,
source migration behavior, and router domain-selection/delegation behavior. The
native domain validator can also clean orphan footnote definitions with `--fix`.
