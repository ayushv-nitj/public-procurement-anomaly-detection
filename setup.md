# Setup Guide — Public Procurement Anomaly Detection

This guide walks you through setting up the project from scratch on your local machine. Follow every step in order. Do not skip the virtual environment step.

---

## System Requirements

Before you begin, make sure you have the following installed on your machine:

- **Python 3.9 or above** — check by running `python --version` in your terminal. If you see 3.9, 3.10, 3.11, or 3.12, you are good. If not, download from [python.org](https://www.python.org/downloads/).
- **pip** — comes bundled with Python. Check with `pip --version`.
- **Git** (optional but recommended) — for version control.
- **VS Code** — recommended editor. Download from [code.visualstudio.com](https://code.visualstudio.com/).

---

## Step 1 — Create the Project Folder

Open your terminal (or VS Code integrated terminal) and run:

```bash
mkdir public-procurement-anomaly-detection
cd public-procurement-anomaly-detection
```

All further commands in this guide must be run from inside this folder.

---

## Step 2 — Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from the rest of your system. This is important — do not skip this step.

```bash
python -m venv venv
```

This creates a folder called `venv` inside your project.

Now activate it:

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**On Mac / Linux:**
```bash
source venv/bin/activate
```

After activation, your terminal prompt will show `(venv)` at the beginning. This confirms the virtual environment is active. Every time you open a new terminal for this project, you must activate the venv again.

---

## Step 3 — Create the Folder Structure

Run the following commands to create all the necessary folders and empty files:

**On Mac / Linux:**
```bash
mkdir data src dashboard
touch requirements.txt
touch data/generate_data.py
touch src/__init__.py
touch src/features.py
touch src/models.py
touch src/nlp.py
touch src/risk_score.py
touch src/explainer.py
touch dashboard/app.py
touch README.md
```

**On Windows (PowerShell):**
```powershell
mkdir data, src, dashboard
New-Item requirements.txt, data/generate_data.py, src/__init__.py, src/features.py, src/models.py, src/nlp.py, src/risk_score.py, src/explainer.py, dashboard/app.py, README.md -ItemType File
```

Your final folder structure should look exactly like this:

```
public-procurement-anomaly-detection/
│
├── data/
│   └── generate_data.py        # generates synthetic contracts.csv
│
├── src/
│   ├── __init__.py             # makes src a Python package
│   ├── features.py             # feature engineering
│   ├── models.py               # Isolation Forest + One-Class SVM
│   ├── nlp.py                  # TF-IDF similarity detection
│   ├── risk_score.py           # weighted risk score fusion
│   └── explainer.py            # SHAP explainability wrapper
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard (main entry point)
│
├── venv/                       # virtual environment (do not touch)
├── requirements.txt            # all dependencies listed here
├── setup.md                    # this file
└── README.md                   # project overview
```

---

## Step 4 — Create requirements.txt

Open `requirements.txt` and paste the following content exactly:

```
pandas==2.1.4
numpy==1.26.4
scikit-learn==1.4.0
shap==0.44.1
streamlit==1.31.0
plotly==5.19.0
fuzzywuzzy==0.18.0
python-Levenshtein==0.25.0
```

These are pinned versions to avoid compatibility issues. If you face any conflicts, you can remove the version numbers and let pip resolve them automatically.

---

## Step 5 — Install Dependencies

Make sure your venv is active (you should see `(venv)` in your terminal), then run:

```bash
pip install -r requirements.txt
```

This will take 2–5 minutes depending on your internet speed. You will see a series of download and install messages — this is normal.

To verify everything installed correctly, run:

```bash
pip list
```

You should see pandas, scikit-learn, shap, streamlit, plotly, and fuzzywuzzy in the list.

---

## Step 6 — Generate the Synthetic Dataset

Once the code for `data/generate_data.py` is written (provided separately), run:

```bash
python data/generate_data.py
```

This will create a file called `data/contracts.csv` containing approximately 500 synthetic procurement records. You should see a confirmation message like:

```
Dataset generated: data/contracts.csv (500 rows)
```

If you see a `FileNotFoundError`, make sure you are running the command from the root of the project folder (`public-procurement-anomaly-detection/`), not from inside the `data/` folder.

---

## Step 7 — Run the Dashboard

Once all source files are written (provided separately), launch the Streamlit app:

```bash
streamlit run dashboard/app.py
```

Streamlit will start a local server and automatically open your browser at:

```
http://localhost:8501
```

If the browser does not open automatically, copy and paste that URL into your browser manually.

To stop the dashboard, press `Ctrl + C` in the terminal.

---

## Step 8 — Open in VS Code (Recommended)

If you are using VS Code, open the project like this:

```bash
code .
```

Then install the following VS Code extensions for a better experience:

| Extension | Why |
|---|---|
| Python (Microsoft) | Syntax highlighting, IntelliSense, run files |
| Pylance | Better type checking and autocomplete |
| Rainbow CSV | Colour-coded view of the contracts.csv file |
| GitLens (optional) | Track changes file by file |

After installing the Python extension, select your interpreter by pressing `Ctrl+Shift+P` → type `Python: Select Interpreter` → choose the one that shows `venv` in its path.

---

## Common Errors and Fixes

| Error Message | Likely Cause | Fix |
|---|---|---|
| `python: command not found` | Python not installed or not in PATH | Install Python from python.org, make sure to check "Add to PATH" during installation |
| `ModuleNotFoundError: No module named 'streamlit'` | venv not activated, or install failed | Activate venv and re-run `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'shap'` | shap not installed | Run `pip install shap` |
| `fuzzywuzzy warning: python-Levenshtein not installed` | Optional speed package missing | Run `pip install python-Levenshtein` |
| `Port 8501 is already in use` | Another Streamlit app is already running | Run `streamlit run dashboard/app.py --server.port 8502` |
| `FileNotFoundError: data/contracts.csv` | generate_data.py not run yet | Run `python data/generate_data.py` first |
| `PermissionError` on venv activation (Windows) | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell as admin |

---

## Every Time You Return to This Project

Each time you open a new terminal session to work on this project, you need to do two things:

1. Navigate to the project folder:
```bash
cd public-procurement-anomaly-detection
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

Then you can run any script or the dashboard as normal.

---

## Deactivating the Virtual Environment

When you are done working, deactivate the venv with:

```bash
deactivate
```
