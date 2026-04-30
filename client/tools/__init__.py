import tkinter as tk
from db import get_connection

class Tool(tk.Toplevel):

    def __init__(self, master:tk.Tk, title:str="Tool", geometry:str=None):
        self.master:tk.Tk = master
        super().__init__(self.master)
        self.master.withdraw()
        self.withdraw()
        self.title(title)
        self._geometry = geometry
        self.show()
        
    def show(self):
        if self._geometry:
            self.deiconify()
            self.geometry(self._geometry)
        else:
            self.state('zoomed')
        self.protocol("WM_DELETE_WINDOW", lambda: [self.destroy(), self.master.deiconify(), self.master.state('zoomed')])

    def close(self):
        self.destroy()
        self.master.deiconify()
        self.master.state('zoomed')


