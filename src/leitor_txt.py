from pathlib import Path

def ler_txt(caminho):
    caminho = Path(caminho)
    texto = None
    for codificacao in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            texto = caminho.read_text(encoding=codificacao)
            break
        except UnicodeDecodeError:
            continue
    if texto is None:
        raise ValueError(f"Não foi possível ler o arquivo: {caminho.name}")

    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    linhas = texto.split("\n")

    # Remove apenas linhas vazias do início e do fim.
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    while linhas and not linhas[-1].strip():
        linhas.pop()

    if not linhas:
        raise ValueError(f"O arquivo {caminho.name} está vazio.")

    titulo = linhas[0].strip()
    letra = linhas[1:]
    if not titulo:
        raise ValueError(f"O arquivo {caminho.name} não possui título na primeira linha.")

    return titulo, letra


def dividir_em_telas(linhas):
    """
    Uma linha vazia separa estrofes.
    Cada estrofe é dividida em blocos de até 2 linhas.
    """
    estrofes = []
    atual = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            if atual:
                estrofes.append(atual)
                atual = []
            continue
        atual.append(linha)

    if atual:
        estrofes.append(atual)

    telas = []
    for estrofe in estrofes:
        for i in range(0, len(estrofe), 2):
            telas.append(estrofe[i:i+2])

    return telas
