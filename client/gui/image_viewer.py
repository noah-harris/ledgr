import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from style import CANVAS_BG, BORDER, TEXT_LIGHT
import fitz  # PyMuPDF
from io import BytesIO
from pathlib import Path
import mimetypes
from urllib.parse import unquote

def get_image_size(img_path: Path | str) -> tuple[int, int]:
    img_path = Path(img_path)
    if img_path.suffix.lower() == ".pdf":
        with fitz.open(img_path) as doc:
            rect = doc[0].rect
            return (int(rect.width), int(rect.height))
    else:
        with Image.open(img_path) as img:
            return img.size


def get_image_size_from_bytes(image_bytes: bytes, filetype: str) -> tuple[int, int]:
    if filetype.lower() == "pdf":
        with fitz.open(stream=image_bytes, filetype="pdf") as doc:
            rect = doc[0].rect
            return (int(rect.width), int(rect.height))
    else:
        with Image.open(BytesIO(image_bytes)) as img:
            return img.size


class ImageQueue:

    def __init__(self, viewer:ImageViewer, queue:list[dict]=[], initial_index:int=0):
        self._viewer = viewer
        self._queue = queue
        self._index = initial_index
        self.viewer.queue_index_var.set(f"{self._index + 1} / {len(self._queue)}")

    @property
    def viewer(self) -> ImageViewer:
        return self._viewer

    @property
    def queue(self) ->list[dict]:
        return self._queue

    @property
    def index(self) -> int:
        return self._index
    
    @index.setter
    def index(self, value:int):
        if (value > len(self._queue)-1):
            self._index = len(self._queue)-1
        elif (value <= 0):
            self._index = 0
        else:
            self._index = value
        self.viewer.queue_index_var.set(f"{self._index + 1} / {len(self._queue)}")
        self._refresh_viewer()

    def _refresh_viewer(self):
        info:dict = self.get_current()
        info["index"] = self.index
        self.viewer.info = info
        if info.get('path') is not None:
            self.viewer.path = info['path']
        elif info.get('bytes') is not None:
            self.viewer.load_from_bytes(info.get('bytes'), info.get("filetype"), info.get("filename_stem"))
        self.viewer._page_number_var.set(f"Page {self.viewer._page_index + 1} of {len(self.viewer._doc) if self.viewer._doc is not None else 1}")

    def get_current(self) -> dict:
        if len(self.queue) == 0:
            return {}
        info = self.queue[self.index]
        if info.get("get_bytes") is not None and callable(info["get_bytes"]):
            try:
                info["bytes"] = info["get_bytes"]()
            except Exception as e:
                info["bytes"] = None
        else:
            info["bytes"] = None
        return info

    def remove_current(self):
        if len(self._queue) == 0:
            return
        else:
            self._queue.pop(self.index)
            self.index -= 1
            return self.get_current()
            
    def next(self):
        self.index += 1

    def prev(self):
        self.index -= 1




class ImageViewer(ttk.Frame):

    def __init__(self, master, show_nav_buttons: bool=True, canvas_size=None):
        super().__init__(master, style="Card.TFrame", padding=6)

        # ── state ───────────────────────────────────────────────
        self._path:Path|None = None
        self._is_pdf = False
        self._doc = None
        self._page_index = 0
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self._img_original = None
        self._tk_img = None
        self._image_id = None
        self._drag_start = (0,0)
        self._pdf_bytes = None

        self._info:dict = {}

        # ── canvas ─────────────────────────────────────────────
        canvas_kwargs = dict(
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            background=CANVAS_BG,
        )
        if canvas_size is not None:
            canvas_kwargs["width"] = canvas_size[0]
            canvas_kwargs["height"] = canvas_size[1]
        self.canvas = tk.Canvas(self, **canvas_kwargs)

        # Row 0: canvas (spans both columns)
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Row 1: filename + page labels
        self._filename_var = tk.StringVar(self, "")
        self.filename_label = ttk.Label(self, anchor="w", textvariable=self._filename_var)
        self.filename_label.grid(row=1, column=0, sticky="w", pady=(5, 0), padx=10)

        self._page_number_var = tk.StringVar(self, f"Page 1 of {len(self._doc) if self._doc is not None else 1}")
        self.page_label = ttk.Label(self, anchor="e", textvariable=self._page_number_var)
        self.page_label.grid(row=1, column=1, sticky="e", pady=(5, 0), padx=10)

        if show_nav_buttons:
            button_frame = ttk.Frame(self)
            button_frame.grid(row=2, column=0, columnspan=2, sticky="w")

            self.prev_image_button = ttk.Button(button_frame, text="<=")
            self.prev_image_button.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=10)

            self.next_image_button = ttk.Button(button_frame, text="=>")
            self.next_image_button.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=10)
            
            self.queue_index_var = tk.StringVar()
            self.queue_index_label = ttk.Label(button_frame, textvariable=self.queue_index_var)
            self.queue_index_label.grid(row=0, column=2, sticky="w", padx=(10, 5), pady=10)

        # Make canvas row/columns expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        # ── bindings ───────────────────────────────────────────
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

        self.canvas.bind("<MouseWheel>", self._zoom_wheel)
        self.canvas.bind("<Button-4>", self._zoom_wheel)
        self.canvas.bind("<Button-5>", self._zoom_wheel)

        self.bind_all("<Up>", self._prev_page)
        self.bind_all("<Down>", self._next_page)


    # ──────────────────────────────────────────────────────────
    # PATH PROPERTY (THE ONLY ENTRY POINT)
    # ──────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        if self.path is None:
            return None
        else:
            return self.path.stem

    @property
    def filetype(self) -> str:
        if self.path is None:
            return None
        else:
            return self.path.suffix.lstrip(".")
    
    @property
    def filename(self) -> str:
        if self.path is None:
            return None
        else:
            return self.path.name
        
    @property
    def lowercase_filename(self) -> str:
        if self.path is None:
            return None
        else:
            return self.path.name.lower()
        
    @property
    def mimetype(self) -> str:
        return mimetypes.types_map.get(self.path.suffix.lower(), "application/octet-stream") if self.path is not None else None


    @property
    def info(self) -> dict:
        return self._info

    @info.setter
    def info(self, info:dict) -> dict:
        self._info = info

    @property
    def path(self) -> Path|None:
        return self._path

    @path.setter
    def path(self, value:Path|None):
        if value is not None and not isinstance(value, Path):
            raise ValueError("Path must be a pathlib.Path object or None")

        if value is None:
            self._clear()
            self._path = None
            return
        
        if value == self._path:
            return

        self._filename_var.set(unquote(value.name))

        self._clear()
        self._path = value
        ext = value.suffix.lower()
        self._is_pdf = ext == ".pdf"

        if self._is_pdf:
            with open(value, "rb") as f:
                self._pdf_bytes = f.read()
            self._doc = fitz.open(stream=self._pdf_bytes, filetype="pdf")
            self._render_pdf_page()

        else:
            with open(value, "rb") as f:
                img_bytes = f.read()
            self._img_original = Image.open(BytesIO(img_bytes))
            self._render_image()

    # ──────────────────────────────────────────────────────────
    # Load from bytes
    # ──────────────────────────────────────────────────────────

    def load_from_bytes(self, image_bytes:bytes, filetype:str, filename_stem:str=""):

        if image_bytes is None or filetype is None or filename_stem is None:
            warn("Incomplete image data provided to load_from_bytes. Clearing viewer.")
            return

        self._clear()

        self._is_pdf = filetype == "pdf"

        if self._is_pdf:
            self._pdf_bytes = image_bytes
            self._doc = fitz.open(stream=self._pdf_bytes, filetype="pdf")
            self._render_pdf_page()
            self._filename_var.set(unquote(filename_stem))

        else:
            self._img_original = Image.open(BytesIO(image_bytes))
            self._filename_var.set(unquote(filename_stem))
            self._render_image()

    # ──────────────────────────────────────────────────────────
    # RENDERING
    # ──────────────────────────────────────────────────────────

    def _render_image(self):
        w, h = self._img_original.size
        resized = self._img_original.resize((int(w * self._zoom), int(h * self._zoom)), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(resized)
        self.canvas.update_idletasks()
        canvas_h = self.canvas.winfo_height()
        self._image_id = self.canvas.create_image(0, 0, image=self._tk_img, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(self._image_id))

    def _render_pdf_page(self):
        page = self._doc[self._page_index]
        mat = fitz.Matrix(self._zoom, self._zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        self._img_original = img
        self._render_image()

    # ──────────────────────────────────────────────────────────
    # INTERNAL RESET
    # ──────────────────────────────────────────────────────────

    def _clear(self):
        self.canvas.delete("all")
        self._zoom = 1.0
        self._page_index = 0

        if self._img_original:
            self._img_original.close()
        self._img_original = None
        self._tk_img = None
        self._image_id = None

        if self._doc:
            self._doc.close()
        self._doc = None
        self._pdf_bytes = None


    def show_placeholder(self, text: str):
        self._clear()
        self._path = None
        self._filename_var.set("")
        self.canvas.update_idletasks()
        cx = max(self.canvas.winfo_width() // 2, 50)
        cy = max(self.canvas.winfo_height() // 2, 50)
        self.canvas.create_text(cx, cy, text=text, fill=TEXT_LIGHT, font=("", 11, "italic"), anchor="center")

    # ──────────────────────────────────────────────────────────
    # DRAGGING
    # ──────────────────────────────────────────────────────────

    def _start_drag(self, event):
        self._drag_start = (event.x, event.y)

    def _drag(self, event):
        if not self._image_id:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self.canvas.move(self._image_id, dx, dy)
        self._drag_start = (event.x, event.y)

    # ──────────────────────────────────────────────────────────
    # ZOOMING
    # ──────────────────────────────────────────────────────────

    def _zoom_wheel(self, event):
        if not self._image_id:
            return
        factor = 0.9 if (event.num == 5 or event.delta < 0) else 1.1
        new_zoom = self._zoom * factor
        if not (self._min_zoom <= new_zoom <= self._max_zoom):
            return
        self._zoom = new_zoom
        self.canvas.delete("all")
        if self._is_pdf:
            self._render_pdf_page()
        else:
            self._render_image()

    # ──────────────────────────────────────────────────────────
    # PDF NAVIGATION
    # ──────────────────────────────────────────────────────────

    def _next_page(self, event=None):
        self.canvas.focus_set()
        if self._is_pdf and self._page_index < len(self._doc) - 1:
            self._page_index += 1
            self._page_number_var.set(f"Page {self._page_index + 1} of {len(self._doc)}")
            self.canvas.delete("all")
            self._render_pdf_page()

    def _prev_page(self, event=None):
        self.canvas.focus_set()
        if self._is_pdf and self._page_index > 0:
            self._page_index -= 1
            self._page_number_var.set(f"Page {self._page_index + 1} of {len(self._doc)}")
            self.canvas.delete("all")
            self._render_pdf_page()
            

