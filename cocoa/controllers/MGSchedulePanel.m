/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGSchedulePanel.h"
#import "MGSchedulePanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGSchedulePanel

@synthesize tabView;
@synthesize startDateField;
@synthesize repeatEveryField;
@synthesize repeatEveryDescLabel;
@synthesize repeatTypePopUpView;
@synthesize stopDateField;
@synthesize descriptionField;
@synthesize payeeField;
@synthesize checknoField;
@synthesize notesField;
@synthesize splitTableView;

- (id)initWithPyRef:(PyObject *)aPyRef parentWindow:(NSWindow *)aParentWindow
{
    PySchedulePanel *m = [[PySchedulePanel alloc] initWithModel:aPyRef];
    self = [super initWithModel:m parentWindow:aParentWindow];
    [m bindCallbackWithoutView:createCallback(@"SchedulePanelView", self)];
    [m release];
    [self setWindow:createMGSchedulePanel_UI(self)];
    splitTable = [[MGSplitTable alloc] initWithPyRef:[[self model] splitTable] tableView:splitTableView];
    repeatTypePopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] repeatTypeList] popupView:repeatTypePopUpView];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)dealloc
{
    [repeatTypePopUp release];
    [splitTable release];
    [super dealloc];
}

- (PySchedulePanel *)model
{
    return (PySchedulePanel *)model;
}

/* MGPanel Override */
- (NSString *)completionAttrForField:(id)aField
{
    if (aField == descriptionField) {
        return @"description";
    }
    else if (aField == payeeField) {
        return @"payee";
    }
    else if (aField == splitTableView) {
        NSString *name = [splitTable editedFieldname];
        if ((name != nil) && ([name isEqualTo:@"account"])) {
            return @"account";
        }
    }
    return nil;
}

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
    [tabView selectFirstTabViewItem:self];
    [startDateField setStringValue:[[self model] startDate]];
    [stopDateField setStringValue:[[self model] stopDate]];
    [repeatEveryField setIntegerValue:[[self model] repeatEvery]];
    [descriptionField setStringValue:[[self model] description]];
    [payeeField setStringValue:[[self model] payee]];
    [checknoField setStringValue:[[self model] checkno]];
    [notesField setStringValue:[[self model] notes]];
    [splitTable refresh];
}

- (void)saveFields
{
    [[self model] setStartDate:[startDateField stringValue]];
    [[self model] setStopDate:[stopDateField stringValue]];
    [[self model] setRepeatEvery:[repeatEveryField intValue]];
    [[self model] setDescription:[descriptionField stringValue]];
    [[self model] setPayee:[payeeField stringValue]];
    [[self model] setCheckno:[checknoField stringValue]];
    [[self model] setNotes:[notesField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"SchedulePanel";
}

/* Actions */
- (void)addSplit
{
    [[splitTable model] add];
}

- (void)deleteSplit
{
    [[splitTable model] deleteSelectedRows];
}

- (void)clearStopDate
{
    [[self model] setStopDate:@""];
    [stopDateField setStringValue:[[self model] stopDate]];
}

/* Python --> Cocoa */
- (void)refreshForMultiCurrency
{
}

- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self model] repeatEveryDesc]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    if (control == repeatEveryField) {
        // must be edited right away to update the desc label
        [[self model] setRepeatEvery:[repeatEveryField intValue]];
    }
    else if (control == startDateField) {
        // must be edited right away to update the repeat options
        [[self model] setStartDate:[startDateField stringValue]];
    }
    // for the repeatType field, it's handled in repeatTypeSelected:
}
@end
