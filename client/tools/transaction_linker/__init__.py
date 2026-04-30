from tools import Tool
import data
from models.Invoice import StatementItem
from .statement_item_invoice_linker import StatementItemInvoiceReceiptLinker
from .transaction_completion_linker import TransactionCompletionLinker

class StatementItemInvoiceLinker(Tool):
    
    def __init__(self, master):
        super().__init__(master, title='Statement Item / Invoice Linking Tool')
        self._open_tool()
        
    @property
    def statement_item(self):
        items = data.v_StatementItemLinkable()
        if len(items) == 0:
            self.close()
            return StatementItem("")
        statement_item_id = items.iloc[0]["StatementItemId"]
        return StatementItem(statement_item_id)
    
    def _open_tool(self):

        match self.statement_item.ImageContentType:

            case 'RECEIPT':
                self.tool = StatementItemInvoiceReceiptLinker(self, self.statement_item, self._close_tool)

            case 'TRANSACTION':
                self.tool = TransactionCompletionLinker(self, self.statement_item, self._close_tool)

            case _:
                self.tool = None
        
    def _close_tool(self):
        self.tool.close()
        self.tool.destroy()
        self._open_tool()