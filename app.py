"""
Fatty Acid Profiler — app.py
============================
Applicazione Tkinter per l'analisi del profilo in acidi grassi
di latte e formaggi da dati cromatografici (GC-FAME).

Calcola automaticamente:
  • Indice di Aterogenicità (AI)
  • Indice di Trombogenicità (TI)
  • Rapporto PUFA/SFA
  • Rapporto n-3/n-6
  • Rapporto h/H (ipocolesterolemizzanti/ipercolesterolemizzanti)
  • Indice di Salute (HI)

Autore : Matteo — LM-9 Animal Biotechnologies, UniBO
Dataset: valori di riferimento da letteratura scientifica
         (Ulbricht & Southgate, 1991; Chilliard et al., 2006)
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from indices import calculate_indices, interpret_index

# ─── Palette ─────────────────────────────────────────────────────────────────
BG        = "#0f0f1a"
PANEL     = "#16213e"
ACCENT    = "#4361ee"
ACCENT2   = "#7209b7"
TEAL      = "#4cc9f0"
GREEN     = "#7bed9f"
PINK      = "#ff6b9d"
TEXT      = "#dde1ff"
MUTED     = "#7a7fa8"
SFA_CLR   = "#ff6b9d"
MUFA_CLR  = "#4cc9f0"
PUFA_CLR  = "#7bed9f"

FONT_TITLE = ("Helvetica", 15, "bold")
FONT_HEAD  = ("Helvetica", 10, "bold")
FONT_BODY  = ("Helvetica", 9)
FONT_NUM   = ("Helvetica", 20, "bold")


# ─── Main Application ─────────────────────────────────────────────────────────
class FattyAcidProfiler:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧪 Fatty Acid Profiler — Latte & Formaggi")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG)

        self.df: pd.DataFrame | None = None

        self._apply_styles()
        self._build_header()
        self._build_toolbar()
        self._build_notebook()
        self._load_default_dataset()

    # ── Style ─────────────────────────────────────────────────────────────────
    def _apply_styles(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")

        s.configure(".",              background=BG,    foreground=TEXT,  font=FONT_BODY)
        s.configure("TFrame",         background=BG)
        s.configure("Panel.TFrame",   background=PANEL)
        s.configure("TLabel",         background=BG,    foreground=TEXT,  font=FONT_BODY)
        s.configure("Muted.TLabel",   background=BG,    foreground=MUTED, font=FONT_BODY)
        s.configure("Title.TLabel",   background=BG,    foreground=TEAL,  font=FONT_TITLE)

        s.configure("TButton",
                    background=ACCENT, foreground="white",
                    font=FONT_HEAD, borderwidth=0, relief="flat", padding=6)
        s.map("TButton",
              background=[("active", ACCENT2), ("pressed", ACCENT2)],
              relief=[("active", "flat")])

        s.configure("TNotebook",     background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL, foreground=MUTED,
                    font=FONT_HEAD, padding=[14, 6])
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", "white")])

        s.configure("Treeview",
                    background=PANEL, foreground=TEXT,
                    fieldbackground=PANEL, font=FONT_BODY,
                    rowheight=26, borderwidth=0)
        s.configure("Treeview.Heading",
                    background=ACCENT, foreground="white",
                    font=FONT_HEAD, relief="flat")
        s.map("Treeview",
              background=[("selected", ACCENT2)],
              foreground=[("selected", "white")])

        s.configure("TCombobox",
                    fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, selectbackground=ACCENT)
        s.configure("Vertical.TScrollbar",
                    background=PANEL, troughcolor=BG,
                    arrowcolor=MUTED, borderwidth=0)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = ttk.Frame(self.root)
        hdr.pack(fill="x", padx=24, pady=(16, 4))

        ttk.Label(hdr, text="Fatty Acid Profiler",
                  style="Title.TLabel").pack(side="left")
        ttk.Label(hdr,
                  text="  |  Analisi nutrizionale da cromatografia GC-FAME · Latte & Formaggi",
                  style="Muted.TLabel").pack(side="left")

        self.status_var = tk.StringVar(value="Nessun file caricato")
        ttk.Label(hdr, textvariable=self.status_var,
                  style="Muted.TLabel").pack(side="right")

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", padx=24, pady=(0, 8))

        ttk.Button(bar, text="📂  Carica CSV",
                   command=self.load_csv).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="💾  Esporta Report",
                   command=self.export_report).pack(side="left", padx=6)

        # Separator
        ttk.Label(bar, text=" | ", style="Muted.TLabel").pack(side="left")

        ttk.Label(bar, text="Campione:").pack(side="left", padx=(6, 4))
        self.sample_var = tk.StringVar()
        self.sample_cb = ttk.Combobox(bar, textvariable=self.sample_var,
                                      state="readonly", width=28)
        self.sample_cb.pack(side="left")
        self.sample_cb.bind("<<ComboboxSelected>>", lambda _: self._analyze())

        # Compare button
        ttk.Button(bar, text="⚖  Confronta campioni",
                   command=self.compare_samples).pack(side="left", padx=10)

    # ── Notebook ──────────────────────────────────────────────────────────────
    def _build_notebook(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        self.nb = nb

        # Tab 1 — Dati
        self.tab_data = ttk.Frame(nb)
        nb.add(self.tab_data, text="  📋  Dati Acidi Grassi  ")
        self._build_tab_data()

        # Tab 2 — Indici
        self.tab_idx = ttk.Frame(nb)
        nb.add(self.tab_idx, text="  📐  Indici Nutrizionali  ")
        self._build_tab_indices()

        # Tab 3 — Grafici
        self.tab_charts = ttk.Frame(nb)
        nb.add(self.tab_charts, text="  📈  Grafici  ")
        self._build_tab_charts()

        # Tab 4 — Confronto
        self.tab_compare = ttk.Frame(nb)
        nb.add(self.tab_compare, text="  ⚖  Confronto  ")
        self._build_tab_compare()

    # ── Tab 1: Dati ───────────────────────────────────────────────────────────
    def _build_tab_data(self):
        cols = ("Acido Grasso", "Abbreviazione", "Categoria", "Tipo n-", "% FAME")
        self.tree = ttk.Treeview(self.tab_data, columns=cols,
                                 show="headings", height=22)

        widths = [220, 120, 90, 80, 100]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center", stretch=False)

        self.tree.tag_configure("SFA",  background="#2a1040", foreground=SFA_CLR)
        self.tree.tag_configure("MUFA", background="#0e2040", foreground=MUFA_CLR)
        self.tree.tag_configure("PUFA", background="#0e2a1e", foreground=PUFA_CLR)

        vsb = ttk.Scrollbar(self.tab_data, orient="vertical",
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", pady=8, padx=(0, 8))

    # ── Tab 2: Indici ─────────────────────────────────────────────────────────
    def _build_tab_indices(self):
        outer = ttk.Frame(self.tab_idx)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        self.idx_cards: dict[str, dict] = {}

        card_defs = [
            ("AI",       "Indice di Aterogenicità",              "AI < 1.0\nbasso = migliore",   "Ulbricht & Southgate, 1991"),
            ("TI",       "Indice di Trombogenicità",             "TI < 1.5\nbasso = migliore",   "Ulbricht & Southgate, 1991"),
            ("PUFA_SFA", "Rapporto PUFA / SFA",                  "≥ 0.45 (WHO)\nalto = migliore","WHO/FAO, 2010"),
            ("n3_n6",    "Rapporto n-3 / n-6",                   "≥ 0.25 ottimale",              "Simopoulos, 2002"),
            ("hH",       "Rapporto h / H",                       "alto = favorevole",            "Santos-Silva et al., 2002"),
            ("HI",       "Indice di Salute (HI)",                "alto = favorevole",            "(MUFA+PUFA)/SFA"),
            ("SFA_pct",  "% Acidi Grassi Saturi",                "% totale SFA",                 "—"),
            ("MUFA_pct", "% Acidi Grassi Monoinsaturi",          "% totale MUFA",                "—"),
            ("PUFA_pct", "% Acidi Grassi Polinsaturi",           "% totale PUFA",                "—"),
        ]

        for i, (key, name, note, ref) in enumerate(card_defs):
            row, col = divmod(i, 3)
            outer.grid_columnconfigure(col, weight=1)
            outer.grid_rowconfigure(row, weight=1)

            card = tk.Frame(outer, bg=PANEL, relief="flat")
            card.grid(row=row, column=col, padx=10, pady=10,
                      sticky="nsew", ipadx=16, ipady=14)

            tk.Label(card, text=name, bg=PANEL, fg=MUTED,
                     font=FONT_HEAD).pack()

            val_lbl = tk.Label(card, text="—", bg=PANEL,
                               fg=TEAL, font=FONT_NUM)
            val_lbl.pack(pady=(6, 2))

            interp_lbl = tk.Label(card, text="", bg=PANEL,
                                  fg=MUTED, font=("Helvetica", 8))
            interp_lbl.pack()

            tk.Label(card, text=note, bg=PANEL, fg="#505070",
                     font=("Helvetica", 7), justify="center").pack(pady=(4, 0))
            tk.Label(card, text=f"Ref: {ref}", bg=PANEL, fg="#404060",
                     font=("Helvetica", 7)).pack()

            self.idx_cards[key] = {"val": val_lbl, "interp": interp_lbl}

    # ── Tab 3: Grafici ────────────────────────────────────────────────────────
    def _build_tab_charts(self):
        self.fig = Figure(figsize=(13, 6), facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.get_tk_widget().pack(fill="both", expand=True,
                                         padx=8, pady=8)
        tb_frame = ttk.Frame(self.tab_charts)
        tb_frame.pack(fill="x")
        NavigationToolbar2Tk(self.canvas, tb_frame)

    # ── Tab 4: Confronto ──────────────────────────────────────────────────────
    def _build_tab_compare(self):
        self.fig_cmp = Figure(figsize=(13, 6), facecolor=BG)
        self.canvas_cmp = FigureCanvasTkAgg(self.fig_cmp,
                                             master=self.tab_compare)
        self.canvas_cmp.get_tk_widget().pack(fill="both", expand=True,
                                              padx=8, pady=8)

    # ── Data Loading ──────────────────────────────────────────────────────────
    def _load_default_dataset(self):
        default = os.path.join(
            os.path.dirname(__file__), "data", "latte_e_formaggi.csv"
        )
        if os.path.exists(default):
            self._load_file(default)

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Seleziona file CSV",
            filetypes=[("CSV", "*.csv"), ("Tutti", "*.*")]
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        try:
            df = pd.read_csv(path)
            required = {"fatty_acid", "abbreviation", "category", "percentage"}
            if not required.issubset(df.columns):
                messagebox.showerror(
                    "Formato non valido",
                    f"Il CSV deve contenere almeno le colonne:\n{required}"
                )
                return

            if "sample" not in df.columns:
                df["sample"] = "Campione"

            self.df = df
            samples = df["sample"].unique().tolist()
            self.sample_cb["values"] = samples
            self.sample_var.set(samples[0])
            self.status_var.set(f"✅  {os.path.basename(path)}  —  {len(samples)} campioni")
            self._analyze()

        except Exception as exc:
            messagebox.showerror("Errore nel caricamento", str(exc))

    # ── Analysis ──────────────────────────────────────────────────────────────
    def _analyze(self):
        if self.df is None:
            return

        sample = self.sample_var.get()
        data = self.df[self.df["sample"] == sample].copy()

        self._update_table(data)
        indices = calculate_indices(data)
        self._update_index_cards(indices)
        self._update_charts(data, indices, sample)

    def _update_table(self, data: pd.DataFrame):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, r in data.iterrows():
            cat    = r.get("category", "")
            n_type = r.get("n_type", "") if "n_type" in data.columns else ""
            vals = (
                r["fatty_acid"],
                r["abbreviation"],
                cat,
                str(n_type) if pd.notna(n_type) else "",
                f"{r['percentage']:.2f} %",
            )
            self.tree.insert("", "end", values=vals, tags=(cat,))

    def _update_index_cards(self, indices: dict):
        pct_keys = {"SFA_pct", "MUFA_pct", "PUFA_pct",
                    "n3_pct", "n6_pct"}

        for key, widgets in self.idx_cards.items():
            val = indices.get(key)
            if val is None:
                widgets["val"].config(text="N/D", fg=MUTED)
                widgets["interp"].config(text="")
                continue

            suffix = " %" if key in pct_keys else ""
            widgets["val"].config(text=f"{val:.3f}{suffix}")

            interp, color = interpret_index(key, val)
            widgets["val"].config(fg=color)
            widgets["interp"].config(text=interp, fg=color)

    def _update_charts(self, data: pd.DataFrame, indices: dict, title: str):
        self.fig.clear()

        ax_bar = self.fig.add_subplot(1, 2, 1)
        ax_pie = self.fig.add_subplot(1, 2, 2)

        for ax in (ax_bar, ax_pie):
            ax.set_facecolor(PANEL)

        # ── Bar chart ────────────────────────────────────────────
        color_map = {"SFA": SFA_CLR, "MUFA": MUFA_CLR, "PUFA": PUFA_CLR}
        bar_colors = [color_map.get(c, MUTED) for c in data["category"].tolist()]

        ax_bar.barh(
            data["abbreviation"].tolist(),
            data["percentage"].to_numpy(dtype=float),
            color=bar_colors, edgecolor="none", height=0.7
        )
        ax_bar.set_xlabel("% FAME", color=TEXT, fontsize=9)
        ax_bar.set_title(f"Profilo Acidi Grassi\n{title}",
                         color=TEAL, fontsize=10, fontweight="bold")
        ax_bar.tick_params(colors=TEXT, labelsize=8)
        for spine in ax_bar.spines.values():
            spine.set_color("#303050")
        ax_bar.spines["top"].set_visible(False)
        ax_bar.spines["right"].set_visible(False)

        legend_patches = [
            mpatches.Patch(color=c, label=l)
            for l, c in color_map.items()
        ]
        ax_bar.legend(handles=legend_patches, facecolor=BG,
                      edgecolor="#303050", labelcolor=TEXT,
                      loc="lower right", fontsize=8)

        # ── Pie chart ─────────────────────────────────────────────
        pie_vals = np.array([
            float(indices.get("SFA_pct", 0)),
            float(indices.get("MUFA_pct", 0)),
            float(indices.get("PUFA_pct", 0)),
        ])
        pie_labels = ["SFA", "MUFA", "PUFA"]
        pie_colors = [SFA_CLR, MUFA_CLR, PUFA_CLR]

        wedges, texts, autotexts = ax_pie.pie(
            pie_vals, labels=pie_labels, colors=pie_colors,
            autopct="%1.1f%%", startangle=90,
            textprops={"color": TEXT, "fontsize": 9},
            wedgeprops={"edgecolor": BG, "linewidth": 2},
            pctdistance=0.75,
        )
        for at in autotexts:
            at.set_color(BG)
            at.set_fontweight("bold")

        ax_pie.set_title("Composizione SFA / MUFA / PUFA",
                         color=TEAL, fontsize=10, fontweight="bold")

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

    # ── Compare ───────────────────────────────────────────────────────────────
    def compare_samples(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Carica prima un dataset.")
            return

        samples = self.df["sample"].unique().tolist()
        if len(samples) < 2:
            messagebox.showinfo("Confronto", "Servono almeno 2 campioni nel dataset.")
            return

        self.fig_cmp.clear()

        index_keys  = ["AI", "TI", "PUFA_SFA", "n3_n6", "hH", "HI"]
        index_names = ["AI", "TI", "PUFA/SFA", "n-3/n-6", "h/H", "HI"]

        data_by_sample = {}
        for s in samples:
            df_s = self.df[self.df["sample"] == s]
            idx  = calculate_indices(df_s)
            data_by_sample[s] = [idx.get(k, 0) for k in index_keys]

        x     = np.arange(len(index_keys))
        n     = len(samples)
        width = 0.7 / n

        ax = self.fig_cmp.add_subplot(1, 1, 1)
        ax.set_facecolor(PANEL)

        colors = [TEAL, PINK, GREEN, "#ffd166", "#ef8c8c", MUTED]

        for i, (sample, vals) in enumerate(data_by_sample.items()):
            offset = (i - n / 2 + 0.5) * width
            bars   = ax.bar(x + offset, vals, width, label=sample,
                            color=colors[i % len(colors)],
                            edgecolor="none", alpha=0.88)

        ax.set_xticks(x)
        ax.set_xticklabels(index_names, color=TEXT, fontsize=10)
        ax.tick_params(axis="y", colors=TEXT)
        ax.set_title("Confronto Indici Nutrizionali tra Campioni",
                     color=TEAL, fontsize=12, fontweight="bold")
        ax.set_ylabel("Valore indice", color=TEXT)
        ax.legend(facecolor=BG, edgecolor="#303050",
                  labelcolor=TEXT, fontsize=9)

        for spine in ax.spines.values():
            spine.set_color("#303050")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        self.fig_cmp.tight_layout(pad=2.5)
        self.canvas_cmp.draw()
        self.nb.select(self.tab_compare)

    # ── Export ────────────────────────────────────────────────────────────────
    def export_report(self):
        if self.df is None:
            messagebox.showwarning("Attenzione", "Nessun dato da esportare.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")],
            title="Salva report",
            initialfile=f"report_{self.sample_var.get().replace(' ', '_')}"
        )
        if not path:
            return

        sample = self.sample_var.get()
        data   = self.df[self.df["sample"] == sample].copy()
        idx    = calculate_indices(data)

        # Append indices as bottom rows
        idx_rows = pd.DataFrame(
            [{"fatty_acid": f"[INDICE] {k}", "abbreviation": k,
              "category": "INDEX", "n_type": "", "percentage": v}
             for k, v in idx.items()]
        )
        report = pd.concat([data, idx_rows], ignore_index=True)

        if path.endswith(".xlsx"):
            report.to_excel(path, index=False)
        else:
            report.to_csv(path, index=False)

        messagebox.showinfo("✅ Esportazione completata",
                            f"Report salvato in:\n{path}")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = FattyAcidProfiler(root)
    root.mainloop()
