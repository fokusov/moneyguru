# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import trget, tr
from hscommon.gui.column import Column
from ..model.account import AccountType
from .report import Report, get_delta_perc

trcol = trget('columns')

class IncomeStatement(Report):
    SAVENAME = 'IncomeStatement'
    COLUMNS = [
        Column('name', display=trcol("Account")),
        Column('account_number', display=trcol("Account #"), visible=False, optional=True),
        Column('cash_flow', display=trcol("Current")),
        Column('last_cash_flow', display=trcol("Last"), optional=True),
        Column('delta', display=trcol("Change"), visible=False, optional=True),
        Column('delta_perc', display=trcol("Change %"), visible=False, optional=True),
        Column('budgeted', display=trcol("Budgeted"), optional=True),
    ]

    #--- Override
    def _compute_account_node(self, node):
        account = node.account
        date_range = self.document.date_range
        currency = self.document.default_currency
        cash_flow = account.entries.normal_cash_flow(date_range)
        cash_flow_native = account.entries.normal_cash_flow(date_range, currency)
        last_cash_flow = account.entries.normal_cash_flow(date_range.prev())
        last_cash_flow_native = account.entries.normal_cash_flow(date_range.prev(), currency)
        remaining = self.document.budgets.normal_amount_for_account(account, date_range)
        remaining_native = self.document.budgets.normal_amount_for_account(account, date_range, currency)
        delta = cash_flow - last_cash_flow

        # Amounts for totals are converted in the document's currency
        node.cash_flow_amount = cash_flow_native
        node.last_cash_flow_amount = last_cash_flow_native
        node.budgeted_amount = remaining_native

        # Amounts for display are kept in the account's currency
        node.cash_flow = self.document.format_amount(cash_flow)
        node.last_cash_flow = self.document.format_amount(last_cash_flow)
        node.budgeted = self.document.format_amount(remaining)
        node.delta = self.document.format_amount(delta)
        node.delta_perc = get_delta_perc(delta, last_cash_flow)

    def _make_node(self, name):
        node = Report._make_node(self, name)
        node.cash_flow = ''
        node.last_cash_flow = ''
        node.budget = ''
        node.budgeted = ''
        node.delta = ''
        node.delta_perc = ''
        node.cash_flow_amount = 0
        node.last_cash_flow_amount = 0
        node.budgeted_amount = 0
        return node

    def _refresh(self):
        self.clear()
        self.has_multiple_currencies = self.document.accounts.has_multiple_currencies()
        self.income = self.make_type_node(tr('INCOME'), AccountType.Income)
        self.expenses = self.make_type_node(tr('EXPENSES'), AccountType.Expense)
        self.net_income = self._make_node(tr('NET INCOME'))
        net_income = self.income.cash_flow_amount - self.expenses.cash_flow_amount
        last_net_income = self.income.last_cash_flow_amount - self.expenses.last_cash_flow_amount
        net_budgeted = self.income.budgeted_amount - self.expenses.budgeted_amount
        delta = net_income - last_net_income
        force_explicit_currency = self.has_multiple_currencies
        self.net_income.cash_flow = self.document.format_amount(
            net_income, force_explicit_currency=force_explicit_currency
        )
        self.net_income.last_cash_flow = self.document.format_amount(
            last_net_income, force_explicit_currency=force_explicit_currency
        )
        self.net_income.budgeted = self.document.format_amount(
            net_budgeted, force_explicit_currency=force_explicit_currency
        )
        self.net_income.delta = self.document.format_amount(
            delta, force_explicit_currency=force_explicit_currency
        )
        self.net_income.delta_perc = get_delta_perc(delta, last_net_income)
        self.net_income.is_total = True
        self.append(self.income)
        self.append(self.expenses)
        self.append(self.net_income)

    #--- Public
    def make_total_node(self, parent, name):
        node = Report.make_total_node(self, name)
        parent.cash_flow_amount = sum(child.cash_flow_amount for child in parent)
        parent.last_cash_flow_amount = sum(child.last_cash_flow_amount for child in parent)
        parent.budgeted_amount = sum(child.budgeted_amount for child in parent)
        delta = parent.cash_flow_amount - parent.last_cash_flow_amount
        force_explicit_currency = self.has_multiple_currencies
        node.cash_flow = parent.cash_flow = self.document.format_amount(
            parent.cash_flow_amount, force_explicit_currency=force_explicit_currency
        )
        node.last_cash_flow = parent.last_cash_flow = self.document.format_amount(
            parent.last_cash_flow_amount, force_explicit_currency=force_explicit_currency
        )
        node.budgeted = parent.budgeted = self.document.format_amount(
            parent.budgeted_amount, force_explicit_currency=force_explicit_currency
        )
        node.delta = parent.delta = self.document.format_amount(
            delta, force_explicit_currency=force_explicit_currency
        )
        node.delta_perc = parent.delta_perc = get_delta_perc(delta, parent.last_cash_flow_amount)
        return node

