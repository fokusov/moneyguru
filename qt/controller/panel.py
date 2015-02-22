# Created By: Virgil Dupras
# Created On: 2009-11-10
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt4.QtCore import Qt, QSignalMapper
from PyQt4.QtGui import QWidget, QDialog, QLineEdit, QSpinBox, QComboBox, QCheckBox, QPlainTextEdit

class Panel(QDialog):
    # A list of two-sized tuples (QWidget's name, model field name).
    FIELDS = []

    def __init__(self, parent=None):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self._widget2ModelAttr = {}

    def _changeComboBoxItems(self, comboBox, newItems):
        # When a combo box's items are changed, its currentIndex changed with a currentIndexChanged
        # signal, and if that signal results in the model being updated, it messes the model.
        # We thus have to disconnect the combo box's signal before changing the items.
        if comboBox in self._widget2ModelAttr:
            comboBox.currentIndexChanged.disconnect(self.comboBoxCurrentIndexChanged)
        index = comboBox.currentIndex()
        comboBox.clear()
        comboBox.addItems(newItems)
        comboBox.setCurrentIndex(index)
        if comboBox in self._widget2ModelAttr:
            comboBox.currentIndexChanged.connect(self.comboBoxCurrentIndexChanged)

    def _connectSignals(self):
        self._signalMapper = QSignalMapper()
        for widgetName, modelAttr in self.FIELDS:
            widget = getattr(self, widgetName)
            self._widget2ModelAttr[widget] = modelAttr
            self._signalMapper.setMapping(widget, widget)
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._signalMapper.map)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._signalMapper.map)
            elif isinstance(widget, QLineEdit):
                widget.editingFinished.connect(self._signalMapper.map)
            elif isinstance(widget, QPlainTextEdit):
                widget.textChanged.connect(self._signalMapper.map)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self._signalMapper.map)
        self._signalMapper.mapped[QWidget].connect(self.widgetChanged)

    def _loadFields(self):
        for widgetName, modelAttr in self.FIELDS:
            widget = getattr(self, widgetName)
            value = getattr(self.model, modelAttr)
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(value)
            elif isinstance(widget, QSpinBox):
                widget.setValue(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QPlainTextEdit):
                widget.setPlainText(value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(value)

    def _saveFields(self):
        pass

    def accept(self):
        # The setFocus() call is to force the last edited field to "commit". When the save button
        # is clicked, accept() is called before the last field to have focus has a chance to emit
        # its edition signal.
        self.setFocus()
        self.model.save()
        QDialog.accept(self)

    #--- Event Handlers
    def widgetChanged(self, sender):
        modelAttr = self._widget2ModelAttr[sender]
        if isinstance(sender, QComboBox):
            newvalue = sender.currentIndex()
        elif isinstance(sender, QSpinBox):
            newvalue = sender.value()
        elif isinstance(sender, QLineEdit):
            newvalue = sender.text()
        elif isinstance(sender, QPlainTextEdit):
            newvalue = sender.toPlainText()
        elif isinstance(sender, QCheckBox):
            newvalue = sender.isChecked()
        setattr(self.model, modelAttr, newvalue)

    #--- model --> view
    def pre_load(self):
        pass

    def pre_save(self):
        self._saveFields()

    def post_load(self):
        if not self._widget2ModelAttr: # signal not connected yet
            self._connectSignals()
        self._loadFields()
        self.show()
        # For initial text edits to have their text selected, we *have to* first select the dialog,
        # then setFocus on it with qt.TabFocusReason. Don't ask, I don't know why either...
        self.setFocus()
        focus = self.nextInFocusChain()
        while focus.focusPolicy() == Qt.NoFocus:
            focus = focus.nextInFocusChain()
        focus.setFocus(Qt.TabFocusReason)

