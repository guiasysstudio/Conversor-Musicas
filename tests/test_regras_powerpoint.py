from src.leitor_txt import (
    separar_titulo_e_paragrafos,
    montar_blocos_sem_misturar_paragrafos,
)


TEXTO = """Minha Música
Linha 1
Linha 2
Linha 3
Linha 4
Linha 5

Outra 1
Outra 2
Outra 3
"""


def executar():
    titulo, paragrafos = separar_titulo_e_paragrafos(TEXTO)

    assert titulo == "Minha Música"

    regra_1 = montar_blocos_sem_misturar_paragrafos(paragrafos, 1)
    assert regra_1 == [
        ["Linha 1"],
        ["Linha 2"],
        ["Linha 3"],
        ["Linha 4"],
        ["Linha 5"],
        ["Outra 1"],
        ["Outra 2"],
        ["Outra 3"],
    ]

    regra_2 = montar_blocos_sem_misturar_paragrafos(paragrafos, 2)
    assert regra_2 == [
        ["Linha 1", "Linha 2"],
        ["Linha 3", "Linha 4"],
        ["Linha 5"],
        ["Outra 1", "Outra 2"],
        ["Outra 3"],
    ]

    regra_3 = montar_blocos_sem_misturar_paragrafos(paragrafos, 3)
    assert regra_3 == [
        ["Linha 1", "Linha 2", "Linha 3"],
        ["Linha 4", "Linha 5"],
        ["Outra 1", "Outra 2", "Outra 3"],
    ]

    print("OK - As regras 1, 2 e 3 linhas por slide estão funcionando.")


if __name__ == "__main__":
    executar()
