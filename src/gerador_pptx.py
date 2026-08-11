from pathlib import Path
import shutil

try:
    import win32com.client as win32
except ImportError:
    win32 = None

from .leitor_txt import (
    ler_arquivo_txt,
    separar_titulo_e_paragrafos,
    montar_blocos_sem_misturar_paragrafos,
    formatar_titulo,
    formatar_bloco_letra,
)


NOME_CAIXA_TITULO = "caixa_titulo"
NOME_CAIXA_LETRA = "caixa_letra"


def obter_shape_por_nome(slide, nome_shape):
    try:
        for indice in range(1, slide.Shapes.Count + 1):
            shape = slide.Shapes(indice)
            if str(shape.Name).strip().lower() == nome_shape.strip().lower():
                return shape
    except Exception:
        pass

    return None


def preencher_shape(shape, texto):
    try:
        shape.TextFrame.TextRange.Text = texto
        return True
    except Exception:
        return False


def desligar_autoajuste(shape):
    """
    Replica o comportamento do gerador antigo:
    a caixa da letra fica com tamanho fixo, sem o PowerPoint alterar
    sua geometria por causa do conteúdo.
    """
    acoes = [
        lambda: setattr(shape.TextFrame, "AutoSize", 0),     # ppAutoSizeNone
        lambda: setattr(shape.TextFrame, "WordWrap", True),
        lambda: setattr(shape.TextFrame, "MarginTop", 0),
        lambda: setattr(shape.TextFrame, "MarginBottom", 0),
        lambda: setattr(shape.TextFrame, "MarginLeft", 0),
        lambda: setattr(shape.TextFrame, "MarginRight", 0),
        lambda: setattr(shape.TextFrame, "VerticalAnchor", 3),  # msoAnchorMiddle
        lambda: setattr(
            shape.TextFrame.TextRange.ParagraphFormat,
            "Alignment",
            2,  # ppAlignCenter
        ),
        lambda: setattr(shape.TextFrame2, "AutoSize", 0),    # msoAutoSizeNone
        lambda: setattr(shape.TextFrame2, "WordWrap", True),
        lambda: setattr(shape.TextFrame2, "MarginTop", 0),
        lambda: setattr(shape.TextFrame2, "MarginBottom", 0),
        lambda: setattr(shape.TextFrame2, "MarginLeft", 0),
        lambda: setattr(shape.TextFrame2, "MarginRight", 0),
        lambda: setattr(shape.TextFrame2, "VerticalAnchor", 3),
        lambda: setattr(
            shape.TextFrame2.TextRange.ParagraphFormat,
            "Alignment",
            2,
        ),
    ]

    for acao in acoes:
        try:
            acao()
        except Exception:
            # Algumas versões do PowerPoint podem não expor todas
            # as propriedades em TextFrame e TextFrame2 ao mesmo tempo.
            pass


def restaurar_geometria(shape_destino, left, top, width, height):
    try:
        shape_destino.Left = left
        shape_destino.Top = top
        shape_destino.Width = width
        shape_destino.Height = height
    except Exception:
        pass


def alinhar_shape_ao_meio_vertical_do_slide(shape, altura_slide):
    try:
        shape.Top = int((altura_slide - shape.Height) / 2)
    except Exception:
        pass


def preparar_caixa_letra(shape, left, width, height, altura_slide):
    desligar_autoajuste(shape)

    try:
        shape.Left = left
    except Exception:
        pass

    try:
        shape.Width = width
    except Exception:
        pass

    try:
        shape.Height = height
    except Exception:
        pass

    alinhar_shape_ao_meio_vertical_do_slide(shape, altura_slide)


def _abrir_powerpoint():
    if win32 is None:
        raise RuntimeError(
            "O componente pywin32 não está instalado. "
            "Reinstale o Conversor Músicas ou execute "
            "'py -m pip install pywin32'."
        )

    try:
        powerpoint = win32.Dispatch("PowerPoint.Application")
        powerpoint.Visible = True
        return powerpoint
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível abrir o Microsoft PowerPoint. "
            "Verifique se o PowerPoint está instalado corretamente."
        ) from erro


def gerar_ppt_com_modelo(caminho_modelo, caminho_saida, titulo, blocos):
    """
    Mesmo método do Gerador PPT Músicas original:

    1. copia o modelo inteiro para o arquivo de saída;
    2. abre a cópia no Microsoft PowerPoint;
    3. usa o slide 1 como CAPA;
    4. usa o slide 2 como MODELO DA LETRA;
    5. duplica o slide 2 dentro da própria apresentação para cada bloco;
    6. mantém mestre, fundo, imagens, tema, fontes e demais elementos do PPT;
    7. preserva os slides a partir do slide 3 do modelo.
    """
    caminho_modelo = Path(caminho_modelo)
    caminho_saida = Path(caminho_saida)

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    # Esta é a diferença essencial para a versão anterior:
    # NÃO cria um PPT novo. Trabalha sobre uma cópia exata do modelo.
    shutil.copy2(caminho_modelo, caminho_saida)

    powerpoint = None
    apresentacao = None

    try:
        powerpoint = _abrir_powerpoint()

        apresentacao = powerpoint.Presentations.Open(
            str(caminho_saida.resolve())
        )

        if apresentacao.Slides.Count < 3:
            raise ValueError(
                "O modelo PowerPoint precisa ter pelo menos 3 slides: "
                "slide 1 para título, slide 2 para letra e slide 3 como encerramento."
            )

        slide_titulo = apresentacao.Slides(1)
        slide_letra_modelo = apresentacao.Slides(2)

        caixa_titulo = obter_shape_por_nome(
            slide_titulo,
            NOME_CAIXA_TITULO
        )
        caixa_letra = obter_shape_por_nome(
            slide_letra_modelo,
            NOME_CAIXA_LETRA
        )

        if caixa_titulo is None:
            raise ValueError(
                f"Não encontrei a caixa '{NOME_CAIXA_TITULO}' no slide 1."
            )

        if caixa_letra is None:
            raise ValueError(
                f"Não encontrei a caixa '{NOME_CAIXA_LETRA}' no slide 2."
            )

        # Geometria original da capa.
        titulo_left = caixa_titulo.Left
        titulo_top = caixa_titulo.Top
        titulo_width = caixa_titulo.Width
        titulo_height = caixa_titulo.Height

        # Geometria-base da letra.
        letra_left = caixa_letra.Left
        letra_width = caixa_letra.Width
        letra_height = caixa_letra.Height
        altura_slide = apresentacao.PageSetup.SlideHeight

        # CAPA
        titulo_formatado = formatar_titulo(titulo)

        if not preencher_shape(caixa_titulo, titulo_formatado):
            raise RuntimeError(
                "Não consegui preencher a caixa do título."
            )

        # O modelo pode ter AutoSize ativo na capa.
        # Restauramos exatamente a caixa original após trocar o texto.
        restaurar_geometria(
            caixa_titulo,
            titulo_left,
            titulo_top,
            titulo_width,
            titulo_height,
        )

        # PRIMEIRO SLIDE DE LETRA
        primeira_letra = (
            formatar_bloco_letra(blocos[0])
            if blocos
            else ""
        )

        preparar_caixa_letra(
            caixa_letra,
            letra_left,
            letra_width,
            letra_height,
            altura_slide,
        )

        if not preencher_shape(caixa_letra, primeira_letra):
            raise RuntimeError(
                "Não consegui preencher a caixa da letra no slide 2."
            )

        preparar_caixa_letra(
            caixa_letra,
            letra_left,
            letra_width,
            letra_height,
            altura_slide,
        )

        # Os novos slides entram a partir da posição 3.
        # Assim, qualquer slide 3+ do modelo continua no final.
        indice_insercao = 3

        for numero_bloco, bloco in enumerate(blocos[1:], start=2):
            texto_bloco = formatar_bloco_letra(bloco)

            # Copia o slide dentro do PowerPoint real.
            # Isso preserva fundo, master, tema, imagens e formatação.
            slide_letra_modelo.Copy()

            faixa_colada = apresentacao.Slides.Paste(
                Index=indice_insercao
            )

            # SlideRange retornado pelo PowerPoint é indexado a partir de 1.
            try:
                novo_slide = faixa_colada(1)
            except Exception:
                try:
                    novo_slide = faixa_colada.Item(1)
                except Exception:
                    novo_slide = apresentacao.Slides(indice_insercao)

            nova_caixa_letra = obter_shape_por_nome(
                novo_slide,
                NOME_CAIXA_LETRA
            )

            if nova_caixa_letra is None:
                raise ValueError(
                    f"Não encontrei a caixa '{NOME_CAIXA_LETRA}' "
                    f"no slide duplicado {indice_insercao}."
                )

            preparar_caixa_letra(
                nova_caixa_letra,
                letra_left,
                letra_width,
                letra_height,
                altura_slide,
            )

            if not preencher_shape(nova_caixa_letra, texto_bloco):
                raise RuntimeError(
                    "Não consegui preencher a caixa da letra "
                    f"no slide duplicado {indice_insercao}."
                )

            preparar_caixa_letra(
                nova_caixa_letra,
                letra_left,
                letra_width,
                letra_height,
                altura_slide,
            )

            indice_insercao += 1

        apresentacao.Save()

    finally:
        if apresentacao is not None:
            try:
                apresentacao.Close()
            except Exception:
                pass

        if powerpoint is not None:
            try:
                powerpoint.Quit()
            except Exception:
                pass


def gerar_pptx(caminho_txt, pasta_saida, modelo_pptx, linhas_por_slide=2):
    caminho_txt = Path(caminho_txt)
    pasta_saida = Path(pasta_saida)
    modelo_pptx = Path(modelo_pptx)

    if not caminho_txt.is_file():
        raise FileNotFoundError(
            f"Arquivo TXT não encontrado: {caminho_txt}"
        )

    if linhas_por_slide not in (1, 2, 3):
        raise ValueError("A regra de linhas por slide deve ser 1, 2 ou 3.")

    if not modelo_pptx.is_file():
        raise FileNotFoundError(
            "O modelo PowerPoint selecionado não foi encontrado."
        )

    texto = ler_arquivo_txt(caminho_txt)
    titulo, paragrafos = separar_titulo_e_paragrafos(texto)

    blocos = montar_blocos_sem_misturar_paragrafos(
        paragrafos,
        linhas_por_slide=linhas_por_slide,
    )

    caminho_saida = pasta_saida / f"{caminho_txt.stem}.pptx"

    gerar_ppt_com_modelo(
        caminho_modelo=modelo_pptx,
        caminho_saida=caminho_saida,
        titulo=titulo,
        blocos=blocos,
    )

    return caminho_saida
