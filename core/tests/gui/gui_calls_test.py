# Created By: Virgil Dupras
# Created On: 2009-11-07
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

# GUI calls are often made under the same conditions for multiple guis. Duplicating that condition
# in every test unit can get tedious, so this test unit is a "theme based" unit which tests calls
# made to GUIs' view.

from hscommon.currency import EUR

from ...document import FilterType
from ...model.account import AccountType
from ..base import TestApp, with_app, testdata

#--- No Setup
def test_initial_gui_calls():
    app = TestApp()
    app.show_nwview()
    app.bsheet.view.check_gui_calls(['refresh'])
    expected = ['refresh_panes', 'change_current_pane', 'refresh_status_line', 'update_area_visibility']
    app.mw.view.check_gui_calls(expected)
    app.drsel.view.check_gui_calls(['refresh_custom_ranges', 'refresh'])

#--- Cleared GUI calls
def app_cleared_gui_calls():
    app = TestApp()
    app.clear_gui_calls()
    return app

@with_app(app_cleared_gui_calls)
def test_add_account_and_show_it(app):
    # When an account is shown, the reconciliation button is refreshed.
    app.add_account()
    app.show_account()
    app.check_gui_calls_partial(app.aview.view, ['refresh_reconciliation_button'])

def test_add_group():
    # Adding a group refreshes the view and goes into edit mode.
    app = app_cleared_gui_calls()
    app.show_nwview()
    app.bsheet.add_account_group()
    expected_calls = ['stop_editing', 'start_editing', 'refresh', 'update_selection']
    app.check_gui_calls(app.bsheet_gui, expected_calls)
    # When doing an action that modifies the undo stack, refresh_undo_actions is called
    # (we're not testing all actions on this one because it's just tiresome and, frankly, a
    # little silly, but assume that all events broadcasted when the undo stack is changed
    # have been connected)
    app.check_gui_calls(app.mainwindow_gui, ['refresh_undo_actions'])

def test_add_transaction():
    # Adding a transaction causes a refresh_undo_actions() gui call and the main window status line.
    app = app_cleared_gui_calls()
    app.show_tview()
    app.clear_gui_calls()
    app.ttable.add()
    app.ttable[0].description = 'foobar'
    app.ttable.save_edits()
    app.check_gui_calls(app.mainwindow_gui, ['refresh_undo_actions', 'refresh_status_line'])

@with_app(app_cleared_gui_calls)
def test_change_column_visibility(app):
    # Changing the visibility option of a column calls the table's gui to actually hide the thing.
    app.show_tview()
    app.set_column_visible('description', False)
    app.ttable.columns.view.check_gui_calls(['set_column_visible'])
    # Also works for sheets
    app.show_nwview()
    app.set_column_visible('delta', True)
    app.bsheet.columns.view.check_gui_calls(['set_column_visible'])

def test_change_default_currency():
    # When the default currency is changed, all gui refresh themselves
    app = app_cleared_gui_calls()
    app.show_nwview()
    app.doc.default_currency = EUR
    app.check_gui_calls(app.bsheet_gui, ['refresh'])
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])
    app.check_gui_calls(app.nwview.pie.view, ['refresh'])
    # but not if it stays the same
    app.doc.default_currency = EUR
    app.check_gui_calls_partial(app.bsheet_gui, not_expected=['refresh'])

@with_app(app_cleared_gui_calls)
def test_mainwindow_move_pane(app):
    # Moving a pane in the mainwindow calls refresh_panes on the view.
    app.mw.move_pane(0, 1)
    app.mainwindow_gui.check_gui_calls(['refresh_panes'])

def test_new_budget():
    # Repeat options must be updated upon panel load
    app = app_cleared_gui_calls()
    app.add_account('income', account_type=AccountType.Income) # we need an account for the panel to load
    app.show_bview()
    app.mw.new_item()
    app.bpanel.repeat_type_list.view.check_gui_calls_partial(['refresh'])

def test_new_schedule():
    # Repeat options and mct notices must be updated upon panel load
    app = app_cleared_gui_calls()
    app.show_scview()
    app.mw.new_item()
    app.scpanel.repeat_type_list.view.check_gui_calls_partial(['refresh'])

@with_app(app_cleared_gui_calls)
def test_select_mainwindow_next_previous_view(app):
    app.mw.select_next_view()
    app.check_gui_calls(app.mainwindow_gui, ['change_current_pane', 'refresh_status_line'])
    app.mw.select_previous_view()
    app.check_gui_calls(app.mainwindow_gui, ['change_current_pane', 'refresh_status_line'])

def test_show_transaction_table():
    # main window's status is refreshed upon showing.
    app = app_cleared_gui_calls()
    app.show_tview()
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

def test_sort_table():
    # sorting a table refreshes it.
    app = app_cleared_gui_calls()
    app.show_tview()
    app.clear_gui_calls()
    app.ttable.sort_by('description')
    app.check_gui_calls(app.ttable_gui, ['refresh'])

def test_ttable_add_and_cancel():
    # gui calls on the ttable are correctly made
    app = app_cleared_gui_calls()
    app.show_tview()
    app.clear_gui_calls()
    app.ttable.add()
    # stop_editing must happen first
    expected = ['stop_editing', 'refresh', 'start_editing']
    app.check_gui_calls(app.ttable_gui, expected, verify_order=True)
    app.ttable.cancel_edits()
    # again, stop_editing must happen first
    expected = ['stop_editing', 'refresh']
    app.check_gui_calls(app.ttable_gui, expected, verify_order=True)

@with_app(app_cleared_gui_calls)
def test_save_custom_range(app):
    # Saving a custom range causes the date range selector's view to refresh them.
    app.drsel.select_custom_date_range()
    app.cdrpanel.slot_index = 1
    app.cdrpanel.slot_name = 'foo'
    app.cdrpanel.save()
    app.drsel.view.check_gui_calls(['refresh_custom_ranges', 'refresh'])

def test_show_account():
    # on show_account() status line is refreshed
    app = app_cleared_gui_calls()
    app.add_account()
    app.clear_gui_calls()
    app.show_account()
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

@with_app(app_cleared_gui_calls)
def test_stop_editing_on_applying_filter(app):
    # Applying a filter on the filter bar stops table editing.
    tview = app.show_tview()
    app.clear_gui_calls()
    tview.filter_bar.filter_type = FilterType.Income
    tview.ttable.view.check_gui_calls_partial(['stop_editing'])

#--- On transaction view
def app_on_transaction_view():
    app = TestApp()
    app.show_tview()
    app.clear_gui_calls()
    return app

def test_changing_date_range_refreshes_transaction_totals():
    # totals label should be refreshed when the date range changes
    app = app_on_transaction_view()
    app.drsel.select_quarter_range()
    app.check_gui_calls(app.mainwindow_gui, ['refresh_status_line'])

@with_app(app_on_transaction_view)
def test_stop_editing_on_pane_change(app):
    # To avoid buggy editing (for example, #283), stop all editing before a pane switch occurs.
    app.mw.select_next_view()
    app.check_gui_calls_partial(app.ttable_gui, ['stop_editing'])

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account('foobar')
    app.show_account()
    app.clear_gui_calls()
    return app
    
def test_add_entry():
    # Before adding a new entry, make sure the entry table is not in edition mode. Then, start 
    # editing the new entry. Adding an entry also refreshes account totals.
    app = app_one_account()
    app.add_entry()
    app.check_gui_calls_partial(app.etable_gui, ['stop_editing', 'refresh', 'start_editing'])
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

def test_change_aview_filter():
    # Changing aview's filter type updates the totals
    app = app_one_account()
    app.efbar.filter_type = FilterType.Reconciled
    app.check_gui_calls(app.mainwindow_gui, ['refresh_status_line'])

def test_changing_date_range_refreshes_account_totals():
    # totals label should be refreshed when the date range changes
    app = app_one_account()
    app.drsel.select_quarter_range()
    app.check_gui_calls(app.mainwindow_gui, ['refresh_status_line'])

def test_delete_entry():
    app = app_one_account()
    app.add_entry()
    app.clear_gui_calls()
    app.mainwindow.delete_item()
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

@with_app(app_one_account)
def test_edit_account(app):
    app.show_nwview()
    app.mw.edit_item() # apanel popping up
    # Popping the panel refreshes the type list selection
    app.apanel.type_list.view.check_gui_calls(['update_selection'])

def test_jump_to_account():
    app = app_one_account()
    app.mainwindow.jump_to_account()
    app.alookup.view.check_gui_calls(['refresh', 'show'])
    app.alookup.search_query = 'foo'
    app.alookup.view.check_gui_calls(['refresh'])
    app.alookup.go()
    app.alookup.view.check_gui_calls(['hide'])

@with_app(app_one_account)
def test_export_panel(app):
    app.mw.export()
    app.expanel.view.check_gui_calls_partial(['set_table_enabled'])
    app.expanel.export_all = False
    # We enable the table, and because there's no account selected, we disable the export button
    app.expanel.view.check_gui_calls(['set_table_enabled', 'set_export_button_enabled'])    
    app.expanel.account_table[0].export = True
    app.expanel.view.check_gui_calls(['set_export_button_enabled'])    

#--- One transaction
def app_one_transaction():
    app = TestApp()
    app.add_txn()
    app.clear_gui_calls()
    return app

@with_app(app_one_transaction)
def test_delete_transaction(app):
    # Deleting a transaction refreshes the totals label
    app.mw.delete_item()
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

@with_app(app_one_transaction)
def test_change_tview_filter(app):
    # Changing tview's filter type updates the totals
    app.tfbar.filter_type = FilterType.Reconciled
    app.check_gui_calls_partial(app.mainwindow_gui, ['refresh_status_line'])

#--- Load file with balance sheet selected
def app_load_file_with_bsheet_selected():
    app = TestApp()
    app.show_nwview()
    app.clear_gui_calls()
    app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
    return app

@with_app(app_load_file_with_bsheet_selected)
def test_views_are_refreshed(app):
    # view.refresh() is called on file load
    app.check_gui_calls_partial(app.bsheet_gui, ['refresh'])
    app.check_gui_calls_partial(app.nwgraph_gui, ['refresh'])

#--- Transaction between income and expense
def app_transaction_between_income_and_expense():
    app = TestApp()
    app.add_account('income', account_type=AccountType.Income)
    app.add_account('expense', account_type=AccountType.Expense)
    app.add_txn(from_='income', to='expense', amount='42')
    app.clear_gui_calls()
    return app

@with_app(app_transaction_between_income_and_expense)
def test_etable_show_income_account(app):
    # show_transfer_account() correctly refreshes the gui even if the graph type doesn't change.
    income_aview = app.show_account('income')
    app.clear_gui_calls()
    app.etable.show_transfer_account()
    app.link_aview()
    income_aview.etable.view.check_gui_calls(['stop_editing'])
    app.etable.view.check_gui_calls(['update_selection', 'show_selected_row', 'refresh'])
    app.bargraph.view.check_gui_calls(['refresh'])

#--- Transaction between asset and liability
def app_transaction_between_asset_and_liability():
    app = TestApp()
    app.add_account('asset', account_type=AccountType.Asset)
    app.add_account('liability', account_type=AccountType.Liability)
    app.add_txn(from_='liability', to='asset', amount='42')
    app.clear_gui_calls()
    return app

@with_app(app_transaction_between_asset_and_liability)
def test_etable_show_asset_account(app):
    # show_transfer_account() correctly refreshes the gui even if the graph type doesn't change.
    asset_aview = app.show_account('asset')
    app.clear_gui_calls()
    app.etable.show_transfer_account()
    app.link_aview()
    asset_aview.etable.view.check_gui_calls(['stop_editing'])
    app.etable.view.check_gui_calls(['update_selection', 'show_selected_row', 'refresh'])
    app.balgraph.view.check_gui_calls(['refresh'])

#--- Transaction with panel loaded
def app_transaction_with_panel_loaded():
    app = TestApp()
    app.add_txn('20/02/2010', from_='foo', to='bar', amount='42')
    app.tpanel.load()
    app.clear_gui_calls()
    return app

def test_move_split():
    # The split table is refreshed after a move
    app = app_transaction_with_panel_loaded()
    app.stable.move_split(0, 1)
    app.stable.view.check_gui_calls_partial(['refresh'])

#--- Completable edit
def app_completable_edit():
    app = TestApp()
    app.add_txn(description='Bazooka')
    app.add_txn(description='buz')
    app.add_txn(description='bar')
    app.add_txn(description='foo')
    app.ce = app.completable_edit('description')
    app.ce_gui = app.ce.view
    app.clear_gui_calls()
    return app

@with_app(app_completable_edit)
def test_cedit_set_text(app):
    # Setting the text of the cedit results in a refresh of the view
    app.ce.text = 'f'
    app.check_gui_calls(app.ce_gui, ['refresh'])

@with_app(app_completable_edit)
def test_cedit_set_text_no_completion(app):
    # Setting the text when there's no completion doesn't result in a refresh.
    app.ce.text = 'nomatch'
    app.check_gui_calls_partial(app.ce_gui, not_expected=['refresh'])

@with_app(app_completable_edit)
def test_cedit_up(app):
    # Pressing up() refreshes the view
    app.ce.text = 'b'
    app.clear_gui_calls()
    app.ce.up()
    app.check_gui_calls(app.ce_gui, ['refresh'])

@with_app(app_completable_edit)
def test_cedit_up_no_completion(app):
    # Pressing up() when there's no completion doesn't result in a refresh
    app.ce.up()
    app.check_gui_calls_partial(app.ce_gui, not_expected=['refresh'])

@with_app(app_completable_edit)
def test_cedit_commit_partial_value(app):
    # Commiting when the text is a partial value of the completion results in a view refresh
    app.ce.text = 'b'
    app.clear_gui_calls()
    app.ce.commit()
    app.check_gui_calls(app.ce_gui, ['refresh'])

@with_app(app_completable_edit)
def test_cedit_commit_complete_value(app):
    # Commiting when cedit's text is the whole completion doesn't result in a refresh.
    app.ce.text = 'bazooka'
    app.clear_gui_calls()
    app.ce.commit()
    app.check_gui_calls_partial(app.ce_gui, not_expected=['refresh'])

@with_app(app_completable_edit)
def test_cedit_lookup_and_select(app):
    # When selecting a value through the completion lookup, the edit view is refreshed.
    app.ce.lookup()
    app.clookup.go()
    app.check_gui_calls(app.ce_gui, ['refresh'])