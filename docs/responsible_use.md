# Responsible use

BioMethodLens is an author-support and research-quality-assurance tool. It is not an autonomous peer reviewer, a misconduct detector, or a clinical decision system.

## Required human checks

- Verify every quoted location and excerpt against the source manuscript.
- Recompute important numerical concerns from code or data when available.
- Ask a domain expert to review biological and clinical interpretations.
- Ask a statistician to review high-impact design or inference concerns.
- Treat `cannot_verify` as a request for evidence, not proof of an error.
- Do not use a generated score or finding count as an acceptance decision.

## Confidentiality

Planning, offline demonstrations, validation, and report assembly are local. Model-backed review sends extracted manuscript text to the configured provider. Before doing that, confirm that submission terms, collaborator agreements, patient privacy obligations, data-use agreements, and institutional policies allow the transfer.

Remove direct identifiers and unnecessary sensitive details. Do not place credentials in configuration files, command history, reports, issues, or commits.

## Bias and scope

Automated review may favor familiar methods, common terminology, English-language reporting conventions, and well-represented research areas. A method being unusual is not evidence that it is wrong. Specialist prompts are public so researchers can inspect and challenge the assumptions encoded in them.

## Reporting use of the tool

If BioMethodLens materially shapes a manuscript or formal review, follow the relevant journal or institutional policy on disclosing AI-assisted work. Human authors and reviewers remain responsible for the final content.
