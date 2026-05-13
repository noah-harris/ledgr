import pandas as pd
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from style import TABLE_BUTTON

class Table(ttk.Treeview):
    """
        A simple wrapper around ttk.Treeview that provides a convenient interface for displaying tabular data from a pandas DataFrame.
    """

    def __init__(
        self,
        master: ttk.Widget,
        columns: dict[str, dict],
        border: dict | None = None,
        visible_rows: int | None = None
    ):
        """
        columns maps each column name to an attribute dict with optional keys:
          - is_hidden: bool              — stored but not displayed (data columns only)
          - button: tuple[str, callable] — (label, callback); makes this a button-overlay column
          - width: int                   — pixel width of the column
          - justify: str                 — text alignment: "left", "center" (default), or "right"

        border: optional dict with keys:
          - color: str     — border color (e.g. "red", "#ff0000")
          - thickness: int — border thickness in pixels (default 1)
        """
        _justify_map = {"left": "w", "center": "center", "right": "e"}
        data_cols = {n: a for n, a in columns.items() if "button" not in a}
        btn_col_defs = {n: a for n, a in columns.items() if "button" in a}

        self._columns = tuple(data_cols)
        self._hidden_columns = tuple(n for n, a in data_cols.items() if a.get("is_hidden"))
        self._visible_columns = tuple(c for c in self._columns if c not in self._hidden_columns)
        self._button_columns: dict[str, dict] = {}
        self._place_btn_job = None
        self._column_widths: dict[str, int] = {n: a["width"] for n, a in columns.items() if "width" in a}
        self._column_anchors: dict[str, str] = {
            n: _justify_map.get(a["justify"], "center")
            for n, a in columns.items()
            if "justify" in a
        }

        # Optional border wrapper
        if border is not None:
            color = border.get("color", "black")
            thickness = border.get("thickness", 1)
            self._border_frame = tk.Frame(
                master,
                highlightthickness=thickness,
                highlightbackground=color,
                highlightcolor=color,
                bd=0,
            )
            tree_parent = self._border_frame
        else:
            self._border_frame = None
            tree_parent = master

        tree_kwargs: dict = {"columns": self._columns, "displaycolumns": self._visible_columns, "show": "headings"}
        if visible_rows is not None:
            tree_kwargs["height"] = visible_rows
        super().__init__(tree_parent, **tree_kwargs)

        # If wrapped, fill the border frame with the treeview
        if self._border_frame is not None:
            super().pack(fill="both", expand=True)

        self._data: pd.DataFrame = pd.DataFrame(columns=self._columns)

        for col in self._visible_columns:
            self.heading(col, text=col)
            kw: dict = {"anchor": self._column_anchors.get(col, "center")}
            if col in self._column_widths:
                kw["width"] = self._column_widths[col]
            self.column(col, **kw)

        for name, attrs in btn_col_defs.items():
            label, callback = attrs["button"]
            self.add_button_column(name, label, callback)

        self.bind("<Configure>", self._on_configure)
        self.bind("<MouseWheel>", self._on_scroll)

    # ──────────────────────────────────────────────────────────
    # Geometry manager passthroughs (so table.pack/grid/place
    # transparently apply to the border frame when present)
    # ──────────────────────────────────────────────────────────

    @property
    def container(self) -> tk.Widget:
        return self._border_frame if self._border_frame is not None else self

    def pack(self, **kwargs):
        if self._border_frame is not None:
            return self._border_frame.pack(**kwargs)
        return super().pack(**kwargs)

    def grid(self, **kwargs):
        if self._border_frame is not None:
            return self._border_frame.grid(**kwargs)
        return super().grid(**kwargs)

    def place(self, **kwargs):
        if self._border_frame is not None:
            return self._border_frame.place(**kwargs)
        return super().place(**kwargs)

    def pack_forget(self):
        if self._border_frame is not None:
            return self._border_frame.pack_forget()
        return super().pack_forget()

    def grid_forget(self):
        if self._border_frame is not None:
            return self._border_frame.grid_forget()
        return super().grid_forget()

    def place_forget(self):
        if self._border_frame is not None:
            return self._border_frame.place_forget()
        return super().place_forget()

    # ──────────────────────────────────────────────────────────

    def _schedule_place_buttons(self, delay: int = 50):
        if self._place_btn_job:
            self.after_cancel(self._place_btn_job)
        self._place_btn_job = self.after(delay, self._place_buttons)

    def _on_configure(self, _event):
        if self._button_columns:
            self._schedule_place_buttons(10)

    def _on_scroll(self, _event):
        if self._button_columns:
            self._schedule_place_buttons()

    def add_button_column(self, name: str, label: str, callback: callable, width: int = 80):
        """
        Add a button column. When clicked, the button calls `callback(row)` where
        `row` is a dict of the data columns for that row.
        """
        if name in self._columns or name in self._button_columns:
            raise ValueError(f"Column '{name}' already exists.")
        if name not in self._column_widths:
            self._column_widths[name] = width
        self._button_columns[name] = {"label": label, "callback": callback, "widgets": []}
        all_cols = self._columns + tuple(self._button_columns.keys())
        all_display = self._visible_columns + tuple(self._button_columns.keys())
        self["columns"] = all_cols
        self["displaycolumns"] = all_display
        for col in self._visible_columns:
            self.heading(col, text=col)
            kw: dict = {"anchor": self._column_anchors.get(col, "center")}
            if col in self._column_widths:
                kw["width"] = self._column_widths[col]
            self.column(col, **kw)
        for btn_name, btn_info in self._button_columns.items():
            self.heading(btn_name, text=btn_info["label"])
            self.column(btn_name, anchor="center", width=self._column_widths.get(btn_name, 80), stretch=False)

    @property
    def columns(self) -> tuple:
        return self._columns

    @property
    def visible_columns(self) -> tuple:
        return self._visible_columns

    @property
    def hidden_columns(self) -> tuple:
        return self._hidden_columns

    @property
    def visible_rows(self) -> int:
        return self.cget("height")

    @visible_rows.setter
    def visible_rows(self, value: int):
        self.configure(height=value)

    @property
    def data(self) -> pd.DataFrame:
        n = len(self._columns)
        rows = [self.item(item_id)["values"][:n] for item_id in self.get_children()]
        self._data = pd.DataFrame(rows, columns=self._columns)
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame):
        if value is None:
            value = pd.DataFrame(columns=list(self._columns))
        missing = set(self._columns) - set(value.columns)
        if missing:
            raise ValueError(f"DataFrame missing required columns: {missing}")
        self._data = value[list(self._columns)].copy()
        self._refresh_treeview()

    def _refresh_treeview(self):
        self._clear_button_widgets()
        for col in self._visible_columns:
            self.column(col, anchor=self._column_anchors.get(col, "center"))
        for row in self.get_children():
            self.delete(row)
        tags = ("_disabled",) if not getattr(self, "_table_enabled", True) else ()
        for _, row in self._data.iterrows():
            self.insert("", "end", values=tuple(row), tags=tags)
        if self._button_columns:
            self._schedule_place_buttons(10)

    def _clear_button_widgets(self):
        for col_info in self._button_columns.values():
            for w in col_info["widgets"]:
                w.destroy()
            col_info["widgets"].clear()

    def _place_buttons(self):
        self._clear_button_widgets()
        n = len(self._columns)
        for item_id in self.get_children():
            values = self.item(item_id)["values"]
            row_dict = dict(zip(self._columns, values[:n]))
            for col_name, col_info in self._button_columns.items():
                bbox = self.bbox(item_id, col_name)
                if not bbox:
                    continue
                x, y, w, h = bbox
                btn = tk.Button(
                    self,
                    text=col_info["label"],
                    command=lambda rd=row_dict, cb=col_info["callback"]: cb(rd),
                    **TABLE_BUTTON
                )
                btn.place(x=x, y=y, width=w, height=h)
                col_info["widgets"].append(btn)

    def yview(self, *args):
        result = super().yview(*args)
        if self._button_columns:
            self._schedule_place_buttons()
        return result

    def get_selected_row(self) -> dict | None:
        selected_row_ids = self.selection()
        if len(selected_row_ids) == 0:
            return None
        elif len(selected_row_ids) > 1:
            raise ValueError("Multiple rows selected, expected only one.")
        row_id = selected_row_ids[0]
        item = self.item(row_id).get("values")
        n = len(self._columns)
        return dict(zip(self._columns, item[:n]))

    def clear(self):
        self.data = pd.DataFrame(columns=self._columns)

    def set_table_state(self, enabled: bool):
        self._table_enabled = enabled
        btn_state = "normal" if enabled else "disabled"
        for col_info in self._button_columns.values():
            for w in col_info["widgets"]:
                w.configure(state=btn_state)
        if enabled:
            self.state(["!disabled"])
            if hasattr(self, "_overlay"):
                self._overlay.place_forget()
        else:
            self.state(["disabled"])
            if not hasattr(self, "_overlay"):
                self._overlay = tk.Frame(self, bg="#d3d3d3")
            self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._overlay.lift()