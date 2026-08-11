from __future__ import annotations

import json
import os
from pathlib import Path


PADRAO = {
    "linhas_por_slide": 2,
}


def _pasta_configuracoes() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        pasta = Path(base) / "ConversorMusicas"
    else:
        pasta = Path.home() / ".conversor_musicas"

    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


ARQUIVO_CONFIG = _pasta_configuracoes() / "config.json"


def carregar_configuracoes():
    dados = dict(PADRAO)

    if not ARQUIVO_CONFIG.exists():
        return dados

    try:
        carregado = json.loads(ARQUIVO_CONFIG.read_text(encoding="utf-8"))
        if isinstance(carregado, dict):
            dados.update(carregado)
    except Exception:
        # Se o arquivo estiver inválido, o programa volta ao padrão.
        return dict(PADRAO)

    linhas = dados.get("linhas_por_slide", 2)
    if linhas not in (1, 2, 3):
        linhas = 2

    dados["linhas_por_slide"] = linhas
    return dados


def salvar_configuracoes(dados):
    atuais = carregar_configuracoes()
    atuais.update(dados)

    linhas = atuais.get("linhas_por_slide", 2)
    if linhas not in (1, 2, 3):
        linhas = 2

    atuais["linhas_por_slide"] = linhas

    ARQUIVO_CONFIG.write_text(
        json.dumps(atuais, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def restaurar_padrao():
    salvar_configuracoes(PADRAO)
    return dict(PADRAO)
