import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import pandas as pd
import requests

from tools import Tool
from gui import ImageViewer, Table
from config import IMAGE_DIRECTORY, SUPPORTED_IMAGE_FORMATS, FILE_EXPLORER_IMAGE_TYPES, make_logger
from resolve_image_bytes import resolve_image_bytes
from db import get_connection
import data

logger = make_logger(__name__)

_STATUS_DISPLAY = {"u": "Unsorted", "s": "Skipped", "o": "Orphan", "c": "Complete"}
_STATUS_CODES = {v: k for k, v in _STATUS_DISPLAY.items()}

_TABLE_COLUMNS = {
    "ImageId":     {"is_hidden": True},
    "ImageFileName": {"is_hidden": True},
    "FileName":    {"justify": "left", "width": 280},
    "FileType":    {"justify": "left", "width": 60},
    "ContentType": {"justify": "left", "width": 140},
    "StatusName":  {"justify": "center", "width": 100},
    "StatusType":  {"is_hidden": True},
}


class ImageUploader(Tool):

    def __init__(self, master):
        super().__init__(master, title="Image Uploader")

        self._df: pd.DataFrame = pd.DataFrame()
        self._selected_image_id: str | None = None
        self._original_row: dict | None = None

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._build_toolbar()
        self._build_left_panel()
        self._build_right_panel()
        self._refresh()

    # ── Toolbar ───────────────────────────────────────────────

    def _build_toolbar(self):
        toolbar = ttk.Frame(self, style="Surface.TFrame")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))

        ttk.Button(toolbar, text="Upload Files", command=self._on_upload).pack(side="left", padx=(0, 8))
        self._delete_btn = ttk.Button(
            toolbar, text="Delete", style="Danger.TButton",
            command=self._on_delete, state="disabled"
        )
        self._delete_btn.pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="Refresh", style="Ghost.TButton", command=self._refresh).pack(side="left")

    # ── Left panel ────────────────────────────────────────────

    def _build_left_panel(self):
        panel = ttk.Frame(self, style="Surface.TFrame")
        panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        panel.rowconfigure(1, weight=1)
        panel.columnconfigure(0, weight=1)

        filter_bar = ttk.Frame(panel, style="Surface.TFrame")
        filter_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        filter_bar.columnconfigure(1, weight=1)

        ttk.Label(filter_bar, text="Search:").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_filters())
        ttk.Entry(filter_bar, textvariable=self._search_var).grid(row=0, column=1, sticky="ew", padx=(0, 12))

        ttk.Label(filter_bar, text="Status:").grid(row=0, column=2, sticky="w", padx=(0, 4))
        self._status_filter_var = tk.StringVar(value="All")
        status_cb = ttk.Combobox(
            filter_bar, textvariable=self._status_filter_var,
            values=["All"] + list(_STATUS_DISPLAY.values()),
            state="readonly", width=12,
        )
        status_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        status_cb.grid(row=0, column=3, padx=(0, 12))

        ttk.Label(filter_bar, text="Content:").grid(row=0, column=4, sticky="w", padx=(0, 4))
        self._content_filter_var = tk.StringVar(value="All")
        self._content_filter_cb = ttk.Combobox(
            filter_bar, textvariable=self._content_filter_var,
            state="readonly", width=18,
        )
        self._content_filter_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self._content_filter_cb.grid(row=0, column=5)

        self._table = Table(panel, columns=_TABLE_COLUMNS)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.bind("<<TreeviewSelect>>", self._on_select)

    # ── Right panel ───────────────────────────────────────────

    def _build_right_panel(self):
        panel = ttk.Frame(self, style="Surface.TFrame")
        panel.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)
        panel.rowconfigure(0, weight=1)
        panel.rowconfigure(1, weight=0)
        panel.columnconfigure(0, weight=1)

        self._viewer = ImageViewer(panel, show_nav_buttons=False)
        self._viewer.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        form = ttk.Frame(panel, style="Card.TFrame", padding=12)
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)

        self._fn_var = tk.StringVar()
        self._ft_var = tk.StringVar()
        self._ct_var = tk.StringVar()
        self._st_var = tk.StringVar()

        fields = [
            ("FileName",    ttk.Entry(form, textvariable=self._fn_var)),
            ("FileType",    ttk.Entry(form, textvariable=self._ft_var, state="readonly")),
            ("ContentType", ttk.Combobox(form, textvariable=self._ct_var, state="readonly")),
            ("StatusType",  ttk.Combobox(form, textvariable=self._st_var, state="readonly",
                                         values=[""] + list(_STATUS_DISPLAY.values()))),
        ]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=3, padx=(0, 10))
            widget.grid(row=i, column=1, sticky="ew", pady=3)

        self._ct_cb = fields[2][1]

        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(8, 0))
        self._save_btn = ttk.Button(btn_row, text="Save", command=self._on_save, state="disabled")
        self._save_btn.pack(side="left", padx=(0, 8))
        self._cancel_btn = ttk.Button(btn_row, text="Cancel", style="Ghost.TButton",
                                      command=self._on_cancel, state="disabled")
        self._cancel_btn.pack(side="left")

    # ── Data ──────────────────────────────────────────────────

    def _refresh(self):
        self._selected_image_id = None
        self._original_row = None
        self._df = data.v_Image()

        content_types_in_data = sorted(self._df["ContentType"].dropna().unique().tolist())
        self._content_filter_cb.configure(values=["All"] + content_types_in_data)
        if self._content_filter_var.get() not in ["All"] + content_types_in_data:
            self._content_filter_var.set("All")

        ct_values = data.ImageContentType()["ContentType"].tolist()
        self._ct_cb.configure(values=[""] + ct_values)

        self._apply_filters()
        self._clear_form()
        self._viewer.show_placeholder("Select an image to preview")

    def _apply_filters(self):
        df = self._df.copy()

        search = self._search_var.get().strip().lower()
        if search:
            df = df[df["FileName"].str.lower().str.contains(search, na=False)]

        status_display = self._status_filter_var.get()
        if status_display != "All":
            code = _STATUS_CODES.get(status_display)
            if code:
                df = df[df["StatusType"] == code]

        ct = self._content_filter_var.get()
        if ct != "All":
            df = df[df["ContentType"] == ct]

        display_cols = list(_TABLE_COLUMNS.keys())
        self._table.data = df[display_cols] if not df.empty else pd.DataFrame(columns=display_cols)

    # ── Selection ─────────────────────────────────────────────

    def _on_select(self, event=None):
        row = self._table.get_selected_row()
        if row is None:
            self._clear_form()
            self._viewer.show_placeholder("Select an image to preview")
            return

        self._selected_image_id = str(row["ImageId"])
        self._original_row = row.copy()

        self._fn_var.set(row.get("FileName") or "")
        self._ft_var.set(row.get("FileType") or "")
        self._ct_var.set(row.get("ContentType") or "")
        self._st_var.set(_STATUS_DISPLAY.get(row.get("StatusType"), ""))

        self._save_btn.configure(state="normal")
        self._cancel_btn.configure(state="normal")
        self._delete_btn.configure(state="normal")

        filename = row.get("FileName")
        filetype = row.get("FileType")
        if filename and filetype:
            url = f"{IMAGE_DIRECTORY}/{filename}.{filetype}"
            self.after(10, lambda u=url, ft=filetype, fn=filename: self._load_preview(u, ft, fn))
        else:
            self._viewer.show_placeholder("No image file available")

    def _load_preview(self, url: str, filetype: str, filename_stem: str):
        img_bytes = resolve_image_bytes(url)
        if img_bytes:
            self._viewer.load_from_bytes(img_bytes, filetype, filename_stem)
        else:
            self._viewer.show_placeholder("Could not load image")

    def _clear_form(self):
        self._fn_var.set("")
        self._ft_var.set("")
        self._ct_var.set("")
        self._st_var.set("")
        self._save_btn.configure(state="disabled")
        self._cancel_btn.configure(state="disabled")
        self._delete_btn.configure(state="disabled")

    def _on_cancel(self):
        if not self._original_row:
            return
        self._fn_var.set(self._original_row.get("FileName") or "")
        self._ct_var.set(self._original_row.get("ContentType") or "")
        self._st_var.set(_STATUS_DISPLAY.get(self._original_row.get("StatusType"), ""))

    # ── Upload ────────────────────────────────────────────────

    def _on_upload(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images to Upload",
            filetypes=FILE_EXPLORER_IMAGE_TYPES,
        )
        if not file_paths:
            return

        success = 0
        errors = []
        for path_str in file_paths:
            path = Path(path_str)
            filename = path.stem
            filetype = path.suffix.lstrip(".").lower()

            if filetype not in SUPPORTED_IMAGE_FORMATS:
                errors.append(f"{path.name}: unsupported format")
                continue

            try:
                file_bytes = path.read_bytes()
                server_url = f"{IMAGE_DIRECTORY}/{filename}.{filetype}"
                resp = requests.post(server_url, data=file_bytes, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                errors.append(f"{path.name}: server upload failed — {e}")
                continue

            try:
                with get_connection("ldr") as conn:
                    data.insert_image(conn, filename, filetype)
                success += 1
            except Exception as e:
                errors.append(f"{path.name}: database insert failed — {e}")

        if errors:
            messagebox.showerror("Upload Errors", "\n".join(errors))
        if success:
            messagebox.showinfo("Upload Complete", f"{success} file(s) uploaded successfully.")

        self._refresh()

    # ── Save ──────────────────────────────────────────────────

    def _on_save(self):
        if not self._selected_image_id or not self._original_row:
            return

        new_filename = self._fn_var.get().strip()
        if not new_filename:
            messagebox.showwarning("Validation", "FileName cannot be empty.")
            return

        old_filename = self._original_row.get("FileName", "")
        filetype = self._original_row.get("FileType", "")
        old_ct = self._original_row.get("ContentType")
        old_st = self._original_row.get("StatusType")

        new_ct = self._ct_var.get().strip() or None
        new_st_display = self._st_var.get().strip()
        new_st = _STATUS_CODES.get(new_st_display) if new_st_display else None

        filename_changed = new_filename != old_filename
        sort_changed = new_ct != old_ct or new_st != old_st

        if not filename_changed and not sort_changed:
            return

        try:
            with get_connection("ldr") as conn:
                if filename_changed:
                    data.update_image_filename(conn, self._selected_image_id, new_filename)
                if sort_changed:
                    data.update_image_sort(conn, self._selected_image_id, new_ct, new_st)
        except Exception as e:
            messagebox.showerror("Save Error", f"Database update failed: {e}")
            return

        if filename_changed:
            try:
                self._rename_on_server(old_filename, new_filename, filetype)
            except Exception as e:
                messagebox.showwarning(
                    "Server Warning",
                    f"Database updated but server rename failed:\n{e}"
                )

        self._refresh()

    def _rename_on_server(self, old_filename: str, new_filename: str, filetype: str):
        old_url = f"{IMAGE_DIRECTORY}/{old_filename}.{filetype}"
        new_url = f"{IMAGE_DIRECTORY}/{new_filename}.{filetype}"
        old_bytes = resolve_image_bytes(old_url)
        if old_bytes is None:
            raise RuntimeError(f"Could not fetch file from server: {old_url}")
        resp = requests.post(new_url, data=old_bytes, timeout=15)
        resp.raise_for_status()
        try:
            requests.delete(old_url, timeout=5)
        except Exception:
            pass

    # ── Delete ────────────────────────────────────────────────

    def _on_delete(self):
        if not self._selected_image_id or not self._original_row:
            return

        filename = self._original_row.get("FileName", "")
        filetype = self._original_row.get("FileType", "")
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{filename}.{filetype}'?\n\nThis removes the database record. "
            f"The file on the server will be deleted if supported.",
        )
        if not confirmed:
            return

        try:
            with get_connection("ldr") as conn:
                data.delete_image(conn, self._selected_image_id)
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))
            return

        try:
            requests.delete(f"{IMAGE_DIRECTORY}/{filename}.{filetype}", timeout=5)
        except Exception:
            pass

        self._refresh()
