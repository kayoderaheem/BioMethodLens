# Architecture

BioMethodLens separates judgment from orchestration so that each layer can be inspected and tested.

## Data flow

1. **Local ingestion** reads plain text, Markdown, or—when the optional dependency is installed—PDF text. The input hash is recorded.
2. **Deterministic routing** combines an author-supplied manuscript profile with explicit text cues. Universal safeguards always run. The selection and its reasons are visible before review.
3. **Prompt assembly** combines a fixed safety and evidence contract with one narrow specialist scope. Manuscript content is delimited and treated as untrusted data.
4. **Concurrent review** sends independent tasks through a provider interface. The worker limit is configurable.
5. **Validation** enforces the JSON contract and additional semantic rules. A result with a mismatched paper or reviewer ID is rejected.
6. **Conservative normalization** suppresses only exact semantic duplicates. Similar but distinct findings remain separate.
7. **Deterministic reporting** orders findings by severity and preserves their source evidence. A model is not used to rewrite the final report.
8. **Run manifest** records the input hash, routing mode, selected and completed lenses, and failures.

## Trust boundaries

```text
local-only                                      external when `review` is used

manuscript file ──► extraction ──► routing ──► provider request
                                           ◄── structured result
                         validation ◄──────────┘
                              │
                              ▼
                  local report and manifest
```

The current PDF reader extracts text but does not provide layout coordinates or OCR. Scanned PDFs should be converted carefully to reviewed text before use. BioMethodLens refuses inputs with too little extractable text instead of pretending the parse succeeded.

## Core modules

- `config.py`: registry loading and integrity checks
- `router.py`: transparent specialist selection
- `prompts.py`: bounded prompt construction
- `providers.py`: model-provider protocol and adapters
- `models.py`: result models and semantic validation
- `pipeline.py`: concurrency, isolation, and run manifests
- `report.py`: deduplication and deterministic Markdown output
- `io.py`: manuscript ingestion and hashing

## Failure behavior

One failed specialist does not erase successful results. Failures are listed in the run manifest, and completed reviews still produce a report. The run fails completely only if every selected specialist fails. This supports useful partial recovery while keeping missing coverage visible.

## Performance choices

- Independent specialists run concurrently with a bounded worker pool.
- The registry and schema are loaded once per pipeline.
- Each specialist result is written immediately after validation, limiting loss during interrupted runs.
- Report generation is linear in the number of findings.
- Exact deduplication is intentionally conservative; scientific distinctions are preferred over aggressive compression.

Model calls dominate runtime and cost. Use `plan` before `review`, choose `minimal` during early drafting, and reserve `conservative` for final audits.
