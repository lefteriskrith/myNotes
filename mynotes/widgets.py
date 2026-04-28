import customtkinter as ctk
from .config import C, NOTE_COLORS

# Two rows of color swatches shown in the NoteDialog color picker.
_COLOR_ROWS = [
    ["default", "red", "flamingo", "peach", "yellow", "green", "teal"],
    ["sky", "sapphire", "blue", "lavender", "mauve", "pink", "rosewater"],
]


class NoteDialog(ctk.CTkToplevel):
    def __init__(self, parent, tags: list[str], current_tag: str = "General", note: dict | None = None):
        super().__init__(parent)
        self.result: dict | None = None
        self.tags = tags

        self.title("Edit Note" if note else "New Note")
        self.geometry("500x620")
        self.resizable(True, True)
        self.configure(fg_color=C["base"])
        self.transient(parent)
        self.grab_set()
        self.focus()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._label("Title", row=0)
        self.title_entry = ctk.CTkEntry(
            self, placeholder_text="Note title…",
            fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], height=38, font=ctk.CTkFont(size=14),
        )
        self.title_entry.grid(row=1, column=0, padx=20, sticky="ew")

        self._label("Content", row=2)
        self.content_box = ctk.CTkTextbox(
            self, fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], border_width=1, font=ctk.CTkFont(size=13),
        )
        self.content_box.grid(row=3, column=0, padx=20, sticky="nsew")

        self._label("Tag", row=4)
        self.tag_var = ctk.StringVar(value=note["tag"] if note else current_tag)
        ctk.CTkOptionMenu(
            self, values=self.tags, variable=self.tag_var,
            fg_color=C["surface0"], button_color=C["surface1"],
            button_hover_color=C["surface2"], text_color=C["text"],
            dropdown_fg_color=C["surface0"], dropdown_text_color=C["text"],
            dropdown_hover_color=C["surface1"],
        ).grid(row=5, column=0, padx=20, sticky="ew")

        # ── color picker (2 rows × 7 swatches) ───────────────────────────────
        self._label("Color", row=6)
        picker = ctk.CTkFrame(self, fg_color="transparent")
        picker.grid(row=7, column=0, padx=20, pady=(0, 4), sticky="w")

        self._selected_color: str = note.get("color", "default") if note else "default"
        self._color_btns: dict[str, ctk.CTkButton] = {}

        for r, row_keys in enumerate(_COLOR_ROWS):
            for c, key in enumerate(row_keys):
                col_def = NOTE_COLORS[key]
                circle = col_def["accent"] if col_def["accent"] else C["surface2"]
                btn = ctk.CTkButton(
                    picker, text="", width=26, height=26, corner_radius=13,
                    fg_color=circle, hover_color=circle,
                    border_width=2 if key == self._selected_color else 0,
                    border_color=C["text"],
                    command=lambda k=key: self._pick_color(k),
                )
                btn.grid(row=r, column=c, padx=3, pady=3)
                self._color_btns[key] = btn

        # ── save / cancel ─────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=8, column=0, padx=20, pady=16, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color=C["surface1"],
            text_color=C["text"], hover_color=C["surface2"],
            command=self.destroy,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            btn_frame, text="Save", fg_color=C["blue"],
            text_color=C["crust"], hover_color=C["sapphire"],
            font=ctk.CTkFont(weight="bold"), command=self._save,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        if note:
            self.title_entry.insert(0, note.get("title", ""))
            self.content_box.insert("1.0", note.get("content", ""))

    def _label(self, text: str, row: int) -> None:
        ctk.CTkLabel(
            self, text=text, text_color=C["subtext0"],
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=row, column=0, padx=20, pady=(14, 4), sticky="w")

    def _pick_color(self, key: str) -> None:
        for k, btn in self._color_btns.items():
            btn.configure(border_width=2 if k == key else 0)
        self._selected_color = key

    def _save(self) -> None:
        self.result = {
            "title":   self.title_entry.get().strip(),
            "content": self.content_box.get("1.0", "end-1c").strip(),
            "tag":     self.tag_var.get(),
            "color":   self._selected_color,
        }
        self.destroy()


class NoteCard(ctk.CTkFrame):
    def __init__(self, master, note: dict, accent: str, bg: str, on_edit, on_delete, on_move_up, on_move_down, **kw):
        super().__init__(
            master, corner_radius=12,
            fg_color=bg, border_width=1, border_color=C["surface1"],
            **kw,
        )
        self._accent = accent
        self.grid_columnconfigure(0, weight=1)

        # Thin colored stripe at the top of the card.
        ctk.CTkFrame(self, height=3, corner_radius=0, fg_color=accent).grid(
            row=0, column=0, columnspan=2, sticky="ew",
        )

        if note.get("title"):
            ctk.CTkLabel(
                self, text=note["title"], anchor="w", justify="left",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=C["text"], wraplength=230,
            ).grid(row=1, column=0, columnspan=2, padx=14, pady=(10, 3), sticky="ew")

        preview = note.get("content", "")
        if len(preview) > 200:
            preview = preview[:200] + "…"
        if preview:
            ctk.CTkLabel(
                self, text=preview, anchor="nw", justify="left",
                font=ctk.CTkFont(size=12), text_color=C["subtext0"], wraplength=230,
            ).grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(
            self, text=note.get("created", "")[:10],
            font=ctk.CTkFont(size=10), text_color=C["overlay0"],
        ).grid(row=3, column=0, padx=14, pady=(0, 10), sticky="w")

        acts = ctk.CTkFrame(self, fg_color="transparent")
        acts.grid(row=3, column=1, padx=10, pady=(0, 8), sticky="e")
        ctk.CTkButton(
            acts, text="Edit", width=46, height=24,
            fg_color=C["blue"], text_color=C["crust"],
            hover_color=C["sapphire"], font=ctk.CTkFont(size=11),
            command=on_edit,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            acts, text="Del", width=40, height=24,
            fg_color=C["red"], text_color=C["crust"],
            hover_color=C["maroon"], font=ctk.CTkFont(size=11),
            command=on_delete,
        ).pack(side="left", padx=2)

        move = ctk.CTkFrame(self, fg_color="transparent")
        move.grid(row=4, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="w")
        ctk.CTkButton(
            move, text="↑", width=40, height=24,
            fg_color=C["surface1"], text_color=C["text"],
            hover_color=C["surface2"], font=ctk.CTkFont(size=11),
            command=on_move_up,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            move, text="↓", width=40, height=24,
            fg_color=C["surface1"], text_color=C["text"],
            hover_color=C["surface2"], font=ctk.CTkFont(size=11),
            command=on_move_down,
        ).pack(side="left", padx=2)

        # Recursively bind hover events so the border highlight triggers anywhere
        # on the card, not just on the frame background itself.
        self._bind_hover(self)

    def _bind_hover(self, w) -> None:
        w.bind("<Enter>", self._enter)
        w.bind("<Leave>", self._leave)
        for child in w.winfo_children():
            self._bind_hover(child)

    def _enter(self, _) -> None:
        self.configure(border_color=self._accent)

    def _leave(self, e) -> None:
        rx, ry = e.x_root, e.y_root
        cx, cy = self.winfo_rootx(), self.winfo_rooty()
        if not (cx <= rx <= cx + self.winfo_width() and cy <= ry <= cy + self.winfo_height()):
            self.configure(border_color=C["surface1"])
