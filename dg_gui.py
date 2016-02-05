#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - implement updating the database (rounds only, to update score)

    - handle conflict when trying to add a new round, when
      it is not unique

    - handle case when we calculate, and no values change, but
      DB thinks it has been modified

    - use real fraction math to get fractions correct for "score"

    - make setup window become the scoring window for a round,
      instead of just replacing one window with the next

    - implement looking at results (including graphing?)
    - display results, e.g. year-to-date, custom-range?
      (and what about a graph? woo hoo!)

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



__author__ = "Lee Duncan"
__version__ = "1.8"


class SetupRoundFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SetupRoundFrame, self).__init__(*args, **kwargs)
        self.SetSize((wx.Size(400, 400)))
        self.InitUI()
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

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
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.PlayerListSelected,
                  source=self.player_list,
                  id=wx.ID_ANY)
        ################################################################
        hbox2.AddSpacer(15)
        self.course_list = lc.AutoWidthListCtrl(panel)
        #self.course_list.InsertColumn(0, 'Choose a Course', width=100)
        self.course_list.SetupListHdr(['Choose a Course'],
                                      [wx.LIST_FORMAT_LEFT],
                                      ['%s'])
        item_data = {}
        for k, c in rdb.CourseList.iteritems():
            item_data[k] = (c.name,)
        self.course_list.SetupListItems(item_data)
        #cnt = 0
        #for k in rdb.CourseList.iterkeys():
        #    c = rdb.CourseList[k]
        #    self.course_list.InsertStringItem(cnt, c.name)
        #    self.course_list.SetItemData(cnt, k)
        #    dprint("Inserted %s in list, index=%d" % (c, cnt))
        #    cnt += 1
        hbox2.Add(self.course_list, 1, wx.EXPAND|wx.RIGHT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.CourseListSelected,
                  source=self.course_list,
                  id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.CourseListSelected,
                  source=self.course_list,
                  id=wx.ID_ANY)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_EXIT, label='Cancel')
        date_label = wx.StaticText(panel, label='Date')
        self.round_date = wx.DatePickerCtrl(panel, size=wx.Size(110, 20))
        self.score_button = wx.Button(panel, label='Score a Round')
        self.Bind(wx.EVT_BUTTON, self.OnScoreARound,
                  source=self.score_button)
        self.Bind(wx.EVT_BUTTON, self.OnQuit, source=cancel_button)
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
        panel.SetSizer(vbox)

    def SetScoreButtonState(self):
        '''Set appropriate state for the "Score" Button'''
        i = self.course_list.GetFirstSelected()
        dprint("Course Selected: %d; Players Selected: %d" % \
               (i, self.player_list.item_check_count))
        if i >= 0 and self.player_list.item_check_count > 0:
            self.score_button.Enable()
        else:
            self.score_button.Disable()

    def PlayerListSelected(self, e):
        dprint("Player[%d] Selected" % e.Index)
        self.player_list.Select(e.Index, False)
        self.player_list.ToggleItem(e.Index)
        self.SetScoreButtonState()

    def CourseListSelected(self, e):
        dprint("Course[%d] Selected:" % e.Index, e)
        self.SetScoreButtonState()

    def OnScoreARound(self, e):
        dprint("*** 'Score' Button Pressed: players selected=%d:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        ################################################################
        i = self.course_list.GetFirstSelected()
        cnum = self.course_list.GetItemData(i)
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
        this_round = rdb.Round(rdb.next_round_num(), cnum,
                               rdate.strftime("%m/%d/%Y"))
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
            dprint("Created Round Detail:", rd)
        round_details = sorted(round_details, key=lambda rd: rd.player_num)
        ################################################################
        # popup a window to enter the scores for round then go away
        srf = RoundScoreFrame(self.GetParent(), title='Score a Round')
        srf.MyCreate(this_round, round_details, for_update=False)
        self.Destroy()

    def OnQuit(self, e):
        # XXX Do we need to check for database modified here, with a popup?
        dprint("QUITing SetupRoundFrame")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


class RoundScoreFrame(wx.Frame):
    '''
    For Creating an entry for a new Round
    '''
    def __init__(self, *args, **kwargs):
        super(RoundScoreFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(500, 300))
        self.is_edited = False
        self.cnum = None
        self.rdate = None
        self.for_update = None
        self.this_round = None
        self.for_update = None
        self.round_details = None

    def MyCreate(self, this_round, round_details, for_update=False):
        self.cnum = this_round.course_num
        self.rdate = this_round.rdate
        self.for_update = for_update
        dprint("Score Create: Course[%d], round date: %s" % \
               (self.cnum, self.rdate))
        self.this_round = this_round
        self.round_details = round_details
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
        vbox.AddSpacer(10)
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
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.score_list = lc.AutoWidthListEditCtrl(panel)
        self.score_list.SetupListHdr(['Name', 'Front 9', 'Back 9',
                                      'Aces', 'Eagles', 'Score'],
                                     [wx.LIST_FORMAT_LEFT,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_CENTER,
                                      wx.LIST_FORMAT_RIGHT],
                                     ['%s', '%d', '%d',
                                      '%d', '%d', '%5.2f'])
        item_data = self.RoundDetailsAsDict()
        self.score_list.SetupListItems(item_data)
        hbox3.Add(self.score_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        self.Bind(lc.EVT_LIST_EDITED_EVT, self.ListEditedEvent,
                  source=self.score_list)
        ################################################################
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_CANCEL, label='Cancel')
        lab = 'Commit'
        if self.for_update:
            lab = 'Update'
        self.commit_button = wx.Button(panel, id=wx.ID_SAVE, label=lab)
        self.commit_button.Disable()
        self.calc_button = wx.Button(panel, id=wx.ID_SETUP,
                                          label='Calculate')
        #self.calc_button.Disable()
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

    def OnCommit(self, e):
        dprint("Commit/Update DB requested -- hope you're sure")
        if self.for_update:
            dprint("Oh Oh -- DB update NOT YET IMPLEMENTED")
            return # XXX for now
        else:
            rdb.add_round(self.this_round, self.round_details)
            rdb.commit_db()
            dprint("Updating parent ...")
        pub.sendMessage("ROUND UPDATE", self.this_round)
        self.is_edited = False
        self.Close()

    def RoundDetailsAsDict(self):
        dprint("Making Round Details into dictionary ...")
        item_data = {}
        for rd in self.round_details:
            dprint("Round Detail:", rd)
            player = rdb.PlayerList[rd.player_num]
            if False:
                item_data[rd.player_num] = (player.name,
                                            str(rd.fscore),
                                            str(rd.bscore),
                                            str(rd.acnt),
                                            str(rd.ecnt),
                                            str(rd.score))
            else:
                item_data[rd.player_num] = (player.name,
                                            rd.fscore,
                                            rd.bscore,
                                            rd.acnt,
                                            rd.ecnt,
                                            rd.score)
        return item_data

    def OnCalculate(self, e):
        # get data from list into
        cnt = self.score_list.GetItemCount()
        dprint("Our list has %d items" % cnt)
        for c in range(cnt):
            dprint("Looking for round_detail index %d" % c)
            round_detail = self.round_details[c]
            dprint("Round Detail:", round_detail)
            pname = self.score_list.GetItemText(c)
            dprint("Item %d: %s" % (c, pname))
            c1 = self.score_list.GetItem(c, 1).GetText()
            c2 = self.score_list.GetItem(c, 2).GetText()
            dprint("Score: c1=%s, c2=%s" % (c1, c2))
            ################
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
            dprint("Front Nine for player %s: %d" % (pname, f9))
            dprint("Back Nine for player %s: %d" % (pname, b9))
            self.status_bar.SetStatusText("")
            self.status_bar.SetBackgroundColour(wx.NullColour)
        dprint("All fields OK! scoring ...")
        pre_scored_details = copy.deepcopy(self.round_details)
        scored_details = score.score_round(self.round_details)
        self.is_edited = rdb.round_details_equal(pre_scored_details,
                                                 scored_details)
        if self.is_edited:
            self.round_details = scored_details
            item_data = self.RoundDetailsAsDict()
            self.score_list.SetupListItems(item_data)
            #self.calc_button.Disable()
            self.commit_button.Enable()

    def OnCancel(self, e):
        dprint("Cancel!: Edited=%s" % self.is_edited)
        if self.is_edited:
            res = wx.MessageBox('Data Modified. Are you sure?',
                                'Question',
                                wx.YES_NO | wx.ICON_WARNING)
            dprint("Message result:", res)
            if res == wx.NO:
                return
        self.Close()

    def ListEditedEvent(self, evt):
        dprint("Our List has been Edited!!!")
        #self.calc_button.Enable()
        self.commit_button.Disable()
        self.is_edited = True

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class RoundsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(RoundsFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(300, 300))
        self.InitUI()
        pub.subscribe(self.NewRoundExists, "ROUND UPDATE")

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
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListSelected,
                  source=self.round_list, id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ListDeselected,
                  source=self.round_list, id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnShow)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        #self.quit_button = wx.Button(panel, id=wx.ID_EXIT, label='Quit')
        self.show_button = wx.Button(panel, id=wx.ID_EDIT, label='Show Round')
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
        self.SetRounds(item_data)

    def SetRounds(self, rnd_list):
        dprint("Setting rounds list data for this frame")
        self.round_list.SetupListItems(rnd_list)

    def ListSelected(self, e):
        dprint("List Selected")
        self.show_button.Enable()

    def ListDeselected(self, e):
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
        srf = RoundScoreFrame(self, title='Examine a Round')
        srf.MyCreate(rnd, round_details, for_update=True)

    def NewRoundExists(self, message):
        dprint("New Round to be displayed: %s" % message)
        rdb.init_rounds()
        self.SetRoundList()
        self.Show(True)

    def SetUpMenuBar(self):
        # create the 'File' menu and fill it in
        fmenu = wx.Menu()

        qmi = wx.MenuItem(fmenu, wx.ID_EXIT, '&Quit')
        fmenu.AppendItem(qmi)
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([\
                (wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT),
                (wx.ACCEL_CTRL, ord('O'), wx.ID_OPEN),
                (wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE),
                ])
        self.SetAcceleratorTable(accel_tbl)

        # create the help menu
        hmenu = wx.Menu()
        hmi = wx.MenuItem(hmenu, wx.ID_ABOUT, 'About')
        hmenu.AppendItem(hmi)
        self.Bind(wx.EVT_MENU, self.OnAbout, hmi, wx.ID_ABOUT)

        # create and fill in the mnu bar
        mbar = wx.MenuBar()
        mbar.Append(fmenu, '&File')
        mbar.Append(hmenu, '&Help')

        self.SetMenuBar(mbar)

    def DBUpdate(self, e):
        '''A DB Update menu item has been choosen'''
        dprint('DBUpdate: id=', e.GetId())
        if e.GetId() == wx.ID_OPEN:
            dprint("open a new datbase: NOT YET IMPLEMENTED")
        else:
            dprint("save the current datbase: NOT YET IMPLEMENTED")

    def OnQuit(self, e):
        # XXX Do we need to check for database modified here, with a popup?
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

    def InitUI(self):
        self.SetUpMenuBar()
        self.SetUpPanel()
        self.Show(True)

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
