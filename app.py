import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

import data
from config import C, tag_color
from widgets import NoteCard, NoteDialog


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("myNotes")
        self.geometry("1160x740")
        self.minsize(800, 500)
        self.configure(fg_color=C["base"])

        self._data = data.load()
        self._selected_tag: str = self._data["tags"][0]
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_notes())

        self._build_ui()
        self._refresh_sidebar()
        self._refresh_notes()

    # ── layout ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self) -> None:
        sb = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=C["mantle"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(2, weight=1)
        sb.grid_propagate(False)

        ctk.CTkLabel(
            sb, text="myNotes",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=C["lavender"],
        ).grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")

        ctk.CTkLabel(
            sb, text="TAGS", font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["overlay0"],
        ).grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        self._tags_frame = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_button_color=C["surface1"],
            scrollbar_button_hover_color=C["surface2"],
        )
        self._tags_frame.grid(row=2, column=0, padx=6, pady=0, sticky="nsew")
        self._tags_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            sb, text="＋  New Tag",
            fg_color="transparent", border_color=C["surface1"], border_width=1,
            text_color=C["subtext0"], hover_color=C["surface0"],
            height=32, font=ctk.CTkFont(size=12),
            command=self._add_tag,
        ).grid(row=3, column=0, padx=12, pady=14, sticky="ew")

    def _build_main(self) -> None:
        main = ctk.CTkFrame(self, corner_radius=0, fg_color=C["base"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # top bar
        topbar = ctk.CTkFrame(main, height=66, corner_radius=0, fg_color=C["mantle"])
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        self._page_title = ctk.CTkLabel(
            topbar, text=self._selected_tag,
            font=ctk.CTkFont(size=18, weight="bold"), text_color=C["text"],
        )
        self._page_title.grid(row=0, column=0, padx=22, pady=0, sticky="w")

        self._count_lbl = ctk.CTkLabel(
            topbar, text="", font=ctk.CTkFont(size=12), text_color=C["overlay1"],
        )
        self._count_lbl.grid(row=0, column=0, padx=(180, 0), pady=0, sticky="w")

        search = ctk.CTkEntry(
            topbar, placeholder_text="Search…", textvariable=self._search_var,
            fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], placeholder_text_color=C["overlay0"],
            height=34, width=220, font=ctk.CTkFont(size=13),
        )
        search.grid(row=0, column=1, padx=10, pady=16, sticky="e")

        ctk.CTkButton(
            topbar, text="＋  New Note",
            fg_color=C["blue"], text_color=C["crust"],
            hover_color=C["sapphire"], font=ctk.CTkFont(size=13, weight="bold"),
            height=36, command=self._new_note,
        ).grid(row=0, column=2, padx=18, pady=15)

        # notes canvas
        self._notes_frame = ctk.CTkScrollableFrame(
            main, fg_color="transparent",
            scrollbar_button_color=C["surface1"],
            scrollbar_button_hover_color=C["surface2"],
        )
        self._notes_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=14)
        for col in range(3):
            self._notes_frame.grid_columnconfigure(col, weight=1, uniform="col")

    # ── sidebar ───────────────────────────────────────────────────────────────

    def _refresh_sidebar(self) -> None:
        for w in self._tags_frame.winfo_children():
            w.destroy()

        for i, tag in enumerate(self._data["tags"]):
            count = sum(1 for n in self._data["notes"] if n.get("tag") == tag)
            selected = tag == self._selected_tag
            accent = tag_color(self._data["tags"], tag)

            row = ctk.CTkFrame(
                self._tags_frame,
                fg_color=C["surface0"] if selected else "transparent",
                corner_radius=8,
            )
            row.grid(row=i, column=0, padx=4, pady=2, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=10),
                         text_color=accent, width=18,
                         ).grid(row=0, column=0, padx=(10, 0), pady=9, sticky="w")
            ctk.CTkLabel(
                row, text=f"  {tag}", anchor="w",
                font=ctk.CTkFont(size=13, weight="bold" if selected else "normal"),
                text_color=C["text"] if selected else C["subtext1"],
            ).grid(row=0, column=1, pady=9, sticky="ew")
            ctk.CTkLabel(
                row, text=str(count), font=ctk.CTkFont(size=11),
                text_color=C["overlay1"], width=26,
            ).grid(row=0, column=2, padx=(0, 10), pady=9, sticky="e")

            for widget in row.winfo_children():
                widget.bind("<Button-1>", lambda _, t=tag: self._select_tag(t))
            row.bind("<Button-1>", lambda _, t=tag: self._select_tag(t))

    def _select_tag(self, tag: str) -> None:
        self._selected_tag = tag
        self._page_title.configure(text=tag)
        self._search_var.set("")
        self._refresh_sidebar()
        self._refresh_notes()

    def _add_tag(self) -> None:
        d = ctk.CTkInputDialog(
            text="Tag name:", title="New Tag",
            fg_color=C["base"], button_fg_color=C["blue"],
            button_hover_color=C["sapphire"], button_text_color=C["crust"],
            entry_fg_color=C["surface0"], entry_border_color=C["surface1"],
            entry_text_color=C["text"],
        )
        tag = (d.get_input() or "").strip()
        if tag and tag not in self._data["tags"]:
            self._data["tags"].append(tag)
            data.save(self._data)
            self._refresh_sidebar()

    # ── notes grid ────────────────────────────────────────────────────────────

    def _refresh_notes(self) -> None:
        for w in self._notes_frame.winfo_children():
            w.destroy()

        query = self._search_var.get().lower()
        notes = [
            n for n in reversed(self._data["notes"])
            if n.get("tag") == self._selected_tag
            and (
                not query
                or query in n.get("title", "").lower()
                or query in n.get("content", "").lower()
            )
        ]

        total = sum(1 for n in self._data["notes"] if n.get("tag") == self._selected_tag)
        shown = len(notes)
        self._count_lbl.configure(
            text=f"  {shown} note{'s' if shown != 1 else ''}"
            + ("" if not query else f"  (filtered from {total})")
        )

        if not notes:
            msg = "No results for that search." if query else "No notes here yet.\nPress  ＋ New Note  to add one."
            ctk.CTkLabel(
                self._notes_frame, text=msg,
                text_color=C["overlay0"], font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, columnspan=3, pady=80)
            return

        accent = tag_color(self._data["tags"], self._selected_tag)
        for i, note in enumerate(notes):
            NoteCard(
                self._notes_frame, note, accent,
                on_edit=lambda n=note: self._edit_note(n),
                on_delete=lambda n=note: self._delete_note(n),
            ).grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="new")

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _new_note(self) -> None:
        d = NoteDialog(self, self._data["tags"], self._selected_tag)
        self.wait_window(d)
        if d.result:
            self._data["notes"].append({
                **d.result,
                "id":      str(datetime.now().timestamp()),
                "created": datetime.now().isoformat(),
            })
            data.save(self._data)
            self._refresh_sidebar()
            self._refresh_notes()

    def _edit_note(self, note: dict) -> None:
        d = NoteDialog(self, self._data["tags"], note["tag"], note=note)
        self.wait_window(d)
        if d.result:
            note.update(d.result)
            note["updated"] = datetime.now().isoformat()
            data.save(self._data)
            self._refresh_sidebar()
            self._refresh_notes()

    def _delete_note(self, note: dict) -> None:
        if messagebox.askyesno("Delete note", "Delete this note?", parent=self):
            self._data["notes"].remove(note)
            data.save(self._data)
            self._refresh_sidebar()
            self._refresh_notes()
