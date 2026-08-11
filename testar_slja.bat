@echo off
setlocal
cd /d "%~dp0"
py -m tests.test_slja_estrutura
echo.
pause
endlocal
