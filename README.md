# PDF Master — Version 1.0

A beginner-friendly Python web app for:
- Merging multiple PDFs
- Extracting selected pages from a PDF
- Converting JPG/PNG images into a PDF
- Extracting selectable text from PDFs

## Files
- `app.py` — main app
- `requirements.txt` — Python libraries required by the app

## Run on a computer
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`
5. Open the local URL Streamlit shows.

## Publish for free
1. Create/sign in to GitHub and create a new **public** repository.
2. Upload `app.py` and `requirements.txt` to the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select your repository and `app.py`, then deploy.
5. Wait for the app to build and copy the URL ending in `.streamlit.app`.

Free hosting rules and availability can change. A public repository means the code is public. Do not upload customer PDFs to GitHub. Uploaded documents are processed by the running app; avoid sensitive documents on a public demo.

## Current limitations
- No OCR for scanned PDFs.
- Password-protected PDFs are not supported.
- Large files may run into hosting memory/time limits.
- This starter version does not have user accounts, payment features, or guaranteed permanent storage.
