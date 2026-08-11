from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests

from .versao import (
    VERSAO,
    GITHUB_OWNER,
    GITHUB_REPO,
    NOME_ASSET_INSTALADOR,
)

CABECALHOS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Conversor-Musicas",
}

def _normalizar_versao(valor: str):
    numeros = re.findall(r"\d+", valor or "")
    return tuple(int(x) for x in numeros[:4])

def configurado() -> bool:
    return bool(GITHUB_OWNER.strip() and GITHUB_REPO.strip())

def _buscar_asset_instalador(assets):
    if not assets:
        return None

    # 1. Nome exato preferido
    for asset in assets:
        if asset.get("name", "").lower() == NOME_ASSET_INSTALADOR.lower():
            return asset

    # 2. Qualquer setup/installer .exe
    candidatos = []
    for asset in assets:
        nome = asset.get("name", "")
        nome_low = nome.lower()
        if nome_low.endswith(".exe") and ("setup" in nome_low or "installer" in nome_low or "instalador" in nome_low):
            candidatos.append(asset)

    if candidatos:
        return candidatos[0]

    # 3. Qualquer .exe como último recurso
    for asset in assets:
        nome = asset.get("name", "")
        if nome.lower().endswith(".exe"):
            return asset

    return None

def verificar_atualizacao(timeout=10):
    if not configurado():
        return {
            "configurado": False,
            "atualizacao": False,
            "mensagem": "Repositório GitHub ainda não configurado.",
        }

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    resposta = requests.get(url, timeout=timeout, headers=CABECALHOS)

    if resposta.status_code == 404:
        return {
            "configurado": True,
            "atualizacao": False,
            "sem_release": True,
            "mensagem": "Nenhuma Release publicada ainda no GitHub.",
        }

    resposta.raise_for_status()
    dados = resposta.json()

    tag = dados.get("tag_name", "")
    nova = _normalizar_versao(tag)
    atual = _normalizar_versao(VERSAO)
    asset = _buscar_asset_instalador(dados.get("assets", []))

    return {
        "configurado": True,
        "atualizacao": nova > atual,
        "versao_atual": VERSAO,
        "nova_versao": tag,
        "pagina": dados.get("html_url", ""),
        "notas": dados.get("body", "") or "",
        "asset": asset,
        "mensagem": (
            "Atualização disponível."
            if nova > atual
            else "Você já está na versão mais recente."
        ),
    }

def baixar_instalador(asset, callback_progresso=None, timeout=60):
    if not asset:
        raise ValueError("A Release não possui um instalador .exe compatível.")

    url = asset.get("browser_download_url")
    nome = asset.get("name") or NOME_ASSET_INSTALADOR
    if not url:
        raise ValueError("O instalador da Release não possui URL de download.")

    pasta = Path(tempfile.gettempdir()) / "ConversorMusicasUpdate"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome

    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "Conversor-Musicas"}) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        baixado = 0

        with open(destino, "wb") as f:
            for bloco in r.iter_content(chunk_size=1024 * 256):
                if not bloco:
                    continue
                f.write(bloco)
                baixado += len(bloco)
                if callback_progresso and total > 0:
                    callback_progresso(baixado / total)

    return destino

def executar_instalador(caminho_instalador):
    caminho_instalador = Path(caminho_instalador)
    if not caminho_instalador.is_file():
        raise FileNotFoundError("O instalador baixado não foi encontrado.")

    # ShellExecute no Windows permite que o próprio instalador solicite elevação/UAC se necessário.
    os.startfile(str(caminho_instalador))
