@echo off
cd /d "%~dp0"

:loop
call venv\Scripts\activate.bat
python -m mcww.standalone %*

if not exist ".\RESTART_REQUESTED" goto :end

del ".\RESTART_REQUESTED" >nul 2>&1

goto loop

:end
pause
