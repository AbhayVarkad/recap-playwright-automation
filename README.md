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
- `scripts/allure_report.py` - run tests and Allure report
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

Pytest + Allure (writes results for the report step at the end of this README):

```bash
python -m pytest tests/test_recap_allure.py -v --alluredir=allure-results
```

## Notes

- The automation currently launches Chromium in headed mode (`headless=False`).
- Browser context uses `local-network-access` permission via `utils/browser.py`.
- Logging is configured in `utils/logging_config.py`.

## Customization

- Change viewer target URL in `config/settings.py` (`VIEWER_URL`).
- Update selectors in `config/selectors.py` if UI changes.
- Adjust timeout constants in `config/settings.py` as needed.

## Allure report (last step)

Run your tests first. Allure HTML reporting comes **after** the test run.

You need **Java 17+** and the **Allure CLI**. If they are not installed, bootstrap once (downloads into `tools/`, ~200 MB):

```bash
python scripts/allure_report.py --setup-tools
```

From the project root:

```bash
# 1) Run tests and write results
python scripts/allure_report.py test

# 2a) View report — serve straight from results (easiest)
python scripts/allure_report.py serve

# 2b) Or build static HTML, then open it
python scripts/allure_report.py generate
python scripts/allure_report.py open
```

**One shot** — run tests, then start the Allure server (always do this last):

```bash
python scripts/allure_report.py all
```

Equivalent manual commands:

```bash
python -m pytest tests/test_recap_allure.py -v --alluredir=allure-results
allure serve allure-results
```

Do not double-click `allure-report\index.html` — use `serve` or `open` so the browser can load report data.

| Command | What it does |
|--------|----------------|
| `test` | Pytest with `--alluredir=allure-results` |
| `generate` | `allure-results` → `allure-report/` |
| `serve` | Local server from `allure-results` (no separate generate step) |
| `open` | Local server from `allure-report/` (after `generate`) |
| `all` | `test` then `serve` |
