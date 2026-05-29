@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT=%CD%"

call "%~dp0setup_allure_tools.bat"
if errorlevel 1 exit /b 1

call :find_java
call :find_allure

if not exist "%ROOT%\allure-report\index.html" (
    echo [open] Report not found. Generate it first:
    echo   generate_allure_report.bat
    exit /b 1
)

set "LAUNCHER=%ROOT%\allure-report\_open_server.bat"
(
    echo @echo off
    echo set "JAVA_HOME=%JAVA_HOME%"
    echo echo Allure server running. Close this window to stop.
    echo call "%ALLURE_BAT%" open "%ROOT%\allure-report"
) > "%LAUNCHER%"

echo [open] Starting local server (file:// index.html cannot load report data).
echo [open] A new window will open; close it when you are done viewing.
start "Allure Report" cmd /k "%LAUNCHER%"
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
