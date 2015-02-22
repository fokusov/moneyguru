# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.testutil import eq_

from ..base import TestApp, with_app
from ...gui.transaction_print import TransactionPrint

#--- Split transaction
def app_split_transaction():
    app = TestApp()
    splits = [
        ('foo', '', '100', ''),
        ('bar', '', '', '100'),
        ('split1', 'some memo', '10', ''),
        ('split2', '', '', '1'),
        ('', '', '', '9'),
    ]
    app.add_txn_with_splits(splits)
    app.add_txn(from_='foo', to='bar', amount='42')
    app.pv = TransactionPrint(app.tview)
    return app

@with_app(app_split_transaction)
def test_split_count(app):
    eq_(app.pv.split_count_at_row(0), 5)
    eq_(app.pv.split_count_at_row(1), 2)
    # Instead of crashing, split_count_at_row returns 0 on total row
    eq_(app.pv.split_count_at_row(2), 0)

@with_app(app_split_transaction)
def test_split_values(app):
    eq_(app.pv.split_values(0, 2), ('split1', 'some memo', '10.00'))
    eq_(app.pv.split_values(0, 4), ('Unassigned', '', '-9.00'))

