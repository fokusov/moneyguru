# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import tr
from ..const import PaneType
from ..document import FilterType
from ..model.account import AccountType
from ..model.amount import convert_amount
from .base import BaseView, MESSAGES_DOCUMENT_CHANGED
from .filter_bar import FilterBar
from .transaction_table import TransactionTable
from .transaction_print import TransactionPrint

class TransactionView(BaseView):
    VIEW_TYPE = PaneType.Transaction
    PRINT_TITLE_FORMAT = tr('Transactions from {start_date} to {end_date}')
    PRINT_VIEW_CLASS = TransactionPrint
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'filter_applied', 'date_range_changed'}
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self._visible_transactions = None
        self.filter_bar = FilterBar(self)
        self.ttable = TransactionTable(self)
        self.maintable = self.ttable
        self.columns = self.maintable.columns
        self.set_children([self.ttable])
    
    def _revalidate(self):
        self._visible_transactions = None
        self._refresh_totals()
        self.filter_bar.refresh()
    
    #--- Private
    def _invalidate_cache(self):
        self._visible_transactions = None
        self._refresh_totals()
    
    def _refresh_totals(self):
        selected = len(self.mainwindow.selected_transactions)
        total = len(self.visible_transactions)
        currency = self.document.default_currency
        total_amount = sum(convert_amount(t.amount, currency, t.date) for t in self.mainwindow.selected_transactions)
        total_amount_fmt = self.document.format_amount(total_amount)
        msg = tr("{0} out of {1} selected. Amount: {2}")
        self.status_line = msg.format(selected, total, total_amount_fmt)
    
    def _set_visible_transactions(self):
        date_range = self.document.date_range
        txns = [t for t in self.document.oven.transactions if t.date in date_range]
        query_string = self.document.filter_string
        filter_type = self.document.filter_type
        if not query_string and filter_type is None:
            self._visible_transactions = txns
            return
        if query_string:
            query = self.app.parse_search_query(query_string)
            txns = [t for t in txns if t.matches(query)]
        if filter_type is FilterType.Unassigned:
            txns = [t for t in txns if t.has_unassigned_split]
        elif filter_type is FilterType.Income:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == AccountType.Income for s in t.splits)]
        elif filter_type is FilterType.Expense:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == AccountType.Expense for s in t.splits)]
        elif filter_type is FilterType.Transfer:
            def is_transfer(t):
                return len([s for s in t.splits if s.account is not None and s.account.is_balance_sheet_account()]) >= 2
            txns = list(filter(is_transfer, txns))
        elif filter_type is FilterType.Reconciled:
            txns = [t for t in txns if any(s.reconciled for s in t.splits)]
        elif filter_type is FilterType.NotReconciled:
            txns = [t for t in txns if all(not s.reconciled for s in t.splits)]
        self._visible_transactions = txns
    
    #--- Override
    def save_preferences(self):
        self.ttable.columns.save_columns()
    
    #--- Public
    def delete_item(self):
        self.ttable.delete()
    
    def duplicate_item(self):
        self.ttable.duplicate_selected()
    
    def edit_item(self):
        self.mainwindow.edit_selected_transactions()
    
    def move_down(self):
        self.ttable.move_down()
    
    def move_up(self):
        self.ttable.move_up()
    
    def new_item(self):
        self.ttable.add()
    
    def show_account(self):
        self.ttable.show_from_account()
    
    #--- Properties
    @property
    def visible_transactions(self):
        if self._visible_transactions is None:
            self._set_visible_transactions()
        return self._visible_transactions
    
    #--- Event Handlers
    def date_range_changed(self):
        self._invalidate_cache()
    
    def document_changed(self):
        self._invalidate_cache()
    
    def filter_applied(self):
        self._invalidate_cache()
        self.filter_bar.refresh()
    
    def performed_undo_or_redo(self):
        self._invalidate_cache()
    
    def transactions_selected(self):
        self._refresh_totals()
    
    def transaction_changed(self):
        self._invalidate_cache()
    
    def transaction_deleted(self):
        self._invalidate_cache()
    
    def transactions_imported(self):
        self._invalidate_cache()
    
