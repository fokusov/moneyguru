# Created By: Virgil Dupras
# Created On: 2010-02-25
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from ..model.sort import sort_string
from .lookup import Lookup

class AccountLookup(Lookup):
    def _generate_lookup_names(self):
        names = [a.combined_display for a in self.document.accounts]
        return sorted(names, key=sort_string)
    
    def _go(self, name):
        account = self.document.accounts.find(name)
        self.mainwindow.open_account(account)
    
