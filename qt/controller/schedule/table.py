# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt

from qtlib.column import Column
from ..table import Table, AMOUNT_PAINTER

class ScheduleTable(Table):
    COLUMNS = [
        Column('start_date', 80),
        Column('stop_date', 80),
        Column('repeat_type', 80),
        Column('interval', 50),
        Column('description', 110),
        Column('payee', 110),
        Column('checkno', 70),
        Column('from', 100),
        Column('to', 100),
        Column('amount', 97, alignment=Qt.AlignRight, painter=AMOUNT_PAINTER, resizeToFit=True),
    ]
    
    def __init__(self, model, view):
        Table.__init__(self, model, view)
        self.view.sortByColumn(0, Qt.AscendingOrder) # sorted by start_date by default
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
        # we have to prevent Return from initiating editing.
        self.view.editSelected = lambda: None
    
