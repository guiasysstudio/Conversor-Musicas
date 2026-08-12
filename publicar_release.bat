@echo off
setlocal EnableExtensions
title Publicar Atualizacao - Conversor Musicas
cd /d "%~dp0"

set "TAG=v1.3.1"
set "REPO=guiasysstudio/Conversor-Musicas"
set "ARQUIVO=installer_output\Conversor-Musicas-Setup v1.3.1.exe"

echo ==========================================
echo  Conversor Musicas - Publicar Atualizacao
echo  Versao: %TAG%
echo ==========================================
echo.

if not exist "%ARQUIVO%" (
    echo ERRO: instalador nao encontrado:
    echo %CD%\%ARQUIVO%
    echo.
    echo Execute primeiro:
    echo   gerar_instalador.bat
    echo.
    pause
    exit /b 1
)

where gh.exe >nul 2>nul
if errorlevel 1 (
    echo ERRO: ferramenta de publicacao nao encontrada.
    pause
    exit /b 1
)

gh auth status >nul 2>nul
if errorlevel 1 (
    echo ERRO: sessao de publicacao nao autenticada.
    pause
    exit /b 1
)

gh release view "%TAG%" --repo "%REPO%" >nul 2>nul

if errorlevel 1 (
    gh release create "%TAG%" "%ARQUIVO%" --repo "%REPO%" --title "Conversor Musicas v1.3.1" --notes "Versao 1.3.1: adiciona regras individuais por musica, aplicacao de regra em lote, lista de arquivos com rolagem automatica e selecao multipla. Mantem PowerPoint e SLJA validados, seletores de pasta aprimorados e atualizacao automatica."
) else (
    gh release upload "%TAG%" "%ARQUIVO%" --clobber --repo "%REPO%"
)

if errorlevel 1 (
    echo.
    echo ERRO ao publicar a atualizacao.
    pause
    exit /b 1
)

echo.
echo Atualizacao %TAG% publicada com sucesso.
echo.
pause
endlocal
