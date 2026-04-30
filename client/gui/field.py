"""
Declarative field descriptors for Form subclasses.

Declaring a field on a Form subclass automatically provides:
  - instance.name          → typed getter  (str | datetime | Decimal | None)
  - instance.name = value  → typed setter
  - instance.name_widget   → cached_property returning the ttk widget
  - instance.name_time_widget  → (DateTimeField only) cached_property for time entry

Usage
-----
    class MyForm(Form):

        payee = StringField(
            label="Payee:",
            widget="combobox",
            values=lambda: ["Alice", "Bob"],
            row=0, col=0,
        )

        invoice_date = DateTimeField(
            label="Date (YYYY-MM-DD):",
            time_label="Time (HH:MM:SS):",
            row=1, col=0, time_col=2,
        )

        amount = DecimalField(
            label="Amount:",
            row=2, col=0,
            validators=[Required()],
        )
"""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk
from functools import cached_property
from datetime import datetime
from decimal import Decimal
from typing import Callable, Any

# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

class Validator:
    """Base class for field validators."""
    def __call__(self, value: Any) -> str | None:
        raise NotImplementedError


class Required(Validator):
    """Fails when value is None."""
    def __call__(self, value):
        return "This field is required." if value is None else None


# ---------------------------------------------------------------------------
# Base field descriptor
# ---------------------------------------------------------------------------

class BaseField:
    """
    Descriptor base. Subclass this to create typed form fields.

    Parameters
    ----------
    label       : text for the Label widget placed to the left of the input.
    row, col    : grid position of the label. The widget is placed at col+1.
    colspan     : columnspan for the input widget (default 1).
    label_padx  : padx for the label (default 10).
    widget_padx : padx for the input widget (default 10).
    pady        : pady for both label and widget (default 10).
    width       : explicit widget width; None = auto / ttk default.
    validators  : list of Validator instances run by Form.validate().
    """

    def __init__(
        self,
        *,
        label: str,
        row: int,
        col: int,
        colspan: int = 1,
        label_padx: int | tuple = 10,
        widget_padx: int | tuple = 10,
        pady: int = 10,
        width: int | None = None,
        validators: list[Validator] | None = None,
    ):
        self.label = label
        self.row = row
        self.col = col
        self.colspan = colspan
        self.label_padx = label_padx
        self.widget_padx = widget_padx
        self.pady = pady
        self.width = width
        self.validators: list[Validator] = validators or []
        self.name: str | None = None   # filled by __set_name__

    # ------------------------------------------------------------------
    # Descriptor protocol
    # ------------------------------------------------------------------


    def __set_name__(self, owner: type, name: str):
        self.name = name
        self._var_attr = f"_{name}_var"
        self._register_widgets(owner, name)


    def _register_widgets(self, owner: type, name: str):
        """Inject cached_property descriptors onto the owner class."""
        field = self
        cp = cached_property(lambda obj, f=field: f._build_widget(obj))
        cp.attrname = f"{name}_widget"
        setattr(owner, f"{name}_widget", cp)


    def _init_vars(self, obj, master: tk.Widget):
        """Called by Form.__init__ to create StringVar(s) on the instance."""
        setattr(obj, self._var_attr, tk.StringVar(master))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_label(self, obj) -> ttk.Label:
        lbl = ttk.Label(obj, text=self.label)
        lbl.grid(row=self.row, column=self.col, pady=self.pady, padx=self.label_padx, sticky="e")
        return lbl

    def _build_widget(self, obj) -> tk.Widget:
        raise NotImplementedError

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        raise NotImplementedError

    def __set__(self, obj, value):
        raise NotImplementedError

    def validate(self, obj) -> list[tuple[str, str]]:
        """Return list of (field_name, message) for each failing validator."""
        value = self.__get__(obj, type(obj))
        return [
            (self.name, msg)
            for v in self.validators
            if (msg := v(value)) is not None
        ]

    def _validate(self, obj):
        raise NotImplementedError

    @staticmethod
    def handle_datetime_get(date_var: tk.StringVar, time_var: tk.StringVar) -> datetime | None:
        try:
            return datetime.strptime(f"{date_var.get()} {time_var.get()}", "%Y-%m-%d %H:%M:%S")
        except Exception:
            print(f"Failed to parse datetime from {date_var.get()} {time_var.get()}")
            return None

    @staticmethod
    def handle_datetime_set(date_var: tk.StringVar, time_var: tk.StringVar, value: datetime | None):
        try:
            date_var.set(value.strftime("%Y-%m-%d"))
            time_var.set(value.strftime("%H:%M:%S"))
        except Exception:
            print(f"Failed to set datetime from value: {value}")
            date_var.set("")
            time_var.set("")


    @staticmethod
    def handle_decimal_get(var: tk.StringVar) -> Decimal | None:
        amount = var.get()
        if not re.fullmatch(r"-?\d+\.\d{2}", amount):
            return None
        return Decimal(amount)

    @staticmethod
    def handle_decimal_set(var:tk.StringVar, value:Decimal|None):
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


    @staticmethod
    def handle_string_get(var: tk.StringVar) -> str | None:
        value = var.get()
        return None if value == "" else value

    @staticmethod
    def handle_string_set(var: tk.StringVar, value: str | None):
        var.set("" if value is None else value)

    def _bind_focus_out(self, obj, widget):
        widget.bind("<FocusOut>", lambda e: self._validate(obj))

# ---------------------------------------------------------------------------
# Concrete field types
# ---------------------------------------------------------------------------

class StringField(BaseField):
    """
    A ``str | None`` field backed by a ``ttk.Entry`` or ``ttk.Combobox``.

    Extra parameters
    ----------------
    widget      : ``"entry"`` (default) or ``"combobox"``.
    values      : for combobox — a list or a zero-argument callable that
                  returns a list (e.g. a DB query). Evaluated lazily when
                  the widget is first accessed.
    filterable  : attach the standard type-to-filter / lock-when-one
                  bindings from Form (default True, combobox only).
    """

    def __init__(
        self,
        *,
        widget: str = "entry",
        values: Callable[[], list[str]] | list[str] | None = None,
        filterable: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.widget_type = widget
        self.values = values
        self.filterable = filterable

    @staticmethod
    def _lock_when_single(event):
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

    @staticmethod
    def _filter_values(event):
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
                combobox.after(0, lambda: combobox.event_generate("<<NextWindow>>"))
        combobox.after(0, lambda: (combobox.icursor(tk.END)))

    def _build_widget(self, obj) -> ttk.Entry | ttk.Combobox:
        var = getattr(obj, self._var_attr)
        self._build_label(obj)

        if self.widget_type == "combobox":
            all_values = self.values() if callable(self.values) else (self.values or [])
            w = ttk.Combobox(obj, values=all_values, textvariable=var)
            w.config(width=self.width or max((len(v) for v in all_values), default=10))
            w._all_values = all_values
            if self.filterable:
                w.bind("<KeyPress>",   self._lock_when_single)
                w.bind("<KeyRelease>", self._filter_values, add="+")
        else:
            w = ttk.Entry(obj, textvariable=var)
            if self.width is not None:
                w.config(width=self.width)

        w.grid(row=self.row, column=self.col + 1, pady=self.pady, padx=self.widget_padx, columnspan=self.colspan, sticky="w")
        self._bind_focus_out(obj, w)
        return w

    def __get__(self, obj, objtype=None) -> str | None:
        if obj is None:
            return self
        return self.handle_string_get(getattr(obj, self._var_attr))

    def __set__(self, obj, value: str | None):
        self.handle_string_set(getattr(obj, self._var_attr), value)

    def _validate(self, obj):
        print("Validating StringField")
        pass  # no validation rules beyond type, which is handled by the getter/setter

class DecimalField(BaseField):
    """
    A ``Decimal | None`` field backed by a ``ttk.Entry``.
    """
 
    def _build_widget(self, obj) -> ttk.Entry:
        var = getattr(obj, self._var_attr)
        self._build_label(obj)
        w = ttk.Entry(obj, textvariable=var)
        if self.width is not None:
            w.config(width=self.width)
        w.grid(row=self.row, column=self.col + 1, pady=self.pady, padx=self.widget_padx, columnspan=self.colspan, sticky="w")
        self._bind_focus_out(obj, w)
        return w

    def __get__(self, obj, objtype=None) -> Decimal | None:
        if obj is None:
            return self
        return self.handle_decimal_get(getattr(obj, self._var_attr))

    def __set__(self, obj, value):
        self.handle_decimal_set(getattr(obj, self._var_attr), value)


    def _validate(self, obj):
        # Delete the text on focus out if its not 
        # a valid decimal with 2 decimal places (e.g. "12.34" or "-5.00")
        print("Validating DecimalField")
        var = getattr(obj, self._var_attr)
        value = var.get()
        if not re.fullmatch(r"-?(?:\d*\.\d{1,2}|\d+)", value):
            var.set("")
        else:
            var.set(f"{Decimal(value):.2f}")
        


class DateField(BaseField):
    """
    A ``datetime | None`` field backed by a **single** ``ttk.Entry``.

    The time portion is fixed to ``default_time`` (default ``"00:00:00"``),
    which makes this suitable for start/end-date-style fields that want a
    full ``datetime`` but only expose a date picker.
    """

    def __init__(self, *, default_time: str = "00:00:00", **kwargs):
        super().__init__(**kwargs)
        self.default_time = default_time

    def _init_vars(self, obj, master):
        setattr(obj, self._var_attr, tk.StringVar(master))
        setattr(obj, f"_{self.name}_time_var", tk.StringVar(master, self.default_time))

    def _build_widget(self, obj) -> ttk.Entry:
        var = getattr(obj, self._var_attr)
        self._build_label(obj)
        w = ttk.Entry(obj, textvariable=var)
        if self.width is not None:
            w.config(width=self.width)
        w.grid(row=self.row, column=self.col + 1, pady=self.pady, padx=self.widget_padx, columnspan=self.colspan, sticky="w")
        self._bind_focus_out(obj, w)
        return w

    def __get__(self, obj, objtype=None) -> datetime | None:
        if obj is None:
            return self
        return self.handle_datetime_get(getattr(obj, self._var_attr), getattr(obj, f"_{self.name}_time_var"))

    def __set__(self, obj, value: datetime | None):
        if value is None:
            getattr(obj, self._var_attr).set("")
            getattr(obj, f"_{self.name}_time_var").set(self.default_time)
        else:
            self.handle_datetime_set(
                getattr(obj, self._var_attr),
                getattr(obj, f"_{self.name}_time_var"),
                value,
            )

    def _validate(self, obj):
        # Delete the text on focus out if it's not a valid date in YYYY-MM-DD format
        print("Validating DateField")
        var = getattr(obj, self._var_attr)
        value = var.get()
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            var.set("")

class DateTimeField(BaseField):
    """
    A ``datetime | None`` field backed by **two** ``ttk.Entry`` widgets.

    Registers two cached_properties on the owner class:
      - ``name_widget``       → the date entry
      - ``name_time_widget``  → the time entry

    Extra parameters
    ----------------
    time_label      : label text for the time entry.
    time_col        : grid column of the time label.
                      Defaults to ``col + 2`` (i.e. right of the date widget).
    time_label_padx : padx for time label (default 10).
    time_widget_padx: padx for time entry (default 10).
    default_time    : initial value for the time var (default ``"00:00:00"``).
    """

    def __init__(
        self,
        *,
        time_label: str = "Time (HH:MM:SS):",
        time_col: int | None = None,
        time_label_padx: int | tuple = 10,
        time_widget_padx: int | tuple = 10,
        default_time: str = "00:00:00",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.time_label = time_label
        self._time_col_override = time_col
        self.time_label_padx = time_label_padx
        self.time_widget_padx = time_widget_padx
        self.default_time = default_time

    @property
    def time_col(self) -> int:
        return self._time_col_override if self._time_col_override is not None \
               else self.col + 2

    def _register_widgets(self, owner: type, name: str):
        super()._register_widgets(owner, name)
        field = self
        cp = cached_property(lambda obj, f=field: f._build_time_widget(obj))
        cp.attrname = f"{name}_time_widget"
        setattr(owner, f"{name}_time_widget", cp)

    def _init_vars(self, obj, master):
        setattr(obj, self._var_attr, tk.StringVar(master))
        setattr(obj, f"_{self.name}_time_var", tk.StringVar(master, self.default_time))

    def _build_widget(self, obj) -> ttk.Entry:
        var = getattr(obj, self._var_attr)
        self._build_label(obj)
        w = ttk.Entry(obj, textvariable=var)
        if self.width is not None:
            w.config(width=self.width)
        w.grid(row=self.row, column=self.col + 1, pady=self.pady, padx=self.widget_padx, sticky="w")
        self._bind_focus_out(obj, w)
        return w
    
    def _build_time_widget(self, obj) -> ttk.Entry:
        time_var = getattr(obj, f"_{self.name}_time_var")
        ttk.Label(obj, text=self.time_label).grid(row=self.row, column=self.time_col, pady=self.pady, padx=self.time_label_padx, sticky="e")
        w = ttk.Entry(obj, textvariable=time_var)
        w.grid(row=self.row, column=self.time_col + 1, pady=self.pady, padx=self.time_widget_padx, sticky="w")
        self._bind_focus_out(obj, w)
        return w

    def __get__(self, obj, objtype=None) -> datetime | None:
        if obj is None:
            return self
        return self.handle_datetime_get(getattr(obj, self._var_attr), getattr(obj, f"_{self.name}_time_var"))

    def __set__(self, obj, value: datetime | None):
        self.handle_datetime_set(getattr(obj, self._var_attr), getattr(obj, f"_{self.name}_time_var"), value)

    def _validate(self, obj):
        # Delete the text on focus out if it's not a valid date in YYYY-MM-DD format
        print("Validating DateTimeField")
        date_var = getattr(obj, self._var_attr)
        value = date_var.get()
        if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            date_var.set("")

        time_var = getattr(obj, f"_{self.name}_time_var")
        time_value = time_var.get()
        if time_value and not re.fullmatch(r"\d{2}:\d{2}:\d{2}", time_value):
            time_var.set("00:00:00")
        

__all__ = [
    "Validator", "Required",
    "BaseField", "StringField", "DecimalField", "DateField", "DateTimeField",
]
