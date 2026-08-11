from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile

from .leitor_txt import ler_txt, dividir_em_telas

def _normalizar_nome(nome):
    return "".join(c if c not in '<>:"/\\|?*' else "_" for c in nome).strip()

def gerar_slja(caminho_txt, pasta_saida, imagem_capa, imagem_letra):
    caminho_txt = Path(caminho_txt)
    pasta_saida = Path(pasta_saida)
    imagem_capa = Path(imagem_capa)
    imagem_letra = Path(imagem_letra)

    if not imagem_capa.is_file():
        raise FileNotFoundError("A imagem do primeiro slide não foi encontrada.")
    if not imagem_letra.is_file():
        raise FileNotFoundError("A imagem dos demais slides não foi encontrada.")

    titulo, linhas = ler_txt(caminho_txt)
    telas = dividir_em_telas(linhas)

    nome_base = _normalizar_nome(titulo) or caminho_txt.stem
    destino = pasta_saida / f"{nome_base}.slja"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Nomes internos curtos e previsíveis
    ext_capa = imagem_capa.suffix.lower() or ".jpg"
    ext_letra = imagem_letra.suffix.lower() or ".jpg"
    nome_capa = f"capa{ext_capa}"
    nome_letra = f"letra{ext_letra}"

    total_slides = 1 + len(telas)

    linhas_lja = [
        "[Geral]",
        f"slides={total_slides}",
        "audio=0",
        "url_musica=",
        "",
        "[Slide:1]",
        "tipo=CAPA",
        f"letra={titulo}",
        "fundo_letra=1",
        f"imagem=imagens\\{nome_capa}",
        "tempo=00:00:00",
        "",
    ]

    for indice, tela in enumerate(telas, start=2):
        letra = "|".join(tela)
        linhas_lja.extend([
            f"[Slide:{indice}]",
            "tipo=LETRA",
            f"letra={letra}",
            "fundo_letra=1",
            f"imagem=imagens\\{nome_letra}",
            "tempo=00:00:00",
            "",
        ])

    conteudo_lja = "\r\n".join(linhas_lja)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        (temp / "imagens").mkdir()
        (temp / "audio").mkdir()
        (temp / "slides.lja").write_bytes(conteudo_lja.encode("cp1252", errors="replace"))
        shutil.copy2(imagem_capa, temp / "imagens" / nome_capa)
        shutil.copy2(imagem_letra, temp / "imagens" / nome_letra)

        with ZipFile(destino, "w", ZIP_DEFLATED) as zipf:
            for arquivo in temp.rglob("*"):
                if arquivo.is_file():
                    zipf.write(arquivo, arquivo.relative_to(temp))

    return destino
