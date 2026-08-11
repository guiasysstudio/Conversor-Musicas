@echo off
chcp 65001 >nul
cd /d "%~dp0"

py -m pip install -r requirements.txt
py -m pip install pyinstaller

py -m PyInstaller --clean --noconfirm --windowed ^
  --name ConversorMusicas ^
  --collect-all customtkinter ^
  --add-data "modelos;modelos" ^
  --add-data "assets;assets" ^
  main.py

pause
