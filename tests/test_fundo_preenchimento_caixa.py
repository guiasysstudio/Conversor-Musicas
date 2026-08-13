from pathlib import Path

arquivo = Path(__file__).resolve().parents[1] / "src" / "gerador_pptx.py"
texto = arquivo.read_text(encoding="utf-8")

assert "def _caixa_tem_preenchimento_visivel" in texto
assert "shape.Fill.Visible" in texto
assert "def _ajustar_altura_da_caixa_com_preenchimento" in texto
assert 'return "preenchimento_caixa"' in texto
assert 'return "shape_separado"' in texto
assert "ajustar_fundo_letra(slide, caixa_letra, altura_slide)" in texto

print("OK - suporte aos dois tipos de fundo encontrado.")
