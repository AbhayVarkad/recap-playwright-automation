@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%CD%"

echo === Recap automation: tests + Allure report ===

call "%ROOT%\scripts\setup_allure_tools.bat"
if errorlevel 1 exit /b 1

echo.
echo [1/3] Installing Python dependencies...
python -m pip install -q -r "%ROOT%\requirements.txt"
if errorlevel 1 (
    echo Failed to install requirements.txt
    exit /b 1
)

echo.
echo [2/3] Running tests (headed browser, ~2-3 min)...
python -m pytest tests/test_recap_allure.py --alluredir="%ROOT%\allure-results" -v
set "TEST_EXIT=%ERRORLEVEL%"
if not "%TEST_EXIT%"=="0" (
    echo Tests failed with exit code %TEST_EXIT%. Generating report from partial results...
)

echo.
echo [3/3] Generating Allure HTML report...
call "%ROOT%\scripts\generate_allure_report.bat"
if errorlevel 1 exit /b 1

echo.
echo Opening report via local server...
call "%ROOT%\scripts\open_allure_report.bat"

exit /b %TEST_EXIT%
