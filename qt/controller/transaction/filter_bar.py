# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.trans import trget
from core.document import FilterType

from ..filter_bar import FilterBar

tr = trget('ui')

class TransactionFilterBar(FilterBar):
    BUTTONS = [
        (tr("All"), None),
        (tr("Income"), FilterType.Income),
        (tr("Expenses"), FilterType.Expense),
        (tr("Transfers"), FilterType.Transfer),
        (tr("Unassigned"), FilterType.Unassigned),
        (tr("Reconciled"), FilterType.Reconciled),
        (tr("Not Reconciled"), FilterType.NotReconciled),
    ]
