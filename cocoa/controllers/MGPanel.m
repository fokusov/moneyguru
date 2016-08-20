/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGPanel.h"

@implementation MGPanel

@synthesize releaseOnEndSheet;

- (id)initWithModel:(PyPanel *)aModel parentWindow:(NSWindow *)aParentWindow
{
    self = [super initWithWindow:nil];
    model = [aModel retain];
    parentWindow = aParentWindow;
    customFieldEditor = nil; // instantiated by subclasses
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    releaseOnEndSheet = NO;
    return self;
}

- (void)dealloc
{
    [model release];
    [customDateFieldEditor release];
    [customFieldEditor release];
    [super dealloc];
}

- (PyPanel *)model
{
    return (PyPanel *)model;
}

/* Virtual */
- (NSString *)completionAttrForField:(id)aField
{
    // if textField is a field to perform auto-complete on, return the name of the field for auto-completion
    return nil;
}

- (BOOL)isFieldDateField:(id)aField
{
    return NO;
}

- (NSResponder *)firstField
{
    // The first field to get focus after a load
    return nil;
}

- (void)loadFields
{
}

- (void)saveFields
{
}

/* Public */
- (void)save
{
    [[self model] savePanel];
}

/* Actions */
- (void)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (void)save:(id)sender
{
    [self save];
    [NSApp endSheet:[self window]];
}

/* Delegate */
- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ([self isFieldDateField:asker]) {
        return customDateFieldEditor;
    }
    else {
        NSString *attrname = [self completionAttrForField:asker];
        if (attrname != nil) {
            [customFieldEditor setAttrname:attrname];
            return customFieldEditor;
        }
    }
    return nil;
}

- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
    if (releaseOnEndSheet) {
        [self release];
    }
}

/* Python --> Cocoa */
- (void)preLoad
{
    // If the date field is already the first responder, the date being set will not correctly go down
    // the py widget during makeFirstResponder:
    [[self window] makeFirstResponder:nil];
}

- (void)postLoad
{
    [self loadFields];
    [[self window] makeFirstResponder:[self firstField]];
    [NSApp beginSheet:[self window] modalForWindow:parentWindow modalDelegate:self 
            didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (void)preSave
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [self saveFields];
}
@end