from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[1] / "src" / "interface.py"
texto = ARQUIVO.read_text(encoding="utf-8")

assert 'values=["-", "1", "2", "3"]' in texto
assert "CTkScrollableFrame" in texto
assert "_regra_efetiva_arquivo" in texto
assert "linhas_por_slide=regra_arquivo" in texto
assert "_aplicar_regra_selecionados" in texto
assert "_remover_selecionados" in texto

print("OK - regras individuais e lista rolável encontradas.")
