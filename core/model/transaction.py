# Created By: Eric Mc Sween
# Created On: 2008-03-04
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import time
from collections import defaultdict
from copy import copy
import datetime

from hscommon.util import allsame, first, nonone, stripfalse

from ..const import NOEDIT
from .amount import Amount, convert_amount, same_currency, of_currency

class Transaction:
    """A movement of money between two or more accounts at a specific date.

    Money movements that a transaction implies are listed in :attr:`splits`. The splits of a
    transaction *always balance*, which means that the sum of amounts in its splits is always zero.

    Whenever a potentially unbalancing operation is made on the splits, call :meth:`balance` to
    balance the transaction out.

    Initialization arguments are mostly just directly assigned to their relevant attributes in the
    transaction, except for ``account`` and ``amount`` (there is no such attributes). If specified,
    we initialize what would otherwise be an empty split list with two splits: One adding ``amount``
    to ``account``, and the other adding ``-amount`` to ``None`` (an unassigned split).
    """
    def __init__(self, date, description=None, payee=None, checkno=None, account=None, amount=None):
        #: Date at which the transation occurs.
        self.date = date
        #: Description of the transaction.
        self.description = nonone(description, '')
        #: Person or entity related to the transaction.
        self.payee = nonone(payee, '')
        #: Check number related to the transaction.
        self.checkno = nonone(checkno, '')
        #: Freeform note about the transaction.
        self.notes = ''
        if amount is not None:
            self.splits = [Split(self, account, amount), Split(self, None, -amount)]
        else:
            #: The list of :class:`Split` affecting this transaction. These splits always balance.
            self.splits = []
        #: Ordering attributes. When two transactions have the same date, we order them with this.
        self.position = 0
        #: Timestamp of the last modification. Used in the UI to let the user sort his transactions.
        #: This is useful for finding a mistake that we know was introduced recently.
        self.mtime = 0

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.date, self.description)

    @classmethod
    def from_transaction(cls, transaction):
        """Create a copy of ``transaction`` and returns it.

        The goal here is to have a deepcopy of ``transaction``, but *without copying the accounts*.
        We want the splits to link to the same :class:`.Account` instances.
        """
        txn = transaction
        result = cls(txn.date, txn.description, txn.payee, txn.checkno)
        result.notes = txn.notes
        result.position = txn.position
        result.mtime = txn.mtime
        for split in txn.splits:
            newsplit = copy(split)
            newsplit.transaction = result
            result.splits.append(newsplit)
        return result

    def amount_for_account(self, account, currency):
        """Returns the total sum attributed to ``account``.

        All amounts are converted to ``currency`` before doing the sum. This is needed because we
        might have amounts with different currencies here.

        :param account: :class:`.Account`
        :param currency: :class:`.Currency`

        .. seealso:: :func:`.convert_amount`
        """
        splits = (s for s in self.splits if s.account is account)
        return sum(convert_amount(s.amount, currency, self.date) for s in splits)

    def affected_accounts(self):
        """Returns a set of all accounts affected by self.

        ... meaning all accounts references by our :attr:`splits`.
        """
        return set(s.account for s in self.splits if s.account is not None)

    def assign_imbalance(self, target_split):
        """Assigns remaining imbalance to the selected split.

        If the ``target_split`` is not an assigned split, does nothing.
        """
        if target_split.account is None:
            return
        unassigned = [
            split for split in self.splits
            if split.account is None and split.amount
        ]
        if not unassigned:
            return
        if target_split.amount:
            target_currency = target_split.amount.currency
        else:
            # Use whatever is the currency of the first split to show up
            target_currency = unassigned[0].amount.currency
        unassigned = [split for split in unassigned if split.amount.currency == target_currency]
        amount = sum(split.amount for split in unassigned)
        target_split.amount += amount
        for split in unassigned:
            self.splits.remove(split)

    def balance(self, strong_split=None, keep_two_splits=False):
        """Balance out :attr:`splits` if needed.

        A balanced transaction has all its splits making a zero sum. Balancing a transaction is
        rather easy: We sum all our splits and create an unassigned split of the opposite of that
        amount. To avoid polluting our splits, we look if we already have an unassigned split and,
        if we do, we adjust its amount instead of creating a new split.

        There's a special case to that rule, and that is when we have two splits. When those two
        splits are on the same "side" (both positive or both negative), we assume that the user has
        just reversed ``strong_split``'s side and that the logical next step is to also reverse the
        other split (the "weak" split), which we'll do.

        If ``keep_two_splits`` is true, we'll go one step further and adjust the weak split's amount
        to fit what was just entered in the strong split. If it's false, we'll create an unassigned
        split if needed.

        Easy, right? Things get a bit more complicated when a have a
        :ref:`multi-currency transaction <multi-currency-txn>`. When that happens, we do a more
        complicated balancing, which happens in :meth:`balance_currencies`.

        :param strong_split: The split that was last edited. The reason why we're balancing the
                             transaction now. If set, it will not be adjusted by the balancing
                             because we don't want to pull the rug from under our user's feet and
                             undo an edit he's just made.
        :type strong_split: :class:`Split`
        :param bool keep_two_splits: If set and if we have a two-split transaction, we'll keep it
                                     that way, adjusting the "weak" split amount as needed.
        """
        if len(self.splits) == 2 and strong_split is not None:
            weak_split = self.splits[0] if self.splits[0] is not strong_split else self.splits[1]
            if keep_two_splits:
                weak_split.amount = -strong_split.amount
            elif (weak_split.amount > 0) == (strong_split.amount > 0): # on the same side
                weak_split.amount *= -1
        splits_with_amount = [s for s in self.splits if s.amount]
        if splits_with_amount and not allsame(s.amount.currency for s in splits_with_amount):
            self.balance_currencies(strong_split)
            return
        imbalance = sum(s.amount for s in self.splits)
        if not imbalance:
            return
        is_unassigned = lambda s: s.account is None and s is not strong_split
        imbalance = sum(s.amount for s in self.splits)
        if imbalance:
            unassigned = first(s for s in self.splits if is_unassigned(s))
            if unassigned is not None:
                unassigned.amount -= imbalance
            else:
                self.splits.append(Split(self, None, -imbalance))
        for split in self.splits[:]:
            if is_unassigned(split) and split.amount == 0:
                self.splits.remove(split)

    def balance_currencies(self, strong_split=None):
        """Balances a :ref:`multi-currency transaction <multi-currency-txn>`.

        Balancing out multi-currencies transasctions can be real easy because we consider that
        currencies can never mix (and we would never make the gross mistake of using market exchange
        rates to do our balancing), so, if we have at least one split on each side of different
        currencies, we consider ourselves balanced and do nothing.

        However, we might be in a situation of "logical imbalance", which means that the transaction
        doesn't logically makes sense. For example, if all our splits are on the same side, we can't
        possibly balance out. If we have EUR and CAD splits, that CAD splits themselves balance out
        but that EUR splits are all on the same side, we have a logical imbalance.

        This method finds those imbalance and fix them by creating unsassigned splits balancing out
        every currency being in that situation.

        :param strong_split: The split that was last edited. See :meth:`balance`.
        :type strong_split: :class:`Split`
        """
        splits_with_amount = [s for s in self.splits if s.amount != 0]
        if not splits_with_amount:
            return
        currency2balance = defaultdict(int)
        for split in splits_with_amount:
            currency2balance[split.amount.currency] += split.amount
        imbalanced = stripfalse(currency2balance.values()) # filters out zeros (balances currencies)
        # For a logical imbalance to be possible, all imbalanced amounts must be on the same side
        if imbalanced and allsame(amount > 0 for amount in imbalanced):
            unassigned = [s for s in self.splits if s.account is None and s is not strong_split]
            for amount in imbalanced:
                split = first(s for s in unassigned if s.amount == 0 or s.amount.currency == amount.currency)
                if split is not None:
                    if split.amount == amount: # we end up with a null split, remove it
                        self.splits.remove(split)
                    else:
                        split.amount -= amount # adjust
                else:
                    self.splits.append(Split(self, None, -amount))

    def change(
            self, date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT, from_=NOEDIT,
            to=NOEDIT, amount=NOEDIT, currency=NOEDIT, notes=NOEDIT):
        """Changes our transaction and do all proper stuff.

        Sets all specified arguments to their specified values and do proper adjustments, such as
        making sure that our :attr:`Split.reconciliation_date` still make sense and updates our
        :attr:`mtime`.

        Moreover, it offers a convenient interface to specify a two-way transaction with ``from_``,
        ``to`` and ``amount``. When those are set, we'll set up splits corresponding to this two-way
        money movement.

        If ``currency`` is set, it changes the currency of the amounts in all :attr:`splits`,
        without conversion with exchange rates. Amounts are kept intact.

        :param date: ``datetime.date``
        :param description: ``str``
        :param payee: ``str``
        :param checkno: ``str``
        :param from_: :class:`.Account`
        :param to: :class:`.Account`
        :param amount: :class:`.Amount`
        :param currency: :class:`.Currency`
        :param notes: ``str``
        """
        # from_ and to are Account instances
        if date is not NOEDIT:
            # If reconciliation dates were equal to txn date, make it follow
            for split in self.splits:
                if split.reconciliation_date == self.date:
                    split.reconciliation_date = date
            # If the new date is in the future, we de-reconcile the splits
            if date > datetime.date.today():
                for split in self.splits:
                    split.reconciliation_date = None
            self.date = date
        if description is not NOEDIT:
            self.description = description
        if payee is not NOEDIT:
            self.payee = payee
        if checkno is not NOEDIT:
            self.checkno = checkno
        if notes is not NOEDIT:
            self.notes = notes
        # the amount field has to be set first so that splitted_splits() is not confused by splits
        # with no amount.
        if (amount is not NOEDIT) and self.can_set_amount:
            self.amount = abs(amount)
        if from_ is not NOEDIT:
            fsplits, _ = self.splitted_splits()
            if len(fsplits) == 1:
                fsplit = fsplits[0]
                fsplit.account = from_
        if to is not NOEDIT:
            _, tsplits = self.splitted_splits()
            if len(tsplits) == 1:
                tsplit = tsplits[0]
                tsplit.account = to
        if currency is not NOEDIT:
            tochange = (s for s in self.splits if s.amount and s.amount.currency != currency)
            for split in tochange:
                split.amount = Amount(split.amount.value, currency)
                split.reconciliation_date = None
        # Reconciliation can never be lower than txn date
        for split in self.splits:
            if split.reconciliation_date is not None:
                split.reconciliation_date = max(split.reconciliation_date, self.date)
        self.mtime = time.time()

    def matches(self, query):
        """Return whether ``self`` is matching ``query``.

        ``query`` is a ``dict`` of all criteria to look for (example: ``{'payee': 'Barber shop'}``.
        List of possible dict keys:

        * description
        * payee
        * checkno
        * memo
        * amount
        * account
        * group

        All of these queries are string-based, except ``amount``, which requires an
        :class:`.Amount`.

        Returns true if any criteria matches, false otherwise.
        """
        query_description = query.get('description')
        if query_description is not None:
            if query_description in self.description.lower():
                return True
        query_payee = query.get('payee')
        if query_payee is not None:
            if query_payee in self.payee.lower():
                return True
        query_checkno = query.get('checkno')
        if query_checkno is not None:
            if query_checkno == self.checkno.lower():
                return True
        query_memo = query.get('memo')
        if query_memo is not None:
            for split in self.splits:
                if query_memo in split.memo.lower():
                    return True
        query_amount = query.get('amount')
        if query_amount is not None:
            query_value = query_amount.value if query_amount else 0
            for split in self.splits:
                split_value = split.amount.value if split.amount else 0
                if query_value == abs(split_value):
                    return True
        query_account = query.get('account')
        if query_account is not None:
            for split in self.splits:
                if split.account and split.account.name.lower() in query_account:
                    return True
        query_group = query.get('group')
        if query_group is not None:
            for split in self.splits:
                if split.account and split.account.group and split.account.group.name.lower() in query_group:
                    return True
        return False

    def mct_balance(self, new_split_currency):
        """Balances a :ref:`multi-currency transaction <multi-currency-txn>` using exchange rates.

        *This balancing doesn't occur automatically, it is a user-initiated action.*

        Sums up the value of all splits in ``new_split_currency``, using exchange rates for
        :attr:`date`. If not zero, create a new unassigned split with the opposite of that amount.

        Of course, we need to have called :meth:`balance` before we can call this.

        :param new_split_currency: :class:`.Currency`
        """
        converted_amounts = (convert_amount(split.amount, new_split_currency, self.date) for split in self.splits)
        converted_total = sum(converted_amounts)
        if converted_total != 0:
            target = first(s for s in self.splits if (s.account is None) and of_currency(s.amount, new_split_currency))
            if target is not None:
                target.amount -= converted_total
            else:
                self.splits.append(Split(self, None, -converted_total))

    def reassign_account(self, account, reassign_to=None):
        """Reassign all splits from ``account`` to ``reassign_to``.

        All :attr:`splits` belonging to ``account`` will be changed to ``reassign_to``.

        :param account: :class:`.Account`
        :param reassign_to: :class:`.Account`
        """
        for split in self.splits:
            if split.account is account:
                split.reconciliation_date = None
                split.account = reassign_to

    def replicate(self):
        """Returns a copy of self using :meth:`from_transaction`."""
        return Transaction.from_transaction(self)

    def set_splits(self, splits, preserve_instances=False):
        """Sets :attr:`splits` to copies of splits in ``splits``.

        :param bool preserve_instances: Try to "recycle" split instances as much as possible. This
        is because in certain places, notable in the import window, there's an entry binding
        mechanism and entry identity is based on split instances, so it breaks if we don't keep
        instances there. However, we don't want to preserve instances in all cases. For example,
        when spawning transactions from recurrences, we want fresh instances.
        """
        if preserve_instances:
            if len(splits) < len(self.splits):
                del self.splits[len(splits):]
            for split, newsplit in zip(self.splits, splits):
                split.__dict__.update(newsplit.__dict__)
                split.transaction = self
            for split in splits[len(self.splits):]:
                split.transaction = self
                self.splits.append(split)
        else:
            self.splits = []
            for split in splits:
                newsplit = copy(split)
                newsplit.transaction = self
                self.splits.append(newsplit)

    def splitted_splits(self):
        """Returns :attr:`splits` separated in two groups ("froms" and "tos").

        "froms" are splits with a negative amount and "tos", the positive ones. Null splits are
        generally sent to the "froms" side, unless "tos" is empty.

        Returns ``(froms, tos)``.
        """
        splits = self.splits
        null_amounts = [s for s in splits if s.amount == 0]
        froms = [s for s in splits if s.amount < 0]
        tos = [s for s in splits if s.amount > 0]
        if not tos and null_amounts:
            tos.append(null_amounts.pop())
        froms += null_amounts
        return froms, tos

    #--- Properties
    @property
    def amount(self):
        """*get/set*. :class:`.Amount`. Total amount of the transaction.

        In short, the sum of all positive :attr:`splits`.

        Can only be set if :attr:`can_set_amount` is true, that is, if we have less than two splits.
        When set, we'll set :attr:`splits` in order to create a two-way transaction of that amount,
        preserving from and to accounts if needed.
        """
        if self.is_mct:
            # We need an approximation for the amount value. What we do is we take the currency of the
            # first split and use it as a base currency. Then, we sum up all amounts, convert them, and
            # divide the sum by 2.
            splits_with_amount = [s for s in self.splits if s.amount != 0]
            currency = splits_with_amount[0].amount.currency
            convert = lambda a: convert_amount(abs(a), currency, self.date)
            amount_sum = sum(convert(s.amount) for s in splits_with_amount)
            return amount_sum * 0.5
        else:
            return sum(s.debit for s in self.splits)

    @amount.setter
    def amount(self, value):
        assert self.can_set_amount
        if value == self.amount:
            return
        debit = first(s for s in self.splits if s.debit)
        credit = first(s for s in self.splits if s.credit)
        debit_account = debit.account if debit is not None else None
        credit_account = credit.account if credit is not None else None
        self.splits = [Split(self, debit_account, value), Split(self, credit_account, -value)]

    @property
    def can_set_amount(self):
        """*readonly*. ``bool``. Whether we can set :attr:`amount`.

        True is we have two or less splits of the same currency.
        """
        return (len(self.splits) <= 2) and (not self.is_mct)

    @property
    def has_unassigned_split(self):
        """*readonly*. ``bool``. Whether any of our splits is unassigned (None)."""
        return any(s.account is None for s in self.splits)

    @property
    def is_mct(self):
        """*readonly*. ``bool``. Whether our splits contain more than one currency."""
        splits_with_amount = (s for s in self.splits if s.amount != 0)
        try:
            return not allsame(s.amount.currency for s in splits_with_amount)
        except ValueError: # no split with amount
            return False

    @property
    def is_null(self):
        """*readonly*. ``bool``. Whether our splits all have null amounts."""
        return all(not s.amount for s in self.splits)


class Split:
    """Assignment of money to an :class:`.Account` within a :class:`Transaction`."""
    def __init__(self, transaction, account, amount):
        #: Transaction within which our split lives.
        self.transaction = transaction
        self._account = account
        #: Freeform memo about that split.
        self.memo = ''
        self._amount = amount
        #: Date at which the user reconciled this split with an external source.
        self.reconciliation_date = None
        #: Unique reference from an external source.
        self.reference = None

    def __repr__(self):
        return '<Split %r %s>' % (self.account_name, self.amount)

    #--- Public
    def is_on_same_side(self, other_split):
        return (self.amount >= 0) == (other_split.amount >= 0)

    def move_to_index(self, index):
        self.transaction.splits.remove(self)
        self.transaction.splits.insert(index, self)

    def remove(self):
        self.transaction.splits.remove(self)
        self.transaction.balance()

    #--- Properties
    @property
    def account(self):
        """*get/set*. :class:`.Account` our split is assigned to.

        Can be ``None``. We are then considered an "unassigned split".

        Setting this resets :attr:`reconciliation_date` to ``None``.
        """
        return self._account

    @account.setter
    def account(self, value):
        if value is self._account:
            return
        self._account = value
        self.reconciliation_date = None

    @property
    def account_name(self):
        """*readonly*. Name for :attr:`account` or an empty string if ``None``."""
        return self.account.name if self.account is not None else ''

    @property
    def amount(self):
        """*get/set*. :class:`.Amount` by which we affect our :attr:`account`.

        * A value higher than ``0`` makes this a "debit split".
        * A value lower than ``0`` makes this a "credit split".
        * A value of ``0`` makes this a "null split".

        Setting this resets :attr:`reconciliation_date` to ``None``.
        """
        return self._amount

    @amount.setter
    def amount(self, value):
        if not same_currency(value, self._amount):
            self.reconciliation_date = None
        self._amount = value

    @property
    def credit(self):
        """*readonly*. Returns :attr:`amount` (reverted so it's positive) if < 0. Otherwise, 0."""
        return -self._amount if self._amount < 0 else 0

    @property
    def debit(self):
        """*readonly*. Returns :attr:`amount` if > 0. Otherwise, 0."""
        return self._amount if self._amount > 0 else 0

    @property
    def reconciled(self):
        """*readonly*. ``bool``. Whether :attr:`reconciliation_date` is set to something."""
        return self.reconciliation_date is not None

