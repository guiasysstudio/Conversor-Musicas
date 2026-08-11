from __future__ import annotations

import ctypes
from pathlib import Path
from ctypes import wintypes


# FOLDERID_Documents = {FDD39AD0-238F-46AF-ADB4-6C85480369C7}
_FOLDERID_DOCUMENTS = ctypes.c_byte * 16
_FOLDERID_DOCUMENTS_VALUE = _FOLDERID_DOCUMENTS(
    0xD0, 0x9A, 0xD3, 0xFD,
    0x8F, 0x23,
    0xAF, 0x46,
    0xAD, 0xB4,
    0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7
)


def pasta_documentos() -> Path:
    """
    Retorna a pasta Documentos real configurada no Windows.
    Funciona inclusive quando Documentos foi redirecionado para OneDrive
    ou outro local. Em caso de falha, usa ~/Documents.
    """
    try:
        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32

        path_ptr = ctypes.c_wchar_p()

        # SHGetKnownFolderPath(REFKNOWNFOLDERID, DWORD, HANDLE, PWSTR*)
        resultado = shell32.SHGetKnownFolderPath(
            ctypes.byref(_FOLDERID_DOCUMENTS_VALUE),
            0,
            None,
            ctypes.byref(path_ptr),
        )

        if resultado == 0 and path_ptr.value:
            caminho = Path(path_ptr.value)
            ole32.CoTaskMemFree(path_ptr)
            return caminho

    except Exception:
        pass

    fallback = Path.home() / "Documents"
    if fallback.exists():
        return fallback

    return Path.home()


def pasta_inicial_para_diretorio(valor_atual: str | Path | None) -> Path:
    """
    Para seletores de pasta:
    - se o caminho atual existir e for uma pasta, abre nele;
    - se apontar para um arquivo, abre na pasta pai;
    - se não existir, sobe até encontrar um pai existente;
    - por fim, usa Documentos.
    """
    if valor_atual:
        caminho = Path(str(valor_atual)).expanduser()

        if caminho.exists():
            if caminho.is_dir():
                return caminho
            return caminho.parent

        atual = caminho
        while atual != atual.parent:
            atual = atual.parent
            if atual.exists() and atual.is_dir():
                return atual

    return pasta_documentos()


def pasta_inicial_para_arquivo(valor_atual: str | Path | None) -> Path:
    """
    Para seletores de arquivo:
    - se já existe um arquivo selecionado, reabre na pasta dele;
    - se o campo contém uma pasta, abre nessa pasta;
    - caso contrário, usa Documentos.
    """
    if valor_atual:
        caminho = Path(str(valor_atual)).expanduser()

        if caminho.exists():
            if caminho.is_file():
                return caminho.parent
            if caminho.is_dir():
                return caminho

        # Se o arquivo deixou de existir mas a pasta pai ainda existe,
        # ainda abrimos nessa pasta.
        pai = caminho.parent
        if pai.exists() and pai.is_dir():
            return pai

    return pasta_documentos()
