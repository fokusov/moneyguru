/* 
Copyright 2015 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.gnu.org/licenses/gpl-3.0.html
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "PyMassEditionPanel.h"
#import "HSTextField.h"
#import "HSComboBox.h"

@interface MGMassEditionPanel : MGPanel {
    NSTextField *dateFieldView;
    NSTextField *descriptionFieldView;
    NSTextField *payeeFieldView;
    NSTextField *checknoFieldView;
    NSTextField *fromFieldView;
    NSTextField *toFieldView;
    NSTextField *amountFieldView;
    NSComboBox *currencyComboBoxView;
    NSButton *dateCheckBox;
    NSButton *descriptionCheckBox;
    NSButton *payeeCheckBox;
    NSButton *checknoCheckBox;
    NSButton *fromCheckBox;
    NSButton *toCheckBox;
    NSButton *amountCheckBox;
    NSButton *currencyCheckBox;
    
    HSTextField *dateField;
    HSTextField *descriptionField;
    HSTextField *payeeField;
    HSTextField *checknoField;
    HSTextField *fromField;
    HSTextField *toField;
    HSTextField *amountField;
    HSComboBox *currencyComboBox;
}

@property (readwrite, retain) NSTextField *dateFieldView;
@property (readwrite, retain) NSTextField *descriptionFieldView;
@property (readwrite, retain) NSTextField *payeeFieldView;
@property (readwrite, retain) NSTextField *checknoFieldView;
@property (readwrite, retain) NSTextField *fromFieldView;
@property (readwrite, retain) NSTextField *toFieldView;
@property (readwrite, retain) NSTextField *amountFieldView;
@property (readwrite, retain) NSComboBox *currencyComboBoxView;
@property (readwrite, retain) NSButton *dateCheckBox;
@property (readwrite, retain) NSButton *descriptionCheckBox;
@property (readwrite, retain) NSButton *payeeCheckBox;
@property (readwrite, retain) NSButton *checknoCheckBox;
@property (readwrite, retain) NSButton *fromCheckBox;
@property (readwrite, retain) NSButton *toCheckBox;
@property (readwrite, retain) NSButton *amountCheckBox;
@property (readwrite, retain) NSButton *currencyCheckBox;

- (id)initWithPyRef:(PyObject *)aPyRef parentWindow:(NSWindow *)aParentWindow;
- (PyMassEditionPanel *)model;
@end
