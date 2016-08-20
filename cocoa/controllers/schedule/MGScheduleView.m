/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGScheduleView.h"
#import "MGSchedulePrint.h"
#import "MGSchedulePanel.h"
#import "HSPyUtil.h"
#import "Utils.h"

@implementation MGScheduleView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyScheduleView *m = [[PyScheduleView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"BaseViewView", self)];
    [m release];
    tableView = [[MGTableView alloc] initWithFrame:NSMakeRect(0, 0, 100, 100)];
    [self setupTableView:tableView];
    mainResponder = tableView;
    self.view = [tableView wrapInScrollView];
    scheduleTable = [[MGScheduleTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    [tableView release];
    return self;
}
        
- (void)dealloc
{
    [scheduleTable release];
    [super dealloc];
}

- (PyScheduleView *)model
{
    return (PyScheduleView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGSchedulePrint alloc] initWithPyParent:[self model] 
        tableView:[scheduleTable tableView]] autorelease];
}

- (NSString *)tabIconName
{
    return @"schedules_16";
}

- (PyObject *)createPanelWithModelRef:(PyObject *)aPyRef name:(NSString *)name
{
    MGSchedulePanel *panel = [[MGSchedulePanel alloc] initWithPyRef:aPyRef parentWindow:[[self view] window]];
    panel.releaseOnEndSheet = YES;
    return [[panel model] pyRef];
}
@end