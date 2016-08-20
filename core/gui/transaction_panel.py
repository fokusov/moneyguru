# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import weakref
from datetime import date

from hscommon.util import first

from ..model.account import Account, AccountType
from ..model.transaction import Split, Transaction
from .base import MainWindowPanel
from .split_table import SplitTable
from .completable_edit import CompletableEdit

class PanelWithTransaction(MainWindowPanel):
    """Base class for panels working with a transaction"""
    def __init__(self, mainwindow):
        MainWindowPanel.__init__(self, mainwindow)
        self.transaction = Transaction(date.today())
        self._selected_splits = []
        # completable_edit has to be set before split_table is created because split table fetches
        # our completable edit on __init__ (for Qt).
        self.completable_edit = CompletableEdit(mainwindow)
        self.split_table = SplitTable(weakref.proxy(self))

    def change_split(self, split, account_name, amount, memo):
        if account_name:
            if split.account:
                account_type = split.account.type
            else:
                account_type = AccountType.Expense if split.amount < 0 else AccountType.Income
            split.account = Account(account_name, self.document.default_currency, account_type)
        else:
            split.account = None
        split.amount = amount
        split.memo = memo
        if split not in self.transaction.splits:
            self.transaction.splits.append(split)
        self.transaction.balance(split)
        self.split_table.refresh_splits()
        self.view.refresh_for_multi_currency()

    def delete_split(self, split):
        split.remove()
        self.view.refresh_for_multi_currency()

    def new_split(self):
        return Split(self.transaction, None, 0)

    def select_splits(self, splits):
        self._selected_splits = splits

    # --- Properties
    @property
    def description(self):
        return self.transaction.description

    @description.setter
    def description(self, value):
        self.transaction.description = value

    @property
    def payee(self):
        return self.transaction.payee

    @payee.setter
    def payee(self, value):
        self.transaction.payee = value

    @property
    def checkno(self):
        return self.transaction.checkno

    @checkno.setter
    def checkno(self, value):
        self.transaction.checkno = value

    @property
    def notes(self):
        return self.transaction.notes

    @notes.setter
    def notes(self, value):
        self.transaction.notes = value

    @property
    def is_multi_currency(self):
        return self.transaction.is_mct


class TransactionPanel(PanelWithTransaction):
    # --- Override
    def _load(self, transaction):
        self.document.stop_edition()
        self.transaction = transaction.replicate()
        self.original = transaction
        self.view.refresh_for_multi_currency()
        self.split_table.refresh_initial()

    def _save(self):
        self.document.change_transaction(self.original, self.transaction)

    # --- Public
    def mct_balance(self):
        """Balances the mct by using xchange rates.

        The currency of the new split is the currency of the currently selected split.
        """
        self.split_table.edition_must_stop()
        split = first(self._selected_splits)
        new_split_currency = self.document.default_currency
        if split is not None and split.amount != 0:
            new_split_currency = split.amount.currency
        self.transaction.mct_balance(new_split_currency)
        self.split_table.refresh_splits()

    def assign_imbalance(self):
        """Assigns remaining imbalance to the selected split.

        If the selected split is not an assigned split, does nothing.
        """
        split = first(self._selected_splits)
        if split is not None:
            self.transaction.assign_imbalance(split)
            self.split_table.refresh_splits()

    @property
    def date(self):
        return self.app.format_date(self.transaction.date)

    @date.setter
    def date(self, value):
        self.transaction.date = self.app.parse_date(value)

