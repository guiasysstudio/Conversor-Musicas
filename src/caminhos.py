from pathlib import Path
import sys


def raiz_programa() -> Path:
    """
    Pasta editável do programa.
    No executável instalado, é a pasta onde fica o .exe.
    No desenvolvimento, é a raiz do projeto.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def raiz_recursos() -> Path:
    """
    Pasta somente leitura usada pelo PyInstaller para recursos empacotados
    como logo e demais assets.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


RAIZ = raiz_programa()
RECURSOS = raiz_recursos()

# Recursos empacotados
PASTA_ASSETS = RECURSOS / "assets"
ARQUIVO_LOGO = PASTA_ASSETS / "logo.png"

# Pastas editáveis, mantidas dentro da raiz instalada do programa
PASTA_MODELOS = RAIZ / "modelos"
PASTA_MODELOS_PPTX = PASTA_MODELOS / "powerpoint"
PASTA_IMAGENS_SLJA = PASTA_MODELOS / "slja" / "imagens"
PASTA_SAIDA = RAIZ / "saida"


def garantir_pastas():
    """
    Cria somente as pastas que o usuário precisa editar.
    Nunca tenta criar a pasta de assets empacotados.
    """
    for pasta in (PASTA_MODELOS_PPTX, PASTA_IMAGENS_SLJA, PASTA_SAIDA):
        pasta.mkdir(parents=True, exist_ok=True)
