# Created By: Virgil Dupras
# Created On: 2009-11-07
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen

from core.gui.bar_graph import PenID, BrushID
from .graph_view import GraphView

class BarGraphView(GraphView):
    def penForID(self, penId):
        if penId == PenID.Bar:
            return self.linePen
        elif penId == PenID.TodayLine:
            pen = QPen(self.linePen)
            pen.setColor(Qt.red)
            return pen
        else:
            return GraphView.penForID(self, penId)

    def brushForID(self, brushId):
        if brushId == BrushID.NormalBar:
            return self.graphBrush
        elif brushId == BrushID.FutureBar:
            return self.graphFutureBrush

