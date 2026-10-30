# Research notebook

`project2_UTAIGA_Project_2_Full_Code_Notebook_cleaned.ipynb` preserves the research work: source preparation, RAG experiments, prompt optimization, configuration comparisons, and evaluation.

The application imports Python modules in `backend/`. It never executes this notebook to answer a request. Notebook changes do not automatically change the application.

Run the notebook from the project root or `notebooks/`. It requires project `.env`, datasets, notebook-specific packages, and API access. Its dependency cell installs research dependencies. Reruns may incur embedding, generation, optimization, and judge costs. Generated indexes and results stay out of Git.

Moving the notebook required updating its project discovery and self-hash path. Previous saved outputs are historical; they do not verify the edited notebook. The last saved run stopped during optimization. Retired historical comparison inputs are optional.

Promote future experiments deliberately: update Python functions, export selected prompt/configuration, run tests and independent evaluation, and review the changes before deployment. Recorded score provenance is in `backend/artifacts/evaluation/`.
