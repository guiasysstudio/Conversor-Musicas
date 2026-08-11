@echo off
setlocal
cd /d "%~dp0"
py tests\test_regras_powerpoint.py
echo.
pause
endlocal
