from pathlib import Path
import sys

def raiz_programa() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

RAIZ = raiz_programa()
PASTA_MODELOS = RAIZ / "modelos"
PASTA_MODELOS_PPTX = PASTA_MODELOS / "powerpoint"
PASTA_IMAGENS_SLJA = PASTA_MODELOS / "slja" / "imagens"
PASTA_SAIDA = RAIZ / "saida"

def garantir_pastas():
    for pasta in (PASTA_MODELOS_PPTX, PASTA_IMAGENS_SLJA, PASTA_SAIDA):
        pasta.mkdir(parents=True, exist_ok=True)
