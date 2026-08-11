# Conversor Músicas

Programa Windows para conversão em lote de letras em TXT para:

- PowerPoint (`.pptx`)
- SLJA sem áudio (`.slja`)

## Regra do TXT

- Primeira linha: título da música.
- Restante: letra.
- Linha em branco: separa estrofes.
- Cada estrofe é dividida em blocos de até 2 linhas.

Exemplo com 5 linhas:
- slide/tela 1 = linhas 1 e 2
- slide/tela 2 = linhas 3 e 4
- slide/tela 3 = linha 5

## PowerPoint

Os modelos ficam em:

`modelos/powerpoint`

O seletor do programa carrega automaticamente todos os arquivos `.pptx` dessa pasta.

Cada modelo deve ter pelo menos:
- slide 1: modelo de capa/título
- slide 2: modelo da letra

## SLJA

Ao escolher `SLJA sem áudio (.slja)`, o seletor de modelo PowerPoint desaparece.

No lugar dele aparecem:
- Imagem do primeiro slide (título)
- Imagem dos demais slides (letra)

O programa cria o `.slja` sem áudio, com `slides.lja`, pasta `imagens` e pasta `audio`.

## Executar

No terminal do VS Code:

```powershell
py -m pip install -r requirements.txt
py main.py
```
