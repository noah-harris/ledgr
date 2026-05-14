import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk


def _make_icon(draw_fn, size=16) -> ImageTk.PhotoImage:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_fn(draw, size)
    return ImageTk.PhotoImage(img)


def _draw_eye(draw: ImageDraw.ImageDraw, s: int):
    cx, cy = s // 2, s // 2
    draw.ellipse([cx - 6, cy - 4, cx + 6, cy + 4], outline="white", width=1)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill="white")


def _draw_pencil(draw: ImageDraw.ImageDraw, s: int):
    draw.polygon([(3, s - 4), (s - 4, 3), (s - 1, 6), (6, s - 1)], fill="white")
    draw.polygon([(3, s - 4), (1, s - 1), (6, s - 1)], fill="white")


def _draw_trash(draw: ImageDraw.ImageDraw, s: int):
    draw.rectangle([4, 5, s - 4, s - 2], outline="white", width=1)
    draw.line([(2, 4), (s - 2, 4)], fill="white", width=1)
    draw.line([(6, 2), (s - 6, 2)], fill="white", width=2)
    for x in [6, s // 2, s - 6]:
        draw.line([(x, 6), (x, s - 3)], fill="white", width=1)


def _draw_plus(draw: ImageDraw.ImageDraw, s: int):
    cx, cy = s // 2, s // 2
    draw.line([(cx, 2), (cx, s - 2)], fill="white", width=2)
    draw.line([(2, cy), (s - 2, cy)], fill="white", width=2)


_ICONS: dict[str, ImageTk.PhotoImage] = {}


def _get_icons() -> dict[str, ImageTk.PhotoImage]:
    if not _ICONS:
        _ICONS["view"] = _make_icon(_draw_eye)
        _ICONS["edit"] = _make_icon(_draw_pencil)
        _ICONS["delete"] = _make_icon(_draw_trash)
        _ICONS["create"] = _make_icon(_draw_plus)
    return _ICONS


class ControlPanelMixin:
    """
    Wraps a Table in a panel with a title and View / Edit / Delete / Create buttons.

    The mixin creates `_cp_frame` before calling Table.__init__, passing an
    inner sub-frame as the Treeview's master so no re-parenting is needed.

    Usage:
        class MyTable(ControlPanelMixin, Table): ...
        t = MyTable(master, columns, title="Records")
        t.set_edit_command(my_edit_fn)   # fn receives selected row dict
        t.set_create_command(my_create_fn)  # fn receives no args
        t.grid(...)

    View / Edit / Delete buttons are automatically disabled when no row is
    selected and re-enabled on <<TreeviewSelect>>.
    """

    def __init__(self, master: tk.Widget, columns: dict, title: str = "", **kwargs):
        icons = _get_icons()

        self._cp_frame = ttk.Frame(master)
        self._cp_frame.columnconfigure(0, weight=1)
        self._cp_frame.rowconfigure(1, weight=1)

        # ── Header ────────────────────────────────────────────────
        header = ttk.Frame(self._cp_frame, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header, text=title, style="Heading.TLabel")
        self.title_label.grid(row=0, column=0, padx=(10, 0), pady=6, sticky="w")

        btn_group = ttk.Frame(header, style="Surface.TFrame")
        btn_group.grid(row=0, column=1, padx=6, pady=4, sticky="e")

        self.view_btn = ttk.Button(
            btn_group, text=" View", image=icons["view"], compound="left",
            style="Ghost.TButton", state="disabled",
        )
        self.edit_btn = ttk.Button(
            btn_group, text=" Edit", image=icons["edit"], compound="left",
            style="Table.TButton", state="disabled",
        )
        self.delete_btn = ttk.Button(
            btn_group, text=" Delete", image=icons["delete"], compound="left",
            style="Danger.TButton", state="disabled",
        )
        self.create_btn = ttk.Button(
            btn_group, text=" Create", image=icons["create"], compound="left",
            style="TButton",
        )
        self.view_btn.grid(row=0, column=0, padx=(0, 4))
        self.edit_btn.grid(row=0, column=1, padx=(0, 4))
        self.delete_btn.grid(row=0, column=2, padx=(0, 4))
        self.create_btn.grid(row=0, column=3)

        # ── Table area ────────────────────────────────────────────
        self._cp_table_frame = ttk.Frame(self._cp_frame)
        self._cp_table_frame.grid(row=1, column=0, sticky="nsew")
        self._cp_table_frame.columnconfigure(0, weight=1)
        self._cp_table_frame.rowconfigure(0, weight=1)

        super().__init__(self._cp_table_frame, columns=columns, **kwargs)

        # Pack the Table's container (border_frame or Treeview) into _cp_table_frame
        # Bypass our own pack/grid overrides by calling directly on the widget.
        if self._border_frame is not None:
            self._border_frame.grid(row=0, column=0, sticky="nsew")
        else:
            ttk.Treeview.grid(self, row=0, column=0, sticky="nsew")

        self.bind("<<TreeviewSelect>>", self._on_selection_change)

    # ── Geometry passthroughs → _cp_frame ─────────────────────────

    def pack(self, **kwargs):
        return self._cp_frame.pack(**kwargs)

    def grid(self, **kwargs):
        return self._cp_frame.grid(**kwargs)

    def place(self, **kwargs):
        return self._cp_frame.place(**kwargs)

    def pack_forget(self):
        return self._cp_frame.pack_forget()

    def grid_forget(self):
        return self._cp_frame.grid_forget()

    def place_forget(self):
        return self._cp_frame.place_forget()

    # ── Command binding ───────────────────────────────────────────

    def set_view_command(self, func):
        self.view_btn.config(command=lambda: self._call_with_selection(func))

    def set_edit_command(self, func):
        self.edit_btn.config(command=lambda: self._call_with_selection(func))

    def set_delete_command(self, func):
        self.delete_btn.config(command=lambda: self._call_with_selection(func))

    def set_create_command(self, func):
        self.create_btn.config(command=func)

    # ── Internal helpers ──────────────────────────────────────────

    def _call_with_selection(self, func):
        row = self.get_selected_row()
        if row is not None:
            func(row)

    def _on_selection_change(self, _event=None):
        has_selection = bool(self.selection())
        state = "normal" if has_selection else "disabled"
        for btn in (self.view_btn, self.edit_btn, self.delete_btn):
            btn.configure(state=state)
