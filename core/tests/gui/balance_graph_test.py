# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.testutil import eq_
from hscommon.currency import CAD

from ..base import TestApp, with_app
from ...model.account import AccountType

#--- Pristine
@with_app(TestApp)
def test_balgraph_yaxis_scaling_works_if_negative(app):
    # The y axis scaling (ymin being "higher" than 0) works when the balance is negative.
    app.add_account()
    app.show_account()
    app.add_entry('01/01/2010', decrease='1000')
    app.drsel.select_next_date_range()
    eq_(app.balgraph.ymax, -900)
    eq_(app.balgraph.ymin, -1100)

class TestTwoLiabilityTransactions:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account('Visa', account_type=AccountType.Liability)
        app.show_account()
        app.add_entry('3/1/2008', increase='120.00')
        app.add_entry('5/1/2008', decrease='40.00')
        return app
    
    @with_app(do_setup)
    def test_budget(self, app, monkeypatch):
        # when we add a budget, the balance graph will show a regular progression throughout date range
        monkeypatch.patch_today(2008, 1, 27)
        app.add_account('expense', account_type=AccountType.Expense)
        app.add_budget('expense', 'Visa', '100')
        app.show_nwview()
        app.bsheet.selected = app.bsheet.liabilities[0]
        app.show_account()
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), ('06/01/2008', '80.00'), 
            ('28/01/2008', '80.00'), ('01/02/2008', '180.00')]
        eq_(app.graph_data(), expected)
        app.drsel.select_next_date_range()
        eq_(app.graph_data()[0], ('01/02/2008', '180.00'))
    
    @with_app(do_setup)
    def test_budget_on_last_day_of_the_range(self, app, monkeypatch):
        # don't raise a ZeroDivizionError
        monkeypatch.patch_today(2008, 1, 31)
        app.add_account('expense', account_type=AccountType.Expense)
        app.add_budget('expense', 'Visa', '100')
        app.show_nwview()
        app.drsel.select_next_date_range()
    
    @with_app(do_setup)
    def test_budget_with_future_txn(self, app, monkeypatch):
        # when there's a future txn, we want the amount of that txn to be "sharply" displayed
        monkeypatch.patch_today(2008, 1, 15)
        app.add_entry('20/1/2008', decrease='10')
        app.add_account('expense', account_type=AccountType.Expense)
        app.add_budget('expense', 'Visa', '100')
        app.show_nwview()
        app.bsheet.selected = app.bsheet.liabilities[0]
        app.show_account()
        # the amount at the 20th is supposed to include budgeting for the 20th, and the 21st data point
        # has to include budget for the 21st
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), ('06/01/2008', '80.00'), 
            ('16/01/2008', '80.00'), ('20/01/2008', '105.00'), ('21/01/2008', '101.25'), ('01/02/2008', '170.00')]
        eq_(app.graph_data(), expected)
    
    @with_app(do_setup)
    def test_graph(self, app):
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'), 
                    ('06/01/2008', '80.00'), ('01/02/2008', '80.00')]
        eq_(app.graph_data(), expected)
        eq_(app.balgraph.title, 'Visa')
    

class TestForeignAccount:
    def do_setup(self):
        app = TestApp()
        app.add_account('Visa', currency=CAD)
        app.show_account()
        return app
    
    @with_app(do_setup)
    def test_graph(self, app):
        eq_(app.balgraph.currency, CAD)
    

#---
def app_budget_and_no_txn(monkeypatch):
    monkeypatch.patch_today(2008, 1, 1)
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('asset')
    app.add_account('income', account_type=AccountType.Income)
    app.add_budget('income', 'asset', '100')
    return app
    
@with_app(app_budget_and_no_txn)
def test_future_date_range(app):
    # There was a bug where when in a future date range, and also in a range with no transaction,
    # no budget data would be drawn.
    app.drsel.select_next_date_range()
    app.show_nwview()
    # Now, we're supposed to see a graph starting at 100 and ending at 200
    expected = [('01/02/2008', '100.00'), ('01/03/2008', '200.00')]
    eq_(app.nw_graph_data(), expected)

@with_app(app_budget_and_no_txn)
def test_show_budget_data_even_when_account_is_excluded(app):
    # Ticket #332. When accounts were excluded, budget data wouldn't show in the account's balgraph.
    nwview = app.show_nwview()
    app.select_account('asset')
    nwview.bsheet.toggle_excluded()
    app.show_account('asset')
    expected = [('02/01/2008', '0.00'), ('01/02/2008', '100.00')]
    eq_(app.graph_data(), expected)

#---
class TestTwoAccountsOneTransaction:
    def do_setup(self):
        app = TestApp()
        app.add_account('account1')
        app.add_account('account2')
        app.add_txn('12/01/2010', to='account1', amount='42')
        return app
    
    @with_app(do_setup)
    def test_show_to_account(self, app):
        # The data shown in the balgraph when showing account1 is accurate. Previously, the balgraph
        # would use data from the *selected* account, not the *shown* account.
        app.ttable.show_to_account()
        app.link_aview()
        # No account is selected now
        eq_(app.graph_data()[0], ('13/01/2010', '42.00'))
        eq_(app.balgraph.title, 'account1')
    
