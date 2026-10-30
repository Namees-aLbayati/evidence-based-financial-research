# Financial Research Assistant

A Python backend that uses the financial notebook's retrieval, calculations, and answer-validation logic through a FastAPI API. Ask questions about the supplied historical news, prices, and filings, and receive an answer with sources and limitations.

The notebook is retained for experiments. The application runs the extracted Python code instead of executing notebook cells.

## 1. Open your project terminal

In VS Code, open **Terminal → New Terminal**. Make sure you are in this project folder:

```bash
cd "/Users/namees.local/Desktop/Great Learning/finincial_support_P2"
```

## 2. Activate the Python environment

```bash
source .venv/bin/activate
```

This selects the project's Python environment. You will usually see `(.venv)` at the start of your terminal prompt.

The backend packages are already installed in this workspace. If you need to install them again:

```bash
python -m pip install -r requirements-app.txt
```

The backend also needs the existing project `.env`, local datasets, `.app_chroma` index, and `backend/artifacts` files. Keep your real API key in `.env`; do not include it in screenshots or commit it.

## 3. Start the backend

```bash
python -m uvicorn backend.main:app --reload
```

Wait for **Application startup complete**. Keep this terminal running while you use the API. Press **Ctrl+C** when you want to stop it.

- `backend.main:app` tells the server where your FastAPI application lives.
- `--reload` restarts the server when you edit the Python code during development.

## 4. Open the homepage and testing page

Open the homepage in your browser:

**http://127.0.0.1:8000/**

The homepage is a React app. Type your question and click **Generate report**. Answers, sources, and limitations appear on the same page. Example question buttons fill the input without sending a request.

For the API testing page, go to **http://127.0.0.1:8000/docs**.

This is FastAPI's interactive API documentation. You can test the backend here before connecting your own app.

You can also open **http://127.0.0.1:8000/health**. A successfully started backend returns:

```json
{"status": "ready"}
```

The health check confirms local startup; it does not check whether the model provider accepts your API credentials.

## 5. Ask your first question

1. Expand **POST /ask**.
2. Click **Try it out**.
3. Replace the example request body with:

```json
{
  "question": "How did Apple's stock price change?"
}
```

4. Click **Execute** and wait for the response.
5. Look for HTTP status **200** and the answer in **Response body**.

A real question may make paid embedding and model API calls. The first uncached answer can take time.

The response includes:

| Field | Meaning |
| --- | --- |
| `answer` | The released answer and supported calculations |
| `status` | `answered`, `partial`, or `insufficient_evidence` |
| `sources` | Source metadata and citation labels |
| `limitations` | Missing evidence and other answer limitations |
| `coverage_notes` | Dataset coverage information |
| `citation_labels_valid` | Whether citation labels passed a structural check |
| `cache_hit` | Whether an existing saved answer was reused |

`partial` is a valid result: the data supports only part of the question. Valid citation labels do not guarantee factual accuracy. Dates and calculations refer to the supplied historical dataset, not live market prices.

## 6. Add your screenshot

After running a question, capture the **POST /ask request and response**. Save the image in:

```text
docs/screenshots/first-api-response.png
```

Then remove the HTML comment markers around the image line below to display it in this README. If you use another filename, update the image path to match it.

<!-- Uncomment after saving your screenshot:
![First question and API response](docs/screenshots/first-api-response.png)
-->

*Screenshot pending: add your actual run here.*

You can also send the screenshot in this chat and ask me to add it to the README.

## 7. Connect your app

Your frontend sends a question to the backend:

```text
Your app → POST /ask → Python research pipeline → JSON response → Your app
```

Example for a JavaScript frontend:

```javascript
async function askQuestion(question) {
  const response = await fetch("http://127.0.0.1:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.detail || "Request failed");
  }
  return result;
}
```

Display `result.answer`, `result.sources`, and `result.limitations` in your app. Keep API credentials on the backend.

The backend allows frontend origins `http://localhost:3000` and `http://localhost:5173` by default. For another frontend address, configure `FRONTEND_ORIGINS` in `.env` and restart the server. See [APP_SETUP.md](APP_SETUP.md) for details about CORS, index preparation, and deployment considerations.

## Project files

| File or folder | Purpose |
| --- | --- |
| `backend/main.py` | FastAPI endpoints and request/response validation |
| `backend/data.py` | Local source-data loading and filing chunking |
| `backend/pipeline.py` | Retrieval, calculations, answer generation, and validation |
| `backend/artifacts/` | Saved selected prompt and configuration |
| `.app_chroma/` | Separate local application vector index |
| `.app_cache/` | Cached query embeddings and answers |
| `requirements-app.txt` | Backend dependencies |
| `checks/test_app.py` | Offline integration tests |

The application uses a saved prior prompt/configuration selection. The latest saved notebook run stopped during optimization; this backend does not imply that run completed.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Browser cannot connect | Keep the server terminal running and wait for startup to complete. |
| `No module named fastapi` or `uvicorn` | Activate `.venv`, then install `requirements-app.txt`. |
| Port 8000 is already in use | Stop the other server or run with `--port 8001`, then use port 8001 in your browser and frontend URL. |
| HTTP 422 | Send a nonempty text `question` of at most 4,000 characters. |
| HTTP 503 | Check backend logs and your provider's API access, quota, and settings in `.env`, then retry. |
| Index missing or mismatched | Follow the index preparation instructions in [APP_SETUP.md](APP_SETUP.md). |
| Browser reports a CORS error | Add your frontend's exact origin to `FRONTEND_ORIGINS`, then restart. |

## Run offline tests

With `.venv` activated:

```bash
python -m unittest checks.test_app -v
```

Six integration tests passed when the backend was created. They cover local startup, input validation, response filtering, error handling, CORS, calculations, and vector retrieval. Paid model calls are stubbed or bypassed, so these tests do not verify live model access or answer quality.

## React frontend development

The built React app is served by FastAPI at the homepage. You only need the Python server to use it.

After changing files in `frontend/src`, rebuild the frontend:

```bash
cd frontend
npm install
npm run build
cd ..
```

Refresh the homepage after building. For frontend development with automatic refresh, keep FastAPI running and run `npm run dev` from `frontend` in another terminal; open the address Vite prints (under `/ui/`). Vite forwards question requests to the local FastAPI server.

## Project cleanup

Old notebook versions, backups, review reports, experiment outputs, duplicate test-run data and old notebook vector indexes were removed. The current cleaned notebook, datasets, React/FastAPI app, working `.app_chroma` index, `.env`, virtual environment and app integration tests remain. Compact evaluation evidence is retained in `backend/artifacts/evaluation` for the scores shown in the UI.

The notebook's historical before/after comparison now skips if removed inputs are absent. Its previous saved execution is not a verification of this cleanup edit. Notebook reruns can recreate experiment output and incur API costs; use the app normally without rerunning the notebook.
