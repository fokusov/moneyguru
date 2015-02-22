/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGIncomeStatement.h"
#import "MGConst.h"
#import "MGAmountCell.h"
#import "MGTextFieldCell.h"

@implementation MGIncomeStatement

- (id)initWithPyRef:(PyObject *)aPyRef view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyRef:aPyRef view:aOutlineView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"name", 200, 16, 0, NO, [MGTextFieldCell class]},
        {@"account_number", 64, 10, 0, NO, nil},
        {@"cash_flow", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta_perc", 60, 10, 0, NO, [MGAmountCell class]},
        {@"last_cash_flow", 100, 10, 0, NO, [MGAmountCell class]},
        {@"budgeted", 100, 10, 0, NO, [MGAmountCell class]},
        nil
    };
    [[self columns] initializeColumns:defs];
    for (NSTableColumn *c in [[self view] tableColumns]) {
        [c setEditable:NO];
    }
    NSTableColumn *c = [[self view] tableColumnWithIdentifier:@"name"];
    [c setEditable:YES]; // Only account name is editable.
    [[self view] setOutlineTableColumn:c];
    c = [[self view] tableColumnWithIdentifier:@"cash_flow"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    NSFontManager *fontManager = [NSFontManager sharedFontManager];
    NSFont *font = [[c dataCell] font];
    font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
    [[c dataCell] setFont:font];
    c = [[self view] tableColumnWithIdentifier:@"delta"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"delta_perc"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"last_cash_flow"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"budgeted"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

@end 
