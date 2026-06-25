from tools import Tool
import data
from models.Invoice import StatementItem
from .statement_item_invoice_linker import StatementItemInvoiceReceiptLinker
from .transaction_completion_linker import TransactionCompletionLinker

class StatementItemInvoiceLinker(Tool):

    def __init__(self, master):
        super().__init__(master, title='Statement Item / Invoice Linking Tool')
        self._open_tool()

    def _open_tool(self):
        items = data.v_StatementItemLinkable()
        if len(items) == 0:
            self.close()
            return

        receipt_items = items[items["ContentType"] == "RECEIPT"]
        transaction_items = items[items["ContentType"] == "TRANSACTION"]

        if not receipt_items.empty:
            first_item = StatementItem(receipt_items.iloc[0]["StatementItemId"])
            self.tool = StatementItemInvoiceReceiptLinker(self, first_item, receipt_items, self._close_tool)
        elif not transaction_items.empty:
            first_item = StatementItem(transaction_items.iloc[0]["StatementItemId"])
            self.tool = TransactionCompletionLinker(self, first_item, self._close_tool)
        else:
            self.close()

    def _close_tool(self):
        self.tool.close()
        self.tool.destroy()
        self._open_tool()
