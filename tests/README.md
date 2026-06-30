# Tests

Run the native domain verification fixture:

```bash
PYTHONPATH=lib python3 -m loreforge_validator
PYTHONPATH=lib python3 -m loreforge_validator --fix /path/to/domain
python3 skills/loreforge-domain/scripts/validate_native_domain.py
python3 skills/loreforge-domain/scripts/validate_native_domain.py --fix /path/to/domain
python3 tests/test_loreforge_domain_footnote_convention.py
python3 tests/test_loreforge_domain_card_atlas_boundary.py
python3 tests/test_loreforge_component_contract.py
node --test tests/loreforge_cli.test.mjs
python3 tests/simulate_native_domain_operations.py
python3 tests/simulate_wiki_config_flow.py
python3 tests/simulate_loreforge_entrypoint_flow.py
```

These scripts check the current root layout through component, CLI, entrypoint,
paper workflow, and documentation drift tests. The current layout uses
`Cards/<domain>/`, `Sources/Raw/<source-id>/`, `Sources/Papers/`, root
`Spaces/`, root `Atlas/`, and `Extras/Templates/`.

`simulate_native_domain_operations.py` and `simulate_wiki_config_flow.py` are
legacy compatibility smoke tests for the older `Domains/<domain>/` and
`Shared/Raw/` fixture shape. They should not be treated as the current layout
spec.

The native domain validator can also clean orphan footnote definitions with
`--fix`. The `validate_native_domain.py` command is a compatibility wrapper
around the shared `loreforge_validator` module.
