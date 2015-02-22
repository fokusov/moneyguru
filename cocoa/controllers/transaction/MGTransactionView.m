/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGTransactionView.h"
#import "MGTransactionView_UI.h"
#import "MGTransactionPrint.h"
#import "Utils.h"

@implementation MGTransactionView

@synthesize tableView;
@synthesize filterBarView;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyTransactionView *m = [[PyTransactionView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    self.view = createMGTransactionView_UI(self);
    transactionTable = [[MGTransactionTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyRef:[[self model] filterBar] view:filterBarView forEntryTable:NO];
    return self;
}
        
- (void)dealloc
{
    [transactionTable release];
    [filterBar release];
    [super dealloc];
}

- (PyTransactionView *)model
{
    return (PyTransactionView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGTransactionPrint alloc] initWithPyParent:[self model] 
        tableView:[transactionTable tableView]] autorelease];
}

- (NSString *)tabIconName
{
    return @"transaction_table_16";
}

- (id)fieldEditorForObject:(id)asker
{
    return [transactionTable fieldEditorForObject:asker];
}
@end