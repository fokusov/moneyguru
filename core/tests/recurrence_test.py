# Created By: Virgil Dupras
# Created On: 2008-09-12
# Copyright 2015 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.gnu.org/licenses/gpl-3.0.html

from hscommon.testutil import eq_

from ..const import PaneType
from ..document import ScheduleScope
from .base import TestApp, with_app

#--- Pristine
@with_app(TestApp)
def test_schedule_with_eralier_stop_date(app):
    # A schedule with a stop date that is earlier than its start date is never supposed to produce
    # a spawn.
    app.add_schedule(start_date='13/09/2008', description='foobar', stop_date='12/09/2008')
    app.navigate_to_date(2008, 9, 13)
    tview = app.show_tview()
    eq_(tview.ttable.row_count, 0)

#--- One transaction
def app_one_transaction():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('first')
    app.show_account()
    app.add_entry('11/07/2008', 'description', 'payee', transfer='second', decrease='42', checkno='24')
    app.show_tview()
    app.clear_gui_calls()
    return app

@with_app(app_one_transaction)
def test_make_schedule_from_selected(app):
    # make_schedule_from_selected takes the selected transaction, create a monthly schedule out
    # of it, selects the schedule table, and pops the edition panel for it.
    app.mw.make_schedule_from_selected()
    app.check_current_pane(PaneType.Schedule)
    scview = app.current_view()
    sctable = scview.table
    app.scpanel.view.check_gui_calls_partial(['pre_load', 'post_load'])
    eq_(len(sctable), 0) # It's a *new* schedule, only added if we press save
    eq_(app.scpanel.start_date, '11/08/2008')
    eq_(app.scpanel.description, 'description')
    eq_(app.scpanel.repeat_type_list.selected_index, 2) # monthly
    eq_(app.scpanel.repeat_every, 1)
    app.scpanel.save()
    eq_(len(sctable), 1) # now we have it
    # When creating the schedule, we must delete the first occurrence because it overlapse with
    # the base transaction
    app.show_tview()
    eq_(app.ttable.row_count, 1)

@with_app(app_one_transaction)
def test_make_schedule_from_selected_weekly(app):
    # Previously, making a non-monthly schedule from a transaction would result in a duplicate
    # of the model txn.
    app.mw.make_schedule_from_selected()
    app.scpanel.repeat_type_list.select(1) # weekly
    app.scpanel.start_date = '18/07/2008'
    app.scpanel.save()
    app.show_tview()
    eq_(app.ttable[1].date, '18/07/2008')

#--- Daily schedule
def app_daily_schedule(monkeypatch):
    monkeypatch.patch_today(2008, 9, 13)
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('account')
    app.add_schedule(start_date='13/09/2008', description='foobar', account='account',  amount='1',
        repeat_every=3)
    app.show_tview()
    app.clear_gui_calls()
    return app

@with_app(app_daily_schedule)
def test_change_schedule_transaction(app):
    # when modifying a schedule's transaction through the scpanel, make sure that this change
    # is reflected among all spawns (in other words, reset spawn cache).
    app.show_scview()
    app.sctable.select([0])
    app.scpanel.load()
    app.scpanel.description = 'foobaz'
    app.scpanel.save()
    app.show_tview()
    eq_(app.ttable[1].description, 'foobaz')

@with_app(app_daily_schedule)
def test_change_spawn_materializes_it(app):
    # changing a spawn deletes the spawn and adds a new normal transaction instead.
    app.ttable.select([1])
    app.ttable[1].date = '17/09/2008'
    app.ttable[1].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 6)
    assert not app.ttable[1].recurrent
    eq_(app.ttable[1].date, '17/09/2008')
    eq_(app.ttable[1].description, 'changed')
    # change again
    app.ttable[1].date = '20/09/2008'
    app.ttable.save_edits()
    eq_(app.ttable[1].date, '19/09/2008')
    eq_(app.ttable[2].date, '20/09/2008')
    eq_(app.ttable[2].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_cancel(app):
    # When cancelling a spawn change, nothing happens
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Cancel
    app.ttable.select([1])
    app.ttable[1].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable[1].description, 'foobar')
    # The schedule scoping logic used to take place after the under had recorded. What we're
    # testing here is that the undoer, due to the cancellation, has *not* recorded anything
    app.doc.undo()
    eq_(app.ttable.row_count, 0) # the schedule creation has been undone

@with_app(app_daily_schedule)
def test_change_spawn_then_delete_it(app):
    # The correct spawn is deleted when a changed spawn is deleted
    app.ttable.select([1])
    app.ttable[1].date = '17/09/2008'
    app.ttable.save_edits()
    # XXX The line below could eventually be removed. It's only there because there's a glitch
    # causing our selection to be lost on spawn materialization.
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.row_count, 5)
    eq_(app.ttable[1].date, '19/09/2008')

@with_app(app_daily_schedule)
def test_change_spawn_through_etable(app):
    # Changing a spawn through etable queries for a scope.
    app.show_account('account')
    app.etable[1].description = 'changed'
    app.etable.save_edits()
    app.check_gui_calls(app.doc_gui, ['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_change_spawn_through_etable_globally(app):
    # When the user selects a global change through the etable, we listen
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.show_account('account')
    app.etable[1].description = 'changed'
    app.etable.save_edits()
    eq_(app.etable[2].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_through_tpanel(app):
    # Previously, each edition of a spawn through tpanel would result in a new schedule being
    # added even if the recurrence itself didn't change
    app.ttable.select([1])
    app.tpanel.load()
    app.tpanel.description = 'changed'
    app.tpanel.save()
    eq_(app.ttable[1].description, 'changed')
    eq_(app.ttable[2].description, 'foobar')
    eq_(app.ttable[3].description, 'foobar')
    # We were queried for a scope
    app.check_gui_calls(app.doc_gui, ['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope(app):
    # changing a spawn with a global scope makes every following spawn like it.
    # The date progression follows depending on the difference between the "base date" and the
    # changed date
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008' # 2 days before
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    # the explcitely changed one, however, keeps its date
    eq_(app.ttable[2].date, '17/09/2008') # same as edited
    eq_(app.ttable[3].date, '20/09/2008') # 2 days before
    eq_(app.ttable[3].description, 'changed')
    eq_(app.ttable[4].date, '23/09/2008') # 2 days before
    eq_(app.ttable[4].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope_then_with_local_scope(app):
    # Previously, the same instance was used in the previous recurrence exception as well as
    # the new occurence base, making the second change, which is local, global.
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    app.ttable[2].description = 'changed again'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Local
    app.ttable.save_edits()
    eq_(app.ttable[3].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope_twice(app):
    # Previously, the second change would result in schedule duplicating
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    app.ttable[2].description = 'changed again'
    app.ttable.save_edits()
    eq_(app.ttable[3].date, '20/09/2008')
    eq_(app.ttable[3].description, 'changed again')

@with_app(app_daily_schedule)
def test_delete_account(app):
    # Deleting an account affecting a schedule properly update that schedule
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.arpanel.save()
    app.show_scview()
    eq_(app.sctable[0].to, '')

@with_app(app_daily_schedule)
def test_delete_spawn(app):
    # deleting a spawn only deletes this instance
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.row_count, 5)
    eq_(app.ttable[1].date, '19/09/2008')

@with_app(app_daily_schedule)
def test_delete_spawn_cancel(app):
    # When the user cancels a spawn deletion, nothing happens
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Cancel
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.row_count, 6)

@with_app(app_daily_schedule)
def test_delete_spawn_with_global_scope(app):
    # when deleting a spawn and query_for_global_scope returns True, we stop the recurrence 
    # right there
    app.ttable.select([2])
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.delete()
    eq_(app.ttable.row_count, 2)
    eq_(app.ttable[1].date, '16/09/2008')

@with_app(app_daily_schedule)
def test_etable_attrs(app):
    app.show_account('account')
    eq_(app.etable_count(), 6) # same thing in etable
    assert app.etable[0].recurrent
    eq_(app.ttable[0].date, '13/09/2008')
    assert app.ttable[5].recurrent
    eq_(app.ttable[5].date, '28/09/2008')

@with_app(app_daily_schedule)
def test_exceptions_are_always_spawned(app):
    # When an exception has a smaller date than the "spawn date", enough to be in another range,
    # when reloading the document, this exception would not be spawn until the date range
    # reached the "spawn date" rather than the exception date.
    app.drsel.select_next_date_range()
    app.ttable.select([0])
    app.ttable[0].date = '30/09/2008'
    app.ttable.save_edits() # date range now on 09/2008
    app.doc._cook() # little hack to invalidate previously spawned txns
    app.ttable.refresh() # a manual refresh is required
    eq_(app.ttable.row_count, 7) # The changed spawn must be there.

@with_app(app_daily_schedule)
def test_filter(app):
    # scheduled transactions are included in the filters
    app.sfield.query = 'foobar'
    eq_(app.ttable.row_count, 6)

@with_app(app_daily_schedule)
def test_mass_edition(app):
    # When a mass edition has a spawn in it, don't ask for scope, just perform the change in the
    # local scope
    app.ttable.select([1, 2])
    app.mepanel.load()
    app.mepanel.description = 'changed'
    app.mepanel.save()
    eq_(app.ttable[3].description, 'foobar')
    app.check_gui_calls_partial(app.doc_gui, not_expected=['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_ttable_attrs(app):
    eq_(app.ttable.row_count, 6) # this txn happens 6 times this month
    assert app.ttable[0].recurrent # original is not recurrent
    eq_(app.ttable[0].date, '13/09/2008')
    assert app.ttable[1].recurrent
    eq_(app.ttable[1].date, '16/09/2008')
    assert app.ttable[2].recurrent
    eq_(app.ttable[2].date, '19/09/2008')
    assert app.ttable[3].recurrent
    eq_(app.ttable[3].date, '22/09/2008')
    assert app.ttable[4].recurrent
    eq_(app.ttable[4].date, '25/09/2008')
    assert app.ttable[5].recurrent
    eq_(app.ttable[5].date, '28/09/2008')
    # Also test amount. Previously, the spawns would have their amount attributes stuck at 0.
    eq_(app.ttable[0].amount, '1.00')

@with_app(app_daily_schedule)
def test_change_spawn_date_globally(app):
    # When changing the date of a spawn globally, all future spawns' date are offseted by the same
    # number of days.
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.select([1])
    app.ttable[1].date = '15/09/2008'
    app.ttable.save_edits()
    eq_(app.ttable[1].date, '15/09/2008')
    eq_(app.ttable[2].date, '18/09/2008') # one day early
    eq_(app.ttable[3].date, '21/09/2008') # same here

@with_app(app_daily_schedule)
def test_new_global_change_after_previous_global_date_change(app):
    # Performing a global change on a spawn that comes after a previous global change involving a
    # date works. It previously wouldn't because the modified date was looked for in the global
    # instances dict instead of the recurrence date.
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.select([1])
    app.ttable[1].date = '15/09/2008'
    app.ttable.save_edits()
    app.ttable.select([2])
    app.ttable[2].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable[3].description, 'changed')

@with_app(app_daily_schedule)
def test_oven_limits_take_global_date_delta_into_account(app):
    # However unlikely, it's possible to make a global date change go so far in the past that it
    # confuses the oven and makes it not cook spawns that should be cooked for the current date
    # range. This shouldn't happen.
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.select([1])
    app.ttable[1].date = '15/08/2008' # one month earlier
    app.ttable.save_edits()
    # Now, the spawn instances for this date range have already been created previously, so we
    # have to advance the date range to see whether the oven behaves or not.
    app.drsel.select_next_date_range()
    eq_(app.ttable.row_count, 11)

@with_app(app_daily_schedule)
def test_delete_spawns_until_global_change(app):
    # Deleting spawns until a global change sets its ref with this global change and changing the
    # schedule correctly affects the spawns globally.
    app.show_tview()
    app.ttable.select([2])
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Local
    app.ttable.select([0, 1])
    app.mw.delete_item()
    eq_(app.ttable[0].description, 'changed')
    scview = app.show_scview()
    eq_(scview.table[0].description, 'changed')
    app.mw.edit_item()
    app.scpanel.description = 'changed again'
    app.scpanel.save()
    tview = app.show_tview()
    eq_(tview.ttable[0].description, 'changed again')

#--- One Schedule and one normal txn
def app_one_schedule_and_one_normal_txn():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('account')
    app.show_account()
    app.add_entry('19/09/2008', description='bar', increase='2')
    app.add_schedule(start_date='13/09/2008', description='foo', account='account', amount='1',
        repeat_every=3)
    return app

@with_app(app_one_schedule_and_one_normal_txn)
def test_ttable_attrs_with_one_spawn_and_one_regular(app):
    app.show_tview()
    eq_(app.ttable.row_count, 7)
    eq_(app.ttable[2].date, '19/09/2008')
    eq_(app.ttable[2].description, 'bar')
    eq_(app.ttable[3].date, '19/09/2008')
    eq_(app.ttable[3].description, 'foo')
    eq_(app.ttable[3].to, 'account')

@with_app(app_one_schedule_and_one_normal_txn)
def test_etable_attrs_with_one_spawn_and_one_regular(app):
    app.show_account('account')
    eq_(app.etable_count(), 7)
    eq_(app.etable[2].date, '19/09/2008')
    eq_(app.etable[2].description, 'bar')
    eq_(app.etable[3].date, '19/09/2008')
    eq_(app.etable[3].description, 'foo')

@with_app(app_one_schedule_and_one_normal_txn)
def test_schedule_exceptions_are_correctly_reassigned(app):
    # When deleting an account to which schedule exceptions are assigned, correctly reassign these
    # exceptions.
    app.add_account('account2')
    app.show_tview()
    app.ttable.select([3])
    app.ttable[3].to = 'account2'
    # We set a 'from' to avoid have the transaction deleted from the reassignment.
    app.ttable[3].from_ = 'account'
    app.ttable.save_edits()
    eq_(app.ttable[3].to, 'account2')
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.delete()
    app.arpanel.save() # reassign to None
    app.show_tview()
    eq_(app.ttable[3].to, '')

#--- Schedule with local change
def app_schedule_with_local_change(monkeypatch):
    monkeypatch.patch_today(2008, 9, 30)
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.show_tview()
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.ttable.save_edits()
    return app

@with_app(app_schedule_with_local_change)
def test_exceptions_still_hold_the_correct_recurrent_date_after_load(app):
    # Previously, reloading an exception would result in recurrent_date being the same as date
    newapp = app.save_and_load()
    newapp.show_scview()
    newapp.show_tview()
    newapp.ttable.select([2])
    newapp.ttable.delete()
    eq_(newapp.ttable[2].date, '22/09/2008')

@with_app(app_schedule_with_local_change)
def test_save_load_schedule_with_local_changes(app):
    # Ensure that save_and_load preserves correct status.
    newapp = app.save_and_load()
    newapp.show_tview()
    assert not newapp.ttable[2].recurrent
    eq_(newapp.ttable[2].description, 'changed')

#--- Schedule with global change
def app_schedule_with_global_change(monkeypatch):
    monkeypatch.patch_today(2008, 9, 30)
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.show_tview()
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    return app

@with_app(app_schedule_with_global_change)
def test_perform_another_global_change_before_first_global_change(app):
    # Previously, the second global change would not override the first
    app.ttable.select([1])
    app.ttable[1].description = 'changed again'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    eq_(app.ttable[2].description, 'changed again')

@with_app(app_schedule_with_global_change)
def test_delete_spawns_past_global_change(app):
    # Deleting spawns past a global change keeps that global change alive.
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Local
    app.ttable.select([0, 1, 2])
    app.mw.delete_item()
    eq_(app.ttable[0].description, 'changed')
    scview = app.show_scview()
    eq_(scview.table[0].description, 'changed')

#--- Schedule with local deletion
def app_schedule_with_local_deletion(monkeypatch):
    monkeypatch.patch_today(2008, 9, 30)
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.show_tview()
    app.ttable.select([2])
    app.ttable.delete()
    return app

@with_app(app_schedule_with_local_deletion)
def test_perform_another_global_change_before_local_deletion(app):
    # Don't remove the local deletion
    app.ttable.select([1])
    app.ttable[1].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    eq_(app.ttable[2].date, '22/09/2008')

@with_app(app_schedule_with_local_deletion)
def test_delete_account_with_schedule_containing_deletions(app):
    # There was a bug (#298) where a None value in schedule exceptions would make
    # affected_accounts() crash.
    app.select_account('account')
    app.mw.delete_item()
    app.arpanel.save() # no crash

#--- Schedule with stop date
def app_schedule_with_stop_date():
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', repeat_every=3)
    app.show_tview()
    app.ttable.select([3])
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.delete()
    return app

@with_app(app_schedule_with_stop_date)
def test_perform_global_change_on_schedule_with_stop_date(app):
    # Previously, the stop date on the new scheduled txn wouldn't be set
    app.ttable.select([1])
    app.ttable[1].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 3)

#--- Weekly schedule
def app_weekly_schedule():
    app = TestApp()
    app.drsel.select_month_range()
    app.navigate_to_date(2008, 9, 13)
    app.add_schedule(start_date='13/09/2008', repeat_type_index=1, repeat_every=2) # weekly
    app.show_tview()
    return app

@with_app(app_weekly_schedule)
def test_next_date_range(app):
    # The next date range also has the correct recurrent txns
    app.drsel.select_next_date_range()
    eq_(app.ttable.row_count, 2)
    eq_(app.ttable[0].date, '11/10/2008')
    eq_(app.ttable[1].date, '25/10/2008')

@with_app(app_weekly_schedule)
def test_ttable_attrs_for_weekly_schedule(app):
    eq_(app.ttable.row_count, 2)
    eq_(app.ttable[0].date, '13/09/2008')
    eq_(app.ttable[1].date, '27/09/2008')

@with_app(app_weekly_schedule)
def test_global_change_on_first_spawn(app):
    # Performing a global change on the first spawn changes the schedule itself
    app.doc.view.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.select([0])
    app.ttable[0].description = 'changed'
    app.ttable.save_edits()
    scview = app.show_scview()
    eq_(scview.table[0].description, 'changed')

@with_app(app_weekly_schedule)
def test_deleting_first_spawn_changes_start_date(app):
    # Deleting the first spawn changes the start date to the next spawn.
    app.ttable.select([0])
    app.mw.delete_item()
    scview = app.show_scview()
    eq_(scview.table[0].start_date, '27/09/2008')

#--- Monthly schedule on 31st of the month
def app_monthly_schedule_on_thirty_first():
    app = TestApp()
    app.drsel.select_month_range()
    app.navigate_to_date(2008, 8, 31)
    app.add_schedule(start_date='31/08/2008', repeat_type_index=2) # monthly
    app.show_tview()
    return app

@with_app(app_monthly_schedule_on_thirty_first)
def test_use_last_day_in_invalid_months_for_31(app):
    app.drsel.select_next_date_range() # sept
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '30/09/2008') # can't use 31, so it uses 30
    # however, revert to 31st on the next month
    app.drsel.select_next_date_range() # oct
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '31/10/2008')

#--- Yearly schedule on 29th of february
def app_yearly_schedule_on_twenty_ninth():
    app = TestApp()
    app.drsel.select_year_range()
    app.navigate_to_date(2008, 2, 29)
    app.add_schedule(start_date='29/02/2008', repeat_type_index=3) # yearly
    app.show_tview()
    return app

@with_app(app_yearly_schedule_on_twenty_ninth)
def test_use_last_day_in_invalid_years_for_29(app):
    app.drsel.select_next_date_range() # 2009
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '28/02/2009') # can't use 29, so it uses 28
    # however, revert to 29 4 years later
    app.drsel.select_next_date_range() # 2010
    app.drsel.select_next_date_range() # 2011
    app.drsel.select_next_date_range() # 2012
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '29/02/2012')

#--- Schedule on 3rd monday of the month
def app_schedule_on_third_monday_of_the_month():
    app = TestApp()
    app.drsel.select_year_range()
    app.navigate_to_date(2008, 9, 15)
    app.add_schedule(start_date='15/09/2008', repeat_type_index=4) # week no in month
    app.show_tview()
    return app

@with_app(app_schedule_on_third_monday_of_the_month)
def test_spawn_dates_for_weekno_in_month_schedule(app):
    # The next date range also has the correct recurrent txns
    eq_(app.ttable.row_count, 4)
    eq_(app.ttable[0].date, '15/09/2008')
    eq_(app.ttable[1].date, '20/10/2008')
    eq_(app.ttable[2].date, '17/11/2008')
    eq_(app.ttable[3].date, '15/12/2008')

#--- Schedule on 5th tuesday of the month
def app_schedule_on_fifth_tuesday_of_the_month():
    app = TestApp()
    app.drsel.select_month_range()
    app.navigate_to_date(2008, 9, 30)
    app.add_schedule(start_date='30/09/2008', repeat_type_index=4) # week no in month
    app.show_tview()
    return app

@with_app(app_schedule_on_fifth_tuesday_of_the_month)
def test_spawn_dates_for_weekno_in_month_schedule_fifth_weekday(app):
    # There's not a month with a fifth tuesday until december
    app.drsel.select_next_date_range() # oct
    eq_(app.ttable.row_count, 0)
    app.drsel.select_next_date_range() # nov
    eq_(app.ttable.row_count, 0)
    app.drsel.select_next_date_range() # dec
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '30/12/2008')

#--- Schedule on last tuesday of the month
def app_schedule_on_last_tuesday_of_the_month():
    app = TestApp()
    app.drsel.select_month_range()
    app.navigate_to_date(2008, 9, 30)
    app.add_schedule(start_date='30/09/2008', repeat_type_index=5) # last week in month
    app.show_tview()
    return app

@with_app(app_schedule_on_last_tuesday_of_the_month)
def test_spawn_dates_for_weekno_in_month_schedule_last_weekday(app):
    # next month has no 5th tuesday, so use the last one
    app.drsel.select_next_date_range() # oct
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].date, '28/10/2008')

#--- Two daily schedules
def app_two_daily_schedules():
    app = TestApp()
    app.add_account('account')
    app.add_schedule(description='foo')
    app.add_schedule(description='bar')
    return app

@with_app(app_two_daily_schedules)
def test_schedule_spawns_cant_be_reordered(app):
    # scheduled transactions can't be re-ordered
    app.show_tview()
    assert not app.ttable.can_move([3], 2)

#--- Daily schedule with one reconciled spawn
def app_daily_schedule_one_spawn_reconciled():
    app = TestApp()
    app.drsel.select_month_range()
    app.navigate_to_date(2008, 9, 13)
    app.add_account('account')
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.show_account('account')
    app.etable.select([1]) # This one is the spawn on 16/09/2008
    app.aview.toggle_reconciliation_mode()
    app.etable.selected_row.toggle_reconciled()
    app.aview.toggle_reconciliation_mode()    
    return app

@with_app(app_daily_schedule_one_spawn_reconciled)
def test_dont_spawn_before_last_materialization_on_change(app):
    # One tricky problem was that if a schedule was changed to a more frequent one. When it happens,
    # exceptions start to be all out of sync with the recurrence, and trying to figure out which
    # ones should be kept is a nightmare. Thus, when a recurrence's start_date, repeat_type or
    # repeat_every is changed, its exceptions are simply reset.
    app.show_scview()
    app.sctable.select([0])
    app.scpanel.load()
    app.scpanel.repeat_every = 1
    app.scpanel.save()
    app.show_tview()
    # spawns start from the 13th, *not* the 13th, which means 18 spawn. If we add the reconciled
    # spawn which have been materialized, we have 19
    eq_(app.ttable.row_count, 19)

@with_app(app_daily_schedule_one_spawn_reconciled)
def test_spawn_was_materialized(app):
    # reconciling a scheduled transaction "materializes" it
    assert app.etable[1].reconciled
    assert not app.etable[1].recurrent
