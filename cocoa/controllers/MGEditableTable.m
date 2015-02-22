/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGEditableTable.h"
#import "Utils.h"

@implementation MGEditableTable
- (id)initWithModel:(PyTable *)aModel tableView:(MGTableView *)aTableView
{
    self = [super initWithModel:aModel tableView:aTableView];
    customFieldEditor = nil; // created by subclasses;
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (id)initWithPyRef:(PyObject *)aPyRef tableView:(MGTableView *)aTableView
{
    self = [super initWithPyRef:aPyRef tableView:aTableView];
    customFieldEditor = nil; // created by subclasses;
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (void)dealloc
{
    [customFieldEditor release];
    [customDateFieldEditor release];
    [super dealloc];
}

/* Data source */
- (void)tableView:(NSTableView *)tableView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    [[self model] setValue:value forColumn:[column identifier] row:row];
}

/* Delegate */
- (BOOL)tableView:(NSTableView *)tableView shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    return n2b([[self model] canEditColumn:[column identifier] atRow:row]);
}

- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    [[self model] deleteSelectedRows];
    return YES;
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [[self tableView] startEditing];
    return YES;
}

// This is never called on edition cancel (pressing ESC) or stopEditing call
- (void)tableViewDidEndEditing:(MGTableView *)tableView
{
    [[self model] saveEdits];
}

- (void)tableViewCancelsEdition:(MGTableView *)tableView
{
    [[self model] cancelEdits];
}

- (id)fieldEditorForObject:(id)asker
{
    if (asker == [self tableView]) {   
        NSInteger editedColumn = [[self tableView] editedColumn];
        if (editedColumn > -1) {
            NSTableColumn *column = [[[self tableView] tableColumns] objectAtIndex:editedColumn];
            NSString *name = [column identifier];
            if ([[self dateColumns] containsObject:name]) {
                return customDateFieldEditor;
            }
            else if ([[self completableColumns] containsObject:name]) {
                [customFieldEditor setAttrname:name];
                return customFieldEditor;
            }
        }
    }
    return nil;
}

/* Virtual */
- (NSArray *)dateColumns
{
    return [NSArray array];
}

- (NSArray *)completableColumns
{
    return [NSArray array];
}

/* Public */
- (void)startEditing
{
    [[self tableView] startEditing];
}

- (void)stopEditing
{
    [[self tableView] stopEditing];
}

- (NSString *)editedFieldname
{
    NSInteger editedColumn = [[self tableView] editedColumn];
    if (editedColumn > -1) {
        NSTableColumn *column = [[[self tableView] tableColumns] objectAtIndex:editedColumn];
        return [column identifier];
    }
    return nil;
}
@end
