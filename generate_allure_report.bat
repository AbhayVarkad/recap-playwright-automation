@echo off
REM Wrapper so you can run from project root: .\generate_allure_report.bat
call "%~dp0scripts\generate_allure_report.bat" %*
exit /b %ERRORLEVEL%
