/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

/* Pasteboard types */

#define MGEntryPasteboardType @"MGEntryPasteboardType"
#define MGImportEntryPasteboardType @"MGImportEntryPasteboardType"
#define MGTransactionPasteboardType @"MGTransactionPasteboardType"
#define MGPathsPasteboardType @"MGPathsPasteboardType"

/* Toolbar identifiers */

#define MGDateRangeToolbarItemIdentifier @"MGDateRangeToolbarItemIdentifier"
#define MGMainToolbarIdentifier @"MGMainToolbarIdentifier"
#define MGSearchFieldToolbarItemIdentifier @"MGSearchFieldToolbarItemIdentifier"
#define MGBalanceSheetToolbarItemIdentifier @"MGBalanceSheetToolbarItemIdentifier"
#define MGIncomeStatementToolbarItemIdentifier @"MGIncomeStatementToolbarItemIdentifier"
#define MGTransactionsToolbarItemIdentifier @"MGTransactionsToolbarItemIdentifier"

/* Menu Item Tags */

#define MGNewItemMenuItem 1000
#define MGCloseWindowMenuItem 1001
#define MGCustomSavedRangeStart 2000

/* Errors */

#define MGErrorDomain @"com.hardcoded_software.moneyguru.ErrorDomain"
#define MGFileFormatErrorCode 1
#define MGDemoLimitErrorCode 2
#define MGUnknownErrorCode 3

/* Preferences */

// Others
#define TableFontSize @"TableFontSize"
#define PrintFontSize @"PrintFontSize"

// ScheduleScope **Synced with the core**
#define ScheduleScopeLocal 0
#define ScheduleScopeGlobal 1
#define ScheduleScopeCancel 2

// Synced with the core
#define MGPaneTypeNetWorth 0
#define MGPaneTypeProfit 1
#define MGPaneTypeTransaction 2
#define MGPaneTypeAccount 3
#define MGPaneTypeSchedule 4
#define MGPaneTypeBudget 5
#define MGPaneTypeCashculator 6
#define MGPaneTypeGeneralLedger 7
#define MGPaneTypeDocProps 8
#define MGPaneTypeEmpty 100
#define MGPaneTypePlugin 1000
#define MGPaneTypeReadOnlyTablePlugin 1001

// Synced with the core
#define MGPaneAreaMain 1
#define MGPaneAreaBottomGraph 2
#define MGPaneAreaRightChart 3
