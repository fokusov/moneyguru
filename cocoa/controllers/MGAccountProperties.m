/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGAccountProperties.h"
#import "MGAccountProperties_UI.h"
#import "MGConst.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGAccountProperties

@synthesize nameTextField;
@synthesize typeSelector;
@synthesize currencySelector;
@synthesize accountNumberTextField;
@synthesize inactiveCheckBox;
@synthesize notesTextField;

- (id)initWithPyRef:(PyObject *)aPyRef parentWindow:(NSWindow *)aParentWindow
{
    PyAccountPanel *m = [[PyAccountPanel alloc] initWithModel:aPyRef];
    self = [super initWithModel:m parentWindow:aParentWindow];
    [m bindCallbackWithoutView:createCallback(@"PanelView", self)];
    [m release];
    [self setWindow:createMGAccountProperties_UI(self)];
    typePopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] typeList] popupView:typeSelector];
    currencyComboBox = [[HSComboBox alloc] initWithPyRef:[[self model] currencyList] view:currencySelector];
    return self;
}

- (void)dealloc
{
    [typePopUp release];
    [currencyComboBox release];
    [super dealloc];
}

- (PyAccountPanel *)model
{
    return (PyAccountPanel *)model;
}

/* Override */
- (NSResponder *)firstField
{
    return nameTextField;
}

- (void)loadFields
{
    [nameTextField setStringValue:[[self model] name]];
    [accountNumberTextField setStringValue:[[self model] accountNumber]];
    [inactiveCheckBox setState:[[self model] isInactive] ? NSOnState : NSOffState];
    [notesTextField setStringValue:[[self model] notes]];
    [currencySelector setEnabled:[[self model] canChangeCurrency]];
}

- (void)saveFields
{
    [[self model] setName:[nameTextField stringValue]];
    [[self model] setAccountNumber:[accountNumberTextField stringValue]];
    [[self model] setInactive:[inactiveCheckBox state] == NSOnState];
    [[self model] setNotes:[notesTextField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"AccountPanel";
}
@end