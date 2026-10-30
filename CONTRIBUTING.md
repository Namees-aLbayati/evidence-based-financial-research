# Development workflow

1. Create a branch for a focused change.
2. Use `notebooks/` for experiments and explanations. Promote selected behavior explicitly into `backend/`; notebook edits do not change the app.
3. Keep frontend changes in `frontend/src`. Run `npm ci --prefix frontend` then `npm run build --prefix frontend`. Include the compiled assets served by FastAPI with source changes.
4. Run `python -m unittest tests.test_api -v`. For changes to retrieval, calculations or startup, also run `python -m unittest tests.test_integration -v` with a configured local index. Neither suite requires paid model calls.
5. Describe behavior changes and actual validation in the pull request. Use separate, new evaluation questions and human source review when assessing model quality.

Do not commit real `.env` files, credentials, `.venv`, `node_modules`, indexes, answer caches, or generated research output. `.env.example` contains placeholders only. Do not represent prior notebook scores as results of a changed application.

CI builds React and runs API contract checks without secrets or private local state. It does not run notebook optimization or live model-quality evaluation.
