/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGAccountReassignPanel.h"
#import "MGAccountReassignPanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGAccountReassignPanel

@synthesize accountSelector;

- (id)initWithPyRef:(PyObject *)aPyRef parentWindow:(NSWindow *)aParentWindow
{
    PyAccountReassignPanel *m = [[PyAccountReassignPanel alloc] initWithModel:aPyRef];
    self = [super initWithModel:m parentWindow:aParentWindow];
    [m bindCallbackWithoutView:createCallback(@"PanelView", self)];
    [m release];
    [self setWindow:createMGAccountReassignPanel_UI(self)];
    accountPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] accountList] popupView:accountSelector];
    return self;
}

- (void)dealloc
{
    [accountPopUp release];
    [super dealloc];
}

- (PyAccountReassignPanel *)model
{
    return (PyAccountReassignPanel *)model;
}

/* Override */
- (NSResponder *)firstField
{
    return accountSelector;
}
@end
