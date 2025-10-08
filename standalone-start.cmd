:: This script is blindly translated from Linux using LLM.
:: If it contains errors, please make an issue
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
@echo on
python -m mcww.standalone %*
pause
