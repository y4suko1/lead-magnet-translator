@echo off
:: ============================================================
::  Verify a Lead Magnet Translator sources file
::  Usage: drag the sources-[date].txt file and the transcript
::         file onto this together, and optionally a notes
::         file too if the ideas used call notes, OR
::         double-click to be prompted for each path.
::
::  Checks that each quoted fragment in the sources file
::  actually appears in the transcript (or notes) it claims to
::  come from. Prints PASS or FAIL for each one, and if
::  something doesn't match, shows what it searched for.
::
::  This is optional -- you never need this to get an ideas
::  menu out of the tool. It's here only if you want to
::  double-check one yourself. See verify\README.md.
:: ============================================================
setlocal

set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%check.py"

if "%~1"=="" goto promptfiles
if "%~2"=="" goto promptfiles
set "SOURCES=%~1"
set "TRANSCRIPT=%~2"
set "NOTES=%~3"
goto run

:promptfiles
echo ============================================================
echo  Lead Magnet Translator - Source Checker
echo ============================================================
echo.
echo This checks that the quoted fragments in a sources-[date].txt
echo file really are in the transcript (or notes) they claim to
echo come from.
echo.
set /p SOURCES=Path to the sources-[date].txt file:
set "SOURCES=%SOURCES:"=%"
set /p TRANSCRIPT=Path to the transcript file it was generated from:
set "TRANSCRIPT=%TRANSCRIPT:"=%"
echo.
echo If the ideas menu used call notes, and the sources file has
echo any NOTES lines, you can also check those against the notes
echo file. Leave this blank if there weren't any.
set /p NOTES=Path to the notes file (optional, press Enter to skip):
set "NOTES=%NOTES:"=%"

:run
if not exist "%SOURCES%" (
    echo.
    echo [ERROR] File not found: %SOURCES%
    pause
    exit /b 1
)
if not exist "%TRANSCRIPT%" (
    echo.
    echo [ERROR] File not found: %TRANSCRIPT%
    pause
    exit /b 1
)
if not "%NOTES%"=="" if not exist "%NOTES%" (
    echo.
    echo [ERROR] File not found: %NOTES%
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python was not found on this computer.
    echo This tool needs Python 3 installed to run. See verify\README.md.
    pause
    exit /b 1
)

echo.
if "%NOTES%"=="" (
    python "%SCRIPT%" "%SOURCES%" "%TRANSCRIPT%"
) else (
    python "%SCRIPT%" "%SOURCES%" "%TRANSCRIPT%" "%NOTES%"
)

echo.
pause
