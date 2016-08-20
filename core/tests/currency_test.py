# Created By: Virgil Dupras
# Created On: 2008-06-22
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from datetime import date
import threading
import os.path as op

from hscommon.testutil import eq_, log_calls

from ..app import Application
from ..model import currency
from ..model.account import AccountType
from ..model.currency import Currency, USD, EUR, CAD
from ..model.date import MonthRange
from .base import ApplicationGUI, TestApp, with_app, compare_apps
from .model.currency_test import set_ratedb_for_tests


def pytest_funcarg__fake_server(request):
    set_ratedb_for_tests()

# --- Pristine
def test_cache_path_is_auto_created(fake_server, tmpdir):
    # the cache_path directory is automatically created.
    cache_path = str(tmpdir.join('foo/bar'))
    Application(ApplicationGUI(), cache_path=cache_path)
    assert op.exists(cache_path)

def test_cache_path_is_none(fake_server, monkeypatch):
    # currency.initialize_db() is called with :memory: when cache_path is None.
    monkeypatch.setattr(currency, 'initialize_db', log_calls(currency.initialize_db))
    Application(ApplicationGUI()) # default cache_path is None
    expected = [
        {'path': ':memory:'}
    ]
    eq_(currency.initialize_db.calls, expected)

def test_cache_path_is_not_none(fake_server, monkeypatch, tmpdir):
    # currency.initialize_db() is called with cache_path/currency.db when cache_path is not None.
    cache_path = str(tmpdir)
    monkeypatch.setattr(currency, 'initialize_db', log_calls(currency.initialize_db))
    Application(ApplicationGUI(), cache_path=cache_path)
    expected = [
        {'path': op.join(cache_path, 'currency.db')}
    ]
    eq_(currency.initialize_db.calls, expected)

def test_default_currency(fake_server):
    # It's possible to specify a default currency at startup.
    PLN = Currency(code='PLN')
    app = TestApp(app=Application(ApplicationGUI(), default_currency=PLN))
    app.show_tview()
    eq_(app.doc.default_currency, PLN)
    app.add_account()
    eq_(app.doc.default_currency, PLN)

@with_app(TestApp)
def test_set_account_list_currency_on_load(app, fake_server):
    # Document.account.default_currency wasn't previously set on document loading which caused
    # auto-created accounts to be of the wrong currency.
    dpview = app.show_dpview()
    dpview.currency_list.select(1) # EUR
    app = app.save_and_load()
    app.add_txn(from_='foo', amount='12')
    pview = app.show_pview()
    # Because our amount entered earlier is native, we shouldn't get stuff like "USD 15.76"
    eq_(pview.istatement.income[0].cash_flow, '12.00')

# --- One empty account EUR
def app_one_empty_account_eur(monkeypatch):
    monkeypatch.patch_today(2008, 5, 25)
    app = TestApp()
    app.add_account('Checking', EUR)
    app.show_account()
    app.doc.date_range = MonthRange(date(2007, 10, 1))
    return app

@with_app(app_one_empty_account_eur)
def test_add_entry_with_foreign_amount(app):
    # Saving an entry triggers an ensure_rates.
    db, log = set_ratedb_for_tests()
    app.add_entry('20/5/2008', increase='12 usd')
    # A request is made for both the amount that has just been written and the account of the entry
    expected = {
        (date(2008, 5, 20), date(2008, 5, 24), 'USD'),
        (date(2008, 5, 20), date(2008, 5, 24), 'EUR'),
    }
    eq_(set(log), expected)

@with_app(app_one_empty_account_eur)
def test_add_transaction_with_foreign_amount(app):
    # Saving an entry triggers an ensure_rates
    db, log = set_ratedb_for_tests()
    app.show_tview()
    app.ttable.add()
    app.ttable.edited.date = '20/5/2008'
    app.ttable.edited.amount = '12 eur'
    app.ttable.save_edits()
    # A request is made for both the amount that has just been written and the account of the entry
    expected = {
        (date(2008, 5, 20), date(2008, 5, 24), 'EUR'),
        (date(2008, 5, 20), date(2008, 5, 24), 'USD'),
    }
    eq_(set(log), expected)

class TestCaseCADAssetAndUSDAsset:
    def setup_method(self, method):
        app = TestApp()
        app.add_account('CAD Account', CAD)
        app.add_account('USD Account', USD)
        app.show_account()
        self.app = app

    def test_make_amount_native(self, fake_server):
        # Making an amount native when the both sides are asset/liability creates a MCT
        # First, let's add a 'native' transaction
        app = self.app
        app.add_entry(transfer='CAD Account', increase='42 usd')
        # Then, make the other side 'native'
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        row = app.etable.selected_row
        row.decrease = '40 cad'
        app.etable.save_edits()
        # The other side should have *not* followed
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        eq_(app.etable[0].increase, '42.00')


class TestCaseCADLiabilityAndUSDLiability:
    def setup_method(self, method):
        app = TestApp()
        app.add_account('CAD Account', CAD, account_type=AccountType.Liability)
        app.add_account('USD Account', USD, account_type=AccountType.Liability)
        app.show_account()
        self.app = app

    def test_make_amount_native(self, fake_server):
        # Making an amount native when the both sides are asset/liability creates a MCT
        # First, let's add a 'native' transaction
        app = self.app
        app.add_entry(transfer='CAD Account', increase='42 usd')
        # Then, make the other side 'native'
        app.show_nwview()
        app.bsheet.selected = app.bsheet.liabilities[0]
        app.show_account()
        row = app.etable.selected_row
        row.decrease = '40 cad'
        app.etable.save_edits()
        # The other side should have *not* followed
        app.show_nwview()
        app.bsheet.selected = app.bsheet.liabilities[1]
        app.show_account()
        eq_(app.etable[0].increase, '42.00')


# --- Entry with foreign currency
# 2 accounts (including one income), one entry. The entry has an amount that differs from the
# account's currency.
def app_entry_with_foreign_currency():
    PLN = Currency(code='PLN')
    app = TestApp()
    EUR.set_CAD_value(1.42, date(2007, 10, 1))
    PLN.set_CAD_value(0.42, date(2007, 10, 1))
    app.add_account('first', CAD)
    app.add_account('second', PLN, account_type=AccountType.Income)
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.show_account()
    app.add_entry(date='1/10/2007', transfer='second', increase='42 eur')
    app.doc.date_range = MonthRange(date(2007, 10, 1))
    return app

def test_bar_graph_data():
    # The amount shown in the bar graph is a converted amount.
    app = app_entry_with_foreign_currency()
    app.show_pview()
    app.istatement.selected = app.istatement.income[0]
    app.show_account()
    eq_(app.bar_graph_data(), [('01/10/2007', '08/10/2007', '%2.2f' % ((42 * 1.42) / 0.42), '0.00')])

def test_change_currency_from_income_account():
    # Changing an amount to another currency from the perspective of an income account doesn't
    # create an MCT.
    app = app_entry_with_foreign_currency()
    app.show_account() # now on the other side
    app.etable[0].increase = '12pln'
    app.etable.save_edits()
    app.show_account()
    eq_(app.etable[0].increase, 'PLN 12.00')

def test_ensures_rates(tmpdir, fake_server, monkeypatch):
    # Upon calling save and load, rates are asked for both EUR and PLN.
    app = app_entry_with_foreign_currency()
    rates_db = Currency.get_rates_db()
    monkeypatch.setattr(rates_db, 'ensure_rates', log_calls(rates_db.ensure_rates))
    filename = str(tmpdir.join('foo.xml'))
    app.doc.save_to_xml(filename)
    app.doc.load_from_xml(filename)
    calls = rates_db.ensure_rates.calls
    eq_(len(calls), 1)
    eq_(set(calls[0]['currencies']), set(['PLN', 'EUR', 'CAD']))
    eq_(calls[0]['start_date'], date(2007, 10, 1))

def test_entry_balance():
    # The entry's balance is correctly incremented (using the exchange rate).
    app = app_entry_with_foreign_currency()
    eq_(app.etable[0].balance, 'CAD %2.2f' % (42 * 1.42))

def test_opposite_entry_balance():
    # The 'other side' of the entry also have its balance correctly computed.
    app = app_entry_with_foreign_currency()
    app.show_pview()
    app.istatement.selected = app.istatement.income[0]
    app.show_account()
    eq_(app.etable[0].balance, 'PLN %2.2f' % ((42 * 1.42) / 0.42))

class TestCaseCADAssetAndUSDIncome:
    def setup_method(self, method):
        app = TestApp()
        app.add_account('CAD Account', CAD)
        app.add_account('USD Income', USD, account_type=AccountType.Income)
        app.show_account()
        app.add_entry(transfer='CAD Account', increase='42 usd')
        self.app = app

    def test_make_amount_native(self, fake_server):
        # Making an amount native when the other side is an income/expense never creates a MCT
        # First, let's add a 'native' transaction
        # Then, make the asset side 'native'
        app = self.app
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        row = app.etable.selected_row
        row.increase = '40 cad'
        app.etable.save_edits()
        # The other side should have followed
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable[0].increase, 'CAD 40.00')


class TestCaseDifferentCurrencies:
    # 2 accounts. One with the default app currency and the other with another currency.
    # 2 transactions. One with the default currency and one with a different currency. Both
    # transaction have a transfer to the second account.
    def setup_method(self, method):
        app = TestApp(app=Application(ApplicationGUI(), default_currency=CAD))
        app.add_account('first account')
        app.add_account('second account', USD)
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        app.add_entry(description='first entry', transfer='second account', increase='42 usd')
        app.add_entry(description='second entry', transfer='second account', increase='42 eur')
        self.app = app

    def test_save_load(self, fake_server):
        # make sure currency information is correctly saved/loaded
        app = self.app
        newapp = app.save_and_load()
        newapp.doc.date_range = app.doc.date_range
        newapp.doc._cook()
        compare_apps(app.doc, newapp.doc)

    def test_entries_amount(self, fake_server):
        # All entries have the appropriate currency.
        app = self.app
        eq_(app.etable[0].increase, 'USD 42.00')
        eq_(app.etable[1].increase, 'EUR 42.00')
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        eq_(app.etable[0].decrease, 'USD 42.00')
        eq_(app.etable[1].decrease, 'EUR 42.00')


# --- Three currencies two entries
def app_three_currencies_two_entries(monkeypatch):
    # Three account of different currencies, and 2 entries on differenet date. The app is saved,
    # and then loaded (The goal of this is to test that moneyguru ensures it got the rates it needs).
    monkeypatch.patch_today(2008, 4, 30)
    theapp = Application(ApplicationGUI(), default_currency=CAD)
    app = TestApp(app=theapp)
    app.add_account('first account')
    app.add_account('second account', USD)
    app.add_account('third account', EUR)
    app.show_account('first account')
    app.add_entry(date='20/4/2008', increase='42 cad')
    app.add_entry(date='25/4/2008', increase='42 cad')
    return app

@with_app(app_three_currencies_two_entries)
def test_ensures_rates_multiple_currencies(app):
    # Upon calling save and load, rates are asked for the 20-today range for both USD and EUR.
    db, log = set_ratedb_for_tests()
    app.save_and_load()
    expected = {
        (date(2008, 4, 20), date(2008, 4, 29), 'USD'),
        (date(2008, 4, 20), date(2008, 4, 29), 'EUR'),
    }
    eq_(set(log), expected)
    # Now let's test that the rates are in the DB
    eq_(USD.value_in(CAD, date(2008, 4, 20)), 1.42)
    eq_(EUR.value_in(CAD, date(2008, 4, 22)), 1.44)
    eq_(EUR.value_in(USD, date(2008, 4, 24)), 1.0)
    eq_(USD.value_in(CAD, date(2008, 4, 25)), 1.47)
    eq_(USD.value_in(CAD, date(2008, 4, 27)), 1.49)

@with_app(app_three_currencies_two_entries)
def test_ensures_rates_async(app, monkeypatch):
    # ensure_rates() executes asynchronously
    # I can't think of any graceful way to test something like that, so I assume that if I make
    # the mocked get_CAD_values() to sleep for a little while, the next line after it in the test will
    # be executed first. If this test starts to fail randomly, we'll have to think about a better
    # way to test that (or increase the sleep time).
    rates_db, log = set_ratedb_for_tests(async=True, slow_down_provider=True)
    app.save_and_load()
    # This is a weird way to test that we don't have the rate yet. No need to import fallback
    # rates just for that.
    assert rates_db.get_rate(date(2008, 4, 20), 'USD', 'CAD') != 1.42
    for thread in threading.enumerate():
        if thread.getName() != 'MainThread' and thread.isAlive():
            thread.join(1)
    eq_(rates_db.get_rate(date(2008, 4, 20), 'USD', 'CAD'), 1.42)

# --- Multi-currency transaction
def app_multi_currency_transaction():
    app = TestApp()
    app.add_account('CAD Account', CAD)
    app.add_account('USD Account', USD)
    app.show_account()
    app.add_entry(transfer='CAD Account', increase='42 usd')
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.show_account()
    row = app.etable.selected_row
    row.decrease = '40 cad'
    app.etable.save_edits()
    return app

def test_add_imbalancing_split():
    # Adding a split making one of the two currencies balance, while leaving the rest all on
    # the same side makes moneyGuru rebalance this.
    app = app_multi_currency_transaction()
    tpanel = app.mw.edit_item()
    stable = tpanel.split_table
    stable.add()
    row = stable.selected_row
    row.credit = '42 usd'
    stable.save_edits() # Now we have CAD standing all alone
    eq_(len(stable), 4)
    eq_(stable[3].debit, 'CAD 40.00')

def test_set_entry_increase():
    # If we set up the CAD side to be an increase, the USD side must switch to decrease
    # It's not because we changed the amount here that the USD side will have something else than 42
    app = app_multi_currency_transaction()
    row = app.etable.selected_row
    row.increase = '12 cad'
    app.etable.save_edits()
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[1]
    app.show_account()
    eq_(app.etable[0].decrease, '42.00')

def test_set_split_to_logical_imbalance():
    # The first split is the USD entry (a debit). If we set it to be a credit instead, we end
    # up with both splits on the same side. We must create balancing splits.
    app = app_multi_currency_transaction()
    tpanel = app.mw.edit_item()
    stable = tpanel.split_table
    stable.add()
    stable[2].credit = '1 usd'
    stable.save_edits()
    stable[0].credit = '12 usd'
    stable.save_edits()
    eq_(len(stable), 4)
    expected = set(['12.00', 'CAD 40.00'])
    assert stable[2].debit in expected
    assert stable[3].debit in expected

class TestCaseEntryWithXPFAmount:
    def setup_method(self, method):
        XPF = Currency(code='XPF')
        app = TestApp()
        XPF.set_CAD_value(0.42, date(2009, 7, 20))
        app.add_account('account', CAD)
        app.show_account()
        app.add_entry('20/07/2009', increase='100 XPF')
        self.app = app

    def test_account_balance_is_correct(self, fake_server):
        # Because XPF has an exponent of 0, there was a bug where currency conversion wouldn't be
        # done correctly.
        eq_(self.app.etable[0].balance, 'CAD 42.00')

