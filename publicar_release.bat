@echo off
chcp 65001 >nul
title Publicar Release - Conversor Musicas
cd /d "%~dp0"

set "TAG=v1.2.1"
set "ARQUIVO=installer_output\Conversor-Musicas-Setup.exe"

if not exist "%ARQUIVO%" (
    echo.
    echo ERRO: Instalador nao encontrado:
    echo %ARQUIVO%
    echo.
    echo Execute primeiro:
    echo gerar_instalador.bat
    echo.
    pause
    exit /b 1
)

gh auth status >nul 2>nul
if errorlevel 1 (
    echo.
    echo ERRO: GitHub CLI nao esta autenticado.
    echo Execute: gh auth login
    echo.
    pause
    exit /b 1
)

echo.
echo Publicando Release %TAG%...

gh release view "%TAG%" >nul 2>nul
if not errorlevel 1 (
    echo.
    echo A Release %TAG% ja existe.
    echo Enviando/atualizando o instalador...
    gh release upload "%TAG%" "%ARQUIVO%" --clobber
) else (
    gh release create "%TAG%" "%ARQUIVO%" ^
      --repo guiasysstudio/Conversor-Musicas ^
      --title "Conversor Músicas v1.2.1" ^
      --notes "Primeira Release pública do Conversor Músicas. Conversão TXT para PowerPoint e SLJA sem áudio, interface moderna e base de atualização automática via GitHub Releases."
)

if errorlevel 1 (
    echo.
    echo ERRO ao publicar a Release.
    pause
    exit /b 1
)

echo.
echo Release publicada com sucesso.
echo https://github.com/guiasysstudio/Conversor-Musicas/releases/tag/%TAG%
echo.
pause
