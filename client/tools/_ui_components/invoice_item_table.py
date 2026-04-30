from gui import EditableDraggableTable
import tkinter as tk
import data

class InvoiceItemTable(EditableDraggableTable):

    def __init__(self, master):

        columns={"#": {"width":20}, "Category": {"justify":"left", "width":250}, "Description": {"justify":"left", "width":250}, "Quantity": {"width":65}, "Amount": {"width":80}}
        self.rank_col='#'
        editable=['Description', 'Quantity', 'Amount']
        
        super().__init__(master, columns=columns, rank_col=self.rank_col, editable=editable)

        self._cat_col = "Category"
        self._cat_seg_col = "Segment"
        self._cat_cat_col = "Category"
        self._cat_sub_col = "Subcategory"
        self._cat_data = data.InvoiceItemCategory()

        # Runtime editor state
        self._cat_entry = None
        self._cat_listbox_frame = None
        self._cat_listbox = None
        self._cat_item = None
        self._cat_col_index = None

        self.bind("<Double-1>", self._cat_on_double_click, add="+")
        self.bind("<F1>", self._cat_on_f1)
        self.bind("<F2>", lambda e: self._open_editor_by_col("Description"))
        self.bind("<F3>", lambda e: self._open_editor_by_col("Quantity"))
        self.bind("<F4>", lambda e: self._open_editor_by_col("Amount"))
        

    # ── entry points ──────────────────────────────────────────────────────────

    def _cat_on_f1(self, event):
        item = self.focus()
        if not item:
            return
        cols = list(self["columns"])
        if self._cat_col not in cols:
            return
        self._cat_open_editor(item, cols.index(self._cat_col))

    def _cat_on_double_click(self, event):
        item = self.identify_row(event.y)
        col  = self.identify_column(event.x)
        if not item or not col:
            return
        col_index = int(col[1:]) - 1
        col_name  = self["columns"][col_index]
        if col_name != self._cat_col:
            return
        self._cat_open_editor(item, col_index)

    # ── open editor ───────────────────────────────────────────────────────────

    def _cat_open_editor(self, item, col_index):
        bbox = self.bbox(item, f"#{col_index + 1}")
        if not bbox:
            return
        x, y, width, height = bbox

        self._cat_item      = item
        self._cat_col_index = col_index
        self._cat_close()

        # ── Entry ─────────────────────────────────────────────────────────────
        entry = tk.Entry(self, relief="flat", highlightthickness=1, highlightbackground="#0078D7", highlightcolor="#0078D7")
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        self._cat_entry = entry

        # ── Listbox in a Frame ────────────────────────────────────────────────
        lb_frame = tk.Frame(self, bd=1, relief="solid", bg="#cccccc")
        lb = tk.Listbox(lb_frame, selectmode="single", activestyle="none", font=("Segoe UI", 9), relief="flat", highlightthickness=0, height=6)
        lb.pack(fill="both", expand=True, padx=1, pady=1)

        lb_frame.place(x=x, y=y + height, width=max(width, 300))
        lb_frame.lift()
        self._cat_listbox_frame = lb_frame
        self._cat_listbox = lb

        self._cat_refresh_list(entry.get())
        entry.bind("<KeyRelease>", lambda e: self._cat_on_key(e))
        entry.bind("<Down>",       lambda e: self._cat_focus_list())
        entry.bind("<Return>",     lambda e: self._cat_commit())
        entry.bind("<Escape>",     lambda e: self._cat_close())
        lb.bind("<Return>",        lambda e: self._cat_pick_selected())
        lb.bind("<Double-1>",      lambda e: self._cat_pick_selected())
        lb.bind("<Escape>",        lambda e: self._cat_close())
        lb.bind("<Up>", lambda e: entry.focus_set() if lb.curselection() and lb.curselection()[0] == 0 else None)

    # ── typing logic ──────────────────────────────────────────────────────────


    def _cat_on_key(self, event):
        if event.keysym in ("Return", "Escape", "Up", "Down"):
            return
        text = self._cat_entry.get().upper()
        self._cat_refresh_list(text)
        self._cat_try_autocomplete(text)


    def _cat_refresh_list(self, text: str):
        matches = self._cat_get_matches(text)
        lb = self._cat_listbox
        lb.delete(0, "end")
        for m in matches:
            lb.insert("end", m)
        lb.config(height=max(1, len(matches)))  # ← add this
        if matches:
            lb.selection_set(0)

    def _cat_try_autocomplete(self, text: str):
        if self._cat_data.empty:
            return
        parts = text.split(" - ")
        seg_typed = parts[0] if len(parts) >= 1 else ""
        cat_typed = parts[1] if len(parts) >= 2 else None
        sub_typed = parts[2] if len(parts) >= 3 else None
        df = self._cat_data

        # --- resolve segment ---
        seg_matches = df[df[self._cat_seg_col].str.startswith(seg_typed, na=False)][self._cat_seg_col].unique()
        if len(seg_matches) == 1 and cat_typed is None:
            self._cat_set_text(f"{seg_matches[0]} - ")
            return
        if cat_typed is None:
            return

        # --- resolve category ---
        seg = seg_matches[0] if len(seg_matches) == 1 else seg_typed
        cat_df = df[df[self._cat_seg_col] == seg]
        cat_matches = cat_df[cat_df[self._cat_cat_col].str.startswith(cat_typed, na=False)][self._cat_cat_col].unique()
        if len(cat_matches) == 1 and sub_typed is None:
            self._cat_set_text(f"{seg} - {cat_matches[0]} - ")
            return
        if sub_typed is None:
            return

        # --- resolve subcategory ---
        cat = cat_matches[0] if len(cat_matches) == 1 else cat_typed
        sub_df = cat_df[cat_df[self._cat_cat_col] == cat]
        sub_matches = sub_df[sub_df[self._cat_sub_col].str.startswith(sub_typed, na=False)][self._cat_sub_col].unique()
        if len(sub_matches) == 1:
            self._cat_set_text(f"{seg} - {cat} - {sub_matches[0]}")
            self._cat_commit()


    def _cat_get_matches(self, text: str) -> list[str]:
        if self._cat_data.empty:
            return []

        parts = text.split(" - ")
        seg_typed = parts[0] if len(parts) >= 1 else ""
        cat_typed = parts[1] if len(parts) >= 2 else None
        sub_typed = parts[2] if len(parts) >= 3 else None

        df = self._cat_data

        if cat_typed is None:
            segs = df[df[self._cat_seg_col].str.startswith(seg_typed, na=False)][self._cat_seg_col].unique()
            return [f"{s} - ..." for s in segs]

        seg_matches = df[df[self._cat_seg_col].str.startswith(seg_typed, na=False)][self._cat_seg_col].unique()
        seg = seg_matches[0] if len(seg_matches) == 1 else seg_typed
        cat_df = df[df[self._cat_seg_col] == seg]

        if sub_typed is None:
            cats = cat_df[cat_df[self._cat_cat_col].str.startswith(cat_typed, na=False)][self._cat_cat_col].unique()
            return [f"{seg} - {c} - ..." for c in cats]

        cat_matches = cat_df[cat_df[self._cat_cat_col].str.startswith(cat_typed, na=False)][self._cat_cat_col].unique()
        cat = cat_matches[0] if len(cat_matches) == 1 else cat_typed
        sub_df = cat_df[cat_df[self._cat_cat_col] == cat]
        subs = sub_df[sub_df[self._cat_sub_col].str.startswith(sub_typed, na=False)][self._cat_sub_col].unique()
        return [f"{seg} - {cat} - {s}" for s in subs]

    # ── helpers ───────────────────────────────────────────────────────────────

    def _cat_set_text(self, text: str):
        entry = self._cat_entry
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.icursor("end")
        self._cat_refresh_list(text)

    def _cat_focus_list(self):
        lb = self._cat_listbox
        if lb.size():
            lb.focus_set()
            lb.selection_clear(0, "end")
            lb.selection_set(0)
            lb.activate(0)

    def _cat_pick_selected(self):
        lb = self._cat_listbox
        sel = lb.curselection()
        if not sel:
            return
        value = lb.get(sel[0])
        if value.endswith(" - ..."):
            value = value[:-len(" - ...")] + " - "
        self._cat_set_text(value)

        parts = [p.strip() for p in value.split(" - ")]
        if len(parts) == 3 and all(parts):
            self._cat_commit()
        else:
            self._cat_entry.focus_set()
            self._cat_entry.icursor("end")

    def _cat_commit(self):
        text = self._cat_entry.get().strip()
        parts = [p.strip() for p in text.split(" - ")]
        if len(parts) == 3 and all(parts):
            values = list(self.item(self._cat_item, "values"))
            values[self._cat_col_index] = text
            self.item(self._cat_item, values=values)
            self._cat_close()
        else:
            self._cat_listbox.delete(0, "end")
            self._cat_listbox.insert("end", "⚠ Complete all three parts first")

    def _cat_close(self):
        if self._cat_entry:
            self._cat_entry.destroy()
            self._cat_entry = None
        if self._cat_listbox_frame:
            self._cat_listbox_frame.destroy()
            self._cat_listbox_frame = None
        self._cat_listbox = None
        self.focus_set()


    def add_row(self, values=None):
        display_orders = [int(self.set(child, self.rank_col)) for child in self.get_children()]
        next_display_order = max(display_orders, default=0) + 1
        if values is None:
            values = [next_display_order, "", "", "1.000", ""]
        super().add_row(values=values)
        # Set new row as selected row
        self.focus(self.get_children()[-1])
        self.selection_set(self.get_children()[-1])


    def delete_row(self):
        try:
            if not self.selection():
                return
            item_id = self.selection()[0]
            children = list(self.get_children())
            idx = children.index(item_id)
            if len(children) == 1:
                self.selection_set("")
            else:
                next_idx = idx - 1 if idx > 0 else 1
                self.selection_set(children[next_idx])
                self.focus(children[next_idx])
            super().delete_row(item_id)
            # Reset the display_order of remaining items
            for i, child in enumerate(self.get_children()):
                self.set(child, self.rank_col, i + 1)
        except Exception as e:
            print(f"Error deleting row: {e}")
            