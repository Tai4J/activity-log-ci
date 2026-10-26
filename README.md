# activity-log

Small Python CLI that summarises a CSV of activities. Used as the sandbox for the
CI collaboration & merge-style experiments.

```bash
pip install -e ".[dev]"
pytest
python -m activity_log.cli data/log.csv
```

## Contributing

- Never push to `main`; branch → PR → green CI → merge.
- After cloning, run `./scripts/install-hooks.sh` (pre-push guard + `git rerere`).
- CI: ruff lint/format → pytest on Python 3.10/3.11/3.12 → build. The required check is **ci-passed**.
