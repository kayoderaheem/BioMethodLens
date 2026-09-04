# Extension guide

BioMethodLens is designed so a research group can add a method-specific lens without changing the pipeline.

## Add a specialist

1. Choose a unique snake-case ID that describes a scientific scope rather than a person or model.
2. Add one entry to `config/reviewers.json`.
3. Add the referenced Markdown prompt under `prompts/reviewers/`.
4. Set `mandatory: true` only for a safeguard that applies to nearly every bioinformatics manuscript.
5. Add precise modality and study-type tags. Keywords should be distinctive phrases, not broad words such as “data.”
6. Add a routing test and at least one semantic-validation fixture.
7. Run the full offline test suite and demonstration.

A specialist prompt should define what to inspect, common failure modes, and the boundaries of its authority. It should not repeat the shared evidence contract, instruct the model to judge acceptance, or claim that missing reporting proves missing work.

## Add a provider

Implement the `ReviewProvider.review(...)` protocol in `src/biomethodlens/providers.py`. The adapter receives the specialist metadata, paper ID, complete prompt, and result schema. It must return a dictionary; the pipeline validates it before writing anything.

Provider adapters should:

- read credentials from the environment or a secure secret store;
- use the provider’s strongest available structured-output feature;
- expose model choice rather than silently changing it;
- avoid logging manuscript text or credentials;
- make storage and retention behavior explicit; and
- raise a clear error when output cannot be parsed.

## Change the result contract

Update all of the following together:

- `schemas/review_result.schema.json`
- models and semantic checks in `src/biomethodlens/models.py`
- the deterministic report builder
- provider fixtures and tests
- documentation and the example result

Schema validity is necessary but not sufficient. Keep cross-field rules in the semantic validator—for example, verified findings require evidence and unverifiable findings cannot claim high confidence.

## Add an assay pack

For a new assay, prefer a narrow specialist plus explicit routing metadata. Examples include long-read sequencing, metagenomics, digital pathology, CRISPR screens, or mass-spectrometry proteomics. Include domain reviewers in the pull request so prompts reflect real failure modes rather than only vocabulary.

## Compatibility expectations

Breaking schema or CLI changes require a major release. New optional lenses, keywords, and documentation can be minor releases. Correcting prompts without changing their scope can be patch releases.
