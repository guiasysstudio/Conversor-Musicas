# Conversor Músicas v1.2.1

Conversor Windows para:

- TXT → PowerPoint (`.pptx`)
- TXT → SLJA sem áudio (`.slja`)

## GitHub oficial

Repositório:

`guiasysstudio/Conversor-Musicas`

## Atualização automática

O programa verifica automaticamente o **GitHub Releases** aproximadamente 1,4 segundo após abrir.

Se houver uma versão superior à instalada, aparece automaticamente um popup com:

- **Atualizar**
- **Cancelar**

Ao escolher **Atualizar**:

1. o instalador `.exe` anexado à Release é baixado;
2. o progresso é exibido;
3. o programa pede confirmação;
4. abre o instalador;
5. fecha a versão antiga.

O atualizador procura preferencialmente pelo asset:

`Conversor-Musicas-Setup.exe`

Se esse nome não existir, ele procura outro `.exe` que contenha `setup`, `installer` ou `instalador`.

### Tags das Releases

Use tags de versão, por exemplo:

- `v1.2.1`
- `v1.2.2`
- `v1.3.0`

A versão interna fica em:

`src/versao.py`

## Executar

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Primeiro envio ao GitHub pelo VS Code

Na pasta do projeto:

```powershell
git init
git add .
git commit -m "feat: cria Conversor Músicas v1.2.1"
git branch -M main
git remote add origin https://github.com/guiasysstudio/Conversor-Musicas.git
git push -u origin main
```

Se `origin` já existir:

```powershell
git remote set-url origin https://github.com/guiasysstudio/Conversor-Musicas.git
git push -u origin main
```


## Regras de conversão PowerPoint

Em `Configurações > Regras de conversão` é possível selecionar:

- 1 linha por slide
- 2 linhas por slide (padrão)
- 3 linhas por slide

A escolha é persistente e a divisão sempre reinicia a cada estrofe.
