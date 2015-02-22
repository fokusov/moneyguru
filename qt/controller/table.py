# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt4.QtGui import QFontMetrics

from qtlib.table import Table as TableBase

from ..support.completable_edit import DescriptionEdit, PayeeEdit, AccountEdit
from ..support.column_view import AmountPainter
from ..support.date_edit import DateEdit
from ..support.item_delegate import ItemDelegate

NO_EDIT = 'no_edit'
DATE_EDIT = 'date_edit'
DESCRIPTION_EDIT = 'description_edit'
PAYEE_EDIT = 'payee_edit'
ACCOUNT_EDIT = 'account_edit'

# See #14, #15 Added to indicate an amount to be painted to a table
# with nicely aligned currency / value
AMOUNT_PAINTER = 'amount_painter'

EDIT_TYPE2COMPLETABLE_EDIT = {
    DESCRIPTION_EDIT: DescriptionEdit,
    PAYEE_EDIT: PayeeEdit,
    ACCOUNT_EDIT: AccountEdit
}

class TableDelegate(ItemDelegate):
    def __init__(self, model):
        ItemDelegate.__init__(self)
        self._model = model
        self._column_painters = {}
        for column in self._model.columns.column_list:
            if column.painter == AMOUNT_PAINTER:
                # See #14, #15.
                self._column_painters[column.name] = AmountPainter(column.name, self._model)

    def _get_value_painter(self, index):
        column = self._model.columns.column_by_index(index.column())

        if column.name in self._column_painters:
            return self._column_painters[column.name]

    def createEditor(self, parent, option, index):
        column = self._model.columns.column_by_index(index.column())
        editType = column.editor
        if editType is None:
            return ItemDelegate.createEditor(self, parent, option, index)
        elif editType == NO_EDIT:
            return None
        elif editType == DATE_EDIT:
            return DateEdit(parent)
        elif editType in EDIT_TYPE2COMPLETABLE_EDIT:
            return EDIT_TYPE2COMPLETABLE_EDIT[editType](self._model.completable_edit, parent)


class Table(TableBase):
    def __init__(self, model, view):
        TableBase.__init__(self, model, view)
        self.tableDelegate = TableDelegate(self.model)
        self.view.setItemDelegate(self.tableDelegate)
        from ..app import APP_PREFS
        self._updateFontSize(prefs=APP_PREFS)
        APP_PREFS.prefsChanged.connect(self.appPrefsChanged)

    def _updateFontSize(self, prefs):
        font = self.view.font()
        font.setPointSize(prefs.tableFontSize)
        self.view.setFont(font)
        fm = QFontMetrics(font)
        self.view.verticalHeader().setDefaultSectionSize(fm.height()+2)
        # (#14, #15) When a new font was selected in the preferences panel,
        # the column would redraw but not resize appropriately.  A call
        # to resize(sizeHint()) was added on the update of the size info
        # in the custom drawing for the amount field.
        self.view.resize(self.view.sizeHint())

    def appPrefsChanged(self):
        self._updateFontSize(prefs=self.sender())

