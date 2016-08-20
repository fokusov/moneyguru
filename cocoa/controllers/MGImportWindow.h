/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "PSMTabBarControl.h"
#import "MGTableView.h"
#import "MGImportTable.h"
#import "HSPopUpList.h"
#import "PyImportWindow.h"

@interface MGImportWindow : NSWindowController
{
    PSMTabBarControl *tabBar;
    NSTabView *tabView;
    NSView *mainView;
    NSPopUpButton *targetAccountsPopup;
    NSPopUpButton *switchDateFieldsPopup;
    NSButton *applySwapToAllCheckbox;
    NSButton *swapButton;
    MGTableView *importTableView;
    
    PyImportWindow *model;
    MGImportTable *importTable;
    HSPopUpList *swapTypePopUp;
    NSInteger tabToRemoveIndex;
}

@property (readwrite, retain) PSMTabBarControl *tabBar;
@property (readwrite, retain) NSTabView *tabView;
@property (readwrite, retain) NSView *mainView;
@property (readwrite, retain) NSPopUpButton *targetAccountsPopup;
@property (readwrite, retain) NSPopUpButton *switchDateFieldsPopup;
@property (readwrite, retain) NSButton *applySwapToAllCheckbox;
@property (readwrite, retain) NSButton *swapButton;
@property (readwrite, retain) MGTableView *importTableView;

- (id)initWithPyRef:(PyObject *)aPyRef;

/* Actions */
- (void)changeTargetAccount;
- (void)importSelectedPane;
- (void)switchDateFields;

/* Python callbacks */
- (void)close;
- (void)closeSelectedTab;
- (void)refreshTabs;
- (void)refreshTargetAccounts;
- (void)show;
- (void)updateSelectedPane;
@end