import tkinter as tk
import pandas as pd
from tkinter import ttk

class EditMixin:

    def _init_edit(self, editable: list[str] | None = None):
        self._editable = set(editable) if editable is not None else None
        self._validators = {}
        self._col_options: dict[str, list] = {}
        self._options_readonly: dict[str, bool] = {}
        self._edit_entry = None
        self.bind("<Double-1>", self._on_double_click)

    def set_validator(self, col: str, fn):
        """
        Register a validator for a column.
        fn(raw_string) -> coerced_value  (or raise ValueError to block the edit)
        """
        self._validators[col] = fn

    def set_options(self, col: str, options: list, *, readonly: bool = True):
        """
        Register a dropdown option list for a column.
        Columns with options render a ttk.Combobox instead of a plain Entry.
        """
        self._col_options[col] = options
        self._options_readonly[col] = readonly

    # ── helpers ──────────────────────────────────────────────────────────────

    def _visible_column_names(self) -> list:
        """
        Return the list of column names in visible order.
        Treeview's displaycolumns is ("#all",) when no filtering is active.
        """
        disp = self["displaycolumns"]
        if not disp or disp == ("#all",):
            return list(self["columns"])
        return list(disp)

    # ── row editing ──────────────────────────────────────────────────────────

    def add_row(self, values=None):
        if values is None:
            values = [""] * len(self._columns)
        elif len(values) != len(self._columns):
            raise ValueError(f"Expected {len(self._columns)} values, got {len(values)}")
        new_row = pd.DataFrame([values], columns=self._columns)
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        self.event_generate("<<RowChange>>")

    def delete_row(self, item_id):
        if item_id is None:
            return
        self.delete(item_id)
        self.event_generate("<<RowChange>>")

    def get(self):
        return self.data

    # ── entry points ─────────────────────────────────────────────────────────

    def _on_double_click(self, event):
        item = self.identify_row(event.y)
        col  = self.identify_column(event.x)
        if not item or not col:
            return
        self._open_editor(item, col)

    def _open_editor_by_col(self, col_name: str):
        item = self.focus()
        if not item:
            return
        visible = self._visible_column_names()
        if col_name not in visible:
            return
        self._open_editor(item, f"#{visible.index(col_name) + 1}")

    # ── editor ────────────────────────────────────────────────────────────────

    def _open_editor(self, item, col):
        # `col` is "#N" where N is 1-based over *visible* columns.
        visible = self._visible_column_names()
        visible_index = int(col[1:]) - 1
        if visible_index < 0 or visible_index >= len(visible):
            return
        col_name = visible[visible_index]

        # Map column name back to full-column index for reading/writing values.
        full_cols = list(self["columns"])
        col_index = full_cols.index(col_name)

        if self._editable is not None and col_name not in self._editable:
            return

        bbox = self.bbox(item, col)
        if not bbox:
            return
        x, y, width, height = bbox

        original = self.item(item, "values")[col_index]
        self._close_editor()

        options = self._col_options.get(col_name)

        if options is not None:
            widget = self._make_combobox(col_name, options, original, width)
        else:
            widget = self._make_entry(original)

        widget.place(x=x, y=y, width=width, height=height)
        widget.focus_set()
        self._edit_entry = widget

        def commit(e=None):
            raw = widget.get()

            if options is not None and self._options_readonly.get(col_name, True):
                if raw not in options:
                    widget.configure(foreground="#cc0000")
                    return

            validator = self._validators.get(col_name)
            if validator:
                try:
                    new_value = validator(raw)
                except ValueError:
                    widget.configure(foreground="#cc0000")
                    return
            else:
                new_value = raw

            values = list(self.item(item, "values"))
            values[col_index] = new_value
            self.item(item, values=values)
            self._close_editor()

        def cancel(e=None):
            self._close_editor()

        def clear_error(e=None):
            widget.configure(foreground="black")

        widget.bind("<Return>",   commit)
        widget.bind("<Escape>",   cancel)
        widget.bind("<KeyPress>", clear_error)

        if options is not None:
            widget.bind("<<ComboboxSelected>>", commit)

    def _make_entry(self, value: str) -> tk.Entry:
        entry = tk.Entry(
            self, relief="flat",
            highlightthickness=2,
            highlightbackground="#0078D7",
            highlightcolor="#0078D7",
        )
        entry.insert(0, value)
        entry.select_range(0, "end")
        return entry

    def _make_combobox(self, col_name: str, options: list, value: str, width: int) -> ttk.Combobox:
        state = "readonly" if self._options_readonly.get(col_name, True) else "normal"
        combo = ttk.Combobox(self, values=options, state=state)
        combo.set(value)
        combo.after(50, combo.event_generate, "<Button-1>")
        return combo

    # ── cleanup ───────────────────────────────────────────────────────────────

    def _close_editor(self):
        if self._edit_entry:
            self._edit_entry.destroy()
            self._edit_entry = None
            self.event_generate("<<RowChange>>")
            self.focus_set()

# import tkinter as tk
# import pandas as pd
# from tkinter import ttk

# class EditMixin:

#     def _init_edit(self, editable: list[str] | None = None):
#         self._editable = set(editable) if editable is not None else None
#         self._validators = {}
#         self._col_options: dict[str, list] = {}
#         self._options_readonly: dict[str, bool] = {}
#         self._edit_entry = None
#         self.bind("<Double-1>", self._on_double_click)

#     def set_validator(self, col: str, fn):
#         """
#         Register a validator for a column.
#         fn(raw_string) -> coerced_value  (or raise ValueError to block the edit)
#         """
#         self._validators[col] = fn

#     def set_options(self, col:str, options:list, *, readonly:bool=True):
#         """
#         Register a dropdown option list for a column.
#         Columns with options render a ttk.Combobox instead of a plain Entry.

#         Parameters
#         ----------
#         col      : column name
#         options  : list of string choices shown in the dropdown
#         readonly : if True (default), only listed values are accepted;
#                    if False, the combobox is editable and arbitrary input is allowed
#         """
#         self._col_options[col] = options
#         self._options_readonly[col] = readonly

#     # ── row editing ──────────────────────────────────────────────────────────

#     def add_row(self, values=None):
#         if values is None:
#             values = [""] * len(self._columns)
#         elif len(values) != len(self._columns):
#             raise ValueError(f"Expected {len(self._columns)} values, got {len(values)}")
#         new_row = pd.DataFrame([values], columns=self._columns)
#         self.data = pd.concat([self.data, new_row], ignore_index=True)
#         self.event_generate("<<RowChange>>")

#     def delete_row(self, item_id):
#         if item_id is None:
#             return
#         self.delete(item_id)
#         self.event_generate("<<RowChange>>")

#     def get(self):
#         return self.data

#     # ── entry points ─────────────────────────────────────────────────────────

#     def _on_double_click(self, event):
#         item = self.identify_row(event.y)
#         col  = self.identify_column(event.x)
#         if not item or not col:
#             return
#         self._open_editor(item, col)

#     def _open_editor_by_col(self, col_name: str):
#         item = self.focus()
#         if not item:
#             return
#         cols = list(self["columns"])
#         if col_name not in cols:
#             return
#         self._open_editor(item, f"#{cols.index(col_name) + 1}")

#     # ── editor ────────────────────────────────────────────────────────────────

#     def _open_editor(self, item, col):
#         col_index = int(col[1:]) - 1
#         col_name  = self["columns"][col_index]

#         if self._editable is not None and col_name not in self._editable:
#             return

#         bbox = self.bbox(item, col)
#         if not bbox:
#             return
#         x, y, width, height = bbox

#         original = self.item(item, "values")[col_index]
#         self._close_editor()

#         options = self._col_options.get(col_name)

#         if options is not None:
#             widget = self._make_combobox(col_name, options, original, width)
#         else:
#             widget = self._make_entry(original)

#         widget.place(x=x, y=y, width=width, height=height)
#         widget.focus_set()
#         self._edit_entry = widget

#         def commit(e=None):
#             raw = widget.get()

#             # readonly combobox: block values not in the list
#             if options is not None and self._options_readonly.get(col_name, True):
#                 if raw not in options:
#                     widget.configure(foreground="#cc0000")
#                     return

#             validator = self._validators.get(col_name)
#             if validator:
#                 try:
#                     new_value = validator(raw)
#                 except ValueError:
#                     widget.configure(foreground="#cc0000")
#                     return
#             else:
#                 new_value = raw

#             values = list(self.item(item, "values"))
#             values[col_index] = new_value
#             self.item(item, values=values)
#             self._close_editor()

#         def cancel(e=None):
#             self._close_editor()

#         def clear_error(e=None):
#             widget.configure(foreground="black")

#         widget.bind("<Return>",   commit)
#         widget.bind("<Escape>",   cancel)
#         widget.bind("<KeyPress>", clear_error)

#         # For comboboxes, also commit when the user picks an item from the list
#         if options is not None:
#             widget.bind("<<ComboboxSelected>>", commit)

#     def _make_entry(self, value: str) -> tk.Entry:
#         entry = tk.Entry(
#             self, relief="flat",
#             highlightthickness=2,
#             highlightbackground="#0078D7",
#             highlightcolor="#0078D7",
#         )
#         entry.insert(0, value)
#         entry.select_range(0, "end")
#         return entry

#     def _make_combobox(self, col_name: str, options: list, value: str, width: int) -> ttk.Combobox:
#         state = "readonly" if self._options_readonly.get(col_name, True) else "normal"
#         combo = ttk.Combobox(self, values=options, state=state)
#         combo.set(value)
#         # Drop the list immediately so the user doesn't have to click the arrow
#         combo.after(50, combo.event_generate, "<Button-1>")
#         return combo

#     # ── cleanup ───────────────────────────────────────────────────────────────

#     def _close_editor(self):
#         if self._edit_entry:
#             self._edit_entry.destroy()
#             self._edit_entry = None
#             self.event_generate("<<RowChange>>")
#             self.focus_set()