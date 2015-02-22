# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QFrame, QAbstractItemView, QSplitter

from ...support.item_view import TreeView
from ...support.pie_chart_view import PieChartView
from ...support.bar_graph_view import BarGraphView
from ..account_sheet_view import AccountSheetView
from ..chart import Chart
from .sheet import ProfitSheet

class ProfitView(AccountSheetView):
    def _setup(self):
        self._setupUi()
        self.sheet = self.psheet = ProfitSheet(self.model.istatement, view=self.treeView)
        self.graph = self.pgraph = Chart(self.model.pgraph, view=self.graphView)
        self.piechart = Chart(self.model.pie, view=self.pieChart)
    
    def _setupUi(self):
        self.resize(558, 447)
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(0)
        self.splitterView = QSplitter()
        self.splitterView.setChildrenCollapsible(False)
        self.splitterView.setOrientation(Qt.Vertical)
        self.subSplitterView = QSplitter()
        self.subSplitterView.setChildrenCollapsible(False)
        self.treeView = TreeView(self)
        self.treeView.setAcceptDrops(True)
        self.treeView.setFrameShape(QFrame.NoFrame)
        self.treeView.setFrameShadow(QFrame.Plain)
        self.treeView.setEditTriggers(QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.header().setStretchLastSection(False)
        self.subSplitterView.addWidget(self.treeView)
        self.pieChart = PieChartView(self)
        self.pieChart.setMinimumSize(300, 0)
        self.subSplitterView.addWidget(self.pieChart)
        self.splitterView.addWidget(self.subSplitterView)
        self.graphView = BarGraphView(self)
        self.graphView.setMinimumSize(0, 200)
        self.splitterView.addWidget(self.graphView)
        self.splitterView.setStretchFactor(0, 1)
        self.splitterView.setStretchFactor(1, 0)
        self.subSplitterView.setStretchFactor(0, 1)
        self.subSplitterView.setStretchFactor(1, 0)
        self.mainLayout.addWidget(self.splitterView)
    
