# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import logging

from hscommon.notify import Repeater
from hscommon.util import first, minmax
from hscommon.trans import tr
from hscommon.gui.base import GUIObject

from ..const import PaneType
from ..document import FilterType
from ..exception import OperationAborted, FileFormatError
from ..model.budget import BudgetSpawn
from ..model.date import inc_month, DateFormat
from ..model.recurrence import Recurrence, RepeatType
from ..loader import csv, qif, ofx, native
from .base import MESSAGES_DOCUMENT_CHANGED
from .search_field import SearchField
from .date_range_selector import DateRangeSelector
from .account_lookup import AccountLookup
from .completion_lookup import CompletionLookup
from .account_panel import AccountPanel
from .transaction_panel import TransactionPanel
from .mass_edition_panel import MassEditionPanel
from .budget_panel import BudgetPanel
from .schedule_panel import SchedulePanel
from .custom_date_range_panel import CustomDateRangePanel
from .account_reassign_panel import AccountReassignPanel
from .export_panel import ExportPanel
from .import_window import ImportWindow
from .csv_options import CSVOptions
from .networth_view import NetWorthView
from .profit_view import ProfitView
from .transaction_view import TransactionView
from .account_view import AccountView
from .schedule_view import ScheduleView
from .budget_view import BudgetView
from .general_ledger_view import GeneralLedgerView
from .docprops_view import DocPropsView
from .empty_view import EmptyView

PANETYPE2LABEL = {
    PaneType.NetWorth: tr("Net Worth"),
    PaneType.Profit: tr("Profit & Loss"),
    PaneType.Transaction: tr("Transactions"),
    PaneType.Schedule: tr("Schedules"),
    PaneType.Budget: tr("Budgets"),
    PaneType.GeneralLedger: tr("General Ledger"),
    PaneType.DocProps: tr("Document Properties"),
    PaneType.Empty: tr("New Tab"),
}

class Preference:
    OpenedPanes = 'OpenedPanes'
    SelectedPane = 'SelectedPane'
    HiddenAreas = 'HiddenAreas'
    WindowFrame = 'WindowFrame'

class ViewPane:
    def __init__(self, view, label):
        self.view = view
        self.label = label

    def __repr__(self):
        return '<ViewPane {}>'.format(self.label)

    @property
    def account(self):
        if self.view.VIEW_TYPE == PaneType.Account:
            return self.view.account
        else:
            return None


class MainWindow(Repeater, GUIObject):
    #--- model -> view calls:
    # change_current_pane()
    # refresh_panes()
    # refresh_status_line()
    # refresh_undo_actions()
    # restore_window_frame(frame)
    # save_window_frame() -> frame
    # show_custom_date_range_panel()
    # show_message(message)
    # view_closed(index)
    # update_area_visibility()

    def __init__(self, document):
        Repeater.__init__(self, document)
        GUIObject.__init__(self)
        self.document = document
        self.app = document.app
        self._selected_transactions = []
        self._explicitly_selected_transactions = []
        self._selected_schedules = []
        self._selected_budgets = []
        self._account2visibleentries = {}
        self.panes = []
        self.hidden_areas = set()

        self.search_field = SearchField(self)
        self.daterange_selector = DateRangeSelector(self)
        self.account_lookup = AccountLookup(self)
        self.completion_lookup = CompletionLookup(self)

        self.account_panel = AccountPanel(self)
        self.transaction_panel = TransactionPanel(self)
        self.mass_edit_panel = MassEditionPanel(self)
        self.budget_panel = BudgetPanel(self)
        self.schedule_panel = SchedulePanel(self)
        self.custom_daterange_panel = CustomDateRangePanel(self)
        self.account_reassign_panel = AccountReassignPanel(self)
        self.export_panel = ExportPanel(self)

        self.csv_options = CSVOptions(self)
        self.import_window = ImportWindow(self)

        msgs = MESSAGES_DOCUMENT_CHANGED | {'filter_applied', 'date_range_changed'}
        self.bind_messages(msgs, self._invalidate_visible_entries)

    #--- Private
    def _add_pane(self, pane):
        self.panes.append(pane)
        self.view.refresh_panes()
        self.current_pane_index = len(self.panes) - 1

    def _change_current_pane(self, pane):
        if self._current_pane is pane:
            return
        if self._current_pane is not None:
            self._current_pane.view.hide()
        self._current_pane = pane
        self._current_pane.view.show()
        self.view.change_current_pane()
        self.update_status_line()

    def _close_irrelevant_account_panes(self):
        indexes_to_close = []
        for index, pane in enumerate(self.panes):
            if pane.view.VIEW_TYPE == PaneType.Account and pane.account not in self.document.accounts:
                indexes_to_close.append(index)
        if self.current_pane_index in indexes_to_close:
            self.select_pane_of_type(PaneType.NetWorth)
        for index in reversed(indexes_to_close):
            self.close_pane(index)

    def _create_pane(self, pane_type, account=None):
        view = self._get_view_for_pane_type(pane_type, account)
        if pane_type == PaneType.Account:
            return ViewPane(view, account.name)
        else:
            return ViewPane(view, PANETYPE2LABEL[pane_type])

    def _create_pane_from_plugin(self, plugin):
        plugin_inst = plugin(self)
        plugin_inst.view.connect()
        return ViewPane(plugin_inst.view, plugin_inst.NAME)

    def _get_view_for_pane_type(self, pane_type, account):
        if pane_type == PaneType.Account: # we don't cache Account panes
            result = AccountView(self, account)
            result.connect()
            return result
        for pane in self.panes:
            if pane.view.VIEW_TYPE == pane_type:
                return pane.view
        if pane_type == PaneType.NetWorth:
            result = NetWorthView(self)
        elif pane_type == PaneType.Profit:
            result = ProfitView(self)
        elif pane_type == PaneType.Transaction:
            result = TransactionView(self)
        elif pane_type == PaneType.Schedule:
            result = ScheduleView(self)
        elif pane_type == PaneType.Budget:
            result = BudgetView(self)
        elif pane_type == PaneType.GeneralLedger:
            result = GeneralLedgerView(self)
        elif pane_type == PaneType.DocProps:
            result = DocPropsView(self)
        elif pane_type == PaneType.Empty:
            result = EmptyView(self)
        else:
            raise ValueError("Cannot create view of type {}".format(pane_type))
        result.connect()
        return result

    def _invalidate_visible_entries(self):
        self._account2visibleentries = {}

    def _perform_if_possible(self, action_name):
        current_view = self._current_pane.view
        if current_view.can_perform(action_name):
            getattr(current_view, action_name)()

    def _restore_default_panes(self):
        pane_types = [
            PaneType.NetWorth, PaneType.Profit, PaneType.Transaction,
            PaneType.Schedule, PaneType.Budget
        ]
        pane_data = list(zip(pane_types, [None] * len(pane_types)))
        self._set_panes(pane_data)

    def _restore_opened_panes(self):
        stored_panes = self.document.get_default(Preference.OpenedPanes)
        logging.debug('Restoring panes from data %r', stored_panes)
        if not stored_panes:
            return
        pane_data = []
        for data in stored_panes:
            pane_type = data['pane_type']
            if pane_type == PaneType.Account:
                account_name = str(data.get('account_name', '')) # str() because the value might be an int
                account = self.document.accounts.find(account_name)
                if account is None:
                    continue
                arg = account
            elif pane_type >= PaneType.Plugin:
                arg = str(data.get('plugin_name', ''))
            else:
                arg = None
            pane_data.append((pane_type, arg))
        if pane_data:
            self._set_panes(pane_data)
            selected_pane_index = self.document.get_default(Preference.SelectedPane)
            if selected_pane_index is not None:
                self.current_pane_index = selected_pane_index

    def _save_preferences(self):
        opened_panes = []
        for pane in self.panes:
            data = {}
            data['pane_type'] = pane.view.VIEW_TYPE
            if pane.account is not None:
                data['account_name'] = pane.account.name
            if pane.view.VIEW_TYPE >= PaneType.Plugin:
                data['plugin_name'] = pane.view.plugin.NAME
            opened_panes.append(data)
        logging.debug('Saving panes with data %r', opened_panes)
        self.document.set_default(Preference.OpenedPanes, opened_panes)
        self.document.set_default(Preference.SelectedPane, self._current_pane_index)
        self.document.set_default(Preference.HiddenAreas, list(self.hidden_areas))
        window_frame = self.view.save_window_frame()
        if window_frame:
            self.document.set_default(Preference.WindowFrame, list(window_frame))

    def _set_panes(self, pane_data):
        # Replace opened panes with new panes from `pane_data`, which is a [(pane_type, arg)]
        self._current_pane = None
        self._current_pane_index = -1
        for pane in self.panes:
            pane.view.disconnect()
        self.panes = []
        for pane_type, arg in pane_data:
            if pane_type >= PaneType.Plugin:
                plugin = first(p for p in self.app.plugins if p.NAME == arg)
                if plugin is not None:
                    self.panes.append(self._create_pane_from_plugin(plugin))
                else:
                    self.panes.append(self._create_pane(PaneType.NetWorth))
            else:
                try:
                    self.panes.append(self._create_pane(pane_type, account=arg))
                except ValueError:
                    self.panes.append(self._create_pane(PaneType.NetWorth))
        self.view.refresh_panes()
        self.current_pane_index = 0

    def _set_current_pane(self, newpane):
        index = self.current_pane_index
        self.panes[index] = newpane
        self.view.refresh_panes()
        self._change_current_pane(newpane)

    def _update_area_visibility(self):
        self.notify('area_visibility_changed')
        self.view.update_area_visibility()

    def _visible_entries_for_account(self, account):
        date_range = self.document.date_range
        entries = [e for e in account.entries if e.date in date_range]
        query_string = self.document.filter_string
        filter_type = self.document.filter_type
        if query_string:
            query = self.app.parse_search_query(query_string)
            entries = [e for e in entries if e.transaction.matches(query)]
        if filter_type is FilterType.Unassigned:
            entries = [e for e in entries if not e.transfer]
        elif (filter_type is FilterType.Income) or (filter_type is FilterType.Expense):
            if account.is_credit_account():
                want_positive = filter_type is FilterType.Expense
            else:
                want_positive = filter_type is FilterType.Income
            if want_positive:
                entries = [e for e in entries if e.amount > 0]
            else:
                entries = [e for e in entries if e.amount < 0]
        elif filter_type is FilterType.Transfer:
            entries = [
                e for e in entries if
                any(s.account is not None and s.account.is_balance_sheet_account() for s in e.splits)
            ]
        elif filter_type is FilterType.Reconciled:
            entries = [e for e in entries if e.reconciled]
        elif filter_type is FilterType.NotReconciled:
            entries = [e for e in entries if not e.reconciled]
        return entries

    #--- Override
    def _view_updated(self):
        self.daterange_selector.refresh()
        self.daterange_selector.refresh_custom_ranges()
        self.document_restoring_preferences()
        if self.document.can_restore_from_prefs():
            # Under Cocoa, document.load_from_xml() is called before the creation of our main
            # window, which means that all our view children don't receive the
            # document_restoring_preferences notification. Force it here.
            self.notify('document_restoring_preferences')
        if not self.panes:
            self._restore_default_panes()

    #--- Public
    def close_pane(self, index):
        if self.pane_count == 1: # don't close the last pane
            return
        if index == self.current_pane_index:
            # we must select another pane before we close it.
            if index == len(self.panes)-1:
                self.current_pane_index -= 1
            else:
                self.current_pane_index += 1
        pane = self.panes[index]
        del self.panes[index]
        if not any(p.view is pane.view for p in self.panes):
            pane.view.save_preferences()
            pane.view.disconnect()
        self.view.view_closed(index)
        # The index of the current view might have changed
        newindex = self.panes.index(self._current_pane)
        if newindex != self._current_pane_index:
            self._current_pane_index = newindex
            self.view.change_current_pane()

    def delete_item(self):
        self._perform_if_possible('delete_item')

    def duplicate_item(self):
        self._perform_if_possible('duplicate_item')

    def edit_item(self):
        try:
            self._perform_if_possible('edit_item')
        except OperationAborted:
            pass

    def edit_selected_transactions(self):
        editable_txns = [txn for txn in self.selected_transactions if not isinstance(txn, BudgetSpawn)]
        if len(editable_txns) > 1:
            self.mass_edit_panel.load()
        elif len(editable_txns) == 1:
            self.transaction_panel.load()

    def export(self):
        self.export_panel.load()

    def jump_to_account(self):
        self.account_lookup.show()

    def load_parsed_file_for_import(self):
        """Load a parsed file for import and trigger the opening of the Import window.

        When the document's ``loader`` has finished parsing (either after having done CSV
        configuration or directly after :meth:`parse_file_for_import`), call this method to load the
        parsed data into model instances, ready to be shown in the Import window.
        """
        self.loader.load()
        if self.loader.accounts and self.loader.transactions:
            self.import_window.show()
        else:
            raise FileFormatError('This file does not contain any account to import.')

    def make_schedule_from_selected(self):
        current_view = self._current_pane.view
        if current_view.VIEW_TYPE in {PaneType.Transaction, PaneType.Account}:
            if not self.selected_transactions:
                return
            # There's no test case for this, but select_pane_of_type() must happen before
            # new_schedule_from_transaction() or else the sctable's selection upon view switch will
            # overwrite our selection.
            self.select_pane_of_type(PaneType.Schedule)
            ref = self.selected_transactions[0].replicate()
            ref.date = inc_month(ref.date, 1)
            schedule = Recurrence(ref, RepeatType.Monthly, 1)
            self.selected_schedules = [schedule]
            self.edit_item()

    def move_down(self):
        self._perform_if_possible('move_down')

    def move_up(self):
        self._perform_if_possible('move_up')

    def move_pane(self, pane_index, dest_index):
        pane = self.panes[pane_index]
        del self.panes[pane_index]
        self.panes.insert(dest_index, pane)
        self.current_pane_index = self.panes.index(self._current_pane)
        self.view.refresh_panes()

    def navigate_back(self):
        self._perform_if_possible('navigate_back')

    def new_item(self):
        try:
            self._perform_if_possible('new_item')
        except OperationAborted as e:
            if e.message:
                self.view.show_message(e.message)

    def new_group(self):
        self._perform_if_possible('new_group')

    def new_tab(self):
        self.panes.append(self._create_pane(PaneType.Empty))
        self.view.refresh_panes()
        self.current_pane_index = len(self.panes) - 1

    def open_account(self, account):
        if account is not None:
            # Try to find a suitable pane, or add a new one
            index = first(i for i, p in enumerate(self.panes) if p.account is account)
            if index is None:
                self._add_pane(self._create_pane(PaneType.Account, account))
            else:
                self.current_pane_index = index
        elif self._current_pane.view.VIEW_TYPE == PaneType.Account:
            self.select_pane_of_type(PaneType.NetWorth)

    def pane_label(self, index):
        pane = self.panes[index]
        return pane.label

    def pane_type(self, index):
        pane = self.panes[index]
        return pane.view.VIEW_TYPE

    def pane_view(self, index):
        return self.panes[index].view

    def parse_file_for_import(self, filename):
        """Parses ``filename`` in preparation for importing.

        Opens and parses ``filename`` and try to determine its format by successively trying to read
        is as a moneyGuru file, an OFX, a QIF and finally a CSV. Once parsed, take the appropriate
        action for the file which is either to show the CSV options window or to call
        :meth:`load_parsed_file_for_import`.
        """
        default_date_format = DateFormat(self.app.date_format).sys_format
        for loaderclass in (native.Loader, ofx.Loader, qif.Loader, csv.Loader):
            try:
                loader = loaderclass(
                    self.document.default_currency, default_date_format=default_date_format
                )
                loader.parse(filename)
                break
            except FileFormatError:
                pass
        else:
            # No file fitted
            raise FileFormatError(tr('%s is of an unknown format.') % filename)
        self.loader = loader
        if isinstance(self.loader, csv.Loader):
            self.csv_options.show()
        else:
            self.load_parsed_file_for_import()

    def select_pane_of_type(self, pane_type, clear_filter=True):
        if clear_filter:
            self.document.filter_string = ''
        index = first(i for i, p in enumerate(self.panes) if p.view.VIEW_TYPE == pane_type)
        if index is None:
            self._add_pane(self._create_pane(pane_type))
        else:
            self.current_pane_index = index

    def select_next_view(self):
        if self.current_pane_index == len(self.panes) - 1:
            return
        self.current_pane_index += 1

    def select_previous_view(self):
        if self.current_pane_index == 0:
            return
        self.current_pane_index -= 1

    def set_current_pane_type(self, pane_type):
        self._set_current_pane(self._create_pane(pane_type))

    def set_current_pane_with_plugin(self, plugin):
        self._set_current_pane(self._create_pane_from_plugin(plugin))

    def show_account(self):
        """Shows the currently selected account in the Account view.

        If a sheet is selected, the selected account will be shown.
        If the Transaction or Account view is selected, the related account (From, To, Transfer)
        of the selected transaction will be shown.
        """
        current_view = self._current_pane.view
        if hasattr(current_view, 'show_account'):
            current_view.show_account()

    def show_message(self, message):
        self.view.show_message(message)

    def toggle_area_visibility(self, area):
        if area in self.hidden_areas:
            self.hidden_areas.remove(area)
        else:
            self.hidden_areas.add(area)
        self._update_area_visibility()

    def update_status_line(self):
        self.view.refresh_status_line()

    def visible_entries_for_account(self, account):
        if account is None:
            return []
        if account not in self._account2visibleentries:
            self._account2visibleentries[account] = self._visible_entries_for_account(account)
        return self._account2visibleentries[account]

    #Column menu
    def column_menu_items(self):
        # Returns a list of (display_name, marked) items for each optional column in the current
        # view (marked means that it's visible).
        if not hasattr(self._current_pane.view, 'columns'):
            return None
        return self._current_pane.view.columns.menu_items()

    def toggle_column_menu_item(self, index):
        if not hasattr(self._current_pane.view, 'columns'):
            return None
        self._current_pane.view.columns.toggle_menu_item(index)

    #--- Properties
    @property
    def current_pane_index(self):
        return self._current_pane_index

    @current_pane_index.setter
    def current_pane_index(self, value):
        if value == self._current_pane_index:
            return
        self.document.stop_edition()
        value = minmax(value, 0, len(self.panes)-1)
        pane = self.panes[value]
        self._current_pane_index = value
        self._change_current_pane(pane)

    @property
    def pane_count(self):
        return len(self.panes)

    @property
    def selected_schedules(self):
        return self._selected_schedules

    @selected_schedules.setter
    def selected_schedules(self, schedules):
        self._selected_schedules = schedules

    @property
    def selected_budgets(self):
        return self._selected_budgets

    @selected_budgets.setter
    def selected_budgets(self, budgets):
        self._selected_budgets = budgets

    @property
    def selected_transactions(self):
        return self._selected_transactions

    @selected_transactions.setter
    def selected_transactions(self, transactions):
        self._selected_transactions = transactions
        self.notify('transactions_selected')

    @property
    def explicitly_selected_transactions(self):
        return self._explicitly_selected_transactions

    @explicitly_selected_transactions.setter
    def explicitly_selected_transactions(self, transactions):
        self._explicitly_selected_transactions = transactions
        self.selected_transactions = transactions

    @property
    def status_line(self):
        return self._current_pane.view.status_line

    #--- Event callbacks
    def _undo_stack_changed(self):
        self.view.refresh_undo_actions()

    account_added = _undo_stack_changed

    def account_changed(self):
        self._undo_stack_changed()
        tochange = first(p for p in self.panes if p.account is not None and p.account.name != p.label)
        if tochange is not None:
            tochange.label = tochange.account.name
            self.view.refresh_panes()

    account_deleted = _undo_stack_changed
    budget_changed = _undo_stack_changed
    budget_deleted = _undo_stack_changed

    def custom_date_range_selected(self):
        self.custom_daterange_panel.load()

    def date_range_will_change(self):
        self.daterange_selector.remember_current_range()

    def date_range_changed(self):
        self.daterange_selector.refresh()

    def document_changed(self):
        self._close_irrelevant_account_panes()
        self._undo_stack_changed()

    def document_will_close(self):
        self._save_preferences()
        for pane in self.panes:
            pane.view.save_preferences()
        if self._current_pane.view.VIEW_TYPE == PaneType.Account:
            # if our current pane is an account view, we need to hide it for it to save its prefs.
            # Since account panes are closed with the document, it doesn't matter if we hide them.
            # However, it's a bit of a kludge and if hide() is called on another type of pane, you
            # risk getting view refresh bugs under Qt because in there, closing a document doesn't
            # always mean closing the window (unlike under Cocoa).
            self._current_pane.view.hide()

    def document_restoring_preferences(self):
        window_frame = self.document.get_default(Preference.WindowFrame)
        if window_frame:
            self.view.restore_window_frame(tuple(window_frame))
        self._restore_opened_panes()
        self.hidden_areas = set(self.document.get_default(Preference.HiddenAreas, fallback_value=[]))
        self._update_area_visibility()

    def filter_applied(self):
        is_txn_pane = self._current_pane.view.VIEW_TYPE in {PaneType.Transaction, PaneType.Account}
        if self.document.filter_string and not is_txn_pane:
            self.select_pane_of_type(PaneType.Transaction, clear_filter=False)
        self.search_field.refresh()

    def performed_undo_or_redo(self):
        self._close_irrelevant_account_panes()
        self.view.refresh_undo_actions()

    def saved_custom_ranges_changed(self):
        self.daterange_selector.refresh_custom_ranges()

    schedule_changed = _undo_stack_changed
    schedule_deleted = _undo_stack_changed
    transaction_changed = _undo_stack_changed

    def transaction_deleted(self):
        self._explicitly_selected_transactions = []
        self._selected_transactions = []
        self._close_irrelevant_account_panes() # after an auto-clean
        self.view.refresh_undo_actions()

    transactions_imported = _undo_stack_changed
