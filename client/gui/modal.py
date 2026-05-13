import tkinter as tk

class Modal(tk.Toplevel):

    def __init__(self, master:tk.Tk, background_color:str=None,  border_thickness:int=None, border_color:str=None, is_fullscreen:bool=False):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        self.configure(bg=background_color, highlightthickness=border_thickness, highlightcolor=border_color, highlightbackground=border_color)
        self.bind("<Escape>", lambda e: self.destroy())
        if is_fullscreen:
            self.state('zoomed')
        self.grab_set()
        self.after(0, self._center)

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        px = self.master.winfo_rootx()
        py = self.master.winfo_rooty()
        pw = self.master.winfo_width()
        ph = self.master.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def close(self):
        self.grab_release()
        self.destroy()