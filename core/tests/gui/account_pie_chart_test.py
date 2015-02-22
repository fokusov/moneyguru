# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from datetime import date

from hscommon.testutil import eq_
from hscommon.currency import Currency, USD, CAD

from ..base import ApplicationGUI, TestApp, with_app
from ...app import Application
from ...gui.pie_chart import MIN_SLICE_COUNT, MIN_VIEW_SIZE, SIZE_COST_FOR_SLICE, COLOR_COUNT
from ...model.account import AccountType

#--- Slice count
def app_show_nwview():
    app = TestApp()
    app.show_nwview()
    return app

@with_app(app_show_nwview)
def test_min_slice_count(app):
    # There's a threshold under which we don't go for slice count
    app.nwview.pie.set_view_size(1, 1)
    eq_(app.nwview.pie.slice_count, MIN_SLICE_COUNT)

@with_app(app_show_nwview)
def test_two_extra_slices(app):
    size = MIN_VIEW_SIZE + (2 * SIZE_COST_FOR_SLICE)
    app.nwview.pie.set_view_size(size, size)
    eq_(app.nwview.pie.slice_count, MIN_SLICE_COUNT + 2)

@with_app(app_show_nwview)
def test_min_between_width_and_height_used(app):
    # The minimum value between width and height is used for calculating the number of slices
    size = MIN_VIEW_SIZE + (2 * SIZE_COST_FOR_SLICE)
    app.nwview.pie.set_view_size(size, 1)
    eq_(app.nwview.pie.slice_count, MIN_SLICE_COUNT)
    app.nwview.pie.set_view_size(1, size)
    eq_(app.nwview.pie.slice_count, MIN_SLICE_COUNT)

#---
def app_some_assets_and_liabilities(monkeypatch):
    monkeypatch.patch_today(2009, 1, 29) # On the last day of the month, some tests fail
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('a1')
    app.show_account()
    app.add_entry(increase='1.01') # values are trucated
    app.add_account('a2')
    app.show_account()
    app.add_entry(increase='4')
    app.add_account('a3')
    app.show_account()
    app.add_entry(increase='2')
    app.add_account('a4')
    app.show_account()
    app.add_entry(increase='3')
    app.add_account('empty') # doesn't show
    app.add_account('l1', account_type=AccountType.Liability)
    app.show_account()
    app.add_entry(increase='3')
    app.add_account('l2', account_type=AccountType.Liability)
    app.show_account()
    app.add_entry(increase='5')
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets
    app.clear_gui_calls()
    return app

class TestSomeAssetsAndLiabilities:
    def do_setup(self, monkeypatch):
        return app_some_assets_and_liabilities(monkeypatch)
    
    @with_app(do_setup)
    def test_asset_pie_chart_values(self, app):
        # The asset pie chart values are sorted in reversed order of amount and have correct titles
        eq_(app.nwview.pie.title, 'Assets & Liabilities')
        expected = [
            ('a2 40.0%', 4, 0),
            ('a4 30.0%', 3, 1),
            ('a3 20.0%', 2, 2),
            ('a1 10.1%', 1.01, 3),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
    @with_app(do_setup)
    def test_budget_multiple_currency(self, app):
        # just make sure it doesn't crash
        app.bsheet.selected = app.bsheet.assets[0]
        app.mw.edit_item()
        app.apanel.currency_list.select(Currency.all.index(CAD))
        app.apanel.save()
        app.add_account('income', account_type=AccountType.Income)
        app.add_budget('income', None, '5')
        app.show_nwview() # don't crash
    
    @with_app(do_setup)
    def test_exclude_account(self, app):
        # excluding an account removes it from the pie chart
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.toggle_excluded()
        expected = [
            ('a2 44.4%', 4, 0),
            ('a4 33.3%', 3, 1),
            ('a3 22.2%', 2, 2),
        ]
        eq_(app.nwview.pie.pie1, expected)
        app.nwview.pie.view.check_gui_calls(['refresh'])
    
    @with_app(do_setup)
    def test_liabilities_pie(self, app):
        # the liability pie also works
        expected = [
            ('l2 62.5%', 5, 0),
            ('l1 37.5%', 3, 1),
        ]
        eq_(app.nwview.pie.pie2, expected)
    

class TestSomeAssetsAndLiabilitiesWithBudget:
    def do_setup(self, monkeypatch):
        app = app_some_assets_and_liabilities(monkeypatch)
        app.drsel.select_today_date_range()
        app.add_account('income', account_type=AccountType.Income)
        app.add_budget('income', 'a3', '5')
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_future_date_range(self, app):
        # the budget amounts used for the pie chart include all previous budgets
        app.drsel.select_next_date_range()
        expected = [
            ('a3 60.0%', 12, 0),
            ('a2 20.0%', 4, 1),
            ('a4 15.0%', 3, 2),
            ('a1 5.0%', 1.01, 3),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
    @with_app(do_setup)
    def test_pie_values(self, app):
        # budgeted amounts are also reflected in the pie chart
        expected = [
            ('a3 46.6%', 7, 0),
            ('a2 26.6%', 4, 1),
            ('a4 20.0%', 3, 2),
            ('a1 6.7%', 1.01, 3),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
#---
def app_more_assets_than_slice_count():
    app = TestApp()
    app.show_nwview()
    for i in range(app.nwview.pie.slice_count + 2):
        app.add_account('account %d' % i)
        app.show_account()
        app.add_entry(increase='1')
    app.show_nwview()
    return app

@with_app(app_more_assets_than_slice_count)
def test_others_slice_values(app):
    # When there's more data point than max slice count, we group all data points in one and
    # call it "Others".
    data = app.nwview.pie.pie1
    eq_(len(data), app.nwview.pie.slice_count)
    other = data[-1]
    expected_name = 'Others %1.1f%%' % (3 / (app.nwview.pie.slice_count + 2) * 100)
    expected_amount = 3
    expected_color = COLOR_COUNT-1
    eq_(other, (expected_name, expected_amount, expected_color))

@with_app(app_more_assets_than_slice_count)
def test_recompute_data_on_view_size_change(app):
    # When the view size change and that this change results in a change in slice count, recompute
    # the data.
    app.nwview.pie.set_view_size(9999, 9999)
    eq_(len(app.nwview.pie.pie1), len(app.account_names()))

class TestSomeIncomeAndExpenses:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account('foo')
        app.show_account()
        app.add_entry(transfer='i1', increase='2')
        app.add_entry(transfer='i2', increase='4')
        app.add_entry(transfer='i3', increase='1')
        app.add_entry(transfer='i4', increase='3')
        app.add_entry(transfer='e1', decrease='3')
        app.add_entry(transfer='e2', decrease='1')
        app.add_entry(transfer='e3', decrease='4')
        app.add_entry(transfer='e4', decrease='2')
        app.show_pview()
        app.istatement.selected = app.istatement.expenses
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_budget(self, app, monkeypatch):
        # budgeted amounts are also reflected in the pie chart
        monkeypatch.patch_today(2009, 1, 29) # On the last day of the month, this test fails
        app.add_budget('e1', None, '5')
        app.show_pview()
        expected = [
            ('e1 41.7%', 5, 0),
            ('e3 33.3%', 4, 1),
            ('e4 16.7%', 2, 2),
            ('e2 8.3%', 1, 3),
        ]
        eq_(app.pview.pie.pie2, expected)
    
    @with_app(do_setup)
    def test_expenses_pie_chart_values(self, app):
        # The expenses pie chart values are sorted in reversed order of amount and have correct titles
        expected = [
            ('e3 40.0%', 4, 0),
            ('e1 30.0%', 3, 1),
            ('e4 20.0%', 2, 2),
            ('e2 10.0%', 1, 3),
        ]
        eq_(app.pview.pie.pie2, expected)
    
    @with_app(do_setup)
    def test_exclude_account(self, app):
        # excluding an account removes it from the pie chart
        app.istatement.selected = app.istatement.expenses[0]
        app.istatement.toggle_excluded()
        expected = [
            ('e3 57.1%', 4, 0),
            ('e4 28.6%', 2, 1),
            ('e2 14.3%', 1, 2),
        ]
        eq_(app.pview.pie.pie2, expected)
        app.pview.pie.view.check_gui_calls(['refresh'])
    
    @with_app(do_setup)
    def test_income_pie(self, app):
        # the income pie also works
        app.istatement.selected = app.istatement.income[0]
        eq_(app.pview.pie.title, 'Income & Expenses')
        expected = [
            ('i2 40.0%', 4, 0),
            ('i4 30.0%', 3, 1),
            ('i1 20.0%', 2, 2),
            ('i3 10.0%', 1, 3),
        ]
        eq_(app.pview.pie.pie1, expected)
    

class TestDifferentDateRanges:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account('foo')
        app.show_account()
        app.add_entry(date='01/08/2008', transfer='baz', increase='5')
        app.add_entry(date='01/08/2008', transfer='bar', decrease='1')
        app.add_entry(date='01/09/2008', transfer='bar', decrease='2')
        app.show_nwview()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_balance_pie_chart(self, app):
        # the data in the balance pie chart reflects the currencly selected date range
        eq_(app.nwview.pie.pie1, [('foo 100.0%', 2, 0)])
        app.drsel.select_prev_date_range()
        eq_(app.nwview.pie.pie1, [('foo 100.0%', 4, 0)])
        app.nwview.pie.view.check_gui_calls(['refresh'])
    
    @with_app(do_setup)
    def test_cash_flow_pie_chart(self, app):
        # the data in the cash flow pie chart reflects the currencly selected date range
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[0]
        app.clear_gui_calls()
        eq_(app.pview.pie.pie2, [('bar 100.0%', 2, 0)])
        app.drsel.select_prev_date_range()
        eq_(app.pview.pie.pie2, [('bar 100.0%', 1, 0)])
        app.pview.pie.view.check_gui_calls(['refresh'])
    

class TestMultipleCurrencies:
    def do_setup(self):
        app = TestApp(app=Application(ApplicationGUI(), default_currency=CAD))
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        app.add_account('USD income', account_type=AccountType.Income, currency=USD)
        app.add_account('CAD income', account_type=AccountType.Income, currency=CAD)
        app.add_account('USD asset', currency=USD)
        app.show_account()
        app.add_entry('1/1/2008', 'USD entry', transfer='USD income', increase='1')
        app.add_account('CAD asset', currency=CAD)
        app.show_account()
        app.add_entry('1/1/2008', 'CAD entry', transfer='CAD income', increase='1')
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_balance_pie_chart(self, app):
        # the amounts are converted to the default currency before being weighted
        expected = [
            ('CAD asset 55.6%', 1, 0),
            ('USD asset 44.4%', 0.8, 1),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
    @with_app(do_setup)
    def test_cash_flow_pie_chart(self, app):
        # the amounts are converted to the default currency before being weighted
        app.show_pview()
        expected = [
            ('CAD income 55.6%', 1, 0),
            ('USD income 44.4%', 0.8, 1),
        ]
        eq_(app.pview.pie.pie1, expected)
    

class TestNegativeAssetValue:
    def do_setup(self):
        app = TestApp()
        app.add_account('foo')
        app.add_account('bar')
        app.show_account()
        app.add_entry(date='01/08/2008', transfer='foo', increase='1')
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_balance_pie_chart(self, app):
        # negative balances are ignored
        eq_(app.nwview.pie.pie1, [('bar 100.0%', 1, 0)])
    

class TestAccountGroup:
    def do_setup(self):
        app = TestApp()
        app.show_nwview()
        app.bsheet.add_account_group()
        app.bsheet.selected.name = 'group'
        app.bsheet.save_edits()
        app.bsheet.add_account() # the group is now expanded
        app.bsheet.selected.name = 'foo'
        app.bsheet.save_edits()
        app.show_account()
        app.add_entry(increase='1')
        app.add_account('bar', group_name='group')
        app.show_account()
        app.add_entry(increase='2')
        app.add_account('baz')
        app.show_account()
        app.add_entry(increase='7')
        app.show_nwview()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_collapse_group(self, app):
        # when we collapse the group, 'foo' and 'bar' are grouped together
        app.bsheet.collapse_node(app.bsheet.assets[0])
        # we must not refresh the bsheet. group collapsing is called in the middle of an outline
        # view event, refreshing the outline during that call causes a crash
        app.bsheet_gui.check_gui_calls_partial(not_expected=['refresh'])
        expected = [
            ('baz 70.0%', 7, 0),
            ('group 30.0%', 3, 1),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
    @with_app(do_setup)
    def test_expand_group(self, app):
        # when we expand the group again, 'foo' and 'bar' go back to separate
        app.bsheet.expand_node(app.bsheet.assets[0])
        app.bsheet_gui.check_gui_calls_partial(not_expected=['refresh']) # see test_collapse_group
        expected = [
            ('baz 70.0%', 7, 0),
            ('bar 20.0%', 2, 1),
            ('foo 10.0%', 1, 2),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
    @with_app(do_setup)
    def test_pie_chart_data(self, app):
        # when the group is expanded, show all accounts individually
        expected = [
            ('baz 70.0%', 7, 0),
            ('bar 20.0%', 2, 1),
            ('foo 10.0%', 1, 2),
        ]
        eq_(app.nwview.pie.pie1, expected)
    
