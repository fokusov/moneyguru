/* 
Copyright 2016 Virgil Dupras

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGEmptyView.h"
#import "MGEmptyView_UI.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGEmptyView

@synthesize pluginTableView;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyEmptyView *m = [[PyEmptyView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    self.view = createMGEmptyView_UI(self);
    pluginList = [[HSSelectableList alloc] initWithPyRef:[[self model] pluginList] tableView:pluginTableView];
    [pluginTableView setTarget:self];
    [pluginTableView setDoubleAction:@selector(selectPluginView)];
    return self;
}
        
- (PyEmptyView *)model
{
    return (PyEmptyView *)model;
}

/* Actions */
- (void)selectNetWorthView
{
    [[self model] selectPaneType:MGPaneTypeNetWorth];
}

- (void)selectProfitView
{
    [[self model] selectPaneType:MGPaneTypeProfit];
}

- (void)selectTransactionView
{
    [[self model] selectPaneType:MGPaneTypeTransaction];
}

- (void)selectScheduleView
{
    [[self model] selectPaneType:MGPaneTypeSchedule];
}

- (void)selectBudgetView
{
    [[self model] selectPaneType:MGPaneTypeBudget];
}

- (void)selectGeneralLedgerView
{
    [[self model] selectPaneType:MGPaneTypeGeneralLedger];
}

- (void)selectDocPropsView
{
    [[self model] selectPaneType:MGPaneTypeDocProps];
}

- (void)selectPluginListView
{
    [[self model] selectPaneType:MGPaneTypePluginList];
}

- (void)selectPluginView
{
    [[self model] openSelectedPlugin];
}
@end