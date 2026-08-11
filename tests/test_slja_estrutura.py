from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from PIL import Image

from src.gerador_slja import gerar_slja


def executar():
    with TemporaryDirectory() as tmp:
        raiz = Path(tmp)

        entrada = raiz / "musica.txt"
        entrada.write_text("""Música Teste
Linha 1
Linha 2
Linha 3

Nova 1
Nova 2
""", encoding="utf-8")

        capa = raiz / "capa.png"
        letra = raiz / "letra.png"
        Image.new("RGB", (640, 360), (20, 40, 80)).save(capa)
        Image.new("RGB", (640, 360), (80, 20, 60)).save(letra)

        arquivo = gerar_slja(
            entrada,
            raiz / "saida",
            capa,
            letra,
            linhas_por_slide=2,
        )

        with ZipFile(arquivo, "r") as z:
            nomes = z.namelist()
            assert "slides.lja" in nomes
            assert r"imagens\capa.jpg" in nomes
            assert r"imagens\letra.jpg" in nomes
            conteudo = z.read("slides.lja").decode("cp1252")

        assert "slides=5" in conteudo
        assert "[Slide:5]" in conteudo

        bloco_final = conteudo.split("[Slide:5]", 1)[1]
        linhas_finais = bloco_final.splitlines()[:7]

        assert "tipo=LETRA" in bloco_final
        assert r"imagem=imagens\letra.jpg" in bloco_final
        assert not any(linha.startswith("letra=") for linha in linhas_finais)

        print("OK - SLJA com tela final vazia validado.")


if __name__ == "__main__":
    executar()
