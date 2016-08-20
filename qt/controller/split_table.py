# Created By: Virgil Dupras
# Created On: 2009-11-04
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt, QMimeData, QByteArray

from qtlib.column import Column
from .table import Table, ACCOUNT_EDIT

MIME_INDEX = 'application/moneyguru.splitindex'

class SplitTable(Table):
    COLUMNS = [
        Column('account', 100, editor=ACCOUNT_EDIT),
        Column('memo', 70),
        Column('debit', 90, alignment=Qt.AlignRight),
        Column('credit', 90, alignment=Qt.AlignRight),
    ]
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
    
    def __init__(self, model, view):
        Table.__init__(self, model, view)
        # XXX If we don't call that, our columns will all be very small. Find a more elegant way,
        # prefeably in the core, to avoid these situations.
        self.columns.setColumnsWidth(None)
        view.keyPressed.connect(self.keyPressed)
    
    def _getFlags(self, row, column):
        flags = Table._getFlags(self, row, column)
        return flags | Qt.ItemIsDragEnabled
    
    # --- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_INDEX):
            return False
        # Since we only drop in between items, parentIndex must be invalid, and we use the row arg
        # to know where the drop took place.
        if parentIndex.isValid():
            return False
        index = int(bytes(mimeData.data(MIME_INDEX)).decode())
        self.model.move_split(index, row)
        return True
    
    def mimeData(self, indexes):
        data = str(indexes[0].row())
        mimeData = QMimeData()
        mimeData.setData(MIME_INDEX, QByteArray(data.encode()))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_INDEX]
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
    # --- Event Handlers
    def keyPressed(self, event):
        # return
        if (event.key() == Qt.Key_Down) and (self.model.selected_index == len(self.model)-1):
            event.ignore()
            self.model.add()
    
