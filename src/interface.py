import os
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from .caminhos import (
    PASTA_MODELOS, PASTA_MODELOS_PPTX, PASTA_IMAGENS_SLJA,
    PASTA_SAIDA, ARQUIVO_LOGO, garantir_pastas
)
from .gerador_pptx import gerar_pptx
from .gerador_slja import gerar_slja
from .versao import VERSAO, NOME_APP
from .pastas_windows import (
    pasta_documentos,
    pasta_inicial_para_diretorio,
    pasta_inicial_para_arquivo,
)
from .configuracoes import carregar_configuracoes, salvar_configuracoes, restaurar_padrao
from .atualizador import verificar_atualizacao, configurado, baixar_instalador, executar_instalador


# Paleta oficial
FUNDO = "#071526"
FUNDO_2 = "#0D2340"
CARD = "#12345A"
AZUL = "#008CFF"
CIANO = "#00D9FF"
ROXO = "#7A18FF"
MAGENTA = "#D719FF"
POWERPOINT = "#F04418"
SLJA = "#6A0DDB"
TEXTO = "#F4F8FF"
TEXTO_2 = "#A8BAD0"
BORDA = "#29496C"
SUCESSO = "#25C985"
AVISO = "#FFBF3F"
ERRO = "#FF4D5E"


class ConversorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        garantir_pastas()

        ctk.set_appearance_mode("dark")
        self.title(f"{NOME_APP} v{VERSAO}")
        self.geometry("1120x760")
        self.minsize(1040, 700)
        self.configure(fg_color=FUNDO)

        self.arquivos = []
        # Regra individual por arquivo:
        # "-" = segue a regra padrão do programa.
        self.regras_arquivo = {}
        self.selecao_arquivo = {}
        self.tipo = tk.StringVar(value="PowerPoint")
        self.modelo = tk.StringVar()
        self.pasta_saida = tk.StringVar(value=str(pasta_documentos()))
        self.imagem_capa = tk.StringVar()
        self.imagem_letra = tk.StringVar()
        self.status = tk.StringVar(value="Pronto para converter.")
        self.configuracoes = carregar_configuracoes()
        self.linhas_por_slide = int(self.configuracoes.get("linhas_por_slide", 2))
        self.regra_atual = tk.StringVar()
        self._atualizar_texto_regra()

        self._montar_interface()
        self._carregar_modelos()
        self._trocar_tipo("PowerPoint")
        self.after(1400, self._verificar_update_automatico)

    # ---------- layout ----------
    def _montar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=30, pady=(24, 14))
        cabecalho.grid_columnconfigure(1, weight=1)

        if ARQUIVO_LOGO.exists():
            imagem = Image.open(ARQUIVO_LOGO)
            imagem.thumbnail((88, 62))
            self.logo_img = ctk.CTkImage(imagem, size=imagem.size)
            ctk.CTkLabel(cabecalho, text="", image=self.logo_img).grid(
                row=0, column=0, rowspan=2, padx=(0, 16)
            )

        ctk.CTkLabel(
            cabecalho, text=NOME_APP,
            text_color=TEXTO,
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=1, sticky="sw")

        ctk.CTkLabel(
            cabecalho,
            text="Converta letras TXT para PowerPoint ou SLJA sem áudio",
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=1, sticky="nw", pady=(2, 0))

        self.chip_regra = ctk.CTkLabel(
            cabecalho,
            textvariable=self.regra_atual,
            fg_color=FUNDO_2,
            text_color=TEXTO_2,
            corner_radius=10,
            padx=14,
            pady=8,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.chip_regra.grid(row=0, column=2, rowspan=2, padx=(14, 0))

        ctk.CTkButton(
            cabecalho,
            text="⚙",
            width=48,
            height=42,
            corner_radius=12,
            fg_color=FUNDO_2,
            hover_color=CARD,
            border_width=1,
            border_color=BORDA,
            font=ctk.CTkFont(size=22),
            command=self._abrir_configuracoes
        ).grid(row=0, column=3, rowspan=2, padx=(10, 0))

        conteudo = ctk.CTkFrame(
            self,
            fg_color=FUNDO_2,
            corner_radius=18,
            border_width=1,
            border_color=BORDA
        )
        conteudo.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 18))
        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_columnconfigure(1, weight=1)
        conteudo.grid_rowconfigure(1, weight=1)

        # Seletor
        seletor = ctk.CTkFrame(conteudo, fg_color="transparent")
        seletor.grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(22, 14))
        seletor.grid_columnconfigure((0, 1), weight=1)

        self.btn_ppt = ctk.CTkButton(
            seletor, text="▣  PowerPoint",
            height=50, corner_radius=14,
            fg_color=POWERPOINT, hover_color="#C93816",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self._trocar_tipo("PowerPoint")
        )
        self.btn_ppt.grid(row=0, column=0, sticky="ew", padx=(0, 7))

        self.btn_slja = ctk.CTkButton(
            seletor, text="♫  SLJA sem áudio",
            height=50, corner_radius=14,
            fg_color=CARD, hover_color=SLJA,
            text_color=TEXTO,
            border_width=1, border_color=BORDA,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self._trocar_tipo("SLJA")
        )
        self.btn_slja.grid(row=0, column=1, sticky="ew", padx=(7, 0))

        # Esquerda: arquivos
        arquivos_card = self._card(conteudo, "Arquivos TXT", "Selecione uma ou várias músicas")
        arquivos_card.grid(row=1, column=0, sticky="nsew", padx=(22, 10), pady=(0, 22))
        arquivos_card.grid_rowconfigure(4, weight=1)
        arquivos_card.grid_columnconfigure(0, weight=1)

        botoes = ctk.CTkFrame(arquivos_card, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 10))

        ctk.CTkButton(
            botoes, text="+ Selecionar TXT",
            fg_color=AZUL, hover_color="#0075D6",
            height=38, corner_radius=10,
            font=ctk.CTkFont(weight="bold"),
            command=self._selecionar_txt
        ).pack(side="left")

        ctk.CTkButton(
            botoes, text="Limpar",
            fg_color="transparent", hover_color=CARD,
            border_width=1, border_color=BORDA,
            height=38, corner_radius=10,
            command=self._limpar
        ).pack(side="left", padx=(10, 0))

        # Cabeçalho da lista.
        cab_lista = ctk.CTkFrame(arquivos_card, fg_color="transparent")
        cab_lista.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 5))
        cab_lista.grid_columnconfigure(1, weight=1)

        self.var_todos = tk.BooleanVar(value=False)
        self.chk_todos = ctk.CTkCheckBox(
            cab_lista,
            text="",
            variable=self.var_todos,
            width=26,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=AZUL,
            hover_color="#0075D6",
            command=self._marcar_todos,
        )
        self.chk_todos.grid(row=0, column=0, sticky="w", padx=(2, 7))

        ctk.CTkLabel(
            cab_lista,
            text="Arquivo",
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            cab_lista,
            text="Regra",
            width=66,
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(row=0, column=2, sticky="e", padx=(8, 3))

        # Área rolável. Quando a quantidade ultrapassar a altura do card,
        # a barra de rolagem aparece automaticamente.
        self.lista_scroll = ctk.CTkScrollableFrame(
            arquivos_card,
            fg_color=FUNDO,
            border_width=1,
            border_color=BORDA,
            corner_radius=12,
            scrollbar_button_color=CARD,
            scrollbar_button_hover_color=AZUL,
        )
        self.lista_scroll.grid(
            row=4, column=0, sticky="nsew",
            padx=18, pady=(0, 10)
        )
        self.lista_scroll.grid_columnconfigure(0, weight=1)

        # Aplicação em lote das regras.
        lote = ctk.CTkFrame(arquivos_card, fg_color="transparent")
        lote.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 16))
        lote.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            lote,
            text='Regra dos selecionados  ("-" = padrão)',
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=10),
        ).grid(row=0, column=0, sticky="w")

        self.regra_lote = tk.StringVar(value="-")
        self.combo_regra_lote = ctk.CTkComboBox(
            lote,
            variable=self.regra_lote,
            values=["-", "1", "2", "3"],
            width=72,
            height=34,
            state="readonly",
            fg_color=FUNDO,
            border_color=BORDA,
            button_color=AZUL,
            button_hover_color="#0075D6",
            text_color=TEXTO,
        )
        self.combo_regra_lote.grid(row=0, column=1, padx=(8, 6))

        ctk.CTkButton(
            lote,
            text="Aplicar",
            width=72,
            height=34,
            fg_color=CARD,
            hover_color="#18436F",
            border_width=1,
            border_color=BORDA,
            command=self._aplicar_regra_selecionados,
        ).grid(row=0, column=2)

        ctk.CTkButton(
            lote,
            text="Remover",
            width=76,
            height=34,
            fg_color="transparent",
            hover_color="#5A1F2A",
            border_width=1,
            border_color=BORDA,
            command=self._remover_selecionados,
        ).grid(row=0, column=3, padx=(6, 0))

        # Direita: configuração
        config_card = self._card(conteudo, "Configuração", "Opções da conversão selecionada")
        config_card.grid(row=1, column=1, sticky="nsew", padx=(10, 22), pady=(0, 22))
        config_card.grid_columnconfigure(0, weight=1)

        self.area_dinamica = ctk.CTkFrame(config_card, fg_color="transparent")
        self.area_dinamica.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 6))
        self.area_dinamica.grid_columnconfigure(0, weight=1)

        self._rotulo(config_card, "Pasta de saída").grid(
            row=3, column=0, sticky="w", padx=18, pady=(10, 5)
        )

        saida_linha = ctk.CTkFrame(config_card, fg_color="transparent")
        saida_linha.grid(row=4, column=0, sticky="ew", padx=18)
        saida_linha.grid_columnconfigure(0, weight=1)

        self.entrada_saida = ctk.CTkEntry(
            saida_linha, textvariable=self.pasta_saida,
            fg_color=FUNDO, border_color=BORDA,
            text_color=TEXTO, height=38
        )
        self.entrada_saida.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            saida_linha, text="Selecionar",
            width=100, height=38,
            fg_color=CARD, hover_color="#18436F",
            command=self._escolher_saida
        ).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkButton(
            config_card, text="Abrir pasta de saída",
            fg_color="transparent", hover_color=CARD,
            border_width=1, border_color=BORDA,
            height=36, command=self._abrir_saida
        ).grid(row=5, column=0, sticky="w", padx=18, pady=(10, 0))

        # Rodapé
        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 24))
        rodape.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            rodape, textvariable=self.status,
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, sticky="w")

        self.btn_converter = ctk.CTkButton(
            rodape,
            text="Converter arquivos",
            width=190, height=46,
            corner_radius=13,
            fg_color=AZUL, hover_color=CIANO,
            text_color=TEXTO,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._converter
        )
        self.btn_converter.grid(row=0, column=1, sticky="e")

    def _card(self, parent, titulo, subtitulo):
        frame = ctk.CTkFrame(
            parent, fg_color=CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDA
        )
        ctk.CTkLabel(
            frame, text=titulo,
            text_color=TEXTO,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 0))
        ctk.CTkLabel(
            frame, text=subtitulo,
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=11)
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(2, 10))
        return frame

    def _rotulo(self, parent, texto):
        return ctk.CTkLabel(
            parent, text=texto,
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=11, weight="bold")
        )

    def _limpar_dinamica(self):
        for w in self.area_dinamica.winfo_children():
            w.destroy()

    # ---------- tipo ----------
    def _trocar_tipo(self, tipo):
        self.tipo.set(tipo)
        self._limpar_dinamica()

        if tipo == "PowerPoint":
            self.btn_ppt.configure(fg_color=POWERPOINT, border_width=0)
            self.btn_slja.configure(fg_color=CARD, border_width=1, border_color=BORDA)
            self.btn_converter.configure(fg_color=POWERPOINT, hover_color="#C93816")

            self._rotulo(self.area_dinamica, "Modelo PowerPoint").grid(
                row=0, column=0, sticky="w", pady=(0, 5)
            )
            self.combo_modelo = ctk.CTkComboBox(
                self.area_dinamica,
                variable=self.modelo,
                values=[""],
                fg_color=FUNDO,
                button_color=POWERPOINT,
                button_hover_color="#C93816",
                border_color=BORDA,
                text_color=TEXTO,
                height=40,
                state="readonly"
            )
            self.combo_modelo.grid(row=1, column=0, sticky="ew")
            self._carregar_modelos()

            ctk.CTkButton(
                self.area_dinamica,
                text="Abrir pasta de modelos PowerPoint",
                fg_color="transparent",
                hover_color="#18436F",
                border_width=1,
                border_color=BORDA,
                height=36,
                command=lambda: os.startfile(PASTA_MODELOS_PPTX)
            ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        else:
            self.btn_slja.configure(fg_color=SLJA, border_width=0)
            self.btn_ppt.configure(fg_color=CARD, border_width=1, border_color=BORDA)
            self.btn_converter.configure(fg_color=SLJA, hover_color=ROXO)

            self._campo_imagem(
                0, "Imagem do primeiro slide (título)",
                self.imagem_capa, self._selecionar_imagem_capa
            )
            self._campo_imagem(
                2, "Imagem dos demais slides (letra)",
                self.imagem_letra, self._selecionar_imagem_letra
            )

            ctk.CTkLabel(
                self.area_dinamica,
                text="Inclui automaticamente uma tela final vazia.",
                text_color=TEXTO_2,
                font=ctk.CTkFont(size=10),
            ).grid(row=4, column=0, sticky="w", pady=(8, 0))

            ctk.CTkButton(
                self.area_dinamica,
                text="Abrir pasta de imagens SLJA",
                fg_color="transparent",
                hover_color="#321567",
                border_width=1,
                border_color=BORDA,
                height=36,
                command=lambda: os.startfile(PASTA_IMAGENS_SLJA)
            ).grid(row=5, column=0, sticky="w", pady=(8, 0))

    def _campo_imagem(self, linha, titulo, variavel, comando):
        self._rotulo(self.area_dinamica, titulo).grid(
            row=linha, column=0, sticky="w", pady=(0 if linha == 0 else 12, 5)
        )
        box = ctk.CTkFrame(self.area_dinamica, fg_color="transparent")
        box.grid(row=linha + 1, column=0, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(
            box, textvariable=variavel,
            fg_color=FUNDO, border_color=BORDA,
            text_color=TEXTO, height=38
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            box, text="Selecionar", width=96,
            height=38, fg_color=SLJA,
            hover_color=ROXO,
            command=comando
        ).grid(row=0, column=1, padx=(8, 0))

    # ---------- arquivos ----------
    def _selecionar_txt(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos TXT",
            filetypes=[("Arquivos TXT", "*.txt")]
        )
        if not arquivos:
            return

        for arq in arquivos:
            if arq not in self.arquivos:
                self.arquivos.append(arq)
                self.regras_arquivo[arq] = "-"
                self.selecao_arquivo[arq] = tk.BooleanVar(value=False)

        self._atualizar_lista()

    def _alterar_regra_arquivo(self, arquivo, valor):
        if valor not in ("-", "1", "2", "3"):
            valor = "-"
        self.regras_arquivo[arquivo] = valor

    def _regra_efetiva_arquivo(self, arquivo):
        valor = self.regras_arquivo.get(arquivo, "-")
        if valor == "-":
            return self.linhas_por_slide
        return int(valor)

    def _marcar_todos(self):
        marcado = bool(self.var_todos.get())
        for arquivo in self.arquivos:
            var = self.selecao_arquivo.get(arquivo)
            if var is not None:
                var.set(marcado)

    def _aplicar_regra_selecionados(self):
        selecionados = [
            arquivo
            for arquivo in self.arquivos
            if self.selecao_arquivo.get(arquivo) is not None
            and self.selecao_arquivo[arquivo].get()
        ]

        if not selecionados:
            messagebox.showwarning(
                NOME_APP,
                "Marque pelo menos uma música para aplicar a regra."
            )
            return

        regra = self.regra_lote.get()
        if regra not in ("-", "1", "2", "3"):
            regra = "-"

        for arquivo in selecionados:
            self.regras_arquivo[arquivo] = regra

        self._atualizar_lista()
        self.status.set(
            f"Regra {regra} aplicada a {len(selecionados)} arquivo(s)."
            if regra != "-"
            else f"{len(selecionados)} arquivo(s) voltaram a seguir a regra padrão."
        )

    def _remover_selecionados(self):
        selecionados = [
            arquivo
            for arquivo in self.arquivos
            if self.selecao_arquivo.get(arquivo) is not None
            and self.selecao_arquivo[arquivo].get()
        ]

        if not selecionados:
            messagebox.showwarning(
                NOME_APP,
                "Marque pelo menos uma música para remover."
            )
            return

        remover = set(selecionados)
        self.arquivos = [
            arquivo for arquivo in self.arquivos
            if arquivo not in remover
        ]

        for arquivo in selecionados:
            self.regras_arquivo.pop(arquivo, None)
            self.selecao_arquivo.pop(arquivo, None)

        self._atualizar_lista()

    def _atualizar_lista(self):
        # Recria somente as linhas visuais, mantendo as regras em memória.
        for widget in self.lista_scroll.winfo_children():
            widget.destroy()

        for i, arquivo in enumerate(self.arquivos, 1):
            linha = ctk.CTkFrame(
                self.lista_scroll,
                fg_color=FUNDO_2 if i % 2 == 0 else "transparent",
                corner_radius=8,
            )
            linha.grid(
                row=i - 1,
                column=0,
                sticky="ew",
                padx=4,
                pady=2,
            )
            linha.grid_columnconfigure(1, weight=1)

            var_sel = self.selecao_arquivo.setdefault(
                arquivo,
                tk.BooleanVar(value=False),
            )

            ctk.CTkCheckBox(
                linha,
                text="",
                variable=var_sel,
                width=26,
                checkbox_width=18,
                checkbox_height=18,
                fg_color=AZUL,
                hover_color="#0075D6",
            ).grid(row=0, column=0, padx=(7, 5), pady=7)

            ctk.CTkLabel(
                linha,
                text=f"{i:02d}. {Path(arquivo).name}",
                text_color=TEXTO,
                anchor="w",
                font=ctk.CTkFont(size=11),
            ).grid(
                row=0, column=1,
                sticky="ew",
                padx=(0, 8),
                pady=7,
            )

            regra_var = tk.StringVar(
                value=self.regras_arquivo.get(arquivo, "-")
            )
            combo = ctk.CTkComboBox(
                linha,
                variable=regra_var,
                values=["-", "1", "2", "3"],
                width=64,
                height=30,
                state="readonly",
                fg_color=FUNDO,
                border_color=BORDA,
                button_color=AZUL,
                button_hover_color="#0075D6",
                text_color=TEXTO,
                command=lambda valor, arq=arquivo:
                    self._alterar_regra_arquivo(arq, valor),
            )
            combo.grid(
                row=0, column=2,
                padx=(0, 7),
                pady=5,
            )

        if hasattr(self, "var_todos"):
            self.var_todos.set(False)

        self.status.set(f"{len(self.arquivos)} arquivo(s) selecionado(s).")
        self.btn_converter.configure(
            text=(
                f"Converter {len(self.arquivos)} arquivo(s)"
                if self.arquivos
                else "Converter arquivos"
            )
        )

    def _limpar(self):
        self.arquivos.clear()
        self.regras_arquivo.clear()
        self.selecao_arquivo.clear()
        self._atualizar_lista()
        self.status.set("Pronto para converter.")

    # ---------- modelos e imagens ----------
    def _carregar_modelos(self):
        modelos = sorted(PASTA_MODELOS_PPTX.glob("*.pptx"))
        nomes = [m.name for m in modelos]
        if hasattr(self, "combo_modelo"):
            self.combo_modelo.configure(values=nomes or ["Nenhum modelo encontrado"])
        if nomes:
            self.modelo.set(nomes[0])
        else:
            self.modelo.set("")

    def _selecionar_imagem_capa(self):
        self._selecionar_imagem(self.imagem_capa, "Imagem do primeiro slide (título)")

    def _selecionar_imagem_letra(self):
        self._selecionar_imagem(self.imagem_letra, "Imagem dos demais slides (letra)")

    def _selecionar_imagem(self, variavel, titulo):
        pasta_inicial = pasta_inicial_para_arquivo(
            variavel.get()
        )

        caminho = filedialog.askopenfilename(
            title=titulo,
            initialdir=str(pasta_inicial),
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if caminho:
            variavel.set(caminho)

    # ---------- pastas ----------
    def _escolher_saida(self):
        pasta_inicial = pasta_inicial_para_diretorio(
            self.pasta_saida.get()
        )

        pasta = filedialog.askdirectory(
            title="Selecionar pasta de saída",
            initialdir=str(pasta_inicial),
        )

        if pasta:
            self.pasta_saida.set(pasta)

    def _abrir_saida(self):
        pasta = Path(self.pasta_saida.get())
        pasta.mkdir(parents=True, exist_ok=True)
        os.startfile(pasta)

    # ---------- conversão ----------
    def _converter(self):
        if not self.arquivos:
            messagebox.showwarning(NOME_APP, "Selecione pelo menos um arquivo TXT.")
            return

        destino = Path(self.pasta_saida.get())
        destino.mkdir(parents=True, exist_ok=True)

        if self.tipo.get() == "PowerPoint":
            if not self.modelo.get():
                messagebox.showwarning(NOME_APP, "Selecione um modelo PowerPoint.")
                return
            modelo = PASTA_MODELOS_PPTX / self.modelo.get()
        else:
            if not self.imagem_capa.get() or not self.imagem_letra.get():
                messagebox.showwarning(
                    NOME_APP,
                    "Selecione a imagem do primeiro slide e a imagem dos demais slides."
                )
                return

        sucessos, erros = 0, []
        self.btn_converter.configure(state="disabled")

        try:
            for indice, arquivo in enumerate(self.arquivos, 1):
                regra_arquivo = self._regra_efetiva_arquivo(arquivo)

                self.status.set(
                    f"Convertendo {indice} de {len(self.arquivos)} "
                    f"• regra {regra_arquivo}..."
                )
                self.update_idletasks()

                try:
                    if self.tipo.get() == "PowerPoint":
                        gerar_pptx(
                            arquivo,
                            destino,
                            modelo,
                            linhas_por_slide=regra_arquivo,
                        )
                    else:
                        gerar_slja(
                            arquivo,
                            destino,
                            self.imagem_capa.get(),
                            self.imagem_letra.get(),
                            linhas_por_slide=regra_arquivo,
                        )
                    sucessos += 1
                except Exception as exc:
                    erros.append(f"{Path(arquivo).name}: {exc}")
        finally:
            self.btn_converter.configure(state="normal")

        if erros:
            self.status.set(f"{sucessos} convertido(s) • {len(erros)} erro(s)")
            messagebox.showerror(
                "Conversão concluída com erros",
                "\n".join(erros[:12])
            )
        else:
            self.status.set(f"{sucessos} arquivo(s) convertido(s) com sucesso.")
            messagebox.showinfo(
                NOME_APP,
                f"{sucessos} arquivo(s) convertido(s) com sucesso."
            )

    # ---------- regras de conversão ----------
    def _texto_linhas(self, quantidade):
        return "1 linha por slide" if quantidade == 1 else f"{quantidade} linhas por slide"

    def _atualizar_texto_regra(self):
        self.regra_atual.set(
            f"Regra atual: {self._texto_linhas(self.linhas_por_slide)}"
        )

    def _abrir_regras(self, janela_pai=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Regras de conversão")
        janela.geometry("590x500")
        janela.resizable(False, False)
        janela.configure(fg_color=FUNDO)

        if janela_pai is not None:
            janela.transient(janela_pai)
        else:
            janela.transient(self)

        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text="Regras de conversão",
            text_color=TEXTO,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=26, pady=(24, 4))

        ctk.CTkLabel(
            janela,
            text="Defina quantas linhas de uma mesma estrofe entram em cada slide.",
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=26, pady=(0, 18))

        card = ctk.CTkFrame(
            janela,
            fg_color=FUNDO_2,
            border_width=1,
            border_color=BORDA,
            corner_radius=16,
        )
        card.pack(fill="both", expand=True, padx=26, pady=(0, 18))

        ctk.CTkLabel(
            card,
            text="Título",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="A primeira linha do TXT é sempre o título e vai para o primeiro slide.",
            text_color=TEXTO_2,
            wraplength=500,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 18))

        ctk.CTkLabel(
            card,
            text="Linhas da letra por slide",
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(0, 8))

        regra_temp = tk.IntVar(value=self.linhas_por_slide)

        seletor = ctk.CTkSegmentedButton(
            card,
            values=["1 linha", "2 linhas", "3 linhas"],
            fg_color=FUNDO,
            selected_color=AZUL,
            selected_hover_color="#0075D6",
            unselected_color=CARD,
            unselected_hover_color="#18436F",
            text_color=TEXTO,
            height=42,
            command=lambda valor: regra_temp.set(
                {"1 linha": 1, "2 linhas": 2, "3 linhas": 3}[valor]
            ),
        )
        seletor.pack(fill="x", padx=20, pady=(0, 18))
        seletor.set(
            {1: "1 linha", 2: "2 linhas", 3: "3 linhas"}[
                self.linhas_por_slide
            ]
        )

        ctk.CTkLabel(
            card,
            text=(
                "A divisão sempre reinicia quando começa uma nova estrofe. "
                "Linhas de estrofes diferentes nunca são colocadas no mesmo slide."
            ),
            text_color=TEXTO_2,
            wraplength=500,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 18))

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(fill="x", padx=26, pady=(0, 24))

        def restaurar():
            regra_temp.set(2)
            seletor.set("2 linhas")

        def salvar():
            self.linhas_por_slide = int(regra_temp.get())
            salvar_configuracoes({
                "linhas_por_slide": self.linhas_por_slide,
            })
            self.configuracoes["linhas_por_slide"] = self.linhas_por_slide
            self._atualizar_texto_regra()
            janela.destroy()

        ctk.CTkButton(
            botoes,
            text="Restaurar padrão",
            fg_color="transparent",
            hover_color=CARD,
            border_width=1,
            border_color=BORDA,
            width=150,
            height=42,
            command=restaurar,
        ).pack(side="left")

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="transparent",
            hover_color=CARD,
            border_width=1,
            border_color=BORDA,
            width=110,
            height=42,
            command=janela.destroy,
        ).pack(side="right")

        ctk.CTkButton(
            botoes,
            text="Salvar",
            fg_color=AZUL,
            hover_color="#0075D6",
            width=120,
            height=42,
            font=ctk.CTkFont(weight="bold"),
            command=salvar,
        ).pack(side="right", padx=(0, 10))

    # ---------- configurações ----------
    def _abrir_configuracoes(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Configurações")
        janela.geometry("680x650")
        janela.resizable(False, False)
        janela.configure(fg_color=FUNDO)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(
            janela, text="Configurações",
            text_color=TEXTO,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=26, pady=(24, 4))

        ctk.CTkLabel(
            janela, text=f"{NOME_APP} • versão {VERSAO}",
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=26, pady=(0, 18))

        caixa = ctk.CTkFrame(
            janela, fg_color=FUNDO_2,
            border_width=1, border_color=BORDA,
            corner_radius=16
        )
        caixa.pack(fill="both", expand=True, padx=26, pady=(0, 24))

        self._secao_config(caixa, "Regras de conversão", 0)
        ctk.CTkLabel(
            caixa,
            textvariable=self.regra_atual,
            text_color=TEXTO_2,
        ).grid(row=1, column=0, sticky="w", padx=20)

        ctk.CTkButton(
            caixa,
            text="Configurar regras",
            fg_color=AZUL,
            hover_color="#0075D6",
            command=lambda: self._abrir_regras(janela),
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(10, 14))

        self._secao_config(caixa, "Modelos", 3)
        ctk.CTkButton(
            caixa, text="Abrir pasta de modelos",
            fg_color=CARD, hover_color="#18436F",
            command=lambda: os.startfile(PASTA_MODELOS)
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 14))

        self._secao_config(caixa, "Atualizações", 5)
        texto_update = (
            "Sistema de atualizações ativo."
            if configurado()
            else "Sistema de atualizações ainda não configurado."
        )
        ctk.CTkLabel(
            caixa, text=texto_update,
            text_color=TEXTO_2
        ).grid(row=6, column=0, sticky="w", padx=20)

        ctk.CTkButton(
            caixa, text="Verificar atualizações",
            fg_color=AZUL, hover_color="#0075D6",
            command=lambda: self._verificar_update(janela)
        ).grid(row=7, column=0, sticky="w", padx=20, pady=(10, 18))

        self._secao_config(caixa, "Sobre", 8)
        ctk.CTkLabel(
            caixa,
            text=f"{NOME_APP}\nVersão {VERSAO}\nGuiaSys Studio",
            justify="left",
            text_color=TEXTO_2
        ).grid(row=9, column=0, sticky="w", padx=20, pady=(0, 18))

    def _secao_config(self, parent, titulo, row):
        ctk.CTkLabel(
            parent, text=titulo,
            text_color=TEXTO,
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(18, 8))

    def _popup_atualizacao(self, info, automatico=False):
        popup = ctk.CTkToplevel(self)
        popup.title("Atualização disponível")
        popup.geometry("540x380")
        popup.resizable(False, False)
        popup.configure(fg_color=FUNDO)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="Nova atualização disponível",
            text_color=TEXTO,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w", padx=24, pady=(24, 4))

        ctk.CTkLabel(
            popup,
            text=f"Versão instalada: {VERSAO}   •   Nova versão: {info.get('nova_versao', '')}",
            text_color=TEXTO_2,
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=24, pady=(0, 16))

        notas = (info.get("notas") or "").strip()
        if notas:
            caixa = ctk.CTkTextbox(
                popup,
                fg_color=FUNDO_2,
                text_color=TEXTO_2,
                border_width=1,
                border_color=BORDA,
                corner_radius=12,
                height=190,
                wrap="word"
            )
            caixa.pack(fill="both", expand=True, padx=24, pady=(0, 16))
            caixa.insert("1.0", notas)
            caixa.configure(state="disabled")
        else:
            ctk.CTkLabel(
                popup,
                text="Há uma nova versão do Conversor Músicas disponível.",
                text_color=TEXTO_2,
                wraplength=470,
                justify="left"
            ).pack(anchor="w", padx=24, pady=(6, 40))

        botoes = ctk.CTkFrame(popup, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=(0, 22))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            fg_color="transparent",
            hover_color=CARD,
            border_width=1,
            border_color=BORDA,
            height=42,
            width=120,
            command=popup.destroy
        ).pack(side="right")

        ctk.CTkButton(
            botoes,
            text="Atualizar",
            fg_color=AZUL,
            hover_color="#0075D6",
            height=42,
            width=140,
            font=ctk.CTkFont(weight="bold"),
            command=lambda: self._iniciar_atualizacao(info, popup)
        ).pack(side="right", padx=(0, 10))

    def _iniciar_atualizacao(self, info, popup):
        asset = info.get("asset")
        if not asset:
            popup.destroy()
            if info.get("pagina"):
                if messagebox.askyesno(
                    "Atualização",
                    "A nova versão foi encontrada, mas não há um instalador compatível disponível.\n\n"
                    "Deseja abrir a página de atualização?"
                ):
                    webbrowser.open(info["pagina"])
            else:
                messagebox.showwarning(
                    "Atualização",
                    "Não há um instalador compatível disponível para download."
                )
            return

        for widget in popup.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            popup,
            text="Baixando atualização...",
            text_color=TEXTO,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=24, pady=(30, 8))

        ctk.CTkLabel(
            popup,
            text=f"Preparando {info.get('nova_versao', '')}",
            text_color=TEXTO_2
        ).pack(anchor="w", padx=24)

        barra = ctk.CTkProgressBar(
            popup,
            progress_color=AZUL,
            fg_color=FUNDO_2,
            height=14
        )
        barra.pack(fill="x", padx=24, pady=(28, 10))
        barra.set(0)

        texto_progresso = ctk.CTkLabel(
            popup,
            text="0%",
            text_color=TEXTO_2
        )
        texto_progresso.pack(anchor="e", padx=24)

        def progresso(valor):
            self.after(0, lambda: (
                barra.set(valor),
                texto_progresso.configure(text=f"{int(valor * 100)}%")
            ))

        def trabalho():
            try:
                instalador = baixar_instalador(asset, callback_progresso=progresso)
                def concluir():
                    barra.set(1)
                    texto_progresso.configure(text="100%")
                    if messagebox.askyesno(
                        "Atualização baixada",
                        "A atualização foi baixada com sucesso.\n\n"
                        "O instalador será aberto agora e o Conversor Músicas será fechado.\n\n"
                        "Continuar?"
                    ):
                        executar_instalador(instalador)
                        self.destroy()
                    else:
                        popup.destroy()
                self.after(0, concluir)
            except Exception as exc:
                self.after(
                    0,
                    lambda: (
                        popup.destroy(),
                        messagebox.showerror(
                            "Erro na atualização",
                            f"Não foi possível baixar ou iniciar a atualização.\n\n{exc}"
                        )
                    )
                )

        threading.Thread(target=trabalho, daemon=True).start()

    def _verificar_update_automatico(self):
        def trabalho():
            try:
                info = verificar_atualizacao()
                if info.get("atualizacao"):
                    self.after(0, lambda: self._popup_atualizacao(info, automatico=True))
            except Exception:
                # A verificação automática é silenciosa se não houver internet.
                pass

        threading.Thread(target=trabalho, daemon=True).start()

    def _verificar_update(self, parent=None):
        self.status.set("Verificando atualizações...")

        def trabalho():
            try:
                info = verificar_atualizacao()

                def mostrar():
                    self.status.set(info.get("mensagem", "Verificação concluída."))

                    if info.get("atualizacao"):
                        self._popup_atualizacao(info)
                    elif info.get("sem_release"):
                        messagebox.showinfo(
                            "Atualizações",
                            "O sistema de atualizações está ativo, mas ainda não existe nenhuma atualização publicada."
                        )
                    elif not info.get("configurado"):
                        messagebox.showinfo(
                            "Atualizações",
                            "O sistema de atualizações ainda não está configurado."
                        )
                    else:
                        messagebox.showinfo(
                            "Atualizações",
                            info.get("mensagem", "Você já está na versão mais recente.")
                        )

                self.after(0, mostrar)

            except Exception as exc:
                self.after(
                    0,
                    lambda: (
                        self.status.set("Falha ao verificar atualizações."),
                        messagebox.showerror(
                            "Atualizações",
                            f"Não foi possível verificar atualizações.\n\n{exc}"
                        )
                    )
                )

        threading.Thread(target=trabalho, daemon=True).start()


def run_app():
    app = ConversorApp()
    app.mainloop()
