import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import messagebox

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes_data.json")

# Catppuccin Mocha palette
C = {
    "base":    "#1e1e2e",
    "mantle":  "#181825",
    "crust":   "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "overlay1": "#7f849c",
    "text":    "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "blue":    "#89b4fa",
    "lavender":"#b4befe",
    "sapphire":"#74c7ec",
    "sky":     "#89dceb",
    "teal":    "#94e2d5",
    "green":   "#a6e3a1",
    "yellow":  "#f9e2af",
    "peach":   "#fab387",
    "maroon":  "#eba0ac",
    "red":     "#f38ba8",
    "mauve":   "#cba6f7",
    "pink":    "#f5c2e7",
    "flamingo":"#f2cdcd",
    "rosewater":"#f5e0dc",
}

TAG_ACCENT_COLORS = [
    C["blue"], C["mauve"], C["teal"], C["peach"],
    C["green"], C["yellow"], C["sapphire"], C["pink"],
    C["lavender"], C["maroon"],
]


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tags": ["General"], "notes": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def tag_color(tags_list, tag):
    try:
        idx = tags_list.index(tag) % len(TAG_ACCENT_COLORS)
    except ValueError:
        idx = 0
    return TAG_ACCENT_COLORS[idx]


class NoteDialog(ctk.CTkToplevel):
    def __init__(self, parent, tags, current_tag="General", note=None):
        super().__init__(parent)
        self.result = None
        self.tags = tags

        self.title("Edit Note" if note else "New Note")
        self.geometry("520x540")
        self.resizable(True, True)
        self.configure(fg_color=C["base"])
        self.transient(parent)
        self.grab_set()
        self.focus()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Title", text_color=C["subtext0"],
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=20, pady=(20, 4), sticky="w")
        self.title_entry = ctk.CTkEntry(
            self, placeholder_text="Note title...",
            fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], height=38, font=ctk.CTkFont(size=14))
        self.title_entry.grid(row=1, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(self, text="Content", text_color=C["subtext0"],
                     font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=20, pady=(14, 4), sticky="w")
        self.content_box = ctk.CTkTextbox(
            self, fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], border_width=1, font=ctk.CTkFont(size=13))
        self.content_box.grid(row=3, column=0, padx=20, sticky="nsew")

        ctk.CTkLabel(self, text="Tag", text_color=C["subtext0"],
                     font=ctk.CTkFont(size=12)).grid(row=4, column=0, padx=20, pady=(14, 4), sticky="w")
        self.tag_var = ctk.StringVar(value=note["tag"] if note else current_tag)
        self.tag_menu = ctk.CTkOptionMenu(
            self, values=self.tags, variable=self.tag_var,
            fg_color=C["surface0"], button_color=C["surface1"],
            button_hover_color=C["surface2"], text_color=C["text"],
            dropdown_fg_color=C["surface0"], dropdown_text_color=C["text"],
            dropdown_hover_color=C["surface1"])
        self.tag_menu.grid(row=5, column=0, padx=20, sticky="ew")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_frame, text="Cancel", fg_color=C["surface1"],
                      text_color=C["text"], hover_color=C["surface2"],
                      command=self.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(btn_frame, text="Save", fg_color=C["blue"],
                      text_color=C["crust"], hover_color=C["sapphire"],
                      font=ctk.CTkFont(weight="bold"),
                      command=self._save).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        if note:
            self.title_entry.insert(0, note.get("title", ""))
            self.content_box.insert("1.0", note.get("content", ""))

    def _save(self):
        self.result = {
            "title":   self.title_entry.get().strip(),
            "content": self.content_box.get("1.0", "end-1c").strip(),
            "tag":     self.tag_var.get(),
        }
        self.destroy()


class NoteCard(ctk.CTkFrame):
    def __init__(self, master, note, tag_color_hex, on_edit, on_delete, **kwargs):
        super().__init__(master, corner_radius=12, fg_color=C["surface0"],
                         border_width=1, border_color=C["surface1"], **kwargs)
        self.grid_columnconfigure(0, weight=1)

        # Colored top accent bar
        accent = ctk.CTkFrame(self, height=4, corner_radius=0, fg_color=tag_color_hex)
        accent.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)

        if note.get("title"):
            ctk.CTkLabel(self, text=note["title"], anchor="w", justify="left",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=C["text"], wraplength=240
                         ).grid(row=1, column=0, columnspan=2, padx=14, pady=(10, 4), sticky="ew")

        preview = note.get("content", "")
        if len(preview) > 220:
            preview = preview[:220] + "…"
        if preview:
            ctk.CTkLabel(self, text=preview, anchor="nw", justify="left",
                         font=ctk.CTkFont(size=12), text_color=C["subtext0"],
                         wraplength=240
                         ).grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="ew")

        date_str = note.get("created", "")[:10]
        ctk.CTkLabel(self, text=date_str, font=ctk.CTkFont(size=10),
                     text_color=C["overlay0"]).grid(row=3, column=0, padx=14, pady=(0, 10), sticky="w")

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="e")
        ctk.CTkButton(actions, text="Edit", width=46, height=24,
                      fg_color=C["blue"], text_color=C["crust"],
                      hover_color=C["sapphire"], font=ctk.CTkFont(size=11),
                      command=on_edit).pack(side="left", padx=2)
        ctk.CTkButton(actions, text="Del", width=40, height=24,
                      fg_color=C["red"], text_color=C["crust"],
                      hover_color=C["maroon"], font=ctk.CTkFont(size=11),
                      command=on_delete).pack(side="left", padx=2)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("myNotes")
        self.geometry("1150x720")
        self.minsize(780, 480)
        self.configure(fg_color=C["base"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.data = load_data()
        self.selected_tag = self.data["tags"][0] if self.data["tags"] else "General"

        self._build_ui()
        self._refresh_sidebar()
        self._refresh_notes()

    # ── UI skeleton ──────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=C["mantle"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(3, weight=1)
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="myNotes",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=C["lavender"]
                     ).grid(row=0, column=0, padx=20, pady=(24, 6), sticky="w")

        ctk.CTkLabel(sidebar, text="TAGS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=C["overlay0"]
                     ).grid(row=1, column=0, padx=20, pady=(8, 4), sticky="w")

        self.tags_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent",
                                                  scrollbar_button_color=C["surface1"],
                                                  scrollbar_button_hover_color=C["surface2"])
        self.tags_frame.grid(row=3, column=0, padx=6, pady=(0, 6), sticky="nsew")
        self.tags_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(sidebar, text="＋  New Tag", fg_color="transparent",
                      border_color=C["surface1"], border_width=1,
                      text_color=C["subtext0"], hover_color=C["surface0"],
                      height=32, font=ctk.CTkFont(size=12),
                      command=self._add_tag
                      ).grid(row=4, column=0, padx=12, pady=12, sticky="ew")

        # ── Main area ──
        main = ctk.CTkFrame(self, corner_radius=0, fg_color=C["base"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # Top bar
        topbar = ctk.CTkFrame(main, height=62, corner_radius=0, fg_color=C["mantle"])
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        self.page_title_lbl = ctk.CTkLabel(topbar, text=self.selected_tag,
                                            font=ctk.CTkFont(size=18, weight="bold"),
                                            text_color=C["text"])
        self.page_title_lbl.grid(row=0, column=0, padx=22, pady=16)

        ctk.CTkButton(topbar, text="＋  New Note", fg_color=C["blue"],
                      text_color=C["crust"], hover_color=C["sapphire"],
                      font=ctk.CTkFont(size=13, weight="bold"), height=36,
                      command=self._new_note
                      ).grid(row=0, column=2, padx=18, pady=13)

        # Notes canvas
        self.notes_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                                    scrollbar_button_color=C["surface1"],
                                                    scrollbar_button_hover_color=C["surface2"])
        self.notes_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        for col in range(3):
            self.notes_scroll.grid_columnconfigure(col, weight=1, uniform="col")

    # ── Sidebar ──────────────────────────────────────────────────────────────

    def _refresh_sidebar(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()

        for i, tag in enumerate(self.data["tags"]):
            count = sum(1 for n in self.data["notes"] if n.get("tag") == tag)
            selected = tag == self.selected_tag
            accent = tag_color(self.data["tags"], tag)

            row_frame = ctk.CTkFrame(self.tags_frame,
                                     fg_color=C["surface0"] if selected else "transparent",
                                     corner_radius=8)
            row_frame.grid(row=i, column=0, padx=4, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)

            dot = ctk.CTkLabel(row_frame, text="●", font=ctk.CTkFont(size=10),
                                text_color=accent, width=18)
            dot.grid(row=0, column=0, padx=(10, 0), pady=8, sticky="w")

            lbl = ctk.CTkLabel(row_frame,
                                text=f"  {tag}",
                                anchor="w",
                                font=ctk.CTkFont(size=13, weight="bold" if selected else "normal"),
                                text_color=C["text"] if selected else C["subtext1"])
            lbl.grid(row=0, column=1, pady=8, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)

            badge = ctk.CTkLabel(row_frame, text=str(count),
                                  font=ctk.CTkFont(size=11),
                                  text_color=C["overlay1"],
                                  width=24)
            badge.grid(row=0, column=2, padx=(0, 10), pady=8, sticky="e")

            # bind clicks on all children
            for widget in (row_frame, dot, lbl, badge):
                widget.bind("<Button-1>", lambda e, t=tag: self._select_tag(t))

    def _select_tag(self, tag):
        self.selected_tag = tag
        self.page_title_lbl.configure(text=tag)
        self._refresh_sidebar()
        self._refresh_notes()

    def _add_tag(self):
        dialog = ctk.CTkInputDialog(text="Tag name:", title="New Tag",
                                     fg_color=C["base"], button_fg_color=C["blue"],
                                     button_hover_color=C["sapphire"],
                                     button_text_color=C["crust"],
                                     entry_fg_color=C["surface0"],
                                     entry_border_color=C["surface1"],
                                     entry_text_color=C["text"])
        tag = dialog.get_input()
        if tag:
            tag = tag.strip()
        if tag and tag not in self.data["tags"]:
            self.data["tags"].append(tag)
            save_data(self.data)
            self._refresh_sidebar()

    # ── Notes grid ───────────────────────────────────────────────────────────

    def _refresh_notes(self):
        for w in self.notes_scroll.winfo_children():
            w.destroy()

        notes = [n for n in self.data["notes"] if n.get("tag") == self.selected_tag]

        if not notes:
            ctk.CTkLabel(self.notes_scroll,
                         text="No notes here yet.\nPress  ＋ New Note  to add one.",
                         text_color=C["overlay0"],
                         font=ctk.CTkFont(size=14)
                         ).grid(row=0, column=0, columnspan=3, pady=80)
            return

        accent = tag_color(self.data["tags"], self.selected_tag)
        for i, note in enumerate(reversed(notes)):
            col = i % 3
            row = i // 3
            card = NoteCard(
                self.notes_scroll, note, accent,
                on_edit=lambda n=note: self._edit_note(n),
                on_delete=lambda n=note: self._delete_note(n),
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="new")

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def _new_note(self):
        d = NoteDialog(self, self.data["tags"], self.selected_tag)
        self.wait_window(d)
        if d.result:
            self.data["notes"].append({
                **d.result,
                "id":      str(datetime.now().timestamp()),
                "created": datetime.now().isoformat(),
            })
            save_data(self.data)
            self._refresh_sidebar()
            self._refresh_notes()

    def _edit_note(self, note):
        d = NoteDialog(self, self.data["tags"], note["tag"], note=note)
        self.wait_window(d)
        if d.result:
            note.update(d.result)
            note["updated"] = datetime.now().isoformat()
            save_data(self.data)
            self._refresh_sidebar()
            self._refresh_notes()

    def _delete_note(self, note):
        if messagebox.askyesno("Delete note", "Are you sure you want to delete this note?",
                                parent=self):
            self.data["notes"].remove(note)
            save_data(self.data)
            self._refresh_sidebar()
            self._refresh_notes()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()
