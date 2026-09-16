"""A small desktop playground for the Vega programming language."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def _load_gui_library():
    """Use tkinter when available and explain how to install its system package otherwise."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Vega Studio için tkinter gerekli. Bazzite host terminalinde şu komutu çalıştırın: "
            "ujust install-system-package python3-tkinter; sonra sistemi yeniden başlatın."
        ) from error
    return tk, filedialog, messagebox, ttk


tk, filedialog, messagebox, ttk = _load_gui_library()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import LexerError, tokenize
from src.parser import ParserError, parse
from src.transpiler import transpile


COLORS = {
    "background": "#f4f1ea",
    "panel": "#fffdf8",
    "ink": "#252321",
    "muted": "#746f68",
    "line": "#ddd7cc",
    "accent": "#c85b3d",
    "accent_dark": "#98422d",
    "editor": "#202629",
    "editor_text": "#f4eee4",
    "output": "#172b2b",
    "output_text": "#d8f1e4",
}


class VegaGui(tk.Tk):
    """Desktop editor and runner for Vega source files."""

    def __init__(self) -> None:
        super().__init__()
        self.current_path: Path | None = None
        self.title("Vega Studio")
        self.geometry("1180x760")
        self.minsize(900, 600)
        self.configure(bg=COLORS["background"])
        self._configure_style()
        self._build_ui()
        self._load_starter_source()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background=COLORS["background"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure(
            "Toolbar.TButton",
            background=COLORS["panel"],
            foreground=COLORS["ink"],
            bordercolor=COLORS["line"],
            padding=(12, 7),
            font=("DejaVu Sans", 10),
        )
        style.map(
            "Toolbar.TButton",
            background=[("active", "#eee7db")],
            foreground=[("active", COLORS["accent_dark"])],
        )
        style.configure(
            "Run.TButton",
            background=COLORS["accent"],
            foreground="white",
            bordercolor=COLORS["accent"],
            padding=(16, 8),
            font=("DejaVu Sans", 10, "bold"),
        )
        style.map("Run.TButton", background=[("active", COLORS["accent_dark"])])
        style.configure(
            "Status.TLabel",
            background=COLORS["background"],
            foreground=COLORS["muted"],
            font=("DejaVu Sans", 9),
        )

    def _build_ui(self) -> None:
        header = ttk.Frame(self, style="App.TFrame", padding=(28, 24, 28, 16))
        header.pack(fill="x")

        title_block = ttk.Frame(header, style="App.TFrame")
        title_block.pack(side="left")
        tk.Label(
            title_block,
            text="VEGA / STUDIO",
            bg=COLORS["background"],
            fg=COLORS["accent"],
            font=("DejaVu Sans", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_block,
            text="Dilinle düşün, anında çalıştır.",
            bg=COLORS["background"],
            fg=COLORS["ink"],
            font=("DejaVu Serif", 22, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        actions = ttk.Frame(header, style="App.TFrame")
        actions.pack(side="right", anchor="s", pady=(0, 3))
        ttk.Button(actions, text="Yeni", style="Toolbar.TButton", command=self._new_file).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(actions, text="Aç", style="Toolbar.TButton", command=self._open_file).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(actions, text="Kaydet", style="Toolbar.TButton", command=self._save_file).pack(
            side="left", padx=(0, 14)
        )
        ttk.Button(actions, text="Çalıştır  ▶", style="Run.TButton", command=self._run_program).pack(
            side="left"
        )

        body = ttk.Frame(self, style="App.TFrame", padding=(28, 0, 28, 18))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(1, weight=1)

        self._section_label(body, "VEGA KODU", 0).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self._section_label(body, "PYTHON ÇIKTISI", 1).grid(row=0, column=1, sticky="w", pady=(0, 8), padx=(18, 0))

        editor_panel = tk.Frame(body, bg=COLORS["editor"], highlightthickness=0)
        editor_panel.grid(row=1, column=0, sticky="nsew")
        output_panel = tk.Frame(body, bg=COLORS["output"], highlightthickness=0)
        output_panel.grid(row=1, column=1, sticky="nsew", padx=(18, 0))

        self.editor = tk.Text(
            editor_panel,
            wrap="none",
            undo=True,
            bg=COLORS["editor"],
            fg=COLORS["editor_text"],
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["accent_dark"],
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=16,
            font=("DejaVu Sans Mono", 12),
        )
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<Control-Return>", lambda _event: self._run_program())

        self.python_output = self._make_output_text(output_panel)
        self.python_output.pack(fill="both", expand=True)

        input_bar = tk.Frame(output_panel, bg="#20403c", padx=14, pady=12)
        input_bar.pack(fill="x", side="bottom")
        tk.Label(
            input_bar,
            text="GİRDİ",
            bg="#20403c",
            fg="#9ecbb4",
            font=("DejaVu Sans", 9, "bold"),
        ).pack(anchor="w")
        self.input_text = tk.Entry(
            input_bar,
            bg="#2b514b",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("DejaVu Sans", 10),
        )
        self.input_text.pack(fill="x", pady=(5, 0), ipady=5)

        footer = ttk.Frame(self, style="App.TFrame", padding=(28, 0, 28, 16))
        footer.pack(fill="x")
        self.status = ttk.Label(footer, text="Hazır", style="Status.TLabel")
        self.status.pack(side="left")
        ttk.Button(
            footer, text="Çıktıyı temizle", style="Toolbar.TButton", command=self._clear_output
        ).pack(side="right")

    def _section_label(self, parent: Any, text: str, _column: int) -> Any:
        return tk.Label(
            parent,
            text=text,
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("DejaVu Sans", 9, "bold"),
        )

    @staticmethod
    def _make_output_text(parent: Any) -> Any:
        return tk.Text(
            parent,
            wrap="word",
            state="disabled",
            bg=COLORS["output"],
            fg=COLORS["output_text"],
            insertbackground="white",
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=16,
            font=("DejaVu Sans Mono", 11),
        )

    def _load_starter_source(self) -> None:
        self.editor.insert("1.0", 'sayisal sayim = 10\nyazdir sayim\n\nyazdir "Merhaba Vega!"\n')
        self._set_status("Yeni Vega dosyası")

    def _new_file(self) -> None:
        self.current_path = None
        self.editor.delete("1.0", "end")
        self._load_starter_source()

    def _open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Vega dosyası aç",
            filetypes=[("Vega dosyaları", "*.veg"), ("Tüm dosyalar", "*.*")],
        )
        if not path:
            return
        try:
            source = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            self._show_error(f"Dosya açılamadı: {error}")
            return
        self.current_path = Path(path)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", source)
        self._set_status(f"Açıldı: {self.current_path.name}")

    def _save_file(self) -> bool:
        if self.current_path is None:
            path = filedialog.asksaveasfilename(
                title="Vega dosyasını kaydet",
                defaultextension=".veg",
                filetypes=[("Vega dosyaları", "*.veg")],
            )
            if not path:
                return False
            self.current_path = Path(path)
        try:
            self.current_path.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8")
        except (OSError, UnicodeError) as error:
            self._show_error(f"Dosya kaydedilemedi: {error}")
            return False
        self._set_status(f"Kaydedildi: {self.current_path.name}")
        return True

    def _compile_source(self) -> str:
        return transpile(parse(tokenize(self.editor.get("1.0", "end-1c"))))

    def _run_program(self) -> None:
        try:
            python_code = self._compile_source()
        except (LexerError, ParserError, ValueError) as error:
            self._set_output(self._friendly_compile_error(str(error)), error=True)
            self._set_status("Derleme hatası")
            return

        self._set_output(python_code)
        try:
            result = subprocess.run(
                [sys.executable, "-c", python_code],
                input=self.input_text.get(),
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
                check=False,
            )
        except OSError as error:
            self._set_output(f"Çalıştırma hatası: {error}", error=True)
            self._set_status("Çalıştırma başarısız")
            return

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{self._friendly_runtime_error(result.stderr)}"
        if output:
            self._set_output(f"{python_code}\n--- çıktı ---\n{output}")
        self._set_status("Başarıyla çalıştı" if result.returncode == 0 else f"Program {result.returncode} koduyla durdu")

    def _clear_output(self) -> None:
        self._set_output("")
        self._set_status("Çıktı temizlendi")

    def _set_output(self, value: str, error: bool = False) -> None:
        self.python_output.configure(state="normal", fg="#ffb7a8" if error else COLORS["output_text"])
        self.python_output.delete("1.0", "end")
        self.python_output.insert("1.0", value)
        self.python_output.configure(state="disabled")

    @staticmethod
    def _friendly_compile_error(error: str) -> str:
        if "Expected a statement" in error or "found 'ekle'" in error:
            return (
                "Komut bulunamadı: 'ekle' tek başına kullanılamaz.\n\n"
                "Önce bir liste oluşturun:\n"
                "liste sayilar = liste.yeni 1\n\n"
                "Sonra liste adına nokta ile ekleyin:\n"
                "sayilar.ekle 2"
            )
        return error

    @staticmethod
    def _friendly_runtime_error(error: str) -> str:
        marker = "NameError: name '_vega_"
        if marker in error:
            name = error.split(marker, 1)[1].split("'", 1)[0]
            return (
                f"Değişken bulunamadı: '{name}'.\n"
                "Metin yazdıracaksanız tırnak kullanın: yazdir \"metin\""
            )
        return error

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def _show_error(self, text: str) -> None:
        messagebox.showerror("Vega Studio", text)


if __name__ == "__main__":
    VegaGui().mainloop()