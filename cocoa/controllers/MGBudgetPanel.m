/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGBudgetPanel.h"
#import "MGBudgetPanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGBudgetPanel

@synthesize startDateField;
@synthesize repeatEveryField;
@synthesize repeatEveryDescLabel;
@synthesize repeatTypePopUpView;
@synthesize stopDateField;
@synthesize accountSelector;
@synthesize targetSelector;
@synthesize amountField;
@synthesize notesField;

- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyBudgetPanel *m = [[PyBudgetPanel alloc] initWithModel:[[aParent model] budgetPanel]];
    self = [super initWithModel:m parent:aParent];
    [m bindCallback:createCallback(@"BudgetPanelView", self)];
    [m release];
    [self setWindow:createMGBudgetPanel_UI(self)];
    repeatTypePopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] repeatTypeList] popupView:repeatTypePopUpView];
    accountPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] accountList] popupView:accountSelector];
    targetPopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] targetList] popupView:targetSelector];
    return self;
}

- (void)dealloc
{
    [repeatTypePopUp release];
    [super dealloc];
}

- (PyBudgetPanel *)model
{
    return (PyBudgetPanel *)model;
}

/* Override */
- (BOOL)isFieldDateField:(id)aField
{
    return (aField == startDateField) || (aField == stopDateField);
}

- (NSResponder *)firstField
{
    return startDateField;
}

- (void)loadFields
{
    [startDateField setStringValue:[[self model] startDate]];
    [stopDateField setStringValue:[[self model] stopDate]];
    [repeatEveryField setIntegerValue:[[self model] repeatEvery]];
    [amountField setStringValue:[[self model] amount]];
    [notesField setStringValue:[[self model] notes]];
}

- (void)saveFields
{
    [[self model] setStartDate:[startDateField stringValue]];
    [[self model] setStopDate:[stopDateField stringValue]];
    [[self model] setRepeatEvery:[repeatEveryField intValue]];
    [[self model] setAmount:[amountField stringValue]];
    [[self model] setNotes:[notesField stringValue]];
}

/* Python --> Cocoa */
- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self model] repeatEveryDesc]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    if (control == repeatEveryField) // must be edited right away to update the desc label
        [[self model] setRepeatEvery:[repeatEveryField intValue]];
    else if (control == startDateField) // must be edited right away to update the repeat options
        [[self model] setStartDate:[startDateField stringValue]];
}

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ((asker == startDateField) || (asker == stopDateField))
        return customDateFieldEditor;
    return nil;
}
@end