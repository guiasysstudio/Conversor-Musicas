from pathlib import Path
from src.leitor_txt import ler_musica_txt


def test_divisao_por_estrofe(tmp_path: Path):
    p = tmp_path / "m.txt"
    p.write_text("Titulo\n1\n2\n3\n4\n5\n\nA\nB\nC", encoding="utf-8")
    m = ler_musica_txt(p)
    assert m.titulo == "Titulo"
    assert m.telas == [["1", "2"], ["3", "4"], ["5"], ["A", "B"], ["C"]]
