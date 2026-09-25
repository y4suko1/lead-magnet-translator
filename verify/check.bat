@echo off
:: ============================================================
::  Verify a Lead Magnet Translator sources file
::  Usage: drag the sources-[date].txt file and the transcript
::         file onto this together, and optionally a notes
::         file too if the ideas used call notes, OR
::         double-click to be prompted for each path.
::
::  Runs two checks, one after the other:
::
::  1. check.py: does each quoted fragment in the sources file
::     actually appear in the transcript (or notes) it claims
::     to come from. Prints PASS or FAIL for each one, and if
::     something doesn't match, shows what it searched for.
::
::  2. speaker_check.py: for each quote, which transcript
::     speaker actually said it, and whether a claim's stated
::     count ("two attendees") or attribution ("the host")
::     matches. Catches a real quote used to back a wrong count
::     or the wrong person, something check.py alone can't see.
::     This one does NOT check whether a quote is characterized
::     fairly ("the room reacted well") -- that's still a
::     judgement call, not something either script can verify.
::
::  This is optional -- you never need this to get an ideas
::  menu out of the tool. It's here only if you want to
::  double-check one yourself. See verify\README.md.
:: ============================================================
setlocal

set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%check.py"
set "SCRIPT2=%SCRIPT_DIR%speaker_check.py"

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
echo ============================================================
echo  Check 1 of 2: are the quotes real?
echo ============================================================
if "%NOTES%"=="" (
    python "%SCRIPT%" "%SOURCES%" "%TRANSCRIPT%"
) else (
    python "%SCRIPT%" "%SOURCES%" "%TRANSCRIPT%" "%NOTES%"
)

echo.
echo ============================================================
echo  Check 2 of 2: do the counts and who-said-it match?
echo ============================================================
echo  (This doesn't check the notes file -- notes aren't
echo   speaker-labelled the way a transcript is.)
echo.
python "%SCRIPT2%" "%SOURCES%" "%TRANSCRIPT%"

echo.
echo ============================================================
echo  Neither check above confirms a quote was characterized
echo  fairly (e.g. "the comparison worked", "the room reacted
echo  well"). That's a judgement call, not something a script
echo  can verify -- see rules.md section 7b.
echo ============================================================
echo.
pause
