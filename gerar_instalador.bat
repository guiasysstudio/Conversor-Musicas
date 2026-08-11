@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

call build_windows.bat
if errorlevel 1 exit /b 1

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if not defined ISCC (
  echo Inno Setup 6 nao encontrado.
  pause
  exit /b 1
)

"%ISCC%" "instalador\ConversorMusicas.iss"
if errorlevel 1 (
  echo Erro ao gerar instalador.
  pause
  exit /b 1
)

echo.
echo Instalador criado em installer_output\ConversorMusicas_Setup_1.0.0.exe
pause
