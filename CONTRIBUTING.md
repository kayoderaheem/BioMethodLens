# Contributing

Thank you for helping make bioinformatics review more rigorous and transparent.

## Good contributions

- failure modes grounded in published methods or expert practice;
- new assay-specific lenses with clear boundaries;
- synthetic regression fixtures that contain no confidential manuscript text;
- safer ingestion, validation, and privacy behavior;
- benchmark design and blinded evaluation tools; and
- clearer documentation for researchers with limited programming experience.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
```

Before opening a pull request, also run the offline demonstration from the README and confirm that no manuscript, generated review, credential, or sensitive filename is staged.

## Pull requests

Explain the scientific failure mode being addressed, the evidence supporting the checklist, routing changes, privacy impact, and tests. Keep prompts narrow. New clinical or assay-specific lenses should be reviewed by someone with relevant expertise.

By contributing, you agree that your contribution is licensed under the MIT License.
