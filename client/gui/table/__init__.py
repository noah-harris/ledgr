from  .edit import EditMixin
from .table import Table
from .drag import DragMixin
from tkinter import ttk
import pandas as pd 

class DraggableTable(DragMixin, Table):

    def __init__(self, master: ttk.Widget, columns: dict[str, dict],
                 rank_col: str | None = None):
        super().__init__(master, columns=columns)
        self._init_drag(rank_col=rank_col, on_reorder=self._sync_data_from_tree)

    def _sync_data_from_tree(self, rows):
        self._data = pd.DataFrame(rows, columns=self._columns)


class EditableDraggableTable(DragMixin, EditMixin, Table):
    def __init__(self, master, columns: dict[str, dict], rank_col=None, editable=None):
        super().__init__(master, columns=columns)
        self._init_drag(rank_col=rank_col, on_reorder=self._sync_data_from_tree)
        self._init_edit(editable=editable)

    def _sync_data_from_tree(self, rows):
        self._data = pd.DataFrame(rows, columns=self._columns)

class EditableTable(EditMixin, Table):
    def __init__(self, master, columns: dict[str, dict], rank_col=None, editable=None):
        super().__init__(master, columns=columns)
        self._init_edit(editable=editable)

    def _sync_data_from_tree(self, rows):
        self._data = pd.DataFrame(rows, columns=self._columns)


__all__ = ["DraggableTable", "EditableDraggableTable", "EditableTable", "Table"]