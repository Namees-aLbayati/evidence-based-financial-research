# Architecture

## Application path

```text
React question form → POST /ask → evidence retrieval
                                 → model generation
                                 → Python calculations and validation
                                 → structured JSON → research report
```

FastAPI loads the pipeline once at startup. Cleaned source data and filing chunks determine the expected Chroma record IDs. Startup requires a matching local `.app_chroma` index. It does not build embeddings, optimize prompts, or run model judges.

The frontend displays the released answer, historical calculations, citations and limitations. Structural citation validity is not factual verification. Internal model drafts are filtered out of the API response.

## Repository boundaries

- `backend/`: application code and selected prompt/configuration artifacts.
- `frontend/`: React source and lockfile; compiled assets are served by FastAPI.
- `notebooks/`: research experiments retained for explanation and iteration.
- `tests/test_api.py`: isolated API contract checks for CI, with injected inference.
- `tests/test_integration.py`: local checks using the real dataset and index, without paid requests.
- `Financial_Dataset/`: supplied source and benchmark files. Benchmark answers do not enter the retrieval index.
- `docs/`: setup, architecture and screenshots.

## Operational limits

This is a local research prototype organized for maintenance, not an approved production financial service. Add authentication, request limits, controlled concurrency, monitoring, and a deployment-specific secrets/index strategy before hosting it for multiple users. Current caches are process-local/file-based; run one worker. Repaired source prices and historical periods require review.

CI builds the frontend and tests the API without paid calls. Passing CI does not establish financial accuracy, live provider access, or full deployment readiness. Live model quality needs separate human review and new evaluation examples.
