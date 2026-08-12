@echo off
setlocal EnableExtensions
title Instalador - Conversor Musicas
cd /d "%~dp0"

echo ==========================================
echo  Conversor Musicas - Instalador v1.3.1
echo ==========================================
echo.

call build_windows.bat
if errorlevel 1 exit /b 1

if exist installer_output rmdir /s /q installer_output

set "ISCC="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

if not defined ISCC if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not defined ISCC (
    where ISCC.exe >nul 2>nul
    if not errorlevel 1 set "ISCC=ISCC.exe"
)

if not defined ISCC (
    echo.
    echo ERRO: Inno Setup 6 nao encontrado.
    pause
    exit /b 1
)

echo.
echo Gerando instalador...
"%ISCC%" "ConversorMusicas.iss"

if errorlevel 1 (
    echo.
    echo ERRO ao gerar o instalador.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  CONCLUIDO
echo ==========================================
echo.
echo Instalador:
echo installer_output\Conversor-Musicas-Setup v1.3.1.exe
echo.
pause
endlocal
