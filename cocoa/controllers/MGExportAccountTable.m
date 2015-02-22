/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGExportAccountTable.h"
#import "MGTableView.h"

@implementation MGExportAccountTable
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView
{
    self = [super initWithPyRef:aPyRef tableView:aTableView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"name", 100, 20, 0, NO, nil},
        {@"export", 60, 60, 60, NO, [NSButtonCell class]},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"name"];    
    [c setResizingMask:NSTableColumnAutoresizingMask];
    c = [[self tableView] tableColumnWithIdentifier:@"export"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    [c setResizingMask:NSTableColumnNoResizing];
    [[self tableView] sizeToFit];
}
@end