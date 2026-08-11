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
        self.tipo = tk.StringVar(value="PowerPoint")
        self.modelo = tk.StringVar()
        self.pasta_saida = tk.StringVar(value=str(PASTA_SAIDA))
        self.imagem_capa = tk.StringVar()
        self.imagem_letra = tk.StringVar()
        self.status = tk.StringVar(value="Pronto para converter.")

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
        ).grid(row=0, column=2, rowspan=2, padx=(14, 0))

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
        arquivos_card.grid_rowconfigure(3, weight=1)
        arquivos_card.grid_columnconfigure(0, weight=1)

        botoes = ctk.CTkFrame(arquivos_card, fg_color="transparent")
        botoes.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 12))

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

        self.lista = ctk.CTkTextbox(
            arquivos_card,
            fg_color=FUNDO,
            text_color=TEXTO,
            border_width=1,
            border_color=BORDA,
            corner_radius=12,
            font=("Consolas", 12)
        )
        self.lista.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.lista.configure(state="disabled")

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

            ctk.CTkButton(
                self.area_dinamica,
                text="Abrir pasta de imagens SLJA",
                fg_color="transparent",
                hover_color="#321567",
                border_width=1,
                border_color=BORDA,
                height=36,
                command=lambda: os.startfile(PASTA_IMAGENS_SLJA)
            ).grid(row=4, column=0, sticky="w", pady=(8, 0))

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

        self._atualizar_lista()

    def _atualizar_lista(self):
        self.lista.configure(state="normal")
        self.lista.delete("1.0", "end")
        for i, arq in enumerate(self.arquivos, 1):
            self.lista.insert("end", f"{i:02d}. {Path(arq).name}\n")
        self.lista.configure(state="disabled")
        self.status.set(f"{len(self.arquivos)} arquivo(s) selecionado(s).")
        self.btn_converter.configure(
            text=f"Converter {len(self.arquivos)} arquivo(s)" if self.arquivos else "Converter arquivos"
        )

    def _limpar(self):
        self.arquivos.clear()
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
        caminho = filedialog.askopenfilename(
            title=titulo,
            initialdir=PASTA_IMAGENS_SLJA,
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if caminho:
            variavel.set(caminho)

    # ---------- pastas ----------
    def _escolher_saida(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_saida.get())
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
                self.status.set(f"Convertendo {indice} de {len(self.arquivos)}...")
                self.update_idletasks()
                try:
                    if self.tipo.get() == "PowerPoint":
                        gerar_pptx(arquivo, destino, modelo)
                    else:
                        gerar_slja(
                            arquivo, destino,
                            self.imagem_capa.get(),
                            self.imagem_letra.get()
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

    # ---------- configurações ----------
    def _abrir_configuracoes(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Configurações")
        janela.geometry("620x520")
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

        self._secao_config(caixa, "Modelos", 0)
        ctk.CTkButton(
            caixa, text="Abrir pasta de modelos",
            fg_color=CARD, hover_color="#18436F",
            command=lambda: os.startfile(PASTA_MODELOS)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 14))

        self._secao_config(caixa, "Atualizações", 2)
        texto_update = (
            "GitHub Releases configurado."
            if configurado()
            else "Aguardando configuração do repositório GitHub."
        )
        ctk.CTkLabel(
            caixa, text=texto_update,
            text_color=TEXTO_2
        ).grid(row=3, column=0, sticky="w", padx=20)

        ctk.CTkButton(
            caixa, text="Verificar atualizações",
            fg_color=AZUL, hover_color="#0075D6",
            command=lambda: self._verificar_update(janela)
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(10, 18))

        self._secao_config(caixa, "Sobre", 5)
        ctk.CTkLabel(
            caixa,
            text=f"{NOME_APP}\nVersão {VERSAO}\nGuiaSys Studio",
            justify="left",
            text_color=TEXTO_2
        ).grid(row=6, column=0, sticky="w", padx=20, pady=(0, 18))

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
                text="Há uma nova versão do Conversor Músicas disponível no GitHub Releases.",
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
                    "A nova versão foi encontrada, mas a Release não possui um instalador .exe.\n\n"
                    "Deseja abrir a página da Release?"
                ):
                    webbrowser.open(info["pagina"])
            else:
                messagebox.showwarning(
                    "Atualização",
                    "A Release não possui um instalador .exe disponível para download."
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
                            "O repositório está configurado, mas ainda não existe nenhuma Release publicada."
                        )
                    elif not info.get("configurado"):
                        messagebox.showinfo(
                            "Atualizações",
                            "O repositório GitHub ainda não está configurado."
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
