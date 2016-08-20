# Created By: Virgil Dupras
# Created On: 2009-12-04
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter

from .layout import LayoutPage, LayoutViewElement
from .item_view import (
    ItemViewLayoutElement, ItemViewPrintStats, TablePrintDatasource, TreePrintDatasource
)

# XXX I think it might be possible to push down some of the layout logic to the model part of the
# app so that it can be re-used on the Cocoa side (this code is messy too).

# The PDF preview is all blurry, I don't know how it looks on a real printer. This guy seems to have
# the same problem:
# http://lists.trolltech.com/pipermail/qt-interest/2009-November/015375.html

class ViewPrinter:
    def __init__(self, printer, baseView):
        self.document = baseView.model.document
        self.app = self.document.app
        self.model = baseView.model.PRINT_VIEW_CLASS(baseView.model)
        self.title = self.model.title
        self.printer = printer
        self.pageSize = printer.pageRect().size()
        self.layoutPages = [LayoutPage(self)]

    def _fitItemView(self, ds):
        # It is currently assumed that the current page's width availability is going to be the same
        # as possible additonnal pages (in other words, place it first).
        stats = ItemViewPrintStats(ds)
        page = self.layoutPages[-1]
        currentRow = 0
        while True:
            maxPageWidth = page.maxAvailableWidth
            elementWidth = min(maxPageWidth, stats.maxWidth)
            element = ItemViewLayoutElement(ds, stats, elementWidth, currentRow)
            page.fit(element, expandV=True)
            currentRow = element.endRow+1
            if currentRow >= ds.rowCount():
                break
            page = LayoutPage(self)
            self.layoutPages.append(page)

    def fit(self, view, minWidth, minHeight, expandH=False, expandV=False):
        rect = QRect(0, 0, minWidth, minHeight)
        element = LayoutViewElement(view, rect)
        for page in self.layoutPages:
            if page.fit(element, expandH, expandV):
                break
        else:
            page = LayoutPage(self)
            page.fit(element, expandH, expandV)
            self.layoutPages.append(page)

    def fitTable(self, table):
        self._fitItemView(TablePrintDatasource(self.model, table))

    def fitTree(self, tree):
        self._fitItemView(TreePrintDatasource(self.model, tree))

    def render(self):
        painter = QPainter(self.printer)
        for page in self.layoutPages[:-1]:
            page.render(painter)
            self.printer.newPage()
        self.layoutPages[-1].render(painter)
        painter.end()

