/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGAccountSheetView.h"
#import "MGConst.h"
#import "MGAccountProperties.h"
#import "MGAccountReassignPanel.h"
#import "HSPyUtil.h"
#import "Utils.h"

@implementation MGAccountSheetView

@synthesize mainSplitView;
@synthesize subSplitView;
@synthesize outlineView;
@synthesize pieChartsView;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyAccountSheetView *m = [[PyAccountSheetView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"BaseViewView", self)];
    [m release];
    return self;
}

/* Override */
- (PyAccountSheetView *)model
{
    return (PyAccountSheetView *)model;
}

- (void)applySubviewsSizeRestoration
{
    if ([self.model graphHeightToRestore] > 0) {
        [mainSplitView setPosition:NSHeight([mainSplitView frame])-[self.model graphHeightToRestore] ofDividerAtIndex:0];
        graphCollapsed = NO;
    }
    if ([self.model pieWidthToRestore] > 0) {
        [subSplitView setPosition:NSWidth([subSplitView frame])-[self.model pieWidthToRestore] ofDividerAtIndex:0];
        pieCollapsed = NO;
    }
    [self updateVisibility];
}

/* Delegate */

- (CGFloat)splitView:(NSSplitView *)splitView constrainMinCoordinate:(CGFloat)proposedMin ofSubviewAt:(NSInteger)dividerIndex
{
    if (splitView == mainSplitView) {
        return 200;
    }
    else if (splitView == subSplitView) {
        return 100;
    }
    return proposedMin;
}

- (CGFloat)splitView:(NSSplitView *)splitView constrainMaxCoordinate:(CGFloat)proposedMax ofSubviewAt:(NSInteger)dividerIndex
{
    if (splitView == mainSplitView) {
        return NSHeight([splitView frame]) - 130;
    }
    else if (splitView == subSplitView) {
        return NSWidth([splitView frame]) - 170;
    }
    return proposedMax;
}

- (BOOL)splitView:(NSSplitView *)splitView canCollapseSubview:(NSView *)subview
{
    if (subview == pieChartsView) {
        return pieCollapsed;
    }
    if (subview == graphView) {
        return graphCollapsed;
    }
    return NO;
}

/* model --> view */
- (PyObject *)createPanelWithModelRef:(PyObject *)aPyRef name:(NSString *)name
{
    MGPanel *panel;
    if ([name isEqual:@"AccountReassignPanel"]) {
        panel = [[MGAccountReassignPanel alloc] initWithPyRef:aPyRef parentWindow:[[self view] window]];
    }
    else {
        panel = [[MGAccountProperties alloc] initWithPyRef:aPyRef parentWindow:[[self view] window]];
    }
    panel.releaseOnEndSheet = YES;
    return [[panel model] pyRef];
}

- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    BOOL pieVisible = ![hiddenAreas containsIndex:MGPaneAreaRightChart];
    if (graphVisible) {
        if (graphCollapsed) {
            graphCollapsed = NO;
            CGFloat pos = NSHeight([mainSplitView frame])- graphCollapseHeight - [mainSplitView dividerThickness];
            [mainSplitView setPosition:pos ofDividerAtIndex:0];
        }
    }
    else {
        if (!graphCollapsed) {
            graphCollapsed = YES;
            graphCollapseHeight = NSHeight([graphView frame]);
            [mainSplitView setPosition:NSHeight([mainSplitView frame]) ofDividerAtIndex:0];
        }
    }
    if (pieVisible) {
        if (pieCollapsed) {
            pieCollapsed = NO;
            CGFloat pos = NSWidth([subSplitView frame])- pieCollapseWidth - [subSplitView dividerThickness];
            [subSplitView setPosition:pos ofDividerAtIndex:0];
        }
    }
    else {
        if (!pieCollapsed) {
            pieCollapsed = YES;
            pieCollapseWidth = NSWidth([pieChartsView frame]);
            [subSplitView setPosition:NSWidth([subSplitView frame]) ofDividerAtIndex:0];
        }
    }
}
@end