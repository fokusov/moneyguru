/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGTable.h"
#import "Utils.h"

@implementation MGTable
/* MGTableView delegate */
- (NSIndexSet *)selectedIndexes
{
    return [Utils array2IndexSet:[[self model] selectedRows]];
}

- (BOOL)tableView:(NSTableView *)tableView shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    return NO;
}

- (NSString *)dataForCopyToPasteboard
{
    return [[self model] selectionAsCSV];
}

/* Public */
- (MGTableView *)tableView
{
    return (MGTableView *)view;
}
@end
