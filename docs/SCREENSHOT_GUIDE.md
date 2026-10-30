# Add screenshots to your GitHub README

Repository: [evidence-based-financial-research](https://github.com/Namees-aLbayati/evidence-based-financial-research)

## Capture the app

Start the server from the project folder:

```bash
source .venv/bin/activate
python -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/ and take these screenshots. On macOS, press **Shift + Command + 4** and select the area to capture.

| Filename | What to show |
| --- | --- |
| `homepage.png` | App title, research workflow, RAG explanation, and question input |
| `answer-analysis.png` | A real successful question, analysis, calculated figures, and source citations |
| `evaluation.png` | Expanded evaluation section, metric definitions, and prior notebook scores |

Save the images in `docs/screenshots/`. Use the exact filenames above, or update the README paths to match your filenames. Capture the browser window without showing `.env`, tokens, or API keys.

## Display the images

The README now embeds the supplied screenshots with relative image paths. Replace an image using its existing filename to update the preview without editing the README. Additional screenshots include `api-docs.png`, `question-input.png`, and `sources-and-limitations.png`.

Preview the README in VS Code with **Shift + Command + V**.

## Upload your changes

From the project folder:

```bash
git add README.md docs/SCREENSHOT_GUIDE.md docs/screenshots/
git commit -m "Add app screenshots and demo documentation"
git push origin main
```

The README uses relative image paths, so screenshots will display on GitHub. A localhost link alone cannot show your running app to other people.

Alternatively, open this repository on GitHub, choose **Add file → Upload files** in `docs/screenshots`, upload the images, and edit the README image comments on GitHub.
