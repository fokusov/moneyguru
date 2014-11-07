Editing a moneyGuru document
============================

The Basics
----------

There are a few keystrokes and clicks that work the same way for everything in moneyGuru. First, there is this set of 3 buttons at the bottom left corner:

|edition_buttons|

The + button creates a new thing, the - button removes the selected thing and the "i" button shows info about the selected thing. The "thing" depends on the current view. In the Balance Sheet and the Income Statement, it is an account. In the Transactions and Account views, it is a transaction. Also, if you select more than one transaction and click on the "i" button, the Mass Editing panel will show up rather than the transaction details panel.

Of course, it's also possible to do the same thing with the keyboard. |cmd|\ N creates a new thing, Delete or Backspace remove the selected thing and |cmd|\ I shows info about the selected thing.

It's possible to edit things by double clicking on a cell that is editable (for example, the name cell of an account). It is also possible to start editing a thing by selecting it and pressing Return. The first editable cell will be in edit mode.

When in edit mode, Tab and Shift-Tab can be used to navigate editable cells. When there is no more editable cell in a row, editing ends. It's also possible to end editing by pressing Return again. You can cancel editing by pressing Escape. When doing so, everything you edited in the currently edited row will be reverted to its old value.

Accounts
--------

Accounts are edited from the Balance Sheet and the Income Statement. When you create a new account, it will be created under the type of account that currently contains the selection. For example, if I have "Credit Card" selected and press |cmd|\ N, a new liability will be created. You can then type a new then press Return to end editing.

You can also use drag & drop to change an account type or group (yeah, account group. use |cmd_shift|\ N to create one).

|edition_account_panel|

Using Show Info on an account will bring the account editing panel shown above. From there, you can edit an account name, but also change its type, its :doc:`currency <currencies>` and its account number. An account number is a numerical reference to an account. Use this if your accounting has account number (you know, 1000-1999 is for assets, 8000-8999 is for expenses, stuff like that). When an account has an account number, that number will be displayed along with the name in the Transaction and Account views. Moreover, you can type the number instead of the name to reference to that account (if you know the numbers by heart, it will make typing much faster).

About accounts and currencies: You can only change the currency of an account that has no
:doc:`reconciled entry <reconciliation>`. If for some reason you want to change the currency of such
an account, you'll have to de-reconcile its entries first. Note that changing an account's currency
does **not** change the currency of the transactions it contains.

Transactions
------------

Transactions are edited from the Transactions and Account views. When creating a new transaction, the date of the previously selected transaction will be used as the new transaction's date (see "Date Editing" below). The Description, Payee and Account (From, To Transfer) columns are auto-completed (see "Auto-completion" below).

It's possible to re-order a transaction within other transactions of the same date. To do so, you can use drag & drop, or you can use |cmd|\ + and |cmd|\ -.

If you type the name of an account that doesn't exist in an Account column, this account will automatically be created as an income or expense account (depending on the amount of the transaction). Don't worry about typos creating tons of accounts that you'll have to clean up. If you fix a typo in a transaction, the automatically created account will automatically be removed.

|edition_transaction_panel|

Using Show Info on a single transaction brings the panel above up. With it, you can edit everything that you can edit from the Transactions and Account views, and additionally, you can create and edit transaction with more than 2 entries (commonly called a "Split Transaction") with the table at the bottom.

One thing to remember about this entry editing table is that it's constantly auto-balancing. Therefore, if you take a transaction and simply delete one of its entries, it will not disappear. It will instantly re-add an unassigned entry with the same amount. Changing the amount of an entry will also automatically add an unassigned entry with the amount difference. Therefore, if you want to add a split transaction like, for example, a roommate shared bill where you pay a 40$ bill (let's say internet) using direct banking transfer and your roommate gives you 20$ in cash, you would do the following:

#. Add a normal 2 way Checking --> Utilities transaction.
#. Show Info for the transaction.
#. Change the Utilities debit to 20$. This will create a 3rd unassigned row with a 20$ debit.
#. Change the 3rd row account to Cash.

|edition_three_way_split|

Congratulations, you just made a 3 ways split transaction. This transaction correctly reflect
reality where 40$ are out of your checking account, internet had a net cost of 20$ for you and you
end up with 20 more dollars in your pocket.

There are two special buttons under the split table, **Multi-currency balance** and
**Assign imbalance**. We won't cover the first one here because it's covered in :doc:`currencies`.
As for Assign imbalance, it's a handy shortcut for assigning all remaining imbalance amounts
(amounts in splits that are assigned to no account) to the currently selected split.

Let's use our previous split example again. Let's say that instead of changing the amount for
Utilities to 20$, you instead added a new split for 20$ assigned to Cash. Now, you're stuck with
a 4 way split with a 40$ Utilities and a 20$ unassigned split. Of course, you could manually
subtract 20$ to the Utilities split, but that's sometimes tedious when you have complex numbers.

All you have to do instead is to select the Utilities split and click Assign imbalance. Unassigned
splits will then be "merged" with the selected split with a final amount of 20$.

|edition_mass_edition_panel|

Using Show Info with more than one transaction selected bring up the panel above. It allows you to perform mass editing. When you press on Save, all selected transactions will have the attributes that have the checkboxes next to them checked changed to the value of the field next to it.

Date Editing
------------

Whenever a date is edited, it is edited using a special widget. This widget has 3 fields: day, month and year. Whenever an editing operation is initiated, it is always the **day** fields that starts out selected, whatever your date format is. You can navigate the fields with the left and right arrows. You can increment and decrement the currently selected field with the up and down arrows. You can of course type the date out. The widget automatically changes the selection when a date separator is typed or the maximum length of a field is reached. Here is a list of the rules that this widget follows, just to make it clear:

* The display format is always your system's format.
* The **input** format is always day --> month --> year.
* Whatever your system date format is, you can type a date by padding your values with 0. For example, even if your date format is mm/dd/yy, you can enter the date "07/06/08" by typing "060708".
* Whatever your system date format is, you can type a date by using separators. For example, even if your date format is yyyy-mm-dd, you can type "2008-07-06" by typing "6-7-08"
* You can press the letter "T" to quickly set the date to today.

While editing a transaction or entry, if you set the date to something outside the current date range, you will get a |backward_16| or a |forward_16| showing up. This means that if your date range is "navigable" (Month, Quarter, Year), that date range will be adjusted when editing ends to continue to show the edited transaction. If your current date range is not "navigable" (Year to date, Running year, Custom), the transaction will disappear from the current view when editing ends.

Amount Editing
--------------

Fields allowing you to enter amounts have a few hidden features. 

* You can enter simple expressions like "2+4.35/2" and they will be automatically calculated.
* If you enabled the "Automatically place decimals when typing" option, typing numbers without
  decimal point will result in it being automatically placed. For example, if your default currency
  is USD, typing "1234" will result in the amount "12.34".
* You can always explicitly specify the currency of an amount by prepending or appending the
  3-letters ISO code of that currency to that amount (see the
  :doc:`currencies help page <currencies>`).
* When you enter an expression from the amount that was already there (example ``USD 12.34/1.055``),
  try to keep the original amount as the first operand. There's an ambiguity with the ``.``
  character where it's hard to tell when it's a decimal separator or a thousand separator, which has
  been put there during formatting. We consider the first operand to be an amount, and the other
  operands as simple decimals.

Auto-completion, Autofill and Lookups
-------------------------------------

moneyGuru has advanced auto-completion and autofill capabilities. As soon as you type something in an auto-completable field (Description, Payee, Account), moneyGuru will look in other transactions you have and give you a completion proposition. You can cycle through the propositions with the up and down arrows. To accept a proposition, just tab out. You can also, of course, just continue to type.

The autofill feature will automatically fill empty fields after you tab out of an auto-completable field. For example, if Payee is the first auto-completable column, typing an existing payee will make all subsequent fields automatically filled with values from the last transaction containing that payee.

Under Mac OS X, it's possible to summon a lookup list for any auto-completable field. You need to type a payee that you **know** you have somewhere in your transaction, but don't remember what it starts with? Press |cmd|\ L and a lookup dialog will appear, listing all your payees. The search field allows you to run a fuzzy search (which means that you don't have to type the beginning of your payee, just a few letters that are in it) that will make most relevant payees come first in the list.

.. |edition_buttons| image:: image/edition_buttons.png
.. |edition_account_panel| image:: image/edition_account_panel.png
.. |edition_transaction_panel| image:: image/edition_transaction_panel.png
.. |edition_three_way_split| image:: image/edition_three_way_split.png
.. |edition_mass_edition_panel| image:: image/edition_mass_edition_panel.png
.. |backward_16| image:: image/backward_16.png
.. |forward_16| image:: image/forward_16.png

