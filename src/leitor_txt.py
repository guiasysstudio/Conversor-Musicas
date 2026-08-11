from pathlib import Path

LINHAS_POR_SLIDE_PADRAO = 2


def ler_arquivo_txt(caminho_txt):
    caminho_txt = Path(caminho_txt)

    for codificacao in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return caminho_txt.read_text(encoding=codificacao)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Não foi possível ler o arquivo TXT: {caminho_txt.name}")


def separar_titulo_e_paragrafos(texto):
    """
    Regras principais:
    - primeira linha útil = título;
    - linhas seguintes = letra;
    - linha vazia encerra a estrofe;
    - estrofes nunca são misturadas.
    """
    linhas = texto.replace("\r\n", "\n").replace("\r", "\n").splitlines()

    while linhas and not linhas[0].strip():
        linhas.pop(0)

    if not linhas:
        raise ValueError("O arquivo TXT está vazio.")

    titulo = linhas[0].strip()

    if not titulo:
        raise ValueError("A primeira linha do TXT precisa conter o título.")

    paragrafos = []
    atual = []

    for linha in linhas[1:]:
        linha = linha.strip()

        if linha:
            atual.append(linha)
        elif atual:
            paragrafos.append(atual)
            atual = []

    if atual:
        paragrafos.append(atual)

    return titulo, paragrafos


def dividir_paragrafo_em_blocos(paragrafo, linhas_por_slide=LINHAS_POR_SLIDE_PADRAO):
    if linhas_por_slide not in (1, 2, 3):
        raise ValueError("A quantidade de linhas por slide deve ser 1, 2 ou 3.")

    return [
        paragrafo[i:i + linhas_por_slide]
        for i in range(0, len(paragrafo), linhas_por_slide)
    ]


def montar_blocos_sem_misturar_paragrafos(
    paragrafos,
    linhas_por_slide=LINHAS_POR_SLIDE_PADRAO,
):
    """
    Cada estrofe reinicia a divisão.

    Exemplo com 2 linhas/slide:
      Estrofe A: A1, A2, A3 -> [A1,A2] [A3]
      Estrofe B: B1, B2     -> [B1,B2]

    Nunca gera [A3,B1].
    """
    blocos = []

    for paragrafo in paragrafos:
        blocos.extend(
            dividir_paragrafo_em_blocos(paragrafo, linhas_por_slide)
        )

    return blocos


def formatar_titulo(titulo):
    """
    Divide títulos com várias palavras em duas linhas equilibradas.
    A formatação visual continua sendo a do modelo PowerPoint.
    """
    palavras = titulo.split()

    if len(palavras) <= 1:
        return titulo

    meio = (len(palavras) + 1) // 2
    primeira = " ".join(palavras[:meio])
    segunda = " ".join(palavras[meio:])

    if not segunda:
        return primeira

    return primeira + "\r\n" + segunda


def formatar_bloco_letra(bloco):
    return "\r\n".join(bloco)


# Compatibilidade com o módulo SLJA atual.
# O SLJA ainda será revisado separadamente depois.
def ler_txt(caminho):
    texto = ler_arquivo_txt(caminho)
    titulo, paragrafos = separar_titulo_e_paragrafos(texto)

    linhas = []
    for indice, paragrafo in enumerate(paragrafos):
        if indice:
            linhas.append("")
        linhas.extend(paragrafo)

    return titulo, linhas


def dividir_em_telas(linhas, linhas_por_slide=LINHAS_POR_SLIDE_PADRAO):
    paragrafos = []
    atual = []

    for linha in linhas:
        linha = linha.strip()

        if linha:
            atual.append(linha)
        elif atual:
            paragrafos.append(atual)
            atual = []

    if atual:
        paragrafos.append(atual)

    return montar_blocos_sem_misturar_paragrafos(
        paragrafos,
        linhas_por_slide,
    )
