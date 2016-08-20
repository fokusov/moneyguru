# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import weakref

from hscommon.trans import tr
from ..const import PaneType
from .base import BaseView, MESSAGES_EVERYTHING_CHANGED
from .budget_table import BudgetTable
from .budget_panel import BudgetPanel

class BudgetView(BaseView):
    # --- model -> view calls:
    # get_panel_view(panel_model) -> view
    #

    VIEW_TYPE = PaneType.Budget
    PRINT_TITLE_FORMAT = tr('Budgets from {start_date} to {end_date}')
    INVALIDATING_MESSAGES = (
        MESSAGES_EVERYTHING_CHANGED |
        {'budget_changed', 'budget_deleted', 'account_deleted'}
    )

    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        self.table = BudgetTable(self)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)

    def _revalidate(self):
        self.table.refresh_and_show_selection()

    # --- Override
    def save_preferences(self):
        self.table.columns.save_columns()

    # --- Public
    def new_item(self):
        budget_panel = BudgetPanel(self.mainwindow)
        budget_panel.view = weakref.proxy(self.view.get_panel_view(budget_panel))
        budget_panel.new()
        return budget_panel

    def edit_item(self):
        budget_panel = BudgetPanel(self.mainwindow)
        budget_panel.view = weakref.proxy(self.view.get_panel_view(budget_panel))
        budget_panel.load()
        return budget_panel

    def delete_item(self):
        self.table.delete()

