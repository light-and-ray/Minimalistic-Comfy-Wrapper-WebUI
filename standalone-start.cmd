:: This script is blindly translated from Linux using LLM.
:: If it contains errors, please make an issue

@echo off
setlocal

:: Change to script directory
cd /d "%~dp0"

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Enable verbose output
@echo on

:: Run python script with all arguments
python -m mcww.standalone %*

endlocal

pause
