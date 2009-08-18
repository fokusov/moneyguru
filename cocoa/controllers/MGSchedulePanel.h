/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGSplitTable.h"
#import "MGWindowController.h"
#import "PySchedulePanel.h"

@interface MGSchedulePanel : MGWindowController {
    IBOutlet MGTextField *startDateField;
    IBOutlet MGTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet MGTextField *stopDateField;
    IBOutlet MGTextField *descriptionField;
    IBOutlet MGTextField *payeeField;
    IBOutlet MGTextField *checknoField;
    IBOutlet MGSplitTable *splitTable;
    
    NSTextView *customFieldEditor;
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PySchedulePanel *)py;
/* Methods */
- (BOOL)canLoad;
- (void)load;
- (void)new;
- (void)save;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)save:(id)sender;
- (IBAction)repeatTypeSelected:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
- (void)refreshRepeatOptions;
@end