from tkinter import ttk

class DragMixin:
    """
    Mixin that adds drag-and-drop row reordering to any ttk.Treeview subclass.

    Call _init_drag() from your subclass __init__ after super().__init__().

        rank_col (str | None):
            Name of the column to auto-renumber after each drag, or None to skip.

        on_reorder (callable | None):
            Optional callback invoked with the updated list of row-value tuples
            after every reorder, e.g. to sync an external data source.
    """

    def _init_drag(self, rank_col: str | None = None, on_reorder=None):
        self._drag_item       = None
        self._drag_rank_col   = rank_col
        self._drag_on_reorder = on_reorder
        self._indicator       = ttk.Frame(self, style='Primary.TFrame', height=2)

        self.bind("<ButtonPress-1>",   self._on_button_press)
        self.bind("<B1-Motion>",       self._on_mouse_move)
        self.bind("<ButtonRelease-1>", self._on_button_release)

    # ── drag lifecycle ────────────────────────────────────────────────────────

    def _on_button_press(self, event):
        item = self.identify_row(event.y)
        if item:
            self._drag_item = item
            self.selection_set(item)

    def _on_mouse_move(self, event):
        if not self._drag_item:
            return
        target = self.identify_row(event.y)
        if target and target != self._drag_item:
            self._show_indicator(target, event.y)
        else:
            self._hide_indicator()

    def _on_button_release(self, event):
        if not self._drag_item:
            return
        self._hide_indicator()
        target = self.identify_row(event.y)
        if target and target != self._drag_item:
            self._move_item(self._drag_item, target, event.y)
        self._drag_item = None

    # ── indicator ─────────────────────────────────────────────────────────────

    def _show_indicator(self, target, cursor_y):
        bbox = self.bbox(target)
        if not bbox:
            self._hide_indicator()
            return
        x, y, width, height = bbox
        insert_y = y if cursor_y < y + height // 2 else y + height
        self._indicator.place(x=x, y=insert_y - 1, width=width, height=2)
        self._indicator.lift()

    def _hide_indicator(self):
        self._indicator.place_forget()

    # ── move ──────────────────────────────────────────────────────────────────

    def _move_item(self, item, target, cursor_y):
        bbox = self.bbox(target)
        if not bbox:
            return
        _, y, _, height = bbox
        index = self.index(target)
        if cursor_y >= y + height // 2:
            index += 1
        self.move(item, self.parent(target), index)
        self.selection_set(item)
        self.focus(item)

        if self._drag_rank_col is not None:
            self._renumber(self._drag_rank_col)

        if self._drag_on_reorder is not None:
            rows = [self.item(r, "values") for r in self.get_children()]
            self._drag_on_reorder(rows)

    def _renumber(self, rank_col: str):
        col_index = list(self["columns"]).index(rank_col)
        for i, row in enumerate(self.get_children(), start=1):
            values = list(self.item(row, "values"))
            values[col_index] = str(i)
            self.item(row, values=values)





