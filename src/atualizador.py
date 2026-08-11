from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import requests

from .versao import VERSAO, GITHUB_OWNER, GITHUB_REPO


CABECALHOS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Conversor-Musicas",
}


def _normalizar_versao(valor: str):
    numeros = re.findall(r"\d+", valor or "")
    return tuple(int(x) for x in numeros[:4])


def configurado() -> bool:
    return bool(GITHUB_OWNER.strip() and GITHUB_REPO.strip())


def _buscar_instalador(assets, nova_versao: str):
    if not assets:
        return None

    versao_limpa = (nova_versao or "").lstrip("vV").strip().lower()

    for asset in assets:
        nome = asset.get("name", "")
        nome_low = nome.lower()
        if (
            nome_low.endswith(".exe")
            and "conversor-musicas-setup" in nome_low
            and versao_limpa
            and versao_limpa in nome_low
        ):
            return asset

    for asset in assets:
        nome_low = asset.get("name", "").lower()
        if nome_low.endswith(".exe") and "conversor-musicas-setup" in nome_low:
            return asset

    for asset in assets:
        nome_low = asset.get("name", "").lower()
        if nome_low.endswith(".exe") and (
            "setup" in nome_low
            or "installer" in nome_low
            or "instalador" in nome_low
        ):
            return asset

    return None


def verificar_atualizacao(timeout=10):
    if not configurado():
        return {
            "configurado": False,
            "atualizacao": False,
            "mensagem": "Sistema de atualizações ainda não configurado.",
        }

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    resposta = requests.get(url, timeout=timeout, headers=CABECALHOS)

    if resposta.status_code == 404:
        return {
            "configurado": True,
            "atualizacao": False,
            "sem_release": True,
            "mensagem": "Nenhuma atualização publicada ainda.",
        }

    resposta.raise_for_status()
    dados = resposta.json()

    tag = dados.get("tag_name", "")
    nova = _normalizar_versao(tag)
    atual = _normalizar_versao(VERSAO)
    asset = _buscar_instalador(dados.get("assets", []), tag)

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
            else "Você já está usando a versão mais recente."
        ),
    }


def baixar_instalador(asset, callback_progresso=None, timeout=60):
    if not asset:
        raise ValueError("A nova versão não possui um instalador compatível.")

    url = asset.get("browser_download_url")
    nome = asset.get("name") or "Conversor-Musicas-Setup.exe"

    if not url:
        raise ValueError("Não foi possível localizar o endereço do instalador.")

    pasta = Path(tempfile.gettempdir()) / "ConversorMusicasUpdate"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / nome

    with requests.get(
        url,
        stream=True,
        timeout=timeout,
        headers={"User-Agent": "Conversor-Musicas"}
    ) as resposta:
        resposta.raise_for_status()

        total = int(resposta.headers.get("content-length", 0))
        baixado = 0

        with open(destino, "wb") as arquivo:
            for bloco in resposta.iter_content(chunk_size=1024 * 256):
                if not bloco:
                    continue

                arquivo.write(bloco)
                baixado += len(bloco)

                if callback_progresso and total > 0:
                    callback_progresso(baixado / total)

    return destino


def executar_instalador(caminho_instalador):
    caminho_instalador = Path(caminho_instalador)

    if not caminho_instalador.is_file():
        raise FileNotFoundError("O instalador baixado não foi encontrado.")

    os.startfile(str(caminho_instalador))
