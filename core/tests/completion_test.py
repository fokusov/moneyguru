# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.testutil import eq_

from .base import TestApp, with_app
from ..model.account import AccountType

# a little helper that creates a completable edit, sets the text and returns the completion
def complete_table(target_table, value, attrname):
    ce = target_table.completable_edit
    ce.attrname = attrname
    ce.text = value
    return ce.completion

def complete_etable(app, value, attrname):
    return complete_table(app.aview.etable, value, attrname)

def assert_completion(app, s, expected):
    eq_(complete_etable(app, s, 'transfer'), expected)

# ---
def test_complete_transfer_one_empty_account():
    # Don't lookup the selected account for transfer completion.
    app = TestApp()
    app.add_account('Checking')
    app.show_account()
    assert_completion(app, 'c', '')

def test_dont_complete_with_inactive_accounts():
    # Inactive accounts don't show in in auto-completion. ref #412
    app = TestApp()
    app.add_account('inactive', inactive=True)
    tview = app.show_tview()
    eq_(complete_table(tview.ttable, 'i', 'from'), '')

# --- Empty account with whitespace in name
def app_empty_account_with_whitespace_in_name(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account('  Foobar  ')
    app.add_account('foobaz')
    app.show_account()
    return app

@with_app(app_empty_account_with_whitespace_in_name)
def test_complete_transfer_empty_account_with_whitespace_in_name(app):
    # transfer completion looking up account names ignores whitespaces (and case).
    assert_completion(app, 'f', 'oobar')

# --- Three empty accounts
def app_three_empty_accounts(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account('one')
    app.add_account('two')
    app.add_account('three') # This is the selected account (in second position)
    app.show_account()
    return app

@with_app(app_three_empty_accounts)
def test_complete_transfer_three_empty_accounts(app):
    # When no entry match for transfer completion, lookup in accounts.
    assert_completion(app, 'o', 'ne')

@with_app(app_three_empty_accounts)
def test_complete_empty_transfer(app):
    # Don't complete an empty transfer.
    eq_(complete_etable(app, '', 'transfer'), '')

@with_app(app_three_empty_accounts)
def test_complete_description(app):
    # description completion does *not* look into accounts.
    eq_(complete_etable(app, 'o', 'description'), '')

# --- Income account shown
def app_income_account_shown(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account('foobar', account_type=AccountType.Income)
    app.show_account()
    return app

@with_app(app_income_account_shown)
def test_complete_transfer_income_account_shown(app):
    # Ignore selected account in completion in cases where non-asset accounts are shown as well.
    assert_completion(app, 'f', '')

# --- Different account types
def app_different_account_types(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account('income', account_type=AccountType.Income)
    app.add_account('asset')
    app.show_account()
    return app

@with_app(app_different_account_types)
def test_complete_transfer_different_account_types(app):
    # Complete transfer with non-asset categories as well.
    assert_completion(app, 'in', 'come')

# --- Entry in editing mode
def app_entry_in_editing_mode(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account()
    app.show_account()
    app.etable.add()
    row = app.etable.edited
    row.date = '1/10/2007'
    row.description = 'foobar'
    row.increase = '42'
    return app

@with_app(app_entry_in_editing_mode)
def test_complete(app):
    # Don't make completion match with the edited entry.
    eq_(complete_etable(app, 'foo', 'description'), '')

# --- One entry
def app_one_entry(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account('Checking')
    app.show_account()
    app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42')
    return app

@with_app(app_one_entry)
def test_amount_completion_uses_the_latest_entered(app):
    # Even if the date is earlier, we use this newly added entry because it's the latest modified.
    app.add_entry('9/10/2007', 'Deposit', increase='12.34')
    app.etable.add()
    row = app.etable.edited
    row.date = '11/10/2007'
    row.description = 'Deposit'
    eq_(app.etable[app.etable.selected_indexes[0]].increase, '12.34')

@with_app(app_one_entry)
def test_autofill_column_selection_for_description(app):
    # Hidden columns are not autofilled
    app.set_column_visible('payee', False)
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'Deposit'
    eq_(app.etable[1].payee, '')

@with_app(app_one_entry)
def test_autofill_convert_amount_field(app):
    # autofill_columns can be given 'increase' and 'decrease'. It will all be converted into
    # 'amount'.
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'Deposit'
    eq_(app.etable[1].increase, '42.00')

@with_app(app_one_entry)
def test_complete_case_insensitive(app):
    # The completion matching is case insensitive.
    eq_(complete_etable(app, 'de', 'description'), 'posit')
    eq_(complete_etable(app, 'dE', 'description'), 'posit')

@with_app(app_one_entry)
def test_complete_exact(app):
    # Exact match doesn't complete anything
    eq_(complete_etable(app, 'Deposit', 'description'), '')

@with_app(app_one_entry)
def test_complete_goes_to_next(app):
    # As soon as a completion gets longer than the matched entry, find another one.
    app.add_entry('1/10/2007', description='Dep')
    eq_(complete_etable(app, 'De', 'description'), 'p')
    eq_(complete_etable(app, 'Depo', 'description'), 'sit')

@with_app(app_one_entry)
def test_complete_latest_modified(app):
    # Always search the latest modified entries first for completion match.
    app.add_entry('31/10/2007', 'DepositFoo')
    eq_(complete_etable(app, 'De', 'description'), 'positFoo')
    app.etable.delete()
    eq_(complete_etable(app, 'De', 'description'), 'posit')

@with_app(app_one_entry)
def test_complete_partial(app):
    # Partial match returns the attribute of the matched entry.
    eq_(complete_etable(app, 'Dep', 'description'), 'osit')

@with_app(app_one_entry)
def test_complete_other_attr_yields_different_result(app):
    # complete() can do completion on more than one attribute.
    eq_(complete_etable(app, 'sal', 'transfer'), 'ary')

@with_app(app_one_entry)
def test_field_completion_is_case_sensitive(app):
    # When the case of a description/transfer value does not match an entry, completion do not
    # occur.
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'deposit'
    row.transfer = 'deposit'
    eq_(app.etable[app.etable.selected_indexes[0]].increase, '')

@with_app(app_one_entry)
def test_field_completion_on_set_entry_transfer(app):
    # Setting a transfer autocompletes the amount and the description.
    app.set_column_visible('payee', True)
    app.etable.columns.move_column('transfer', 0)
    app.etable.add()
    row = app.etable.selected_row
    row.transfer = 'Salary'
    selected = app.etable.selected_indexes[0]
    eq_(app.etable[selected].increase, '42.00')
    eq_(app.etable[selected].description, 'Deposit')
    eq_(app.etable[selected].payee, 'Payee')

@with_app(app_one_entry)
def test_field_completion_on_set_entry_description(app):
    # Setting a description autocompletes the amount and the transfer.
    app.set_column_visible('payee', True)
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'Deposit'
    selected = app.etable.selected_indexes[0]
    eq_(app.etable[selected].increase, '42.00')
    eq_(app.etable[selected].transfer, 'Salary')
    eq_(app.etable[selected].payee, 'Payee')

@with_app(app_one_entry)
def test_field_completion_on_set_entry_payee(app):
    # Setting a transfer autocompletes the amount and the description.
    app.etable.columns.move_column('payee', 0)
    app.etable.add()
    row = app.etable.selected_row
    row.payee = 'Payee'
    selected = app.etable.selected_indexes[0]
    eq_(app.etable[selected].increase, '42.00')
    eq_(app.etable[selected].description, 'Deposit')
    eq_(app.etable[selected].transfer, 'Salary')

@with_app(app_one_entry)
def test_dont_complete_with_inactive_account_with_transactions(app):
    # Make sure that we don't complete inactive accounts with transactions. We would previously
    # have a cache glitch in the case we made an existing account with txns inactive.
    # This first check is to populate the completion cache
    tview = app.show_tview()
    eq_(complete_table(tview.ttable, 's', 'from'), 'alary')
    app.select_account('Salary')
    app.change_selected_account(inactive=True)
    tview = app.show_tview()
    eq_(complete_table(tview.ttable, 's', 'from'), '')

# --- Entry with blank description
def app_entry_with_blank_description(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account()
    app.show_account()
    app.add_entry('10/10/2007', description='', transfer='Salary', increase='42')
    return app

@with_app(app_entry_with_blank_description)
def test_field_completion_on_description(app):
    # Don't do a field completion on blank values.
    app.etable.add()
    row = app.etable.selected_row
    row.description = ''
    selected = app.etable.selected_indexes[0]
    eq_(app.etable[selected].transfer, '')
    eq_(app.etable[selected].increase, '')
    eq_(app.etable[selected].decrease, '')

@with_app(app_entry_with_blank_description)
def test_complete_empty_string(app):
    # complete() always returns nothing on empty strings.
    eq_(complete_etable(app, '', 'description'), '')

# --- Entry with whitespace in description
def app_entry_with_whitespace_in_description(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account()
    app.show_account()
    app.add_entry('10/10/2007', description='  foobar  ', increase='1')
    return app

@with_app(app_entry_with_whitespace_in_description)
def test_completion_ignore_whitespaces(app):
    # Don't complete string based on whitespaces.
    eq_(complete_etable(app, ' ', 'description'), '')

@with_app(app_entry_with_whitespace_in_description)
def test_completion_strip_whitespace(app):
    # Ignore whitespace when finding a completion match.
    eq_(complete_etable(app, 'foo', 'description'), 'bar')

# --- Two entries
def app_two_entries(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account()
    app.show_account()
    app.add_entry('2/10/2007', 'first', increase='102.00')
    app.add_entry('4/10/2007', 'second', increase='42.00')
    app.etable.select([0])
    return app

@with_app(app_two_entries)
def test_amount_completion(app):
    # Upon setting description, set the amount to the amount of the first matching entry with
    # the same description.
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'first'
    eq_(app.etable[app.etable.selected_indexes[0]].increase, '102.00')

@with_app(app_two_entries)
def test_amount_completion_already_set(app):
    # If the amount is already set, don't complete it.
    row = app.etable.selected_row
    row.description = 'second'
    eq_(app.etable[app.etable.selected_indexes[0]].increase, '102.00')

# --- Three entries in two account types
def app_three_entries_in_two_account_types(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_account()
    app.show_account()
    app.add_entry(description='first')
    app.add_entry(description='second')
    app.add_account()
    app.show_account()
    app.add_entry(description='third') # selected
    return app

@with_app(app_three_entries_in_two_account_types)
def test_completion_from_other_accounts_show_up(app):
    # Even in the entry table, completion from other accounts show up
    eq_(complete_etable(app, 'f', 'description'), 'irst')

# --- Four entries with description and category collision
def app_four_entries_with_description_and_category_collision(monkeypatch):
    # Four entries. Mostly for completion, I can't see any other use. The first is a 'booby trap'.
    # (simply having the completion iterate the list made all tests pass). The second is the base
    # entry. The third has the same description but a different transfer. The fourth has a different
    # transfer but the same description. All have different amounts and dates. Second entry is
    # selected. Also, time.time() is mocked so that the time of the setUp is earlier than the time
    # of the tests.
    app = TestApp()
    app.add_account()
    app.show_account()
    # We call patch_time_ticking so that mtime are correctly used as an ordering key. force_int_diff
    # is because we record mtime as integers in the save file and there's a test below testing the
    # persistence of orders.
    monkeypatch.patch_time_ticking(force_int_diff=True)
    app.add_entry('2/10/2007', description='description', payee='payee', transfer='category', increase='42')
    app.add_entry('3/10/2007', description='desc1', payee='pay1', transfer='cat1', increase='1')
    app.add_entry('4/10/2007', description='desc1', payee='pay1', transfer='cat2', increase='2')
    app.add_entry('5/10/2007', description='desc2', payee='pay1', transfer='cat1', increase='3')
    app.etable.select([1])
    return app

def assert_completion_order_changed(app):
    # complete() returns descriptions for the second entry, and field completion also is based
    # on the second entry.
    app.set_column_visible('payee', True)
    eq_(complete_etable(app, 'd', 'description'), 'esc1')
    eq_(complete_etable(app, 'c', 'transfer'), 'at1')
    eq_(complete_etable(app, 'p', 'payee'), 'ay1')
    app.etable.columns.move_column('description', 0)
    app.etable.add()
    row = app.etable.selected_row
    row.description = 'desc1'
    eq_(app.etable[app.etable.selected_indexes[0]].payee, 'pay1')
    eq_(app.etable[app.etable.selected_indexes[0]].transfer, 'cat1')
    app.etable.columns.move_column('transfer', 0)
    app.etable.add()
    row = app.etable.selected_row
    row.transfer = 'cat1'
    eq_(app.etable[app.etable.selected_indexes[0]].description, 'desc1')
    eq_(app.etable[app.etable.selected_indexes[0]].payee, 'pay1')
    app.etable.columns.move_column('payee', 0)
    app.etable.add()
    row = app.etable.selected_row
    row.payee = 'pay1'
    eq_(app.etable[app.etable.selected_indexes[0]].description, 'desc1')
    eq_(app.etable[app.etable.selected_indexes[0]].transfer, 'cat1')

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_transfer_changes_completion_list_order(app):
    # A transfer edit on the second entry makes it the first candidate for completion.
    row = app.etable.selected_row
    row.transfer = 'cat12'
    app.etable.save_edits()
    row = app.etable.selected_row
    row.transfer = 'cat1'
    app.etable.save_edits()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_credit_changes_completion_list_order(app):
    # A credit edit on the second entry makes it the first candidate for completion.
    row = app.etable.selected_row
    row.decrease = '1'
    app.etable.save_edits()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_date_changes_completion_list_order(app):
    # A date edit on the second entry makes it the first candidate for completion.
    row = app.etable.selected_row
    row.date = '2/10/2007'
    app.etable.save_edits()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_debit_changes_completion_list_order(app):
    # A debit edit on the second entry makes it the first candidate for completion.
    row = app.etable.selected_row
    row.increase = '8'
    app.etable.save_edits()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_description_changes_completion_list_order(app):
    # A description edit on the second entry makes it the first candidate for completion.
    row = app.etable.selected_row
    row.description = 'other desc' # Make sure that edition takes place
    row.description = 'desc1'
    app.etable.save_edits()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_edit_ttable_changes_completion_list_order(app):
    # Changing a txn in the ttable updates the mtime
    app.show_tview()
    app.ttable.selected_row.amount = '1'
    app.ttable.save_edits()
    app.show_aview()
    assert_completion_order_changed(app)

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_after_description(app):
    # next_completion() after a complete_description() returns the next matching description.
    ce = app.completable_edit('description')
    ce.text = 'd' # completion: esc2
    ce.up()
    eq_(ce.completion, 'escription')

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_after_null_completion(app):
    # After a completion that returns nothing, next_completion() just returns None.
    ce = app.completable_edit('description')
    ce.text = 'nothing' # completion: none
    ce.up()
    eq_(ce.completion, '')

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_after_transfer(app):
    # next_completion() after a complete_transfer() returns the next matching transfer.
    ce = app.completable_edit('transfer')
    ce.text = 'c' # completion: at1
    ce.up()
    eq_(ce.completion, 'ategory')

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_rollover(app):
    # next_completion() 3 times rolls over.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.up()
    ce.up()
    ce.up()
    eq_(ce.completion, 'esc2')

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_rollover_plus_one(app):
    # An easy way out for all the other tests was to use negative indexing. But it stops
    # working here.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.up()
    ce.up()
    ce.up()
    ce.up()
    eq_(ce.completion, 'escription')

@with_app(app_four_entries_with_description_and_category_collision)
def test_next_completion_twice(app):
    # next_completion() twice returns the second next completion, skipping duplicates.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.up()
    ce.up()
    eq_(ce.completion, 'esc1')

@with_app(app_four_entries_with_description_and_category_collision)
def test_previous_completion_after_description(app):
    # previous_completion() after a complete_description() returns the previous matching
    # description.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.down()
    eq_(ce.completion, 'esc1')

@with_app(app_four_entries_with_description_and_category_collision)
def test_previous_completion_after_null_completion(app):
    # After a completion that returns nothing, previous_completion() just returns None.
    ce = app.completable_edit('description')
    ce.text = 'nothing'
    ce.down()
    eq_(ce.completion, '')

@with_app(app_four_entries_with_description_and_category_collision)
def test_previous_completion_after_transfer(app):
    # previous_completion() after a complete_transfer() returns the previous matching transfer.
    ce = app.completable_edit('transfer')
    ce.text = 'c' # caompletion: at1
    ce.down()
    eq_(ce.completion, 'at2')

@with_app(app_four_entries_with_description_and_category_collision)
def test_previous_completion_rollover(app):
    # previous_completion() 3 times rolls over.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.down()
    ce.down()
    ce.down()
    eq_(ce.completion, 'esc2')

@with_app(app_four_entries_with_description_and_category_collision)
def test_previous_completion_twice(app):
    # previous_completion() twice returns the second previous completion, skipping duplicates.
    ce = app.completable_edit('description')
    ce.text = 'd'
    ce.down()
    ce.down()
    eq_(ce.completion, 'escription')

@with_app(app_four_entries_with_description_and_category_collision)
def test_persistence_of_completion(app, tmpdir, monkeypatch):
    # Completion (including its order) is persistent.
    row = app.etable.selected_row
    row.transfer = 'cat12'
    app.etable.save_edits()
    row = app.etable.selected_row
    row.transfer = 'cat1'
    app.etable.save_edits()
    filepath = str(tmpdir.join('foo.xml'))
    app.doc.save_to_xml(filepath)
    app = TestApp()
    app.add_txn(description='Duh, that shouldn\'t be here!')
    app.doc.load_from_xml(filepath)
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.show_account()
    assert_completion_order_changed(app)

# --- Account created through transaction table
def app_account_created_through_transaction_table(monkeypatch):
    app = TestApp()
    monkeypatch.patch_time_ticking()
    app.add_txn(from_='foo', to='bar', amount='42')
    app.ttable.show_from_account()
    app.link_aview()
    return app

@with_app(app_account_created_through_transaction_table)
def test_complete_transfer_account_created_through_transaction_table(app):
    # Completion correctly excludes shown account on the transfer column. Previously,
    # selected_account was used instead of shown_account.
    assert_completion(app, 'f', '')

