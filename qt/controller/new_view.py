# Created By: Virgil Dupras
# Created On: 2010-06-09
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QShortcut, QKeySequence, QGridLayout, QIcon, QPixmap, QPushButton, QLabel, QVBoxLayout,
    QListView, QAbstractItemView
)

from hscommon.trans import trget
from qtlib.util import horizontalSpacer, verticalSpacer
from qtlib.selectable_list import ListviewModel
from core.const import PaneType

from .base_view import BaseView

tr = trget('ui')

class NewView(BaseView):
    def _setup(self):
        self._setupUi()

        self.pluginList = ListviewModel(self.model.plugin_list, self.pluginListView)
        self.pluginListView.doubleClicked.connect(self.model.open_selected_plugin)
        self.networthButton.clicked.connect(self.networthButtonClicked)
        self.profitButton.clicked.connect(self.profitButtonClicked)
        self.transactionButton.clicked.connect(self.transactionButtonClicked)
        self.gledgerButton.clicked.connect(self.gledgerButtonClicked)
        self.scheduleButton.clicked.connect(self.scheduleButtonClicked)
        self.budgetButton.clicked.connect(self.budgetButtonClicked)
        self.docpropsButton.clicked.connect(self.docpropsButtonClicked)
        self.shortcut1.activated.connect(self.networthButtonClicked)
        self.shortcut2.activated.connect(self.profitButtonClicked)
        self.shortcut3.activated.connect(self.transactionButtonClicked)
        self.shortcut4.activated.connect(self.gledgerButtonClicked)
        self.shortcut5.activated.connect(self.scheduleButtonClicked)
        self.shortcut6.activated.connect(self.budgetButtonClicked)
        self.shortcut7.activated.connect(self.docpropsButtonClicked)

    def _setupUi(self):
        self.resize(400, 300)
        self.gridLayout = QGridLayout(self)
        self.label = QLabel(tr("Choose a type for this tab:"))
        self.label.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.gridLayout.addItem(horizontalSpacer(), 1, 0, 1, 1)
        self.verticalLayout = QVBoxLayout()
        self.networthButton = QPushButton(tr("1. Net Worth"))
        self.networthButton.setIcon(QIcon(QPixmap(':/balance_sheet_16')))
        self.verticalLayout.addWidget(self.networthButton)
        self.profitButton = QPushButton(tr("2. Profit && Loss"))
        self.profitButton.setIcon(QIcon(QPixmap(':/income_statement_16')))
        self.verticalLayout.addWidget(self.profitButton)
        self.transactionButton = QPushButton(tr("3. Transactions"))
        self.transactionButton.setIcon(QIcon(QPixmap(':/transaction_table_16')))
        self.verticalLayout.addWidget(self.transactionButton)
        self.gledgerButton = QPushButton(tr("4. General Ledger"))
        self.gledgerButton.setIcon(QIcon(QPixmap(':/gledger_16')))
        self.verticalLayout.addWidget(self.gledgerButton)
        self.scheduleButton = QPushButton(tr("5. Schedules"))
        self.scheduleButton.setIcon(QIcon(QPixmap(':/schedules_16')))
        self.verticalLayout.addWidget(self.scheduleButton)
        self.budgetButton = QPushButton(tr("6. Budgets"))
        self.budgetButton.setIcon(QIcon(QPixmap(':/budget_16')))
        self.verticalLayout.addWidget(self.budgetButton)
        self.docpropsButton = QPushButton(tr("7. Document Properties"))
        self.docpropsButton.setIcon(QIcon(QPixmap(':/gledger_16')))
        self.verticalLayout.addWidget(self.docpropsButton)
        self.pluginLabel = QLabel(tr("Plugins (double-click to open)"))
        self.pluginLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.pluginLabel)
        self.pluginListView = QListView()
        self.pluginListView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalLayout.addWidget(self.pluginListView)
        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)
        self.gridLayout.addItem(horizontalSpacer(), 1, 2, 1, 1)
        self.gridLayout.addItem(verticalSpacer(), 2, 1, 1, 1)

        for i in range(1, 8):
            shortcut = QShortcut(QKeySequence(str(i)), self, None, None, Qt.WidgetShortcut)
            setattr(self, 'shortcut{0}'.format(i), shortcut)

    #--- Event Handlers
    def networthButtonClicked(self):
        self.model.select_pane_type(PaneType.NetWorth)

    def profitButtonClicked(self):
        self.model.select_pane_type(PaneType.Profit)

    def transactionButtonClicked(self):
        self.model.select_pane_type(PaneType.Transaction)

    def gledgerButtonClicked(self):
        self.model.select_pane_type(PaneType.GeneralLedger)

    def scheduleButtonClicked(self):
        self.model.select_pane_type(PaneType.Schedule)

    def budgetButtonClicked(self):
        self.model.select_pane_type(PaneType.Budget)

    def docpropsButtonClicked(self):
        self.model.select_pane_type(PaneType.DocProps)

