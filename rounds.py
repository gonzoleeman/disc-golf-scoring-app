#!/usr/bin/python
"""
These are the classes and data for dealing with
'Rounds', where a Round is an instance of a group
of players playing 18 holes of Disc Golf on a
given date at a given course location.
"""

import wx
from wx.lib.pubsub import Publisher as pub
import copy

import rdb
from utils import dprint
from opts import opts
import listctrl as lc
import wxdate
import money_rounds
import score
import report


class CurrentRoundsFrame(wx.Frame):
    '''
    The main frame of the program, with menu bar. This window lists
    the current rounds (if any), and gives the user the choice of editing
    a round, creating a round, or generate a report
    '''
    def __init__(self, *args, **kwargs):
        super(CurrentRoundsFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(300, 300))
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
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRoundListSelected,
                  source=self.round_list)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnRoundListDeselected,
                  source=self.round_list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnShow,
                  source=self.round_list)
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
        pub.subscribe(self.OnNewRoundExists, "ROUND UPDATE")

    def SetRoundList(self):
        '''Set up our rounds list items based on current round data'''
        dprint("Setting Round List for this frame")
        item_data = {}
        for c, rnd in rdb.RoundList.iteritems():
            dprint("looking at %d:" % c, rnd)
            course_name = rdb.CourseList[rnd.course_num].name
            dprint("Searching for players for round number: %d" % rnd.num)
            player_cnt = 0
            dprint("RoundDetailList length is %d" % len(rdb.RoundDetailList))
            for rd in rdb.RoundDetailList:
                dprint("Looking for round %d in:" % rnd.num, rd)
                if rd.round_num == rnd.num:
                    player_cnt += 1
            # items must be strings for the GUI
            item_data[c] = (rnd.rdate.strftime("%m/%d/%Y") ,
                            course_name,
                            str(player_cnt))
        self.round_list.SetupListItems(item_data)

    def OnRoundListSelected(self, e):
        dprint("Round List Selected")
        self.show_button.Enable()

    def OnRoundListDeselected(self, e):
        dprint("Round List Deselected")
        self.show_button.Disable()

    def OnNewRound(self, e):
        dprint("*** New Round!")
        RoundSetupFrame(self, title='Setup a New Round')

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
        srf = RoundDetailsFrame(self, title='Examine a Round')
        srf.MyCreate(rnd, round_details, for_update=True)

    def OnNewRoundExists(self, message):
        '''A "NEW ROUND" message has been received'''
        dprint("Message Received: New Round: %s" % message)
        rdb.init_rounds()
        self.SetRoundList()
        self.Show(True)

    def Quit(self, e):
        dprint("QUITing CurrentRoundsFrame")
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
        report.ReportSetupFrame(self, title='Choose Report Date Range')

    def InitUI(self):
        self.SetUpMenuBar()
        self.SetUpPanel()
        self.Show(True)


class RoundSetupFrame(wx.Frame):
    '''
    This frame is used to get all the information needed to set
    up a round. That information is just the player list. It used
    to be more, but now that is all we need.
    '''
    def __init__(self, *args, **kwargs):
        super(RoundSetupFrame, self).__init__(*args, **kwargs)
        self.SetSize((wx.Size(200, 400)))
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
                  source=self.player_list)
        pub.subscribe(self.OnCheckItem, "ITEM CHECK UPDATE")
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_EXIT, label='Cancel')
        self.start_button = wx.Button(panel, label='Start')
        self.start_button.Bind(wx.EVT_BUTTON, self.OnStartScoring)
        cancel_button.Bind(wx.EVT_BUTTON, self.Quit)
        self.start_button.Disable()
        vbox.AddSpacer(10)
        hbox3.Add(cancel_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.start_button)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.SetNormalStatus("Please choose players")
        ################################################################
        panel.SetSizer(vbox)

    def SetErrorStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.RED)

    def SetNormalStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def SetScoreButtonState(self):
        '''Set appropriate state for the "Score" Button'''
        dprint("%d players selected" % \
               self.player_list.item_check_count)
        if self.player_list.item_check_count > 0:
            self.start_button.Enable()
            self.SetNormalStatus("")
        else:
            self.start_button.Disable()
            self.SetNormalStatus("Please choose players")

    def OnPlayerListSelected(self, e):
        dprint("Player[%d] Selected" % e.Index)
        self.player_list.Select(e.Index, False)
        self.player_list.ToggleItem(e.Index)
        self.SetScoreButtonState()

    def OnCheckItem(self, evt):
        dprint("High level check item!:", evt)
        self.SetScoreButtonState()

    def OnStartScoring(self, e):
        dprint("*** 'Start' Scoring Button Pressed: players[%d]:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        ################################################################
        this_round = rdb.Round(rdb.next_round_num())
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
        srf = RoundDetailsFrame(self.GetParent(), title='Score a Round')
        srf.MyCreate(this_round, round_details, for_update=False)
        self.Destroy()

    def Quit(self, e):
        '''Either .... happened'''
        # Do we need to check for database modified here, with a popup?
        # (I do not think so)
        dprint("QUITing RoundSetupFrame")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


class RoundDetailsFrame(wx.Frame):
    '''
    This is the window used to create or edit a Round and some
    some RoundDetails.
    '''
    def __init__(self, *args, **kwargs):
        super(RoundDetailsFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(700, 300))
        self.for_update = False
        self.this_round = None
        self.this_mround = None
        self.for_update = None
        self.round_details = None
        self.calc_done = False
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        # this means something on the GUI has changed
        self.is_edited = False
        # has ever been committed
        self.is_committed = False
        # this means our internal state matches the GUI
        self.data_from_form_up_to_date = False

    def MyCreate(self, this_round, round_details, for_update=False):
        dprint("Creating (filling in) %s " % self.__class__.__name__)
        self.for_update = for_update
        self.this_round = this_round
        # was there a money round for this round
        self.round_details = sorted(round_details,
                                    key=lambda rd: rd.player_num)
        dprint("Added round with Details:", this_round)
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
        st2 = wx.StaticText(panel, label='Round Date:')
        st2.SetFont(bold_font)
        self.round_date_picker = wx.DatePickerCtrl(panel, size=wx.Size(110, 20))
        self.round_date_picker.SetValue(\
            wxdate.dt_to_wxdt(self.this_round.rdate))
        st3 = wx.StaticText(panel, label='Course Location:')
        st3.SetFont(bold_font)
        course_choices = ['<choose>'] + \
                         [c.name for c in rdb.CourseList.itervalues()]
        self.course_choice = wx.Choice(panel, choices=course_choices)
        dprint("Setting initial course number to:", self.this_round.course_num)
        course_num_selected = self.this_round.course_num
        if course_num_selected is None:
            course_num_selected = 0     # 0 -> no course yet
        self.course_choice.SetSelection(course_num_selected)
        self.Bind(wx.EVT_CHOICE, self.OnCourseChosen, source=self.course_choice)
        hbox2.AddSpacer(20)
        hbox2.Add(st2)
        hbox2.AddSpacer(5)
        hbox2.Add(self.round_date_picker)
        hbox2.AddStretchSpacer(2)
        hbox2.Add(st3)
        hbox2.AddSpacer(5)
        hbox2.Add(self.course_choice)
        hbox2.AddSpacer(20)
        vbox.Add(hbox2, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ####
        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged,
                  source=self.round_date_picker)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.score_list = lc.AutoWidthListEditCtrl(panel)
        self.hdg_items = ['Name', 'Front 9', 'Back 9', 'Overall',
                          'Aces', 'Eagles', 'Ace-Eagles', 'Points']
        self.score_list.SetupListHdr(self.hdg_items,
                                     [wx.LIST_FORMAT_LEFT] + \
                                     [wx.LIST_FORMAT_CENTER] * 7,
                                     ['%s', '%+d', '%+d', '%+d',
                                      '%d', '%d', '%d', '%s'])
        self.RoundDetailsAsDict()
        self.score_list.SetupListItems(self.item_data)
        self.score_list.SetEditColumnOk([1, 2, 4, 5, 6])
        hbox3.Add(self.score_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        self.Bind(lc.EVT_LIST_EDITED_EVT, self.OnListEdited,
                  source=self.score_list)
        ################################################################
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_CANCEL, label='Cancel')
        lab = 'Update' if self.for_update else 'Commit'
        self.commit_button = wx.Button(panel, id=wx.ID_SAVE, label=lab)
        self.calc_button = wx.Button(panel, id=wx.ID_SETUP,
                                     label='Calculate Points')
        self.calc_done = False
        self.mround_button = wx.Button(panel, label=lab)
        self.SetMroundButtonState()
        self.Bind(wx.EVT_BUTTON, self.OnCancel, source=cancel_button)
        self.Bind(wx.EVT_BUTTON, self.OnCommit, source=self.commit_button)
        self.Bind(wx.EVT_BUTTON, self.OnCalculate, source=self.calc_button)
        self.Bind(wx.EVT_BUTTON, self.OnMoneyRound, source=self.mround_button)
        hbox4.AddSpacer(10)
        hbox4.Add(cancel_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.commit_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.mround_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.calc_button)
        vbox.Add(hbox4, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        self.SetCommitButtonState()
        ################################################################
        panel.SetSizer(vbox)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.SetNormalStatus("Please fill in the scores")
        # get data from the frame, just to validate existing data,
        # and to enable the "Edit Frame" button, if needed
        if self.GetDataFromFrameIfNeeded():
            # if data is good enable allow editing now
            self.mround_button.Enable()
        ################################################################
        pub.subscribe(self.OnNewMoneyRoundExists, "MONEY ROUND UPDATE")
        self.SetDateFromPicker()

    def ExistingMoneyRound(self):
        '''Is there a money round for this round? Return None or the number'''
        return rdb.MoneyRoundList.get(self.this_round.num)

    def SetMroundButtonState(self):
        if self.ExistingMoneyRound():
            lab = 'Edit Money Round'
        else:
            lab = 'Create Money Round'
        self.mround_button.SetLabel(lab)

    def OnNewMoneyRoundExists(self, message):
        dprint("New money round! change our button state, if needed")
        rdb.init_rounds()
        dprint("our round no:", self.this_round.num)
        dprint("our mround?: ", rdb.MoneyRoundList.get(self.this_round.num))
        self.SetMroundButtonState()

    def OnDateChanged(self, evt):
        dprint("Round Date Changed!", evt)
        self.is_edited = True
        self.SetDateFromPicker()
        self.SetCommitButtonState()

    def SetDateFromPicker(self):
        # get Month, Day, and Year from DatePicker
        wx_rdate = self.round_date_picker.GetValue()
        dprint("Raw wx_rdate from form:", wx_rdate)
        rdate = wxdate.wxdt_to_dt(wx_rdate)
        dprint("Round Date: %s -> %s" % (wx_rdate, rdate))
        self.this_round.rdate = rdate
        dprint("Set round date to:", rdate)
        dprint("So now:", self.this_round)

    def SetCommitButtonState(self):
        course_num = self.course_choice.GetSelection()
        self.commit_button.Enable(self.is_edited and course_num > 0)
        self.mround_button.Enable(self.is_committed or \
                                  self.ExistingMoneyRound() is not None)

    def OnCommit(self, e):
        dprint("OnCommit: %s Round DB requested" % \
               ('Update' if self.for_update else 'Commit'))
        dprint("DB State: edited=%s, calc_done=%s form_up_to_date=%s, " % \
               (self.is_edited, self.calc_done, self.data_from_form_up_to_date))
        # save the date of our current round, since it can
        # change when we get data from the frame
        this_round_rdate_saved = self.this_round.rdate
        if not self.GetDataFromFrameIfNeeded():
            dprint("XXX need to diplay error status here: data invalid!")
            return
        if not self.is_edited:
            raise Exception("Internal Error: Committing non-edited list?")
        if self.for_update:
            # XXX we should check for this round having the date of a round
            # already in the database (not counting this round)
            # NOT YET IMPLEMENTED
            rdb.modify_round(self.this_round, self.round_details)
        else:
            # check for duplicate round
            for rnd in rdb.RoundList.itervalues():
                dprint("Looking at an existing:", rnd)
                if rnd.rdate == this_round_rdate_saved:
                    self.SetErrorStatus("Duplicate Round Date: Change Date")
                    return False
            rdb.add_round(self.this_round, self.round_details)
            self.SetNormalStatus("")
        rdb.commit_db()
        dprint("Updating parent GUI ...")
        pub.sendMessage("ROUND UPDATE", self.this_round)
        self.is_edited = False
        self.is_committed = True
        self.SetCommitButtonState()
        #self.Close()

    def OnCourseChosen(self, evt):
        '''A course has been choosen'''
        dprint("A Course has been choosen:", evt)
        course_num = self.course_choice.GetSelection()
        if course_num > 0 and \
           course_num != self.this_round.course_num:
            dprint("A Valid and new course choosen: %d" % course_num)
            self.is_edited = True
            self.data_from_form_up_to_date = False
        self.SetCommitButtonState()

    def RoundDetailsAsDict(self):
        dprint("Making Round Details into dictionary ...")
        self.item_data = {}
        for rd in self.round_details:
            dprint(rd)
            player = rdb.PlayerList[rd.player_num]
            self.item_data[rd.player_num] = (player.name,
                                             rd.fstrokes, rd.bstrokes,
                                             rd.OverallStrokes(),
                                             rd.acnt, rd.ecnt, rd.aecnt,
                                             rd.CalcScore())
            dprint("Set item_data[%d] to" % rd.player_num,
                   self.item_data[rd.player_num])

    def SetErrorStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.RED)

    def SetNormalStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def GetDataFromFrameIfNeeded(self):
        '''
        Get data from our score list into our self.round_details

        Return True if data was legal,
        Else return False and leave data partially updated
        '''
        dprint("*** GetDataFromFrameIfNeeded (rounds): form_up_to_date=%s" % \
               self.data_from_form_up_to_date )
        if self.data_from_form_up_to_date:
            return True
        # get data from list into
        ####
        cnt = self.score_list.GetItemCount()
        dprint("Round detail list has %d items for round %d:" % \
               (cnt, self.this_round.num))
        ####
        self.this_round.course_num = self.course_choice.GetSelection()
        dprint("Set round course number to %d" % self.this_round.course_num)
        # XXX not needed?
        if False:
            # get Month, Day, and Year from DatePicker
            wx_rdate = self.round_date_picker.GetValue()
            dprint("Raw wx_rdate from form:", wx_rdate)
            rdate = wxdate.wxdt_to_dt(wx_rdate)
            dprint("Round Date: %s -> %s" % (wx_rdate, rdate))
            self.this_round.rdate = rdate
            dprint("Set round date to:", rdate)
            dprint("So now:", self.this_round)
        ####
        for c in range(cnt):
            dprint("Looking for round_detail index %d" % c)
            round_detail = self.round_details[c]
            dprint(round_detail)
            pname = self.score_list.GetItemText(c)
            dprint("Item %d: %s" % (c, pname))
            try:
                f9 = self.score_list.GetFieldNumericValue(c, 1)
                b9 = self.score_list.GetFieldNumericValue(c, 2)
                acnt = self.score_list.GetFieldNumericValue(c, 4)
                ecnt = self.score_list.GetFieldNumericValue(c, 5)
                aecnt = self.score_list.GetFieldNumericValue(c, 6)
            except ArithmeticError, e:
                col_no = e.args[1]
                hdg = self.hdg_items[col_no]
                self.SetErrorStatus("%s's %s invalid" % (pname, hdg))
                return False
            ####
            self.round_details[c].SetScore(f9, b9)
            self.round_details[c].SetCounts(acnt, ecnt, aecnt)
            self.SetNormalStatus("")
        ####
        self.data_from_form_up_to_date = True
        return True

    def OnCalculate(self, e):
        dprint("*** OnCalculate ...")
        if not self.GetDataFromFrameIfNeeded():
            dprint("Round data AFU!")
            return
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
            # flag that we need to update data from our form
            self.data_from_form_up_to_date = False
            dprint("List *WAS* edited: updating")
            self.round_details = scored_details
            self.RoundDetailsAsDict()
            self.score_list.SetupListItems(self.item_data)
            self.SetCommitButtonState()
        else:
            # else already edited 
            dprint("List was /not/ edited, so nothing to do?")
        self.calc_done = True

    def OnMoneyRound(self, e):
        '''Money Round edit or Create'''
        dprint("Money round time!")
        if not self.GetDataFromFrameIfNeeded():
            dprint("Round data AFU!")
            return
        # do we already have a money round
        mround = rdb.MoneyRoundList.get(self.this_round.num)
        mround_details = []
        if mround:
            dprint("There IS an existing money round, so using it")
            # this must be a money round update
            # get list of matching money round details from the DB
            for mrd in rdb.MoneyRoundDetailList:
                dprint("Coparing against:", mrd)
                if mround.round_num == mrd.round_num:
                    mround_details.append(mrd)
            mrdf = money_rounds.MoneyRoundDetailsFrame(self,
                                                       title='Money Round')
            mrdf.MyCreate(self.this_round, mround, mround_details,
                          for_update=True)
        else:
            dprint("Creating a new money round, from scratch, from:",
                   self.this_round)
            # create a money round -- must pick players first
            mround = rdb.MoneyRound(self.this_round.num)
            # create list of player numbers
            players = [rd.player_num for rd in self.round_details]
            dprint("Found player number list:", players)
            mrdf = money_rounds.MoneyRoundSetupFrame(self,
                                                     title='Set Up Money Round')
            mrdf.MyCreate(self.this_round, mround, players)

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
        dprint("OnListEdited: Col=%d: %s" % (evt.col, evt.message))
        # was editing in the front9/back9 columns?
        if evt.col in [1, 2]:
            self.calc_button.Enable()
            self.calc_done = False
        # but any change means we need to save the changes
        self.is_edited = True
        self.SetCommitButtonState()
        # flag that we need to update data from our form
        self.data_from_form_up_to_date = False

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)

