# Recap Viewer Automation

Python + Playwright automation for Autodesk Recap viewer flows.

## What This Project Covers

- Project Browser flow validation:
  - collects names from Scans, Annotations, View States, and Extracted Features
  - verifies each item via the in-app search
  - reports pass/total summary
- Bottom toolbar Scan Group flow:
  - opens Scan Group
  - handles tutorial modal (`Next` -> `OK`)
  - clicks `Done`

## Project Layout

- `tests/test_project_browser_flow.py` - refactored project browser verification flow
- `tests/test_scan_group_toolbar_flow.py` - refactored bottom toolbar scan group flow
- `pages/` - page objects (`ViewerPage`, `ProjectBrowserPage`, `BottomToolbarPage`)
- `config/selectors.py` - centralized CSS selectors
- `config/settings.py` - shared runtime settings (viewer URL, timeouts, permissions)
- `utils/browser.py` - Playwright context creation helper
- `test.py` - legacy monolithic project browser script
- `test2.py` - legacy monolithic bottom toolbar script

## Prerequisites

- Python 3.10+
- Google Chrome/Chromium-capable environment
- Internet access to load:
  - `https://cdn.recap-staging.autodesk.com`
  - referenced dataset URL in `config/settings.py`

## Setup

```bash
python -m venv .venv
```

Activate virtual environment:

- Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Allure report

One command runs tests and opens the HTML report (uses `.bat` files — no PowerShell execution-policy change needed):

```powershell
.\run_allure.bat
```

First run downloads portable Java + Allure CLI into `tools/` (~200 MB).

Regenerate report only (after tests):

```powershell
.\generate_allure_report.bat
```

**View the report** (required — do not double-click `index.html`; it will stay on "Loading..."):

```powershell
.\open_allure_report.bat
```

This starts a small local web server and opens the report in your browser.

## Run

Refactored flows (recommended):

```bash
python tests/test_project_browser_flow.py
python tests/test_scan_group_toolbar_flow.py
```

Legacy scripts:

```bash
python test.py
python test2.py
```

## Notes

- The automation currently launches Chromium in headed mode (`headless=False`).
- Browser context uses `local-network-access` permission via `utils/browser.py`.
- Logging is configured in `utils/logging_config.py`.

## Customization

- Change viewer target URL in `config/settings.py` (`VIEWER_URL`).
- Update selectors in `config/selectors.py` if UI changes.
- Adjust timeout constants in `config/settings.py` as needed.
