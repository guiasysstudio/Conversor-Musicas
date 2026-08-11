from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from io import BytesIO

from PIL import Image, ImageOps

from .leitor_txt import (
    ler_arquivo_txt,
    separar_titulo_e_paragrafos,
    montar_blocos_sem_misturar_paragrafos,
)


def _normalizar_nome(nome):
    return "".join(
        c if c not in '<>:"/\\|?*' else "_"
        for c in nome
    ).strip()


def _imagem_para_jpeg(caminho_imagem, qualidade=95):
    """
    O formato SLJA de referência usa imagens JPG.
    Para garantir compatibilidade, PNG/BMP/etc. são convertidos
    internamente para JPG antes de entrar no pacote SLJA.
    """
    caminho_imagem = Path(caminho_imagem)

    with Image.open(caminho_imagem) as imagem:
        imagem = ImageOps.exif_transpose(imagem)

        # JPEG não suporta transparência.
        # Quando houver alpha, compõe sobre fundo preto.
        if imagem.mode in ("RGBA", "LA") or "transparency" in imagem.info:
            rgba = imagem.convert("RGBA")
            fundo = Image.new("RGB", rgba.size, (0, 0, 0))
            fundo.paste(rgba, mask=rgba.getchannel("A"))
            imagem = fundo
        else:
            imagem = imagem.convert("RGB")

        memoria = BytesIO()
        imagem.save(
            memoria,
            format="JPEG",
            quality=qualidade,
            optimize=True,
            subsampling=0,
        )
        return memoria.getvalue()


def _adicionar_arquivo_windows(zipf, nome_interno, dados):
    """
    Os SLJA reais fornecidos usam nomes internos no ZIP com barra invertida:
        imagens\\generico_113.jpg

    Alguns leitores aceitam '/' e '\\' como equivalentes, mas o Louvor JA
    utiliza a estrutura Windows original. Por isso gravamos exatamente com '\\'.
    """
    info = ZipInfo(nome_interno)
    info.create_system = 0
    info.external_attr = 0x20
    info.compress_type = ZIP_DEFLATED
    info.flag_bits |= 0x800

    zipf.writestr(info, dados)


def gerar_slja(
    caminho_txt,
    pasta_saida,
    imagem_capa,
    imagem_letra,
    linhas_por_slide=2,
):
    caminho_txt = Path(caminho_txt)
    pasta_saida = Path(pasta_saida)
    imagem_capa = Path(imagem_capa)
    imagem_letra = Path(imagem_letra)

    if linhas_por_slide not in (1, 2, 3):
        raise ValueError(
            "A regra de linhas por tela deve ser 1, 2 ou 3."
        )

    if not caminho_txt.is_file():
        raise FileNotFoundError("O arquivo TXT não foi encontrado.")

    if not imagem_capa.is_file():
        raise FileNotFoundError(
            "A imagem do primeiro slide não foi encontrada."
        )

    if not imagem_letra.is_file():
        raise FileNotFoundError(
            "A imagem dos demais slides não foi encontrada."
        )

    texto = ler_arquivo_txt(caminho_txt)
    titulo, paragrafos = separar_titulo_e_paragrafos(texto)

    telas = montar_blocos_sem_misturar_paragrafos(
        paragrafos,
        linhas_por_slide=linhas_por_slide,
    )

    nome_base = _normalizar_nome(titulo) or caminho_txt.stem

    pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = pasta_saida / f"{nome_base}.slja"

    # O Louvor JA de referência utiliza JPG nos arquivos SLJA.
    nome_capa = "capa.jpg"
    nome_letra = "letra.jpg"

    capa_jpg = _imagem_para_jpeg(imagem_capa)
    letra_jpg = _imagem_para_jpeg(imagem_letra)

    # Capa + telas da letra + uma tela final vazia.
    total_slides = 1 + len(telas) + 1

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

    # Tela final vazia, igual ao padrão dos SLJA reais analisados.
    indice_final = 2 + len(telas)

    linhas_lja.extend([
        f"[Slide:{indice_final}]",
        "tipo=LETRA",
        "fundo_letra=1",
        f"imagem=imagens\\{nome_letra}",
        "tempo=00:00:00",
        "",
    ])

    # O arquivo de referência usa CRLF e Windows-1252.
    conteudo_lja = "\r\n".join(linhas_lja)
    dados_lja = conteudo_lja.encode(
        "cp1252",
        errors="replace",
    )

    with ZipFile(
        destino,
        "w",
        compression=ZIP_DEFLATED,
    ) as zipf:
        _adicionar_arquivo_windows(
            zipf,
            "slides.lja",
            dados_lja,
        )

        _adicionar_arquivo_windows(
            zipf,
            r"imagens\capa.jpg",
            capa_jpg,
        )

        _adicionar_arquivo_windows(
            zipf,
            r"imagens\letra.jpg",
            letra_jpg,
        )

    return destino
