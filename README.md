# Evidence-Based Financial Research

A financial research application built with **React, FastAPI, and retrieval-augmented generation (RAG)**. It answers questions using supplied news, historical prices, and company filings, with Python calculations, source citations, and explicit evidence limitations.

The application runs Python modules. The [research notebook](notebooks/README.md) is retained separately to document experiments, prompt optimization, and evaluation.

## How it works

```text
Question → Retrieve source evidence → Generate an answer
                                   → Calculate supported figures
                                   → Validate citations and coverage
                                   → Display a research report
```

- Retrieve relevant records from a persisted Chroma index.
- Calculate supported historical price changes and financial growth in Python.
- Release an answer with `answered`, `partial`, or `insufficient_evidence` status.
- Display source records, reporting periods, and limitations alongside the analysis.
- Explain prior notebook evaluations separately from checks on the current answer.

## Repository structure

```text
backend/                FastAPI application, inference, and selected artifacts
frontend/               React source, dependency lockfile, and Vite build
notebooks/              Research notebook and experiment notes
tests/                  Isolated API checks and local integration tests
docs/                   Architecture, setup, and screenshots
Financial_Dataset/      Supplied historical source data and benchmark
.github/workflows/      Automated frontend build and API checks
```

See [architecture](docs/ARCHITECTURE.md) and [setup details](APP_SETUP.md).

## Quick start

Use **Python 3.13** and **Node.js 22**. Run commands from the repository root.

### 1. Install and configure

```bash
git clone https://github.com/Namees-aLbayati/evidence-based-financial-research.git
cd evidence-based-financial-research
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-app.txt
cp .env.example .env
```

Edit `.env` with your model API key and provider base URL. Keep real credentials out of Git. If you already have a local `.env`, keep it instead of copying the example over it.

### 2. Prepare the index

The vector index is excluded from Git. A new clone needs an index before normal startup:

```bash
python -m backend.prepare_index --allow-api-calls
```

This uses the configured embedding API and may incur charges for missing records. It resumes saved batches. **Existing local installations with a matching `.app_chroma` can skip this step.** The application does not automatically rebuild the index when starting.

### 3. Build and run

```bash
npm ci --prefix frontend
npm run build --prefix frontend
python -m uvicorn backend.main:app --reload
```

Open **http://127.0.0.1:8000/**. Enter a question or select an example, then click **Generate report**. Keep the server terminal running; stop it with **Ctrl+C**.

- API documentation: http://127.0.0.1:8000/docs
- Local readiness check: http://127.0.0.1:8000/health

Real questions may incur embedding and model charges. Health checks do not verify provider access. `--reload` is for local development.

## API example

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"How did Apple perform?"}'
```

The response contains `question`, `answer`, `status`, `sources`, `limitations`, `coverage_notes`, `citation_labels_valid`, and `cache_hit`. Show sources and limitations together with the answer. A `partial` response is a valid outcome when the evidence supports only part of the request.

## Development and tests

```bash
python -m pip install -r requirements-dev.txt
# API checks: no credentials, vector index, or paid requests required.
python -m unittest tests.test_api -v
# Local integration: requires configured .env, source files, and matching index.
python -m unittest tests.test_integration -v
```

For automatic frontend refresh, keep FastAPI running and run `npm run dev --prefix frontend` in another terminal. Open the Vite URL under `/ui/`. Requests are forwarded to FastAPI on port 8000. Rebuild the frontend to update the version served by FastAPI.

GitHub Actions builds React and runs isolated API checks on pushes and pull requests. Integration tests and model-quality evaluations are separate. No credentials are needed for CI.

## Research and evaluation

The [cleaned notebook](notebooks/project2_UTAIGA_Project_2_Full_Code_Notebook_cleaned.ipynb) preserves data preparation, RAG experiments, GEPA prompt optimization, and evaluation work. Changes to it do not automatically change the application. See [notebook notes](notebooks/README.md) before rerunning it.

Selected prompt/configuration and compact evaluation evidence live in `backend/artifacts/`. Recorded metrics are model-judge estimates from a prior notebook run, not accuracy percentages or confidence scores for current answers. The small held-out set was inspected previously. The latest saved notebook run stopped during optimization; relocation and path edits have not been verified by a full paid rerun.

## Scope and limits

This is a research prototype with historical data, not a live market feed. Numerical calculations currently cover Apple, Amazon, Alphabet, and Bitcoin. Citation-label checks assess structure and do not prove factual support. Review source claims, reporting periods, and repaired price data before relying on an answer.

A public multi-user deployment additionally needs authentication, request limits, monitoring, and an appropriate secrets/index/cache strategy. Run one backend worker for this local implementation. See [architecture and operational limits](docs/ARCHITECTURE.md).

## App screenshots

Screenshots from a local run of the React app and FastAPI backend.

### Research workspace

The homepage introduces the RAG workflow: set a question, retrieve evidence, generate and check, then review the report.

![Research workspace with RAG workflow](docs/screenshots/homepage.png)

### Question input

Users can write a question or select an example, then generate a research report.

![Question input and report generation](docs/screenshots/question-input.png)

### Answer and analysis

The Amazon example shows a partial-answer status, historical price calculations, reporting dates, and a cited news-sentiment finding.

![Research report overview and historical price calculation](docs/screenshots/answer-analysis.png)

### Sources and limitations

The report separates source-supported observations from uncertainty and provides the retrieved source records for review.

![Detailed analysis, limitations, and source records](docs/screenshots/sources-and-limitations.png)

### Evaluation

The expanded section explains answer checks and displays prior notebook evaluation scores. These are model-judge estimates, not accuracy percentages or live confidence scores.

![Evaluation criteria and recorded notebook results](docs/screenshots/evaluation.png)

### FastAPI documentation

Interactive API documentation exposes the health and question endpoints for development and testing. This screenshot shows the documented endpoints, rather than an executed health response.

![FastAPI interactive endpoint documentation](docs/screenshots/api-docs.png)

For updating these images, see the [screenshot guide](docs/SCREENSHOT_GUIDE.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow. Keep notebooks as research artifacts and promote reviewed application behavior into Python modules.
