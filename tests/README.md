# Tests

Run focused shell regressions from the repository root:

```bash
bash tests/setup/run.sh
bash tests/lint/run.sh
```

`tests/setup/run.sh` verifies binding setup, runtime state creation, registry output, and native starter creation.

`tests/lint/run.sh` verifies protocol lint for generic bindings and native lint for the native starter template.
