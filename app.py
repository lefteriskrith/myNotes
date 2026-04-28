import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

import data
from config import C, NOTE_COLORS, tag_color
from note_utils import filter_visible_notes, move_note
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

        # force redraw on resize to prevent canvas artifacts
        self.bind("<Configure>", lambda _: self.after(1, self.update_idletasks))

    # ── layout ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self) -> None:
        sb = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=C["mantle"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_columnconfigure(0, weight=1)
        sb.grid_rowconfigure(2, weight=1)
        sb.grid_propagate(False)

        # title
        ctk.CTkLabel(
            sb, text="myNotes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C["lavender"],
        ).grid(row=0, column=0, padx=16, pady=(22, 0), sticky="w")

        # thin separator
        ctk.CTkFrame(sb, height=1, fg_color=C["surface1"]).grid(
            row=1, column=0, padx=12, pady=(10, 6), sticky="ew",
        )

        # tags list
        self._tags_frame = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_fg_color=C["mantle"],           # hide scrollbar track
            scrollbar_button_color=C["mantle"],       # invisible at rest
            scrollbar_button_hover_color=C["surface2"],  # shows on hover
        )
        self._tags_frame.grid(row=2, column=0, padx=4, pady=0, sticky="nsew")
        self._tags_frame.grid_columnconfigure(0, weight=1)

        # new tag button — compact, fits within 200px
        ctk.CTkButton(
            sb, text="+ New Tag",
            fg_color="transparent", border_color=C["surface1"], border_width=1,
            text_color=C["subtext0"], hover_color=C["surface0"],
            height=28, font=ctk.CTkFont(size=12),
            command=self._add_tag,
        ).grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def _build_main(self) -> None:
        main = ctk.CTkFrame(self, corner_radius=0, fg_color=C["base"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # top bar
        topbar = ctk.CTkFrame(main, height=62, corner_radius=0, fg_color=C["mantle"])
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        title_wrap = ctk.CTkFrame(topbar, fg_color="transparent")
        title_wrap.grid(row=0, column=0, padx=20, pady=0, sticky="w")

        self._page_title = ctk.CTkLabel(
            title_wrap, text=self._selected_tag,
            font=ctk.CTkFont(size=17, weight="bold"), text_color=C["text"],
        )
        self._page_title.pack(side="left")

        self._count_lbl = ctk.CTkLabel(
            title_wrap, text="",
            font=ctk.CTkFont(size=11), text_color=C["overlay1"],
        )
        self._count_lbl.pack(side="left", padx=(8, 0))

        search = ctk.CTkEntry(
            topbar, placeholder_text="Search…", textvariable=self._search_var,
            fg_color=C["surface0"], border_color=C["surface1"],
            text_color=C["text"], placeholder_text_color=C["overlay0"],
            height=32, width=200, font=ctk.CTkFont(size=12),
        )
        search.grid(row=0, column=1, padx=8, pady=15, sticky="e")

        ctk.CTkButton(
            topbar, text="+ New Note",
            fg_color=C["blue"], text_color=C["crust"],
            hover_color=C["sapphire"], font=ctk.CTkFont(size=13, weight="bold"),
            height=34, command=self._new_note,
        ).grid(row=0, column=2, padx=16, pady=14)

        # thin separator under topbar
        ctk.CTkFrame(main, height=1, fg_color=C["surface0"]).grid(
            row=0, column=0, sticky="sew",
        )

        # notes canvas
        self._notes_frame = ctk.CTkScrollableFrame(
            main, fg_color="transparent",
            scrollbar_fg_color=C["base"],             # hide scrollbar track
            scrollbar_button_color=C["surface1"],
            scrollbar_button_hover_color=C["surface2"],
        )
        self._notes_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=14)
        for col in range(3):
            self._notes_frame.grid_columnconfigure(col, weight=1, uniform="col")

        # keep canvas bg in sync to prevent resize artifacts
        def _fix_canvas(*_):
            self._notes_frame._parent_canvas.configure(bg=C["base"])
            self.update_idletasks()

        self._notes_frame._parent_canvas.configure(bg=C["base"])
        self._notes_frame._parent_canvas.bind("<Configure>", _fix_canvas)
        self._notes_frame.bind("<Configure>", _fix_canvas)

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
            row.grid(row=i, column=0, padx=2, pady=2, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=9),
                         text_color=accent, width=16,
                         ).grid(row=0, column=0, padx=(8, 0), pady=8)
            ctk.CTkLabel(
                row, text=f"  {tag}", anchor="w",
                font=ctk.CTkFont(size=12, weight="bold" if selected else "normal"),
                text_color=C["text"] if selected else C["subtext1"],
            ).grid(row=0, column=1, pady=8, sticky="ew")
            ctk.CTkLabel(
                row, text=str(count), font=ctk.CTkFont(size=10),
                text_color=C["overlay1"], width=22,
            ).grid(row=0, column=2, padx=(0, 8), pady=8)

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

        query = self._search_var.get()
        notes = filter_visible_notes(
            self._data["notes"], self._selected_tag, query
        )

        total = sum(1 for n in self._data["notes"] if n.get("tag") == self._selected_tag)
        shown = len(notes)
        suffix = f"  ({shown} of {total})" if query and shown != total else f"  {shown} note{'s' if shown != 1 else ''}"
        self._count_lbl.configure(text=suffix)

        if not notes:
            msg = "No results." if query else "No notes yet.\nPress  + New Note  to add one."
            ctk.CTkLabel(
                self._notes_frame, text=msg,
                text_color=C["overlay0"], font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, columnspan=3, pady=80)
            return

        tag_accent = tag_color(self._data["tags"], self._selected_tag)
        for i, note in enumerate(notes):
            nc = NOTE_COLORS.get(note.get("color", "default"), NOTE_COLORS["default"])
            accent = nc["accent"] or tag_accent
            bg     = nc["bg"]     or C["surface0"]
            NoteCard(
                self._notes_frame, note, accent, bg,
                on_edit=lambda n=note: self._edit_note(n),
                on_delete=lambda n=note: self._delete_note(n),
                on_move_up=lambda n=note: self._move_note(n, "up"),
                on_move_down=lambda n=note: self._move_note(n, "down"),
            ).grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="new")

    def _move_note(self, note: dict, direction: str) -> None:
        moved = move_note(
            self._data["notes"], note["id"], direction,
            self._selected_tag, self._search_var.get(),
        )
        if moved:
            data.save(self._data)
            self._refresh_notes()

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

    def _move_note(self, note: dict, direction: str) -> None:
        moved = move_note(
            self._data["notes"], note["id"], direction,
            self._selected_tag, self._search_var.get(),
        )
        if moved:
            data.save(self._data)
            self._refresh_notes()

    def _delete_note(self, note: dict) -> None:
        if messagebox.askyesno("Delete note", "Delete this note?", parent=self):
            self._data["notes"].remove(note)
            data.save(self._data)
            self._refresh_sidebar()
            self._refresh_notes()
