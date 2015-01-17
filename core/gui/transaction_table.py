# Created By: Virgil Dupras
# Created On: 2008-07-11
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import datetime
from operator import attrgetter

from hscommon.trans import trget, tr
from hscommon.gui.column import Column
from ..model.amount import convert_amount
from ..model.recurrence import Spawn
from ..model.transaction import Transaction
from .table import Row, RowWithDateMixIn, rowattr
from .transaction_table_base import TransactionTableBase

trcol = trget('columns')

class TransactionTable(TransactionTableBase):
    SAVENAME = 'TransactionTable'
    COLUMNS = [
        Column('status', display=''),
        Column('date', display=trcol('Date')),
        Column('checkno', display=trcol('Check #'), visible=False, optional=True),
        Column('description', display=trcol('Description'), optional=True),
        Column('payee', display=trcol('Payee'), visible=False, optional=True),
        Column('from', display=trcol('From')),
        Column('to', display=trcol('To')),
        Column('amount', display=trcol('Amount')),
        Column('mtime', display=trcol('Modification Time'), visible=False, optional=True),
    ]

    #--- Override
    def _do_add(self):
        transactions = self.mainwindow.selected_transactions
        date = transactions[0].date if transactions else datetime.date.today()
        transaction = Transaction(date, amount=0)
        rows = self[:-1] # ignore total row
        for index, row in enumerate(rows):
            if row._date > transaction.date:
                insert_index = index
                break
        else:
            insert_index = len(rows)
        row = TransactionTableRow(self, transaction)
        return row, insert_index

    def _do_delete(self):
        transactions = self.selected_transactions
        if transactions:
            self.document.delete_transactions(transactions)

    def _fill(self):
        self._all_amounts_are_native = True
        total_amount = 0
        for transaction in self.parent_view.visible_transactions:
            self.append(TransactionTableRow(self, transaction))
            convert = lambda a: convert_amount(a, self.document.default_currency, transaction.date)
            total_amount += convert(transaction.amount)
            if not self.document.is_amount_native(transaction.amount):
                self._all_amounts_are_native = False
        self.footer = TotalRow(self, self.document.date_range.end, total_amount)
        self._restore_from_explicit_selection()

    #--- Private
    def _show_account(self, row_index=None, use_to_column=False):
        # if `use_to_column` is True, use the To column, else, use the From column
        if row_index is None:
            if not self.selected_transactions:
                return
            row_index = self.selected_index
        txn = self[row_index].transaction
        froms, tos = txn.splitted_splits()
        splits = tos if use_to_column else froms
        account_to_show = splits[0].account
        self.mainwindow.open_account(account_to_show)

    #--- Public
    def select_transactions(self, transactions):
        TransactionTableBase.select_transactions(self, transactions)
        if self and not self.selected_indexes:
            self.selected_indexes = [len(self) - 1]

    def show_from_account(self, row_index=None):
        self._show_account(row_index, use_to_column=False)

    def show_to_account(self, row_index=None):
        self._show_account(row_index, use_to_column=True)

    #--- Properties
    @property
    def selected_transactions(self):
        return [row.transaction for row in self.selected_rows if hasattr(row, 'transaction')]

    #--- Event handlers
    def date_range_changed(self):
        self.refresh(refresh_view=False)
        self._update_selection()
        self.view.refresh()
        self.view.show_selected_row()

    def transactions_imported(self):
        self.refresh(refresh_view=False)
        self._update_selection()
        self.view.refresh()


AUTOFILL_ATTRS = {'description', 'payee', 'from', 'to', 'amount'}

class TransactionTableRow(Row, RowWithDateMixIn):
    FIELDS = [
        ('_date', 'date'),
        ('_description', 'description'),
        ('_payee', 'payee'),
        ('_checkno', 'checkno'),
    ]

    def __init__(self, table, transaction):
        Row.__init__(self, table)
        RowWithDateMixIn.__init__(self)
        self.document = table.document
        self.transaction = transaction
        self.is_bold = False
        self.load()

    def _autofill_row(self, ref_row, dest_attrs):
        self._amount_fmt = None
        if len(ref_row.transaction.splits) > 2:
            dest_attrs.discard('_from')
            dest_attrs.discard('_to')
        Row._autofill_row(self, ref_row, dest_attrs)

    def _get_autofill_attrs(self):
        return AUTOFILL_ATTRS

    def _get_autofill_rows(self):
        original = self.transaction
        transactions = sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)
        for transaction in transactions:
            if transaction is original:
                continue
            yield TransactionTableRow(self.table, transaction)

    #--- Public
    def can_edit(self):
        return not self.is_budget

    def load(self):
        transaction = self.transaction
        self._load_from_fields(transaction, self.FIELDS)
        self._date_fmt = None
        self._position = transaction.position
        splits = transaction.splits
        froms, tos = self.transaction.splitted_splits()
        self._from_count = len(froms)
        self._to_count = len(tos)
        UNASSIGNED = tr('Unassigned') if len(froms) > 1 else ''
        get_display = lambda s: s.account.combined_display if s.account is not None else UNASSIGNED
        self._from = ', '.join(map(get_display, froms))
        UNASSIGNED = tr('Unassigned') if len(tos) > 1 else ''
        get_display = lambda s: s.account.combined_display if s.account is not None else UNASSIGNED
        self._to = ', '.join(map(get_display, tos))
        self._amount = transaction.amount
        self._amount_fmt = None
        self._mtime = datetime.datetime.fromtimestamp(transaction.mtime)
        if transaction.mtime > 0:
            self._mtime_fmt = self._mtime.strftime('%Y/%m/%d %H:%M')
        else:
            self._mtime_fmt = ''
        self._recurrent = isinstance(transaction, Spawn)
        self._reconciled = any(split.reconciled for split in splits)
        self._is_budget = getattr(transaction, 'is_budget', False)
        self._can_set_amount = transaction.can_set_amount

    def save(self):
        transaction = self.transaction
        changed_fields = self._get_changed_fields(transaction, self.FIELDS)
        if self.can_edit_from:
            changed_fields['from_'] = self._from
        if self.can_edit_to == 1:
            changed_fields['to'] = self._to
        if self.can_edit_amount:
            changed_fields['amount'] = self._amount
        self.document.change_transactions([transaction], **changed_fields)
        self.load()

    def sort_key_for_column(self, column_name):
        if column_name == 'date':
            return (self._date, self._position)
        elif column_name == 'status':
            # First reconciled, then plain ones, then schedules, then budgets
            if self.reconciled:
                return 0
            elif self.recurrent:
                return 2
            elif self.is_budget:
                return 3
            else:
                return 1
        else:
            return Row.sort_key_for_column(self, column_name)

    #--- Properties
    # The "get" part of those properies below are called *very* often, hence, the format caching

    description = rowattr('_description', 'description')
    payee = rowattr('_payee', 'payee')
    checkno = rowattr('_checkno')
    from_ = rowattr('_from', 'from')

    @property
    def can_edit_from(self):
        return self._from_count == 1

    to = rowattr('_to', 'to')

    @property
    def can_edit_to(self):
        return self._to_count == 1

    @property
    def can_edit_amount(self):
        return self._can_set_amount

    @property
    def amount(self):
        if self._amount_fmt is None:
            self._amount_fmt = self.document.format_amount(self._amount)
        return self._amount_fmt

    @amount.setter
    def amount(self, value):
        self._edit()
        try:
            self._amount = self.document.parse_amount(value)
        except ValueError:
            return
        self._amount_fmt = None

    @property
    def mtime(self):
        return self._mtime_fmt

    @property
    def reconciled(self):
        return self._reconciled

    @property
    def recurrent(self):
        return self._recurrent

    @property
    def is_budget(self):
        return self._is_budget


class TotalRow(Row):
    def __init__(self, table, date, total_amount):
        Row.__init__(self, table)
        self._date = date
        self.date = self.table.document.app.format_date(date)
        self.description = tr('TOTAL')
        self.amount = self.table.document.format_amount(total_amount)
        self.payee = ''
        self.checkno = ''
        self.from_ = ''
        self.to = ''
        self.mtime = ''
        self.reconciled = False
        self.recurrent = False
        self.is_budget = False
        self.is_bold = True

    def can_edit(self):
        return False

