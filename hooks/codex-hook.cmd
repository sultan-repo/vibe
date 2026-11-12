@echo off
setlocal
rem Use Python directly on Windows so startup and shell checks do not need WSL.
set "vibe_python=python3"
python3 -V >nul 2>&1
if errorlevel 1 set "vibe_python=py -3"
if "%~1"=="startup" (
  %vibe_python% "%~dp0session-start.py" --core "%~dp0..\core\CLAUDE.md"
  exit /b
)
if not "%~1"=="check" exit /b 2
%vibe_python% "%~dp0check-force-push.py"
if errorlevel 1 (
  echo Blocked by Vibe: force-push detected or safety check failed. 1>&2
  exit /b 2
)
exit /b 0
