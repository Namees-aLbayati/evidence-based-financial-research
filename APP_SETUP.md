# Run your notebook logic as an API

FastAPI is the web layer. `backend/pipeline.py` contains the notebook's extracted search, calculations, generation and validation logic. The notebook remains unchanged. No notebook or benchmark executes on a question request.

## Start

From this project folder:

```bash
source .venv/bin/activate
pip install -r requirements-app.txt
python -m uvicorn backend.main:app --reload
```

Keep the existing `OPENAI_API_KEY` and `OPENAI_BASE_URL` in your project `.env`. They stay on the backend. Existing shell settings take precedence over `.env`.

Open http://127.0.0.1:8000/docs. Expand **POST /ask**, click **Try it out**, enter this JSON, and click **Execute**:

```json
{"question": "How did Apple's stock price change?"}
```

Sending a real question can make paid embedding and model calls. Startup only loads local data and the existing index. `GET /health` checks local startup readiness, not upstream API access.

## Connect your app

Call the backend from your frontend's submit handler:

```javascript
async function askQuestion(question) {
  const response = await fetch("http://127.0.0.1:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || "Request failed");
  return result;
}

// In your existing button handler:
// const result = await askQuestion(questionInput.value);
// answerElement.textContent = result.answer;
```

The result contains `answer`, `status`, `sources`, `limitations`, `coverage_notes`, `citation_labels_valid`, `cache_hit`, and `question`. Show sources and limitations alongside the answer. `partial` means some requested information is unsupported. Citation-label validity is a structural check, not a factual guarantee. Render model text safely; do not insert it as raw HTML.

By default, CORS allows frontends at `http://localhost:3000` and `http://localhost:5173`. If your app uses another address, add its exact origin to `.env`, then restart:

```dotenv
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:5173
```

CORS is a browser permission, not authentication. This backend is intended for local development. Add authentication and request/rate limits before exposing it publicly. A deployed frontend needs a reachable backend URL instead of localhost.

## What is loaded

- Cleaned CSVs and filing text in `Financial_Dataset/Financial_Dataset`.
- Separate fingerprint-matched collection in `.app_chroma`, recovered from existing saved vectors.
- Prompt and configuration retained in `backend/artifacts` from a prior notebook selection. This is a saved prior selection; the latest notebook run stopped during optimization, so these are not newly verified results from that run.
- Separate answer/query caches in `.app_cache`, leaving notebook result files separate.

Questions are serialized within one server process to protect the notebook's shared caches. Run one worker for this local prototype. Dataset-relative dates, entity coverage and calculation limitations are inherited from the notebook; this is historical research, not a live market feed.

## Tests

```bash
python -m unittest tests.test_integration -v
```

Tests use real local startup/data and stub paid answer calls. They do not establish live API access or answer quality.

## Index preparation

The app uses `.app_chroma`, containing 10,320 expected source records. Keep this folder when copying the local project. The older notebook indexes and experiment history were removed during cleanup.

If this index is missing or source data changes, explicitly build/resume it:

```bash
python -m backend.prepare_index --allow-api-calls
```

This can incur embedding API charges for missing records. Normal app startup does not build an index or run benchmarks.

## Retained notebook and evaluation evidence

The current notebook is `notebooks/project2_UTAIGA_Project_2_Full_Code_Notebook_cleaned.ipynb`. Its optional historical before/after comparison skips when deleted backup inputs are absent. Notebook reruns may recreate their own indexes and experiment outputs and incur API costs. The notebook's executable code changed only to make that historical comparison optional; old code-lock hashes must not be treated as validation of this edited version.

The UI's recorded evaluation scores retain compact source reports in `backend/artifacts/evaluation`. Full historical outputs, old review scripts and notebook backups were removed. These recorded scores are not new tests of the current app.
