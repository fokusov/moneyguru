# Created By: Virgil Dupras
# Created On: 2010-10-24
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..saver.csv import save as save_csv
from ..saver.qif import save as save_qif
from .base import MainWindowPanel
from .export_account_table import ExportAccountTable

class ExportFormat:
    QIF = 0
    CSV = 1

class ExportPanel(MainWindowPanel):
    def __init__(self, mainwindow):
        MainWindowPanel.__init__(self, mainwindow)
        self.account_table = ExportAccountTable(self)
    
    def _load(self):
        self.accounts = [a for a in self.document.accounts if a.is_balance_sheet_account()]
        self.exported_names = set()
        self.export_all = True
        self.export_format = ExportFormat.QIF
        self.export_path = None
        self.current_daterange_only = False
        self.account_table.refresh()
    
    def _save(self):
        accounts = self.accounts
        if not self.export_all:
            accounts = [a for a in accounts if a.name in self.exported_names]
        save_func = {
            ExportFormat.QIF: save_qif,
            ExportFormat.CSV: save_csv,
        }[self.export_format]
        if self.current_daterange_only:
            daterange = self.document.date_range
        else:
            daterange = None
        save_func(self.export_path, accounts, daterange=daterange)
    
    #--- Public
    def is_exported(self, name):
        return name in self.exported_names
    
    def set_exported(self, name, value):
        if value:
            self.exported_names.add(name)
        else:
            self.exported_names.discard(name)
        self.view.set_export_button_enabled(bool(self._export_all or self.exported_names))
    
    #--- Properties
    @property
    def export_all(self):
        return self._export_all
    
    @export_all.setter
    def export_all(self, value):
        self._export_all = value
        self.view.set_table_enabled(not self._export_all)
        self.view.set_export_button_enabled(bool(self._export_all or self.exported_names))
    
