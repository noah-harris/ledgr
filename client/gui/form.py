from datetime import datetime
from decimal import Decimal
import re
import tkinter as tk
from tkinter import ttk
from functools import cached_property
from .field import BaseField

class Form(ttk.Frame):
    """
    Base class for declarative tkinter forms.

    Subclass this and declare fields using the descriptors in ``field.py``.
    ``__init__`` automatically creates all required ``StringVar``s; ``get``,
    ``set``, ``clear``, ``set_form_state``, and ``validate`` are provided for
    free based on the declared fields.

    Example
    -------
        class MyForm(Form):
            name   = StringField(label="Name:",   row=0, col=0)
            amount = DecimalField(label="Amount:", row=1, col=0,
                                  validators=[Required()])

        f = MyForm(root)
        f.name = "Alice"
        f.name_widget.bind("<<ComboboxSelected>>", my_handler)
        data = f.get()          # {"name": "Alice", "amount": None}
        errors = f.validate()   # [("amount", "This field is required.")]
    """

    def __init__(self, master: ttk.Widget):
        super().__init__(master)
        for _name, field in self._iter_fields():
            field._init_vars(self, master)
        self._render_all_widgets()

    # ------------------------------------------------------------------
    # Field introspection
    # ------------------------------------------------------------------

    @classmethod
    def _iter_fields(cls):
        """Yield (name, field) for every BaseField declared on this class
        (and its bases), in MRO order, without duplicates."""
        seen: set[str] = set()
        for klass in reversed(cls.__mro__):
            for name, val in vars(klass).items():
                if isinstance(val, BaseField) and name not in seen:
                    seen.add(name)
                    yield name, val

    def _render_all_widgets(self):
        """Force every field's cached_property widget(s) to be realised."""
        cls = type(self)
        for name, _field in self._iter_fields():
            getattr(self, f"{name}_widget")
            if isinstance(getattr(cls, f"{name}_time_widget", None), cached_property):
                getattr(self, f"{name}_time_widget")

    # ------------------------------------------------------------------
    # Default CRUD helpers  (override in subclasses if needed)
    # ------------------------------------------------------------------

    def get(self) -> dict:
        return {name: field.__get__(self, type(self)) for name, field in self._iter_fields()}

    def set(self, data: dict):
        for name, field in self._iter_fields():
            if name in data:
                field.__set__(self, data[name])

    def clear(self):
        self.set({name: None for name, _ in self._iter_fields()})

    def set_form_state(self, enabled: bool):
        """Enable or disable every widget that has already been realised."""
        state = "!disabled" if enabled else "disabled"
        for name, _field in self._iter_fields():
            for suffix in ("_widget", "_time_widget"):
                attr = f"{name}{suffix}"
                widget = self.__dict__.get(attr)   # only if cached
                if widget is not None:
                    try:
                        widget.state([state])
                    except tk.TclError:
                        pass

    # ------------------------------------------------------------------
    # Combobox helpers  (used by StringField via obj._lock_when_single etc.)
    # ------------------------------------------------------------------

    def _lock_when_single(self, event):
        """Locks the combobox when only one value remains, preventing deletion."""
        combobox = event.widget
        vals = combobox["values"]
        if isinstance(vals, str):
            vals = combobox.tk.splitlist(vals)
        if len(vals) == 1:
            if event.keysym == "BackSpace":
                combobox.set("")
                combobox["values"] = combobox._all_values
                return "break"
            combobox.after(0, lambda: combobox.event_generate("<<NextWindow>>"))
            return "break"

    def _filter_values(self, event):
        combobox = event.widget
        combobox.set(combobox.get().upper())
        text = combobox.get().lower()
        if not text:
            combobox["values"] = combobox._all_values
        else:
            vals = [v for v in combobox._all_values if v.lower().startswith(text)]
            combobox["values"] = vals
            if len(vals) == 1:
                combobox.set(vals[0])
                combobox.icursor(tk.END)
        combobox.after(1, lambda: (
            combobox.tk.call("focus", combobox._w),
            combobox.icursor(tk.END),
        ))

    # ------------------------------------------------------------------
    # Typed var helpers  (kept for legacy forms; new forms use field methods)
    # ------------------------------------------------------------------

    @classmethod
    def handle_string_get(cls, var: tk.StringVar) -> str | None:
        value = var.get()
        return None if value == "" else value

    @classmethod
    def handle_string_set(cls, var: tk.StringVar, value: str | None):
        var.set("" if value is None else value)

    @classmethod
    def handle_date_get(cls, date_var: tk.StringVar) -> datetime | None:
        try:
            return datetime.strptime(date_var.get(), "%Y-%m-%d")
        except Exception:
            return None

    @classmethod
    def handle_date_set(cls, date_var: tk.StringVar, value: datetime | None):
        try:
            date_var.set(value.strftime("%Y-%m-%d"))
        except Exception:
            date_var.set("")

    @classmethod
    def handle_datetime_get(cls, date_var: tk.StringVar, time_var: tk.StringVar) -> datetime | None:
        try:
            return datetime.strptime(f"{date_var.get()} {time_var.get()}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    @classmethod
    def handle_datetime_set(cls, date_var: tk.StringVar, time_var: tk.StringVar, value: datetime | None):
        try:
            date_var.set(value.strftime("%Y-%m-%d"))
            time_var.set(value.strftime("%H:%M:%S"))
        except Exception:
            date_var.set("")
            time_var.set("")

    @classmethod
    def handle_decimal_get(cls, var: tk.StringVar) -> Decimal | None:
        amount = var.get()
        if not re.fullmatch(r"-?\d+\.\d{2}", amount):
            return None
        return Decimal(amount)

    @classmethod
    def handle_decimal_set(cls, var: tk.StringVar, value: Decimal | None):
        try:
            value = f"{Decimal(value):.2f}"
        except Exception:
            pass
        try:
            cleaned = "" if value is None else str(value)
            var.set(f"{Decimal(cleaned):.2f}"
                    if re.fullmatch(r"-?\d+\.\d{2}", cleaned) else "")
        except Exception:
            var.set("")


__all__ = ["Form"]