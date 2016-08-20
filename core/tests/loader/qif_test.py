# Created By: Virgil Dupras
# Created On: 2008-02-15
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from datetime import date

from hscommon.testutil import eq_

from ..base import TestApp, testdata
from ...loader.qif import Loader
from ...model.account import AccountType
from ...model.amount import Amount
from ...model.currency import USD

def test_checkbook_values():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'checkbook.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    # Assets
    eq_(len(accounts), 2)
    account = accounts[0]
    eq_(account.name, 'Account 1')
    eq_(account.currency, USD)
    account = accounts[1]
    eq_(account.name, 'Account 2')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 8)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Starting Balance')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(42.32, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-42.32, USD))
    transaction = transactions[1]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Deposit')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(100, USD))
    eq_(transaction.splits[1].account.name, 'Salary')
    eq_(transaction.splits[1].amount, Amount(-100, USD))
    transaction = transactions[2]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Starting Balance')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(3000, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-3000, USD))
    transaction = transactions[3]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'Withdrawal')
    eq_(transaction.payee, '')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(-60, USD))
    eq_(transaction.splits[1].account.name, 'Cash')
    eq_(transaction.splits[1].amount, Amount(60, USD))
    transaction = transactions[4]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'Power Bill')
    eq_(transaction.payee, 'Hydro-Quebec')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(-57.12, USD))
    eq_(transaction.splits[1].account.name, 'Utilities')
    eq_(transaction.splits[1].amount, Amount(57.12, USD))
    transaction = transactions[5]
    eq_(transaction.date, date(2007, 1, 5))
    eq_(transaction.description, 'Interest')
    eq_(transaction.payee, 'My Bank')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(8.92, USD))
    eq_(transaction.splits[1].account.name, 'Interest')
    eq_(transaction.splits[1].amount, Amount(-8.92, USD))
    transaction = transactions[6]
    eq_(transaction.date, date(2007, 2, 4))
    eq_(transaction.description, 'Transfer')
    eq_(transaction.payee, 'Account 2')
    eq_(transaction.splits[0].account.name, 'Account 1')
    eq_(transaction.splits[0].amount, Amount(80.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-80.00, USD))
    transaction = transactions[7]
    eq_(transaction.date, date(2007, 2, 4))
    eq_(transaction.description, 'Transfer')
    eq_(transaction.payee, 'Account 1')
    eq_(transaction.splits[0].account.name, 'Account 2')
    eq_(transaction.splits[0].amount, Amount(-80.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(80.00, USD))

def test_missing_values():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'missing_fields.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.name, 'Account')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 3)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))
    eq_(transaction.description, 'Complete Entry')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    eq_(transaction.splits[1].account.name, 'Category')
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))
    transaction = transactions[1]
    eq_(transaction.date, date(2007, 1, 2))
    eq_(transaction.description, 'No Category')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    assert transaction.splits[1].account is None
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))
    transaction = transactions[2]
    eq_(transaction.date, date(2007, 1, 4))
    eq_(transaction.description, '')
    eq_(transaction.splits[0].account.name, 'Account')
    eq_(transaction.splits[0].amount, Amount(100.00, USD))
    eq_(transaction.splits[1].account.name, 'Category')
    eq_(transaction.splits[1].amount, Amount(-100.00, USD))

def test_four_digit_year():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'four_digit_year.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 1))

def test_ddmmyy():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'ddmmyy.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_ddmmyyyy():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'ddmmyyyy.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_ddmmyyyy_with_dots():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'ddmmyyyy_with_dots.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_yyyymmdd_without_sep():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'yyyymmdd_without_sep.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_yyyymmdd_with_sep():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'yyyymmdd_with_sep.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 1, 22))

def test_chr13_line_sep():
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'chr13_line_sep.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    transactions = loader.transaction_infos
    eq_(len(transactions), 1)
    transaction = transactions[0]
    eq_(transaction.date, date(2007, 2, 27))

def test_first_field_not_account():
    # Previously, when the first field was not an account, a dummy "Account" field was added
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'first_field_not_account.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)

def test_accountless_with_splits():
    # Previously, the split amounts would be reversed
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'accountless_with_splits.qif'))
    loader.load()
    accounts = [a for a in loader.accounts if a.is_balance_sheet_account()]
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.name, 'Account')
    eq_(account.currency, USD)
    transactions = loader.transactions
    eq_(len(transactions), 2)
    transaction = transactions[0]
    eq_(transaction.date, date(2008, 8, 28))
    eq_(transaction.description, 'You\'ve got a payment')
    eq_(transaction.payee, 'Virgil Dupras')
    eq_(len(transaction.splits), 3)
    transaction = transactions[1]
    eq_(len(transaction.splits), 3)

def test_other_sections():
    # Previously, other sections would confuse the qif loader
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'other_sections.qif'))
    loader.load()
    eq_(len(loader.transactions), 3)

def test_missing_line_sep():
    # It is possible sometimes that some apps do bad exports that contain some missing line
    # separators Make sure that it doesn't prevent the QIF from being loaded
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'missing_line_sep.qif'))
    loader.load()
    eq_(len(loader.transactions), 1)
    eq_(loader.transactions[0].splits[0].amount, Amount(42.32, USD))

def test_credit_card():
    # A CCard account is imported as a liability
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'credit_card.qif'))
    loader.load()
    accounts = loader.account_infos
    eq_(len(accounts), 1)
    account = accounts[0]
    eq_(account.type, AccountType.Liability)

def test_autoswitch():
    # autoswitch.qif has an autoswitch section with accounts containing "D" lines
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'autoswitch.qif'))
    loader.load()
    eq_(len(loader.account_infos), 50)
    eq_(len(loader.transaction_infos), 37)

def test_autoswitch_buggy():
    # sp,eQIF exporter put another !Option:AutoSwitch after having cleared it
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'autoswitch_buggy.qif'))
    loader.load()
    eq_(len(loader.account_infos), 50)
    eq_(len(loader.transaction_infos), 37)

def test_autoswitch_none():
    # Some QIF files don't have the autoswitch flag to indicate a list of accounts. The loader used
    # to crash when such an account block would contain a "D" line that couldn't parse to a date.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'autoswitch_none.qif'))
    loader.load() # no crash
    # We don't test for account_info because in such buggy cases, we don't care much. We only care
    # that transactions are correctly loaded.
    eq_(len(loader.transaction_infos), 1)

def test_with_cat():
    # some file have a "!Type:Cat" section with buggy "D" lines
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'with_cat.qif'))
    loader.load()
    eq_(len(loader.account_infos), 1)
    eq_(len(loader.transaction_infos), 1)

def test_transfer():
    # Transfer happen with 2 entries putting [] brackets arround the account names of the 'L'
    # sections.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'transfer.qif'))
    loader.load()
    eq_(len(loader.accounts), 2)
    eq_(len(loader.transactions), 1)

def test_extra_dline():
    # Ignore extra D lines which don't contain dates. Previously, these lines would cause a crash.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'extra_dline.qif'))
    loader.load() # no crash
    eq_(len(loader.transactions), 1)
    txn = loader.transactions[0]
    eq_(txn.date, date(2010, 8, 7))

def test_transfer_space_in_account_names():
    # When "L" lines have a space character at the end (bfore the "]" bracket) it doesn't prevent
    # us from correctly matching the account with seen account names.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'transfer_space_in_account_names.qif'))
    loader.load()
    eq_(len(loader.transactions), 1) # the transactions hasn't been doubled.

def test_export_to_qif(tmpdir):
    # When there's a transfer between 2 assets, export all entries (otherwise some apps will import
    # the QIF wrongly)
    app = TestApp()
    app.add_account('first')
    app.add_account('second')
    app.show_account()
    app.add_entry(date='03/01/2009', description='transfer', transfer='first', increase='42')
    export_filename = str(tmpdir.join('export.qif'))
    app.mw.export()
    expanel = app.get_current_panel()
    expanel.export_path = export_filename
    expanel.save()
    exported = open(export_filename).read()
    reference = open(testdata.filepath('qif', 'export_ref_transfer.qif')).read()
    eq_(exported, reference)

def test_transfer_splits():
    # The transfer_splits file has a split between 3 accounts. The particularity in this is that
    # the account references are placed in [] brackets. There was a bug where bracketed links were
    # correctly handled in "L" lines, but not in split lines.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'transfer_splits.qif'))
    loader.load()
    eq_(len(loader.accounts), 3)
    eq_(len(loader.transactions), 1)

def test_quicken_split_duplicate():
    # Quicken's QIF have an annoying peculiarity: entries that are supposed to match to each other
    # don't have the same split count. In this example, we have a 3 way split (Checking:-1000,
    # Home:500, Interest:500) but the first split we encounter is only two way (Checking:-500,
    # Home:500). What we have to do is to only keep the largest in a group of matching txns.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'quicken_split_duplicate.qif'))
    loader.load()
    eq_(len(loader.transactions), 1)
    eq_(len(loader.transactions[0].splits), 3)

def test_same_date_same_amount():
    # There was a bug in QIF loading where two transactions with the same date and the same amount,
    # regardless of whether they were transfers, would be detected as "duplicates" and de-duplicated.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'same_date_same_amount.qif'))
    loader.load()
    eq_(len(loader.transactions), 3)

def test_same_date_same_amount_transfer():
    # Previously, our test file had two transfer transactions in it, but it turned out that it
    # wasn't enough because, depending on the algo's internal dictionary iteration order (which is
    # random), the test here would falsely pass. Now, with 3 transactions, it's much less likely to
    # falsely pass.
    loader = Loader(USD)
    loader.parse(testdata.filepath('qif', 'same_date_same_amount_transfer.qif'))
    loader.load()
    expected_descs = {
        'Transfer 1, Date 1, Amount 1',
        'Transfer 2, Date 1, Amount 1',
        'Transfer 3, Date 1, Amount 1',
    }
    actual_descs = {txn.description for txn in loader.transactions}
    eq_(actual_descs, expected_descs)

