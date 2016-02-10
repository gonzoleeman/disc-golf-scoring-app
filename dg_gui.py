#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - Update score results frame if a new "score" is done

    - Keep track of Aces, Eagles, and Ace-Eagles on a per-hole basis,
      e.g. have a drop-down radio-button list in the menu for each
      of the 18 hole

    - Add in tracking of 2 (or 3) money rounds: who won, on which of 6
      max rounds, including Miss Kitty if no human won after 6 rounds

    - Add option to backup the DB. (Periodically, or on demand?)

    - figure out true meaning of 9-s, 18-s, and 33-s

    - Allow update of DB any time, but warn user that "calc is needed"
      if they have updated a front or back 9 score

    - Break status window into 2 parts: the first is the file
      name of the database, and the 2nd is for error messages
      (for which frame(s)?)

    - Update status with number of matching round in the report window,
      when setting a date range

    - As soon as any field changed in the Scoring GUI, update
      the status window to say "Edited"

    - report on best front and back rounds

    - handle "E" as the number "0" (i.e. "even") for score fields,
      and display "E" instead of "+0" (enhancement)

    - Add an "All time" date range for the report screen
    - display results as a graph?
    
    - quit guessing what new round number will be, and actually let
      the database decide

    - in general, use use the DB as the backend, with transactions,
      and never have to keep local copies of data? (may be slow?)
    - use DB transactions for changes, so we can just update the DB, then
      throw it away if they say "no"

    - make setup window become the scoring window for a round,
      instead of just replacing one window with the next (optimization)
      (and likewise for the setup-report->report transition)

    - consider RETURN key in main window like Show/Edit button hit
      (optimization) (i.e. Default?, Focus?)

    -------------------------------

    - Support alternate/new Database files (why?)

    - support DB modification for Courses and Players (some day)

    - support modifying a round to add or remove a player,
      or even to remove a round? (not needed?)

    - Properly package for distribution (for who?)

    - implement real help? (like what?)

    - preferences? not really needed yet: nothing to configure/prefer
      - e.g. which players are "usually there"
      - size of windows?

History:
    Version 1.0: menu bar present, hooked up, but on
        Quit works
    Version 1.1: Now using a better list, with columns, and
        faking out a ride database
    Version 1.2: Now under git control. Added list selection
        detection, list edit buttons, and button enable/disable
    version 1.3: trynig to get it arranged correctly
    version 1.4: getting closer: setting up a round correctly now
    version 1.5: have the scoring window populated now!
    version 1.6: now scoring but not saving to the database
        i.e. "Commit" not yet implemented
    version 1.7: add starting "round list" window
    versoin 1.8: all works but commit?
    version 1.9: all works but getting result data!!!
    version 1.10: Now displays results, but no graph
    version 1.11: Total score now a fraction. Round scores displayed
        as "+N", or "-N". Also, now displaying "overall" score
    version 1.12: Now tracking front/rear/overall score separately, per
        round played, for easier tracking of 9-s, 18-s, etc.
'''


import sys
from optparse import OptionParser
import wx
import re
import datetime as dt
from wx.lib.pubsub import Publisher as pub
import copy

import rdb
from utils import dprint
from opts import opts
import score
import listctrl as lc
import money



__author__ = "Lee Duncan"
__version__ = "1.12"


class SetupRoundFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SetupRoundFrame, self).__init__(*args, **kwargs)
        self.SetSize((wx.Size(400, 400)))
        self.InitUI()
        self.Bind(wx.EVT_CLOSE, self.Quit)

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        st1 = wx.StaticText(panel, label='Round Setup')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.player_list = lc.AutoWidthCheckListCtrl(panel)
        player_data = {}
        for k,v in rdb.PlayerList.iteritems():
            player_data[k] = v.name
        self.player_list.SetupList('Choose Players', player_data)
        hbox2.Add(self.player_list, 1, wx.EXPAND|wx.LEFT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPlayerListSelected,
                  source=self.player_list,
                  id=wx.ID_ANY)
        ################################################################
        hbox2.AddSpacer(15)
        self.course_list = lc.AutoWidthListCtrl(panel)
        self.course_list.SetupListHdr(['Choose a Course'],
                                      [wx.LIST_FORMAT_LEFT],
                                      ['%s'])
        item_data = {}
        for k, c in rdb.CourseList.iteritems():
            item_data[k] = (c.name,)
        self.course_list.SetupListItems(item_data)
        hbox2.Add(self.course_list, 1, wx.EXPAND|wx.RIGHT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnCourseListSelected,
                  source=self.course_list,
                  id=wx.ID_ANY)
        #self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnCourseListSelected,
        #          source=self.course_list,
        #          id=wx.ID_ANY)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_EXIT, label='Cancel')
        date_label = wx.StaticText(panel, label='Date')
        self.round_date = wx.DatePickerCtrl(panel, size=wx.Size(110, 20))
        self.score_button = wx.Button(panel, label='Score a Round')
        self.Bind(wx.EVT_BUTTON, self.OnScoreRound,
                  source=self.score_button)
        self.Bind(wx.EVT_BUTTON, self.Quit, source=cancel_button)
        self.Bind(wx.EVT_DATE_CHANGED, self.DateChanged, source=self.round_date)
        self.score_button.Disable()
        vbox.AddSpacer(10)
        hbox3.Add(cancel_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(date_label)
        hbox3.AddSpacer(5)
        hbox3.Add(self.round_date)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.score_button)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Please choose")
        self.status_bar.SetBackgroundColour(wx.NullColour)
        ################################################################
        panel.SetSizer(vbox)

    def DateChanged(self, e):
        dprint("Date Changed!:", e)
        self.status_bar.SetStatusText("")
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def SetScoreButtonState(self):
        '''Set appropriate state for the "Score" Button'''
        i = self.course_list.GetFirstSelected()
        dprint("Course Selected: %d; Players Selected: %d" % \
               (i, self.player_list.item_check_count))
        if i >= 0 and self.player_list.item_check_count > 0:
            self.score_button.Enable()
        else:
            self.score_button.Disable()

    def OnPlayerListSelected(self, e):
        dprint("Player[%d] Selected" % e.Index)
        self.player_list.Select(e.Index, False)
        self.player_list.ToggleItem(e.Index)
        self.SetScoreButtonState()

    def OnCourseListSelected(self, e):
        dprint("Course[%d] Selected:" % e.Index, e)
        self.SetScoreButtonState()

    def OnScoreRound(self, e):
        dprint("*** 'SCORE' Button Pressed: num players selected=%d:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        ################################################################
        idx = self.course_list.GetFirstSelected()
        cnum = self.course_list.GetItemData(idx)
        dprint("Course number: %d" % cnum)
        wx_rdate = self.round_date.GetValue()
        dprint("Raw date:", wx_rdate)
        rdate = dt.datetime(wx_rdate.GetYear(),
                            wx_rdate.GetMonth() + 1,
                            wx_rdate.GetDay())
        dprint("round date (from Yr=%d, month=%d, day=%d):" % \
               (wx_rdate.GetYear(), wx_rdate.GetMonth() + 1, wx_rdate.GetDay()),
               rdate)
        ################################################################
        # make sure this round does not already exist
        rdate_str = rdate.strftime("%m/%d/%Y")
        dprint("looking for dup round on date=%s, loc=%d)" % (rdate_str, cnum))
        for rnd in rdb.RoundList.itervalues():
            dprint("Looking at:", rnd)
            if rnd.rdate == rdate:
                dprint("Duplicate!?")
                self.status_bar.SetStatusText("Duplicate Round Date!")
                self.status_bar.SetBackgroundColour(wx.RED)
                return
        ################################################################
        this_round = rdb.Round(rdb.next_round_num(), cnum, rdate_str)
        dprint("Created:", this_round)
        round_details = []
        for (k, v) in self.player_list.items_checked.iteritems():
            i = self.player_list.GetItemData(k)
            if not v:
                continue # this user not checked
            player = rdb.PlayerList[i]
            dprint("Found player[%d] (from checklist):" % i, player)
            rd = rdb.RoundDetail(this_round.num, player.num)
            round_details.append(rd)
            dprint("Created:", rd)
        round_details = sorted(round_details, key=lambda rd: rd.player_num)
        ################################################################
        # popup a window to enter the scores for round then go away
        srf = RoundScoringFrame(self.GetParent(), title='Score a Round')
        srf.MyCreate(this_round, round_details, for_update=False)
        self.Destroy()

    def Quit(self, e):
        '''Either .... happened'''
        # Do we need to check for database modified here, with a popup?
        # (I do not think so)
        dprint("QUITing SetupRoundFrame")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


class RoundScoringFrame(wx.Frame):
    '''
    For Creating a Round and some RoundDetails, or
    for updating the RoundDetails for an existing round
    '''
    def __init__(self, *args, **kwargs):
        super(RoundScoringFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(700, 300))
        self.is_edited = False
        self.cnum = None
        self.rdate = None
        self.for_update = False
        self.this_round = None
        self.for_update = None
        self.round_details = None
        self.calc_done = False
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

    def MyCreate(self, this_round, round_details, for_update=False):
        self.cnum = this_round.course_num
        self.rdate = this_round.rdate
        self.for_update = for_update
        dprint("Score Create: Course[%d], round date: %s" % \
               (self.cnum, self.rdate))
        self.this_round = this_round
        self.round_details = sorted(round_details, key=lambda rd: rd.player_num)
        dprint("Added round details:")
        for rd in round_details:
            dprint(rd)
        self.InitUI()

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Round Scoring')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(20)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        bold_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        bold_font.SetWeight(wx.FONTWEIGHT_BOLD)
        st2 = wx.StaticText(panel, label='Round Date: ')
        st2.SetFont(bold_font)
        st3 = wx.StaticText(panel, label=self.rdate.strftime('%m/%d/%Y'))
        st4 = wx.StaticText(panel, label='Location: ')
        st4.SetFont(bold_font)
        st5 = wx.StaticText(panel, label=rdb.CourseList[self.cnum].name)
        hbox2.AddSpacer(20)
        hbox2.Add(st2)
        hbox2.Add(st3)
        hbox2.AddStretchSpacer(2)
        hbox2.Add(st4)
        hbox2.Add(st5)
        hbox2.AddSpacer(20)
        vbox.Add(hbox2, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        vbox.AddSpacer(15)
        hbox2_5 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Money Rounds Results:')
        st6.SetFont(bold_font)
        choices = ['<None>'] + \
                  [str(i) for i in range(18)] + \
                  ['<MzKitty>']
        st7 = wx.StaticText(panel, label='First:')
        self.money_finish = []
        self.money_finish.append(wx.Choice(panel, choices=choices))
        st8 = wx.StaticText(panel, label='Second:')
        self.money_finish.append(wx.Choice(panel, choices=choices))
        st9 = wx.StaticText(panel, label='Third:')
        self.money_finish.append(wx.Choice(panel, choices=choices))
        hbox2_5.AddSpacer(20)
        hbox2_5.Add(st6)
        hbox2_5.AddSpacer(15)
        hbox2_5.Add(st7)
        hbox2_5.Add(self.money_finish[0])
        hbox2_5.AddSpacer(15)
        hbox2_5.Add(st8)
        hbox2_5.Add(self.money_finish[1])
        hbox2_5.AddSpacer(15)
        hbox2_5.Add(st9)
        hbox2_5.Add(self.money_finish[2])
        vbox.Add(hbox2_5, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        vbox.AddSpacer(15)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.score_list = lc.AutoWidthListEditCtrl(panel)
        self.score_list.SetupListHdr(['Name', 'Front 9', 'Back 9', 'Overall',
                                      'Aces', 'Eagles', 'Ace-Eagles', 'Score'],
                                     [wx.LIST_FORMAT_LEFT,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER],
                                     ['%s', '%+d', '%+d', '%+d',
                                      '%d', '%d', '%d', '%s'])
        item_data = self.RoundDetailsAsDict()
        self.score_list.SetupListItems(item_data)
        hbox3.Add(self.score_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        self.Bind(lc.EVT_LIST_EDITED_EVT, self.OnListEdited,
                  source=self.score_list)
        ################################################################
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_CANCEL, label='Cancel')
        lab = ('Update' if self.for_update else 'Commit')
        self.commit_button = wx.Button(panel, id=wx.ID_SAVE, label=lab)
        self.commit_button.Disable()
        self.calc_button = wx.Button(panel, id=wx.ID_SETUP,
                                          label='Calculate')
        #self.calc_button.Disable()
        self.calc_done = False
        self.Bind(wx.EVT_BUTTON, self.OnCancel, source=cancel_button)
        self.Bind(wx.EVT_BUTTON, self.OnCommit, source=self.commit_button)
        self.Bind(wx.EVT_BUTTON, self.OnCalculate, source=self.calc_button)
        hbox4.AddSpacer(10)
        hbox4.Add(cancel_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.commit_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.calc_button)
        vbox.Add(hbox4, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Please fill in the scores")
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def OnCommit(self, e):
        dprint("OnCommit: string=%s" % e.GetString())
        dprint("%s DB requested -- hope you're sure" % e.GetString())
        dprint("State: edited=%s, calc_done=%s" % \
               (self.is_edited, self.calc_done))
        if self.is_edited and not self.calc_done:
            self.GetDataFromForm()
        if not self.is_edited:
            dprint("Huh????")
            return
        if self.for_update:
            rdb.modify_round(self.this_round, self.round_details)
        else:
            rdb.add_round(self.this_round, self.round_details)
        rdb.commit_db()
        dprint("Updating parent GUI ...")
        pub.sendMessage("ROUND UPDATE", self.this_round)
        self.is_edited = False
        self.Close()

    def RoundDetailsAsDict(self):
        dprint("Making Round Details into dictionary ...")
        item_data = {}
        for rd in self.round_details:
            dprint(rd)
            player = rdb.PlayerList[rd.player_num]
            item_data[rd.player_num] = (player.name,
                                        rd.fscore, rd.bscore, rd.Overall(),
                                        rd.acnt, rd.ecnt, rd.aecnt,
                                        rd.CalcScore())
        return item_data

    def GetDataFromForm(self):
        '''Get data from our list into our self.round_details'''
        # get data from list into
        cnt = self.score_list.GetItemCount()
        dprint("Our round detail list has %d items" % cnt)
        for c in range(cnt):
            dprint("Looking for round_detail index %d" % c)
            round_detail = self.round_details[c]
            dprint(round_detail)
            pname = self.score_list.GetItemText(c)
            dprint("Item %d: %s" % (c, pname))
            try:
                f9 = self.score_list.GetFieldNumericValue(c, 1)
                b9 = self.score_list.GetFieldNumericValue(c, 2)
            except ArithmeticError, e:
                col_no = e.args[1]
                if col_no == 1:
                    loc = 'Front 9'
                else:
                    loc = 'Back 9'
                self.status_bar.SetStatusText("%s's %s invalid" % (pname, loc))
                self.status_bar.SetBackgroundColour(wx.RED)
                return
            self.round_details[c].SetScore(f9, b9)
            dprint("Front/Back Nine for player %s: %d/%d" % (pname, f9, b9))
            acnt = self.score_list.GetFieldNumericValue(c, 4)
            ecnt = self.score_list.GetFieldNumericValue(c, 5)
            aecnt = self.score_list.GetFieldNumericValue(c, 6)
            self.round_details[c].SetCounts(acnt, ecnt, aecnt)
            self.status_bar.SetStatusText("")
            self.status_bar.SetBackgroundColour(wx.NullColour)

    def OnCalculate(self, e):
        self.GetDataFromForm()
        dprint("All fields OK! scoring ...")
        pre_scored_details = copy.deepcopy(self.round_details)
        scored_details = score.score_round(self.round_details)
        dprint("BEFORE comparing round details, here are both:")
        for rd in pre_scored_details:
            dprint("pre-socred[]: ", rd)
        for rd in scored_details:
            dprint("post-socred[]:", rd)
        # was it changed?
        was_changed = not rdb.round_details_equal(pre_scored_details,
                                                  scored_details)
        # if it was changed, we need update the DB
        if was_changed:
            # set 'edited' in case it was not set before
            self.is_edited = True
            dprint("List *WAS* edited: updating")
            self.round_details = scored_details
            item_data = self.RoundDetailsAsDict()
            self.score_list.SetupListItems(item_data)
            self.commit_button.Enable()
        else:
            # else already edited 
            dprint("List was /not/ edited, so nothing to do?")
        self.calc_done = True

    def OnCancel(self, e):
        dprint("Cancel!: Edited=%s" % self.is_edited)
        if self.is_edited:
            res = wx.MessageBox('Data Modified. Are you sure?',
                                'Question',
                                wx.YES_NO | wx.ICON_WARNING)
            dprint("Message result:", res)
            if res == wx.NO:
                return
            # since our calculate has modifed the rdb data, we
            # need to reload it :(
            rdb.init_rounds()
        self.Destroy()

    def OnListEdited(self, evt):
        dprint("OnListEdited: Col=%d: %s", (evt.col, evt.message))
        # was editing in the front9/back9 columns?
        if evt.col in [1, 2]:
            self.calc_button.Enable()
            self.calc_done = False
        # but any change means we need to save the changes
        self.commit_button.Enable()
        self.is_edited = True

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class DisplayReportFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(DisplayReportFrame, self).__init__(*args, **kwargs)
        self.SetSize((825, 250))

    def MyStart(self, start_rdate, stop_rdate):
        dprint("Report on reults from", start_rdate, "to", stop_rdate)
        start_dt = dt.datetime(start_rdate.GetYear(),
                               start_rdate.GetMonth() + 1,
                               start_rdate.GetDay())
        dprint("Report Starting Date (as datetime):", start_dt)
        end_dt = dt.datetime(stop_rdate.GetYear(),
                             stop_rdate.GetMonth() + 1,
                             stop_rdate.GetDay())
        dprint("Report Ending Date (as datetime):  ", end_dt)
        # make a dictionary of the entries in range:
        matches_found = {k: rdb.SearchResult(v.num) \
                         for k,v in rdb.PlayerList.iteritems()}
        for rd in rdb.RoundDetailList:
            dprint("Looking at:", rd)
            rnd = rdb.RoundList[rd.round_num]
            dprint("From:      ", rnd)
            if not (start_dt <= rnd.rdate <= end_dt):
                continue
            dprint("Found a match!")
            matches_found[rd.player_num].AddResults(rd)
        for pnum,sr in matches_found.iteritems():
            dprint("Found match[%d]:" % pnum, sr)
        # fill in data for our GUI list
        self.item_data = {}
        for pnum,sr in matches_found.iteritems():
            if sr.rnd_cnt > 0:
                pname = rdb.PlayerList[sr.pnum].name
                self.item_data[pnum] = (pname, sr.rnd_cnt, sr.TotalPoints(),
                                        sr.PointsPerRound(),
                                        sr.acnt, sr.ecnt, sr.aecnt,
                                        sr.won_9s, sr.won_18s,
                                        sr.won_33s,
                                        0, 0, 0)
                dprint("Created data item:", self.item_data[pnum])
        self.InitUI()

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Score Results')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(15)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.results_list = lc.AutoWidthListCtrl(panel)
        self.results_list.SetupListHdr(\
            ['Name', 'Rounds', 'TtlPts', 'PPR',
             'Aces', 'Eagles', 'Ace-Eagles',
             '9-s', '18-s', '33-s', '$ Won', 'Best F9', 'Best B9'],
            [wx.LIST_FORMAT_LEFT, wx.LIST_FORMAT_CENTER] + \
            [wx.LIST_FORMAT_RIGHT] * 11,
            ['%s', '%d', '%5.2f', '%5.2f'] + ['%d'] * 9)
        self.results_list.SetupListItems(self.item_data)
        hbox2.Add(self.results_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        panel.SetSizer(vbox)

    def Quit(self, e):
        dprint("Quit? Really?")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class ChooseReportRangeFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChooseReportRangeFrame, self).__init__(*args, **kwargs)
        self.SetSize((350, 250))
        self.InitUI()
        self.Bind(wx.EVT_CLOSE, self.Quit)

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        st1 = wx.StaticText(panel, label='Report Setup')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        start_rdate_label = wx.StaticText(panel, label='Report Starting Date')
        self.start_rdate = wx.DatePickerCtrl(panel, size=(110, 20))
        vbox21 = wx.BoxSizer(wx.VERTICAL)
        vbox21.Add(start_rdate_label, flag=wx.TOP, border=10)
        vbox21.AddSpacer(5)
        vbox21.Add(self.start_rdate, flag=wx.BOTTOM, border=10)
        hbox2.Add(vbox21, flag=wx.LEFT)
        hbox2.AddStretchSpacer(1)
        stop_rdate_label = wx.StaticText(panel, label='Report Ending Date')
        self.stop_rdate = wx.DatePickerCtrl(panel, size=(110, 20))
        vbox22 = wx.BoxSizer(wx.VERTICAL)
        vbox22.Add(stop_rdate_label, flag=wx.TOP, border=10)
        vbox22.AddSpacer(5)
        vbox22.Add(self.stop_rdate, flag=wx.BOTTOM, border=10)
        hbox2.Add(vbox22, flag=wx.RIGHT)
        ####
        self.Bind(wx.EVT_DATE_CHANGED, self.DateChanged,
                  source=self.start_rdate)
        self.Bind(wx.EVT_DATE_CHANGED, self.DateChanged,
                  source=self.stop_rdate)
        ####
        vbox.Add(hbox2, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(panel, label='Precanned Ranges:')
        date_range_choices = ['<Choose a Range>', 'YTD', 'Last Year']
        self.cbox = wx.ComboBox(panel, id=wx.ID_ANY,
                                value=date_range_choices[0],
                                choices=date_range_choices,
                                style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.DateRangeChoosen, source=self.cbox)
        hbox3.Add(st)
        hbox3.AddSpacer(5)
        hbox3.Add(self.cbox)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        self.results_button = wx.Button(panel, label='Show Results')
        vbox.AddSpacer(20)
        vbox.Add(self.results_button, flag=wx.CENTER|wx.ALIGN_CENTER,
                 border=10)
        self.results_button.Disable()
        self.Bind(wx.EVT_BUTTON, self.ShowResults, source=self.results_button)
        vbox.AddSpacer(20)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Please choose a Date Range")
        self.status_bar.SetBackgroundColour(wx.NullColour)
        ################################################################
        panel.SetSizer(vbox)

    def DateChanged(self, e):
        dprint("One of our dates has changed!", e)
        if self.DateRangeValid():
            self.results_button.Enable()
            self.status_bar.SetStatusText("")
            self.status_bar.SetBackgroundColour(wx.NullColour)
        else:
            self.results_button.Disable()

    def DateRangeChoosen(self, e):
        dprint("A pre-canned Date range has been choosen", e)
        dprint("Choice String: %s" % e.GetString())
        canned_choice = e.GetString()
        if canned_choice == 'YTD':
            dprint("Using 1/1/THISYEAR to NOW")
            dt_end = wx.DateTime.Today()
            dprint("Found end date (today) of:", dt_end)
            dt_start = wx.DateTime()
            dt_start.Set(1, 0, dt_end.GetYear())
            dprint("Found end date (today) of:", dt_end)
        elif canned_choice == 'Last Year':
            dprint("Using 1/1/LASTYEAR to 12/31/LASTYEAR")
            last_yr = wx.DateTime.Today().GetYear() - 1
            dt_start = wx.DateTime()
            dt_start.Set(1, 0, last_yr)
            dt_end = wx.DateTime()
            dt_end.Set(31, 11, last_yr)
        else:
            dprint("No valid choice")
            return
        dprint("Starting Date Range:", dt_start)
        dprint("Stopping Date Range:", dt_end)
        self.start_rdate.SetValue(dt_start)
        self.stop_rdate.SetValue(dt_end)
        self.DateChanged(e)

    def DateRangeValid(self):
        '''Is our date range valid?'''
        rd_start = self.start_rdate.GetValue()
        dprint("Date Range Valid: start=", rd_start)
        rd_stop = self.stop_rdate.GetValue()
        dprint("Date Range Valid: stop=", rd_stop)
        return rd_stop > rd_start

    def ShowResults(self, e):
        dprint("Show Results, Damnit!", e)
        df = DisplayReportFrame(self.GetParent(), title="Where's The Beef?")
        df.MyStart(self.start_rdate.GetValue(),
                   self.stop_rdate.GetValue())
        self.Close()

    def Quit(self, e):
        dprint("Quit? Really?")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class RoundsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(RoundsFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(300, 300))
        self.InitUI()
        pub.subscribe(self.OnNewRoundExists, "ROUND UPDATE")

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Current Rounds')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.round_list = lc.AutoWidthListCtrl(panel)
        self.round_list.SetupListHdr(['Date', 'Course', 'Players'],
                                     [wx.LIST_FORMAT_LEFT,
                                      wx.LIST_FORMAT_LEFT,
                                      wx.LIST_FORMAT_LEFT],
                                     ['%s', '%s', '%s'])
        self.SetRoundList()
        hbox2.Add(self.round_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListSelected,
                  source=self.round_list, id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnListDeselected,
                  source=self.round_list, id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnShow)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        #self.quit_button = wx.Button(panel, id=wx.ID_EXIT, label='Quit')
        self.show_button = wx.Button(panel, id=wx.ID_EDIT,
                                     label='Show/Edit Round')
        self.new_button = wx.Button(panel, id=wx.ID_NEW, label='New Round')
        self.show_button.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnNewRound, source=self.new_button)
        self.Bind(wx.EVT_BUTTON, self.OnShow, source=self.show_button)
        hbox3.AddSpacer(10)
        hbox3.Add(self.show_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.new_button)
        hbox3.AddSpacer(10)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################

    def SetRoundList(self):
        dprint("Setting Round List for this frame")
        item_data = {}
        for c, rnd in rdb.RoundList.iteritems():
            dprint("looking at %d:" % c, rnd)
            course_name = rdb.CourseList[rnd.course_num].name
            dprint("Searching for players for round number: %d" % rnd.num)
            player_cnt = 0
            for rd in rdb.RoundDetailList:
                dprint("Looking for round %d in:" % rnd.num, rd)
                if rd.round_num == rnd.num:
                    player_cnt += 1
            # items must be strings for the GUI
            item_data[c] = (rnd.rdate.strftime("%m/%d/%Y") ,
                            course_name,
                            str(player_cnt))
        self.round_list.SetupListItems(item_data)

    def OnListSelected(self, e):
        dprint("List Selected")
        self.show_button.Enable()

    def OnListDeselected(self, e):
        dprint("List Deselected")
        self.show_button.Disable()

    def OnNewRound(self, e):
        dprint("*** New Round!")
        SetupRoundFrame(self, title='Setup a New Round')

    def OnShow(self, e):
        '''show an existing round'''
        dprint("*** Show an existing round")
        idx = self.round_list.GetFirstSelected()
        key = self.round_list.GetItemData(idx)
        rnd = rdb.RoundList[key]
        round_details = []
        for rd in rdb.RoundDetailList:
            dprint("looking for round %d in:" % rnd.num, rd)
            if rnd.num == rd.round_num:
                round_details.append(rd)
        srf = RoundScoringFrame(self, title='Examine a Round')
        srf.MyCreate(rnd, round_details, for_update=True)

    def OnNewRoundExists(self, message):
        '''A "NEW ROUND" message has been received'''
        dprint("Message Received: New Round: %s" % message)
        rdb.init_rounds()
        self.SetRoundList()
        self.Show(True)

    def Quit(self, e):
        dprint("QUITing RoundsFrame")
        self.Destroy()

    def OnAbout(self, e):
        description = """Disc Golf Score Manager manages and scores Disc
Golf rounds. It contains a list of Players and a list of Courses
and it allows users to edit existing rounds or create new ones.
It will also soon support displaying results, dude! New versions
may very well solve the P-vs-NP problem, if we're lucky!"""
        licence = """Disc Golf Score Manager is free software;
you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option)
any later version.

Disc Golf Score Manager is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('AboutIcon.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Disc Golf Score Manager')
        info.SetVersion(__version__)
        info.SetDescription(description)
        info.SetCopyright('(C) 2016 Lee Duncan')
        info.SetWebSite('http://www.gonzoleeman.net')
        info.SetLicence(licence)
        info.AddDeveloper('Lee Duncan')
        info.AddDocWriter('Lee Duncan')
        info.AddArtist('Natty')
        info.AddArtist('DD')
        info.AddTranslator('Cyndi Duncan')
        wx.AboutBox(info)

    def SetUpMenuBar(self):
        # create the 'File' menu and fill it in
        fmenu = wx.Menu()
        qmi = wx.MenuItem(fmenu, wx.ID_EXIT, '&Quit')
        fmenu.AppendItem(qmi)
        self.Bind(wx.EVT_MENU, self.Quit, qmi, wx.ID_EXIT)
        # create the reports menu
        rmenu = wx.Menu()
        rmi = wx.MenuItem(rmenu, wx.ID_VIEW_DETAILS, '&Display Report Window')
        rmenu.AppendItem(rmi)
        self.Bind(wx.EVT_MENU, self.Report, rmi, wx.ID_VIEW_DETAILS)
        # create the help menu
        hmenu = wx.Menu()
        hmi = wx.MenuItem(hmenu, wx.ID_ABOUT, '&About')
        hmenu.AppendItem(hmi)
        self.Bind(wx.EVT_MENU, self.OnAbout, hmi, wx.ID_ABOUT)
        # create and fill in the mnu bar
        mbar = wx.MenuBar()
        mbar.Append(fmenu, '&File')
        mbar.Append(rmenu, '&Reports')
        mbar.Append(hmenu, '&Help')
        self.SetMenuBar(mbar)
        # set shortcuts for menu CTRL-KEY combos ...
        accel_tbl = wx.AcceleratorTable(
            [(wx.ACCEL_CTRL, ord('X'), wx.ID_EXIT),
             (wx.ACCEL_CTRL, ord('R'), wx.ID_VIEW_DETAILS),
             (wx.ACCEL_CTRL, ord('A'), wx.ID_ABOUT)
             ])
        self.SetAcceleratorTable(accel_tbl)

    def Report(self, e):
        dprint("*** Report time!")
        ChooseReportRangeFrame(self, title='Choose Report Date Range')

    def InitUI(self):
        self.SetUpMenuBar()
        self.SetUpPanel()
        self.Show(True)


################################################################

def parse_options():
    parser = OptionParser(version='%prog ' + __version__,
                          usage='usage: %prog [options]',
                          description='Disc Golf Database, version ' + \
                              __version__)
    parser.add_option('-d', '--debug', action='store_true',
                      help='enter debug mode [%default]')
    (o, a) = parser.parse_args()
    opts.debug = o.debug

def main():
    parse_options()
    rdb.init_db()
    app = wx.App()
    RoundsFrame(None, title='DGDB: The Disc Golf Database')
    app.MainLoop()


if __name__ == '__main__':
    main()
    sys.exit(0)
