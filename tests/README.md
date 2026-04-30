# Tests

Run the native domain verification fixture:

```bash
python3 tests/validate_native_domain.py
python3 tests/simulate_native_domain_operations.py
python3 tests/simulate_wiki_config_flow.py
```

These scripts check the minimum single-expert LoreForge domain contract used by
the `loreforge-wiki` skill and smoke-test query, ingest, and update boundaries
on a temporary fixture copy. They also smoke-test wiki config discovery,
initialization, and source-only migration behavior.
