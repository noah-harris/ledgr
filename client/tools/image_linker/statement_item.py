import tkinter as tk
from gui import Modal, Table, ImageQueue
from .._ui_components import StatementItemSearchForm
from functools import cached_property
import data
import pandas as pd
from tkinter import messagebox
from db import get_connection
from search import search, search_one

class StatementItem(Modal):

	def __init__(self, master, image_queue, content_type_caller):
		super().__init__(master, background_color="white", border_thickness=2, border_color="black")
		self.search_form:StatementItemSearchForm = StatementItemSearchForm(self)
	
		self._image_queue:ImageQueue = image_queue
		self.search_form.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
		self.search_results.grid(row=1, column=0, sticky='ew', padx=10, pady=10)

		self.content_type_caller = content_type_caller

		self._bind_ctrls()

	@property
	def current_image_id(self):
		return self._image_queue.get_current()["ImageId"]


	def _bind_ctrls(self):
		self.search_form.account_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")
		self.search_form.payee_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")
		self.search_form.transaction_date_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")
		self.search_form.transaction_date_time_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")
		self.search_form.method_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")
		self.search_form.amount_widget.bind("<KeyRelease>", lambda e: self._handle_form_change(), add="+")

		self.search_form.account_widget.bind("<<ComboboxSelected>>", lambda e: self._handle_form_change(), add="+")
		self.search_form.payee_widget.bind("<<ComboboxSelected>>", lambda e: self._handle_form_change(), add="+")
		self.search_form.method_widget.bind("<<ComboboxSelected>>", lambda e: self._handle_form_change(), add="+")

		self.search_results.bind("<Double-1>", lambda e: self._handle_click(), add="+")


	@cached_property
	def search_results(self) -> Table:
		""" Table for displaying transaction search results """
		columns = {
			"Account": {"justify": "left", "width": 150}, "StatementDate": {"justify":"center", "width": 40}, "Payee": {"justify": "left", "width": 150}, "TransactionDate": {"justify": "center", "width": 80}, "PostDate": {"justify": "center", "width": 40},
			"Method": {"justify": "left", "width": 180}, "ReferenceNumber": {"justify": "left", "width": 100}, "Amount": {"justify": "left", "width": 100}, "Description": {"justify": "left", "width": 400},
			"StatementItemId": {"is_hidden": True}, "StatementId": {"is_hidden": True},
			"InvoiceId": {"is_hidden": True}, "ImageId": {"is_hidden": True},
		}
		return Table(self, columns=columns, visible_rows=40)


	def clear(self):
		self.search_form.clear()
		self.search_form.transaction_date_time_widget.insert(0, "00:00:00")
		self.search_results.clear()


	def _handle_form_change(self):
		state:dict = self.search_form.get()
		result, matches = search_one(
			df = data.v_StatementItemUnmatchedImages(), 
		 	fields={
				"TransactionDate": {"value": state["transaction_date"], "sort_ascending": False},
				"Account": {"value": state["account"], "sort_ascending": True},
				"Method": {"value": state["method"], "sort_ascending": True},
				"Payee": {"value": state["payee"]},
				"Amount": {"value": state["amount"]}
			}
		)
		self.search_results.data = matches
		if result:
			self._handle_search(result["StatementItemId"])

		
	def _handle_click(self):
		selected = self.search_results.get_selected_row()
		if selected is not None:
			self._handle_search(selected["StatementItemId"])


	def _handle_search(self, statement_item_id):

		if statement_item_id is None:
			return None
		
		match = data.v_StatementItem().query(f"StatementItemId == '{statement_item_id}'").iloc[0]

		msg = ''
		for key, value in match.items():
			msg += f"{key}: {value}\n"

		messagebox_result = messagebox.askyesno("Match Found", f"A single matching transaction was found:\n\n{msg}\nDo you want to link the image to this transaction?")
		if not messagebox_result:
			self.clear()
			return
		
		with get_connection() as conn:
			data.update_statement_item_image_id(conn, self.current_image_id, statement_item_id)
			data.update_image_sort(conn, self.current_image_id, self.content_type_caller, {"TRANSACTION": 'i', 'RECEIPT':'c'}.get(self.content_type_caller))
			
		self._image_queue.remove_current()
		self.clear()


