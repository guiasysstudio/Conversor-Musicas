import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .caminhos import (
    PASTA_MODELOS, PASTA_MODELOS_PPTX, PASTA_IMAGENS_SLJA, PASTA_SAIDA,
    garantir_pastas
)
from .gerador_pptx import gerar_pptx
from .gerador_slja import gerar_slja

COR_FUNDO = "#0f1a2e"
COR_PAINEL = "#14223a"
COR_BORDA = "#2a3d5d"
COR_DESTAQUE = "#19c2b4"
COR_TEXTO = "#ffffff"
COR_SECUNDARIO = "#9eb4d2"
COR_CAMPO = "#e8e5dc"

class Aplicacao:
    def __init__(self, root):
        garantir_pastas()
        self.root = root
        self.root.title("Conversor Músicas")
        self.root.geometry("1010x760")
        self.root.minsize(960, 700)
        self.root.configure(bg=COR_FUNDO)

        self.arquivos = []
        self.tipo = tk.StringVar(value="PowerPoint (.pptx)")
        self.modelo = tk.StringVar()
        self.pasta_saida = tk.StringVar(value=str(PASTA_SAIDA))
        self.imagem_capa = tk.StringVar()
        self.imagem_letra = tk.StringVar()
        self.status = tk.StringVar(value="Pronto para converter.")

        self._estilos()
        self._montar()
        self._carregar_modelos()
        self._atualizar_configuracao()

    def _estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", padding=6)

    def _montar(self):
        topo = tk.Frame(self.root, bg=COR_FUNDO)
        topo.pack(fill="x", padx=28, pady=(24, 14))

        tk.Label(
            topo, text="🎼  Conversor Músicas",
            bg=COR_FUNDO, fg=COR_TEXTO,
            font=("Segoe UI", 25, "bold")
        ).pack(side="left")

        tk.Button(
            topo, text="Abrir pasta de modelos",
            command=self.abrir_modelos,
            bg="#182844", fg=COR_TEXTO,
            activebackground="#223657", activeforeground=COR_TEXTO,
            relief="flat", padx=18, pady=12,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right")

        corpo = tk.Frame(self.root, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_columnconfigure(1, weight=1)
        corpo.grid_rowconfigure(0, weight=1)

        self.painel_arquivos = self._painel(corpo, "1. Arquivos TXT")
        self.painel_arquivos.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        botoes = tk.Frame(self.painel_arquivos, bg=COR_PAINEL)
        botoes.pack(fill="x", padx=18, pady=(6, 10))
        self._botao(botoes, "Selecionar TXT", self.selecionar_txt, destaque=True).pack(side="left")
        self._botao(botoes, "Limpar", self.limpar).pack(side="left", padx=(10, 0))

        self.lista = tk.Listbox(
            self.painel_arquivos,
            bg="#091426", fg=COR_TEXTO,
            selectbackground="#1d927f",
            relief="flat", borderwidth=0,
            font=("Segoe UI", 10)
        )
        self.lista.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.painel_config = self._painel(corpo, "2. Configuração")
        self.painel_config.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.area_config = tk.Frame(self.painel_config, bg=COR_PAINEL)
        self.area_config.pack(fill="both", expand=True, padx=18, pady=(6, 18))

        tk.Label(
            self.area_config, text="Converter para",
            bg=COR_PAINEL, fg=COR_SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(2, 5))

        self.combo_tipo = ttk.Combobox(
            self.area_config,
            textvariable=self.tipo,
            values=["PowerPoint (.pptx)", "SLJA sem áudio (.slja)"],
            state="readonly"
        )
        self.combo_tipo.pack(fill="x")
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda _e: self._atualizar_configuracao())

        self.config_dinamica = tk.Frame(self.area_config, bg=COR_PAINEL)
        self.config_dinamica.pack(fill="x", pady=(14, 0))

        tk.Label(
            self.area_config, text="Pasta de saída",
            bg=COR_PAINEL, fg=COR_SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(16, 5))

        tk.Entry(
            self.area_config, textvariable=self.pasta_saida,
            bg="#091426", fg=COR_TEXTO, insertbackground=COR_TEXTO,
            relief="flat", font=("Segoe UI", 10)
        ).pack(fill="x", ipady=8)

        linha_saida = tk.Frame(self.area_config, bg=COR_PAINEL)
        linha_saida.pack(fill="x", pady=(10, 0))
        self._botao(linha_saida, "Escolher pasta", self.escolher_saida).pack(side="left")
        self._botao(linha_saida, "Abrir saída", self.abrir_saida).pack(side="left", padx=(10, 0))

        rodape = tk.Frame(self.root, bg=COR_FUNDO)
        rodape.pack(fill="x", padx=28, pady=(0, 22))

        tk.Label(
            rodape, textvariable=self.status,
            bg=COR_FUNDO, fg=COR_SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(side="left")

        self._botao(
            rodape, "Converter arquivos", self.converter, destaque=True,
            padx=22, pady=13
        ).pack(side="right")

    def _painel(self, parent, titulo):
        frame = tk.Frame(
            parent, bg=COR_PAINEL,
            highlightthickness=1, highlightbackground=COR_BORDA
        )
        tk.Label(
            frame, text=titulo,
            bg=COR_PAINEL, fg=COR_TEXTO,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 10))
        return frame

    def _botao(self, parent, texto, comando, destaque=False, padx=16, pady=10):
        cor = COR_DESTAQUE if destaque else "#182844"
        return tk.Button(
            parent, text=texto, command=comando,
            bg=cor, fg=COR_TEXTO,
            activebackground="#12a99d" if destaque else "#223657",
            activeforeground=COR_TEXTO,
            relief="flat", borderwidth=0,
            padx=padx, pady=pady,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )

    def _limpar_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _atualizar_configuracao(self):
        self._limpar_frame(self.config_dinamica)

        if self.tipo.get().startswith("PowerPoint"):
            tk.Label(
                self.config_dinamica, text="Modelo PowerPoint",
                bg=COR_PAINEL, fg=COR_SECUNDARIO,
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=(0, 5))

            self.combo_modelo = ttk.Combobox(
                self.config_dinamica,
                textvariable=self.modelo,
                state="readonly"
            )
            self.combo_modelo.pack(fill="x")
            self._carregar_modelos()
        else:
            self._campo_imagem(
                self.config_dinamica,
                "Imagem do primeiro slide (título)",
                self.imagem_capa,
                self.selecionar_imagem_capa
            )
            self._campo_imagem(
                self.config_dinamica,
                "Imagem dos demais slides (letra)",
                self.imagem_letra,
                self.selecionar_imagem_letra
            )

    def _campo_imagem(self, parent, titulo, variavel, comando):
        bloco = tk.Frame(parent, bg=COR_PAINEL)
        bloco.pack(fill="x", pady=(0, 12))
        tk.Label(
            bloco, text=titulo,
            bg=COR_PAINEL, fg=COR_SECUNDARIO,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 5))

        linha = tk.Frame(bloco, bg=COR_PAINEL)
        linha.pack(fill="x")
        tk.Entry(
            linha, textvariable=variavel,
            bg="#091426", fg=COR_TEXTO, insertbackground=COR_TEXTO,
            relief="flat", font=("Segoe UI", 9)
        ).pack(side="left", fill="x", expand=True, ipady=7)
        self._botao(linha, "Selecionar", comando, padx=12, pady=7).pack(side="left", padx=(8, 0))

    def _carregar_modelos(self):
        modelos = sorted(PASTA_MODELOS_PPTX.glob("*.pptx"))
        nomes = [p.name for p in modelos]
        if hasattr(self, "combo_modelo"):
            self.combo_modelo["values"] = nomes
        if nomes and self.modelo.get() not in nomes:
            self.modelo.set(nomes[0])
        elif not nomes:
            self.modelo.set("")

    def selecionar_txt(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos TXT",
            filetypes=[("Arquivos TXT", "*.txt")]
        )
        if not arquivos:
            return
        for arquivo in arquivos:
            if arquivo not in self.arquivos:
                self.arquivos.append(arquivo)
                self.lista.insert("end", Path(arquivo).name)
        self.status.set(f"{len(self.arquivos)} arquivo(s) selecionado(s).")

    def limpar(self):
        self.arquivos.clear()
        self.lista.delete(0, "end")
        self.status.set("Pronto para converter.")

    def escolher_saida(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_saida.get())
        if pasta:
            self.pasta_saida.set(pasta)

    def abrir_saida(self):
        pasta = Path(self.pasta_saida.get())
        pasta.mkdir(parents=True, exist_ok=True)
        os.startfile(pasta)

    def abrir_modelos(self):
        PASTA_MODELOS.mkdir(parents=True, exist_ok=True)
        os.startfile(PASTA_MODELOS)

    def selecionar_imagem_capa(self):
        caminho = filedialog.askopenfilename(
            title="Imagem do primeiro slide",
            initialdir=PASTA_IMAGENS_SLJA,
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if caminho:
            self.imagem_capa.set(caminho)

    def selecionar_imagem_letra(self):
        caminho = filedialog.askopenfilename(
            title="Imagem dos demais slides",
            initialdir=PASTA_IMAGENS_SLJA,
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if caminho:
            self.imagem_letra.set(caminho)

    def converter(self):
        if not self.arquivos:
            messagebox.showwarning("Conversor Músicas", "Selecione pelo menos um arquivo TXT.")
            return

        pasta_saida = Path(self.pasta_saida.get())
        pasta_saida.mkdir(parents=True, exist_ok=True)

        tipo = self.tipo.get()
        if tipo.startswith("PowerPoint"):
            if not self.modelo.get():
                messagebox.showwarning(
                    "Conversor Músicas",
                    "Nenhum modelo PowerPoint foi encontrado na pasta de modelos."
                )
                return
            modelo = PASTA_MODELOS_PPTX / self.modelo.get()
        else:
            if not self.imagem_capa.get() or not self.imagem_letra.get():
                messagebox.showwarning(
                    "Conversor Músicas",
                    "Selecione a imagem do primeiro slide e a imagem dos demais slides."
                )
                return

        sucessos = 0
        erros = []

        for indice, arquivo in enumerate(self.arquivos, start=1):
            self.status.set(f"Convertendo {indice} de {len(self.arquivos)}...")
            self.root.update_idletasks()
            try:
                if tipo.startswith("PowerPoint"):
                    gerar_pptx(arquivo, pasta_saida, modelo)
                else:
                    gerar_slja(
                        arquivo, pasta_saida,
                        self.imagem_capa.get(),
                        self.imagem_letra.get()
                    )
                sucessos += 1
            except Exception as exc:
                erros.append(f"{Path(arquivo).name}: {exc}")

        if erros:
            self.status.set(f"{sucessos} convertido(s), {len(erros)} erro(s).")
            messagebox.showerror(
                "Conversão concluída com erros",
                "Alguns arquivos não foram convertidos:\n\n" + "\n".join(erros[:12])
            )
        else:
            self.status.set(f"{sucessos} arquivo(s) convertido(s) com sucesso.")
            messagebox.showinfo(
                "Conversor Músicas",
                f"{sucessos} arquivo(s) convertido(s) com sucesso."
            )


def run_app():
    root = tk.Tk()
    Aplicacao(root)
    root.mainloop()
