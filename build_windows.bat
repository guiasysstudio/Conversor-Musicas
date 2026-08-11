@echo off
chcp 65001 >nul
title Build - Conversor Musicas
cd /d "%~dp0"

echo ==========================================
echo  Conversor Musicas - Gerando programa
echo ==========================================
echo.

py -m pip install -r requirements.txt
py -m pip install pyinstaller

if errorlevel 1 (
    echo ERRO ao instalar dependencias.
    pause
    exit /b 1
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando EXE...
py -m PyInstaller --clean --noconfirm --windowed ^
  --name ConversorMusicas ^
  --icon "assets\app_icon.ico" ^
  --collect-all customtkinter ^
  --add-data "assets;assets" ^
  main.py

if errorlevel 1 (
    echo.
    echo ERRO ao gerar o programa.
    pause
    exit /b 1
)

echo.
echo Programa gerado em:
echo dist\ConversorMusicas\ConversorMusicas.exe
echo.
echo OBS: os modelos editaveis sao adicionados pelo instalador
echo e preservados durante atualizacoes.
echo.
pause
