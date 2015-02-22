/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGBarGraph.h"

@implementation MGBarGraph
- (id)initWithPyRef:(PyObject *)aPyRef
{
    MGBarGraphView *myview = [[MGBarGraphView alloc] init];
    self = [super initWithPyRef:aPyRef];
    [self setView:[myview autorelease]];
    return self;
}
@end
