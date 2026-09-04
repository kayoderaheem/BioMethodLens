# Synthetic spatial-study example

This deliberately imperfect miniature manuscript is fictional and contains no patient data. It exists to exercise routing and demonstrate the shape of a BioMethodLens report.

Run locally:

```bash
biomethodlens plan examples/synthetic-spatial-study/manuscript.txt \
  --modalities spatial-transcriptomics \
  --study-types prediction,benchmarking

biomethodlens demo examples/synthetic-spatial-study/manuscript.txt \
  --modalities spatial-transcriptomics \
  --study-types prediction,benchmarking \
  --output-dir examples/synthetic-spatial-study/generated
```

The offline provider intentionally returns two example findings: patient-level validation is not established, and random spot splitting may leak spatial information. It does not perform a real scientific review.
