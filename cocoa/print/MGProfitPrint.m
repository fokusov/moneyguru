/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGProfitPrint.h"
#import "MGConst.h"

@implementation MGProfitPrint
- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"current",@"last",nil];
}
@end