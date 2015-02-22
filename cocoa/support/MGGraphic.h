/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/


#define SIMPLE_LINE(x1, y1, x2, y2, width)\
{\
NSBezierPath *path = [NSBezierPath bezierPath];\
[path moveToPoint:NSMakePoint(x1, y1)];\
[path lineToPoint:NSMakePoint(x2, y2)];\
[path setLineWidth:width];\
[path stroke];\
}
