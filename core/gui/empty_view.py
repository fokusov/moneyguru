# Created By: Virgil Dupras
# Created On: 2010-05-11
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.gui.selectable_list import GUISelectableList
from hscommon.util import first

from ..const import PaneType
from .base import BaseView

class EmptyView(BaseView):
    VIEW_TYPE = PaneType.Empty
    
    def __init__(self, mainwindow):
        BaseView.__init__(self, mainwindow)
        plugin_names = [p.NAME for p in self.mainwindow.app.plugins if p.IS_VIEW]
        self.plugin_list = GUISelectableList(plugin_names)
    
    #--- Public
    def select_pane_type(self, pane_type):
        self.mainwindow.set_current_pane_type(pane_type)
    
    def open_selected_plugin(self):
        index = self.plugin_list.selected_index
        if index is None:
            return
        plugin_name = self.plugin_list[index]
        plugin = first(p for p in self.mainwindow.app.plugins if p.NAME == plugin_name)
        if plugin is not None:
            self.mainwindow.set_current_pane_with_plugin(plugin)
    
