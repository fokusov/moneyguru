/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import "MGDateFieldEditor.h"
#import "Utils.h"

@implementation MGDateFieldEditor
- (id)init
{
    self = [super initWithFrame:NSMakeRect(0, 0, 0, 0)];
    py = [[PyDateWidget alloc] init];
    [self setEditable:YES];
    [self setFieldEditor:YES];
    [self setSelectable:YES];
    [self refresh];
    return self;
}

- (void)dealloc
{
    [py release];
    [super dealloc];
}

- (void)deleteForward:(id)sender
{
    [py backspace];
    [self refresh];
}

- (void)deleteBackward:(id)sender
{
    [py backspace];
    [self refresh];
}

- (void)moveUp:(id)sender 
{
    [py increase];
    [self refresh];
}

- (void)moveDown:(id)sender
{
    [py decrease];
    [self refresh];
}

- (void)moveLeft:(id)sender 
{
    [py left];
    [self refresh];
}

- (void)moveRight:(id)sender
{
    [py right];
    [self refresh];
}

- (void)insertText:(NSString *)text
{
    [py type:text];
    [self refresh];
}

/* Override */

- (BOOL)becomeFirstResponder
{
    BOOL result = [super becomeFirstResponder];
    [py setDate:[self string]]; // set the initial date
    // This is rather hacking, but I couldn't find any other alternative. If tabbed in, all the 
    // text is selected, if clicked in, nothing is selected, and this all happense somewhere
    // *after* becomeFirstResponder
    [self performSelector:@selector(refresh) withObject:self afterDelay:0];
    return result;
}

- (BOOL)resignFirstResponder
{
    [py exit];
    [self refresh];
    return [super resignFirstResponder];
}

/* Methods */

- (void)refresh
{
    NSString *old = [self string];
    NSString *new = [py text];
    BOOL changed = ([old length] > 0) && (![old isEqualTo:new]);
    // We *have* to call shouldChangeTextInRange: for the system to work. if we don't, the editor
    // will not set its state as "changed"
    if ((changed) && (![self shouldChangeTextInRange:NSMakeRange(0, [old length]) replacementString:new]))
    {
        // The delegate doesn't want us to do the change
        return;
    }
    [self setString:new];
    NSArray *sel = [py selection];
    NSInteger start = n2i([sel objectAtIndex:0]);
    NSInteger end = n2i([sel objectAtIndex:1]);
    [self setSelectedRange:NSMakeRange(start, end - start + 1)];
    if (changed)
    {
        [self didChangeText];
    }
}
@end
