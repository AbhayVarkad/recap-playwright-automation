@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
set "ROOT=%CD%"
set "TOOLS=%ROOT%\tools"

if not exist "%TOOLS%" mkdir "%TOOLS%"

call :find_java
if defined JAVA_HOME goto :have_java

echo [setup] Downloading portable Java 17 JRE...
set "JRE_ZIP=%TEMP%\OpenJDK17-jre.zip"
set "JRE_URL=https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.15%%2B6/OpenJDK17U-jre_x64_windows_hotspot_17.0.15_6.zip"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%JRE_URL%' -OutFile '%JRE_ZIP%' -UseBasicParsing; Expand-Archive -Path '%JRE_ZIP%' -DestinationPath '%TOOLS%' -Force"
if errorlevel 1 (
    echo [setup] Failed to download Java. Check network access and retry.
    exit /b 1
)
call :find_java
if not defined JAVA_HOME (
    echo [setup] Java was extracted but java.exe was not found under tools\
    exit /b 1
)

:have_java
echo [setup] Using JAVA_HOME=%JAVA_HOME%

call :find_allure
if defined ALLURE_BAT goto :have_allure

echo [setup] Downloading Allure CLI 2.34.0...
set "ALLURE_ZIP=%TEMP%\allure-2.34.0.zip"
set "ALLURE_URL=https://github.com/allure-framework/allure2/releases/download/2.34.0/allure-2.34.0.zip"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%ALLURE_URL%' -OutFile '%ALLURE_ZIP%' -UseBasicParsing; Expand-Archive -Path '%ALLURE_ZIP%' -DestinationPath '%TOOLS%' -Force"
if errorlevel 1 (
    echo [setup] Failed to download Allure CLI. Check network access and retry.
    exit /b 1
)
call :find_allure
if not defined ALLURE_BAT (
    echo [setup] Allure was extracted but allure.bat was not found under tools\
    exit /b 1
)

:have_allure
echo [setup] Using ALLURE_BAT=%ALLURE_BAT%
echo [setup] Allure tools are ready.
exit /b 0

:find_java
set "JAVA_HOME="
for /d %%D in ("%TOOLS%\jdk*") do (
    if exist "%%~fD\bin\java.exe" set "JAVA_HOME=%%~fD"
)
exit /b 0

:find_allure
set "ALLURE_BAT="
for /d %%D in ("%TOOLS%\allure-*") do (
    if exist "%%~fD\bin\allure.bat" set "ALLURE_BAT=%%~fD\bin\allure.bat"
)
exit /b 0
