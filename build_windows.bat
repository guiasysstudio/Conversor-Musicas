@echo off
setlocal EnableExtensions
title Build - Conversor Musicas
cd /d "%~dp0"

echo ==========================================
echo  Conversor Musicas - Build v1.3.0
echo ==========================================
echo.

py -m pip install -r requirements.txt
py -m pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando programa...
py -m PyInstaller --clean --noconfirm --windowed ^
  --name ConversorMusicas ^
  --icon "assets\app_icon.ico" ^
  --collect-all customtkinter ^
  --collect-all win32com ^
  --hidden-import win32com.client ^
  --hidden-import pythoncom ^
  --hidden-import pywintypes ^
  --add-data "assets;assets" ^
  main.py

if errorlevel 1 (
    echo.
    echo ERRO ao gerar o executavel.
    pause
    exit /b 1
)

echo.
echo Programa gerado:
echo dist\ConversorMusicas\ConversorMusicas.exe
echo.
pause
endlocal
