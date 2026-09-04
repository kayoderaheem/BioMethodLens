# BioMethodLens

**Evidence-linked specialist review for bioinformatics manuscripts.**

[![Tests](https://github.com/kayoderaheem/BioMethodLens/actions/workflows/tests.yml/badge.svg)](https://github.com/kayoderaheem/BioMethodLens/actions/workflows/tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2EA44F.svg)](LICENSE)

BioMethodLens turns one broad “review this paper” request into a transparent panel of focused scientific audits. Each lens examines a defined failure surface—such as patient leakage, pseudoreplication, spatial dependence, data provenance, omics quality control, or survival analysis—and returns structured findings tied to inspectable evidence.

It is built for manuscript **quality assurance before submission or revision**. It does not decide whether a paper should be accepted, and it does not replace domain experts, statisticians, journal reviewers, or clinical judgment.

## Why this exists

Computational biology papers often combine several methodological layers at once: cohort design, wet-lab assays, preprocessing, statistical inference, machine learning, biological interpretation, and reporting. A single general-purpose review prompt can miss interactions across those layers.

BioMethodLens separates the work:

```text
manuscript + study profile
          │
          ▼
 transparent router
          │
          ├── universal safeguards
          │     study design · provenance · statistics · reproducibility
          │     claim–evidence · biological interpretation · figures
          │
          └── relevant specialists
                omics QC · batch/integration · ML validation · benchmarking
                single-cell · spatial omics · bulk RNA-seq · multi-omics
                survival · clinical prediction · reporting guidelines
          │
          ▼
 schema + semantic validation
          │
          ▼
 conservative deduplication
          │
          ▼
 prioritized report + reproducibility manifest
```

The router records *why* every lens was selected. Every verified finding requires a manuscript excerpt, calculation, data artifact, or external source. Missing information is labeled `cannot_verify`; it is never silently invented.

## What makes it bioinformatics-specific

- **Biological units are first-class.** Donors, patients, sections, fields of view, samples, cells, spots, and technical replicates are not treated as interchangeable.
- **Leakage checks follow the data hierarchy.** The ML lens checks patient, replicate, tissue, drug, cell-line, and preprocessing leakage—not only train/test filenames.
- **Pseudoreplication is actively audited.** Large cell or spot counts do not erase a small donor count.
- **Spatial review understands dependence.** It checks neighborhood construction, autocorrelation, blocked validation, field-of-view structure, and tissue boundaries.
- **Evidence survives synthesis.** Report assembly is deterministic and preserves source anchors rather than asking another model to paraphrase them away.
- **The core is provider-neutral.** The orchestration and validation layers are standard-library Python. An OpenAI Responses API adapter is included, and another provider can implement one small interface.

## Quick start

### 1. Install

```bash
git clone https://github.com/kayoderaheem/BioMethodLens.git
cd BioMethodLens
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Add PDF support if needed:

```bash
python -m pip install -e '.[pdf]'
```

Plain text and Markdown work without third-party Python packages.

### 2. Verify the installation offline

```bash
python -m unittest discover -s tests -v
biomethodlens demo examples/synthetic-spatial-study/manuscript.txt \
  --modalities spatial-transcriptomics \
  --study-types prediction
```

The demo exercises routing, concurrent execution, validation, report assembly, and manifest creation without sending data to an external service.

### 3. Preview reviewer selection

```bash
biomethodlens plan manuscript.pdf \
  --modalities scrna-seq,spatial-transcriptomics \
  --study-types prediction,benchmarking
```

`plan` is local. It lets you inspect the active panel before any external model request.

### 4. Run a model-backed review

Set your API key without placing it in a tracked file:

```bash
export OPENAI_API_KEY="your-key"
```

Then run:

```bash
biomethodlens review manuscript.pdf \
  --model gpt-5.2 \
  --modalities scrna-seq,spatial-transcriptomics \
  --study-types prediction,benchmarking \
  --routing balanced \
  --workers 4
```

Use a model available to your account. Output is written under `runs/<paper-id>/`:

```text
runs/<paper-id>/
├── report.md
├── run_manifest.json
└── reviews/
    ├── study_design.json
    ├── statistical_inference.json
    └── ...
```

## Routing modes

| Mode | Behavior | Good use |
|---|---|---|
| `minimal` | Universal lenses plus explicit profile matches | Fast early drafting |
| `balanced` | Universal lenses plus explicit matches and strong text cues | Recommended default |
| `conservative` | Every enabled lens | Final pre-submission audit |

Passing an explicit study profile is strongly recommended. Text routing is a safeguard, not a replacement for author knowledge.

## Specialist catalog

| Lens | Main questions |
|---|---|
| Study design | Are cohorts, controls, experimental units, and replication valid? |
| Data provenance | Can every sample and data transformation be traced? |
| Statistical inference | Are independence, uncertainty, multiplicity, and effect sizes handled correctly? |
| Reproducibility | Can another group recreate the analysis? |
| Claim–evidence | Do conclusions match the actual evidence and scope? |
| Biological interpretation | Are mechanisms and pathways interpreted with appropriate restraint? |
| Figures and reporting | Are denominators, uncertainty, labels, and visual encodings honest and clear? |
| Omics QC | Are raw-data QC, filtering, normalization, and references appropriate? |
| Batch and integration | Is technical correction separated from biological signal? |
| ML validation | Are splits leakage-free, nested when needed, calibrated, and externally tested? |
| Benchmarking | Are baselines, tuning budgets, metrics, and ablations fair? |
| Single-cell | Are donor replication, ambient RNA, doublets, annotation, and pseudobulk handled? |
| Spatial omics | Are spatial dependence, graphs, tissue boundaries, and blocked validation handled? |
| Bulk transcriptomics | Are count modeling, normalization, contrasts, and composition addressed? |
| Multi-omics | Are modality alignment, missingness, dominance, and integration validated? |
| Survival analysis | Are time origin, censoring, assumptions, calibration, and optimism handled? |
| Clinical prediction | Is the model useful, calibrated, transportable, and compared fairly? |
| Reporting guidelines | Are relevant biomedical reporting requirements covered? |

The complete machine-readable registry is in [`config/reviewers.json`](config/reviewers.json). Each scope prompt lives in [`prompts/reviewers/`](prompts/reviewers/).

## Evidence and severity contract

Each finding includes:

- a stable ID, category, severity, and confidence;
- the manuscript claim and location under review;
- one or more traceable evidence objects when verified;
- a concise scientific rationale and likely impact;
- a specific recommended action; and
- an explicit verification state.

Severity reflects potential effect on conclusions:

- `critical`: likely invalidates a central result or creates a serious ethical/data-integrity risk;
- `major`: could materially change a primary conclusion;
- `moderate`: limits robustness, interpretation, or reproducibility;
- `minor`: improves clarity or completeness without changing the main conclusion.

The JSON Schema is in [`schemas/review_result.schema.json`](schemas/review_result.schema.json). BioMethodLens adds semantic checks that JSON Schema alone cannot express, such as rejecting “verified” findings with no evidence.

## Privacy and responsible use

`plan`, `demo`, and `validate` are local. `review` sends extracted manuscript text to the selected model provider. Do not submit confidential, embargoed, identifiable, controlled-access, or otherwise restricted material unless you have authorization and the provider’s terms satisfy your obligations.

Generated reports can be wrong. Verify every high-impact finding against the manuscript, raw data, code, and appropriate domain expertise before acting on it. See [`SECURITY.md`](SECURITY.md) and [`docs/responsible_use.md`](docs/responsible_use.md).

## Extend BioMethodLens

A new lens requires one registry entry and one focused prompt. No orchestration changes are needed when the existing output contract is sufficient. The extension guide includes a checklist and test expectations: [`docs/extension_guide.md`](docs/extension_guide.md).

Provider adapters implement the `ReviewProvider` protocol in [`src/biomethodlens/providers.py`](src/biomethodlens/providers.py). Keep credentials outside code and return the same validated result shape.

## Project status

BioMethodLens is an alpha research tool. Version 0.1 provides the review framework, deterministic routing, specialist scopes, validation, concurrent execution, offline demonstration, and report generation. Planned work includes layout-aware PDF evidence anchors, blinded benchmark evaluation, additional assay specialists, and community-reviewed reporting-guideline packs.

## Contributing and citation

Contributions from bioinformaticians, biostatisticians, bench scientists, clinicians, journal editors, and research-software engineers are welcome. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md).

If you use BioMethodLens in research, cite the software metadata in [`CITATION.cff`](CITATION.cff).

## Inspiration and independence

BioMethodLens was inspired by the multi-reviewer architecture of [Ingar30/reviewer](https://github.com/Ingar30/reviewer). This repository is an original bioinformatics-focused implementation with its own name, routing system, evidence contract, specialist roster, provider interface, report builder, examples, tests, and documentation. It is not an affiliated project and does not copy the upstream codebase.

## License

MIT © 2026 Kayode Raheem. See [`LICENSE`](LICENSE).
