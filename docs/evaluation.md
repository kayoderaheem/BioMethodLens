# Evaluation strategy

The framework should be evaluated as a scientific instrument, not by how persuasive its prose sounds.

## Current automated checks

- registry integrity and prompt coverage;
- explicit and keyword-based reviewer routing;
- conservative full-panel routing;
- evidence and confidence consistency;
- reviewer and paper identity checks;
- deterministic severity ordering and duplicate handling;
- end-to-end offline artifact generation.

## Recommended benchmark design

Create a blinded corpus of public or author-approved manuscripts with expert-annotated issues. Include clean controls, ambiguous reporting, and realistic injected defects. Stratify by assay, biological domain, study design, paper length, and journal style.

Measure:

- finding-level precision and recall;
- critical and major issue recall;
- false-positive burden per manuscript;
- source-location accuracy;
- severity and confidence calibration;
- inter-expert agreement and model-versus-expert disagreement;
- reviewer-routing recall;
- run-to-run stability;
- cost and latency; and
- performance across underrepresented diseases, populations, organisms, and assays.

Do not tune and report on the same manuscript set. Freeze prompts and routing configuration before the final evaluation, preserve model versions, and publish uncertainty around metrics.

## Release gate for stronger claims

BioMethodLens should not claim that it improves peer-review accuracy until a preregistered or otherwise prospectively frozen evaluation demonstrates benefit on held-out manuscripts. User testimonials and attractive examples are useful for usability, not scientific validation.
