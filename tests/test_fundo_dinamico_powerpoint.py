from pathlib import Path

arquivo = Path(__file__).resolve().parents[1] / "src" / "gerador_pptx.py"
texto = arquivo.read_text(encoding="utf-8")

assert 'NOME_FUNDO_LETRA = "fundo_letra"' in texto
assert "def ajustar_fundo_letra" in texto
assert "BoundTop" in texto
assert "BoundHeight" in texto
assert "slide_letra_modelo" in texto
assert "novo_slide" in texto

print("OK - suporte ao fundo dinâmico encontrado.")
