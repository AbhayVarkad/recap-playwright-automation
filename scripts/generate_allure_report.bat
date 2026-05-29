@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT=%CD%"

call "%~dp0setup_allure_tools.bat"
if errorlevel 1 exit /b 1

call :find_java
call :find_allure

if not exist "%ROOT%\allure-results" (
    echo [report] No allure-results folder. Run tests first:
    echo   run_allure.bat
    exit /b 1
)

set "JAVA_HOME=%JAVA_HOME%"
call "%ALLURE_BAT%" generate "%ROOT%\allure-results" -o "%ROOT%\allure-report" --clean
if errorlevel 1 (
    echo [report] Allure report generation failed.
    exit /b 1
)

echo [report] Report generated: %ROOT%\allure-report\index.html
echo [report] To view, run: open_allure_report.bat
echo [report] (Opening index.html directly shows "Loading..." — browser blocks local JSON.)
exit /b 0

:find_java
set "JAVA_HOME="
for /d %%D in ("%ROOT%\tools\jdk*") do (
    if exist "%%~fD\bin\java.exe" set "JAVA_HOME=%%~fD"
)
exit /b 0

:find_allure
set "ALLURE_BAT="
for /d %%D in ("%ROOT%\tools\allure-*") do (
    if exist "%%~fD\bin\allure.bat" set "ALLURE_BAT=%%~fD\bin\allure.bat"
)
exit /b 0
