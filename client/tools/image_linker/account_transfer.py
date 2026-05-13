import tkinter as tk
from gui import Modal, Table, ImageQueue
from .._ui_components import AccountTransferForm
import data
import pandas as pd
from tkinter import messagebox
from db import get_connection
from tkinter import ttk
import uuid
from search import search, search_one

class AccountTransfer(Modal):

	COLUMNS = {
		"Account": {"justify": "left", "width": 150}, 
		"Method": {"justify": "left", "width": 180}, 
		"TransactionDate": {"justify": "center", "width": 80},
		"Amount": {"justify": "left", "width": 100},
		"Description": {"justify": "left", "width": 250},
		"StatementItemId": {"is_hidden": True},
		"PayeeId": {"is_hidden": True}
	}

	def __init__(self, master, image_queue):
		super().__init__(master, background_color="white", border_thickness=2, border_color="black")
		self._image_queue:ImageQueue = image_queue
		self.transfer_form = AccountTransferForm(self)
		self.transfer_form.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))

		self.search_from_results = Table(self, columns=self.COLUMNS, visible_rows=40)
		self.search_to_results = Table(self, columns=self.COLUMNS, visible_rows=40)
		self.search_from_results.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
		self.search_to_results.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

		ttk.Button(self, text="Search", command=self._link).grid(row=2, column=0, sticky='e', padx=10, pady=(0, 10))

		self._bind_ctrls()

	@property
	def current_image_id(self):
		return self._image_queue.get_current()["ImageId"]

	def _bind_ctrls(self):
		self.transfer_form.account_from_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")
		self.transfer_form.method_from_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")

		self.transfer_form.account_to_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")
		self.transfer_form.method_to_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")

		self.transfer_form.transfer_amount_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")
		self.transfer_form.transfer_fee_amount_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")
		self.transfer_form.transaction_date_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")
		self.transfer_form.transaction_date_time_widget.bind("<KeyRelease>", lambda e: self._get_from_statement_item(), add="+")

		self.transfer_form.transfer_amount_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")
		self.transfer_form.transfer_fee_amount_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")
		self.transfer_form.transaction_date_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")
		self.transfer_form.transaction_date_time_widget.bind("<KeyRelease>", lambda e: self._get_to_statement_item(), add="+")

		self.transfer_form.account_from_widget.bind("<<ComboboxSelected>>", lambda e: self._get_from_statement_item(), add="+")
		self.transfer_form.method_from_widget.bind("<<ComboboxSelected>>", lambda e: self._get_from_statement_item(), add="+")

		self.transfer_form.account_to_widget.bind("<<ComboboxSelected>>", lambda e: self._get_to_statement_item(), add="+")
		self.transfer_form.method_to_widget.bind("<<ComboboxSelected>>", lambda e: self._get_to_statement_item(), add="+")

	def _link(self):
		from_statement_item = self._get_from_statement_item()
		to_statement_item = self._get_to_statement_item()

		if from_statement_item is None or to_statement_item is None:
			messagebox.showinfo("No Match", "No matching transactions were found for the provided transfer details. Please adjust the details and try again.")
			self.clear()
			return
		
		# I NEED IT TO BREAK IF THE TransactionDates of the two statement items are not the same exact value
		if from_statement_item["TransactionDate"] != to_statement_item["TransactionDate"]:
			messagebox.showinfo("Date Mismatch", "The transaction dates of the selected statement items do not match. Please adjust the details and try again.")
			self.clear()
			return
	
		msg = "Matching transactions found for both sides of the transfer:\n\nFROM:\n"
		for key, value in from_statement_item.items():
			msg += f"{key}: {value}\n"
		msg += "\nTO:\n"
		for key, value in to_statement_item.items():
			msg += f"{key}: {value}\n"

		messagebox_result = messagebox.askyesno("Match Found", f"{msg}\n\nDo you want to link the image to these transactions?")
		if not messagebox_result:
			self.clear()
			return
	

		with get_connection("ldr") as conn:

##############################
			from_invoice_id = str(uuid.uuid4()).upper()
			data.update_statement_item_image_id(conn, self.current_image_id, from_statement_item["StatementItemId"])

			invoice_data = {
				"InvoiceId": from_invoice_id,
				"PayeeId": to_statement_item["PayeeId"],
				"InvoiceDate": from_statement_item["TransactionDate"],
				"Amount": from_statement_item["Amount"],
				"ImageId": self.current_image_id,
				"Description": f"Account Transfer to {to_statement_item['Account']} via {from_statement_item['Method']}"
			}

			records = [
				{
					"InvoiceId": from_invoice_id,
					"InvoiceItemId": str(uuid.uuid4()).upper(),
					"CategoryId": "46FDA79F-ACA8-46EE-883C-380C74A8FEB0", # BALANCE TRANSFER TOTAL
					"Description": f"Transfer to {to_statement_item['Account']} via {from_statement_item['Method']}",
					"Quantity": 1,
					"Amount": self.transfer_form.transfer_amount,
					"DisplayOrder": 1,
					"IsAutoGenerated": 0
				}
			]

			if self.transfer_form.transfer_fee_amount and self.transfer_form.transfer_fee_amount > 0:
				records.append(
					{
						"InvoiceId": from_invoice_id,
						"InvoiceItemId": str(uuid.uuid4()).upper(),
						"CategoryId": "0173E9DB-7618-42CD-9D56-680E1CB3A9CD", # BALANCE TRANSFER FEE
						"Description": f"Transfer Fee {to_statement_item['Account']} via {from_statement_item['Method']}",
						"Quantity": 1,
						"Amount": self.transfer_form.transfer_fee_amount,
						"DisplayOrder": 2,
						"IsAutoGenerated": 0
					}
				)

			invoice_item_data = pd.DataFrame(records)
			data.insert_invoice(conn, invoice=invoice_data, invoice_item=invoice_item_data)
			data.update_statement_item_image_id(conn, self.current_image_id, to_statement_item["StatementItemId"])
			data.update_statement_item_invoice_id(conn, from_invoice_id, from_statement_item["StatementItemId"])



##############################
			to_invoice_id = str(uuid.uuid4()).upper()
			data.update_statement_item_image_id(conn, self.current_image_id, to_statement_item["StatementItemId"])

			invoice_data = {
				"InvoiceId": to_invoice_id,
				"PayeeId": from_statement_item["PayeeId"],
				"InvoiceDate": from_statement_item["TransactionDate"],
				"Amount": self.transfer_form.transfer_amount*-1,
				"ImageId": self.current_image_id,
				"Description": f"Incoming transfer from {from_statement_item['Account']} via {to_statement_item['Method']}"
			}

			records = [
				{
					"InvoiceId": to_invoice_id,
					"InvoiceItemId": str(uuid.uuid4()).upper(),
					"CategoryId": "46FDA79F-ACA8-46EE-883C-380C74A8FEB0", # BALANCE TRANSFER TOTAL
					"Description": f"Incoming transfer from {from_statement_item['Account']} via {to_statement_item['Method']}",
					"Quantity": 1,
					"Amount": self.transfer_form.transfer_amount*-1,
					"DisplayOrder": 1,
					"IsAutoGenerated": 0
				}
			]

			invoice_item_data = pd.DataFrame(records)
			data.insert_invoice(conn, invoice=invoice_data, invoice_item=invoice_item_data)
			data.update_statement_item_image_id(conn, self.current_image_id, to_statement_item["StatementItemId"])
			data.update_statement_item_invoice_id(conn, to_invoice_id, to_statement_item["StatementItemId"])
			data.update_image_sort(conn, self.current_image_id, content_type="ACCOUNT TRANSFER", status_type="c")
			
		self._image_queue.remove_current()
		messagebox.showinfo("Success", "The image has been linked to the matching transactions.")
		self.clear()


	def _get_from_statement_item(self):
		d = self.transfer_form.get()
		amount = (d.get("transfer_amount") or 0) + (d.get("transfer_fee_amount") or 0) if d.get("transfer_amount") is not None or d.get("transfer_fee_amount") is not None else None
		fields = {
			"TransactionDate": {"value": d.get("transaction_date")},
			"Account": {"value": d.get("account_from")},
			"Method": {"value": d.get("method_from")},
			"Payee": {"value": d.get("account_to")},
			"Amount": {"value": amount}
		}
		result, matches = search_one(
			df=data.v_StatementItemAccountTransfer(),
			fields=fields
		)
		self.search_from_results.data = matches
		return result


	def _get_to_statement_item(self):
		d = self.transfer_form.get()
		amount = d.get("transfer_amount") * -1 if d.get("transfer_amount") is not None else None
		fields = {
			"TransactionDate": {"value": d.get("transaction_date")},
			"Account": {"value": d.get("account_to")},
			"Method": {"value": d.get("method_to")},
			"Payee": {"value": d.get("account_from")},
			"Amount": {"value": amount}
		}
		result, matches = search_one(
			df=data.v_StatementItemAccountTransfer(),
			fields=fields
		)
		self.search_to_results.data = matches
		return result
	
	
	def clear(self):
		self.transfer_form.clear()
		self.search_from_results.clear()
		self.search_to_results.clear()




	