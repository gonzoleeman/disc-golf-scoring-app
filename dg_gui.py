#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - implement "look at a round" GUI
    - implement updating the database
    - implement saving the database
    - implement opening a new database
    - implement looking at results GUI

    - make setup window go away when scoring a round (use
      same window, with tabs or something?)

    - "are you sure" popup if exit with database modified

    - implement "About" popup

    - support DB modification for Courses (some day)

    - for scoring window:
      - implement "commit"
      - ask "are you sure" when cancel is choose on modified DB
      - update to handle round updates, e.g. "Commit" might
        become "Add/Update", depending on the purpose of the window

    -------------------------------

    - Properly package for distribution

    - implement real help? (like what?)

    - Add pictures to DB some day? (e.g. for start screen?)

    - preferences? not really needed yet: nothing to configure/prefer
      - e.g. which players are "usually there"
      - size of windows?

    - disable/enable menu choices as DB gets modified/saved
      (not needed?)

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
'''


import sys
from optparse import OptionParser
import wx
import re

import rdb
from utils import dprint
from opts import opts
import score
import listctrl as lc



__author__ = "Lee Duncan"
__version__ = "1.6"


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
        self.player_list.InsertColumn(0, 'Choose Players', width=100)
        cnt = 0
        for k in rdb.PlayerList.iterkeys():
            p = rdb.PlayerList[k]
            dprint("Setting up:", p)
            self.player_list.InsertStringItem(cnt, p.name)
            self.player_list.SetItemData(cnt, k)
            dprint("Inserted %s in list, index=%d" % (p, cnt))
            cnt += 1
        hbox2.Add(self.player_list, 1, wx.EXPAND|wx.LEFT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.PlayerListSelected,
                  source=self.player_list,
                  id=wx.ID_ANY)
        ################################################################
        hbox2.AddSpacer(15)
        self.course_list = lc.AutoWidthListCtrl(panel)
        self.course_list.InsertColumn(0, 'Choose a Course', width=100)
        cnt = 0
        for k in rdb.CourseList.iterkeys():
            c = rdb.CourseList[k]
            self.course_list.InsertStringItem(cnt, c.name)
            self.course_list.SetItemData(cnt, k)
            dprint("Inserted %s in list, index=%d" % (c, cnt))
            cnt += 1
        hbox2.Add(self.course_list, 1, wx.EXPAND|wx.RIGHT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.CourseListSelected,
                  source=self.course_list,
                  id=wx.ID_ANY)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_EXIT, label='Done')
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
        dprint("Course[%d] Selected" % e.Index)
        self.SetScoreButtonState()

    def OnScoreARound(self, e):
        dprint("Button Pressed: %d players selected:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        player_numbers = []
        for (k, v) in self.player_list.items_checked.iteritems():
            i = self.player_list.GetItemData(k)
            if v:
                player_numbers.append(i)
        dprint("Player number list:", player_numbers)
        player_numbers = sorted(player_numbers)
        dprint("Sorted Player number list:", player_numbers)
        i = self.course_list.GetFirstSelected()
        course_number = self.course_list.GetItemData(i)
        dprint("Course number: %d" % course_number)
        rdate = self.round_date.GetValue()
        dprint("round date:", rdate)
        self.ScoreRound(course_number, rdate, player_numbers)

    def ScoreRound(self, course_number, rdate, player_numbers):
        '''popup a window to enter the scores for round'''
        srf = ScoreRoundFrame(self, title='Score a Round')
        srf.Create(course_number, rdate, player_numbers)

    def OnQuit(self, e):
        # XXX Need to check for database modified here, with a popup?
        dprint("QUITing ...")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


class ScoreRoundFrame(wx.Frame):
    '''
    For Creating an entry for a new Round
    '''
    def __init__(self, *args, **kwargs):
        super(ScoreRoundFrame, self).__init__(*args, **kwargs)

    def Create(self, cnum, rdate, pnum_list):
        self.SetSize(wx.Size(500, 300))
        self.cnum = cnum
        self.rdate = rdate
        self.pnum_list = pnum_list
        dprint("Course number: %d, round date: %s" % (cnum, rdate))
        dprint("Player numbers:", pnum_list)
        self.this_round = rdb.Round(rdb.next_round_num(), cnum, rdate)
        self.round_details = []
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
        st3 = wx.StaticText(panel, label=self.rdate.Format('%m/%d/%Y'))
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
                                      'Aces', 'Eagles', 'Score'])
        item_data = {}
        for c in self.pnum_list:
            player = rdb.PlayerList[c]
            round = rdb.RoundDetail(self.this_round.num, player.num, 0, 0)
            self.round_details.append(round)
            item_data[player.num] = (player.name, "None", "None", "0", "0", "0")
        self.score_list.SetupListItems(item_data)
        hbox3.Add(self.score_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        self.Bind(lc.EVT_LIST_EDITED_EVT, self.ListEditedEvent,
                  source=self.score_list)
        ################################################################
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_CANCEL, label='Cancel')
        self.commit_button = wx.Button(panel, id=wx.ID_SAVE, label='Commit')
        self.commit_button.Disable()
        self.calc_button = wx.Button(panel, id=wx.ID_SETUP,
                                          label='Calculate')
        self.calc_button.Disable()
        self.Bind(wx.EVT_BUTTON, self.Cancel, source=cancel_button)
        self.Bind(wx.EVT_BUTTON, self.Commit, source=self.commit_button)
        self.Bind(wx.EVT_BUTTON, self.Calculate, source=self.calc_button)
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

    def Commit(self, e):
        dprint("Commit DB: NOT YET IMPLEMENTED")

    def Calculate(self, e):
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
        scored_details = score.score_round(self.round_details)
        for d in scored_details:
            dprint("Score Details Calculated:", d)
        self.round_details = scored_details
        item_data = {}
        for rnd in self.round_details:
            player = rdb.PlayerList[rnd.player_num]
            item_data[rnd.player_num] = (player.name,
                                        str(rnd.front_score),
                                        str(rnd.back_score),
                                        str(rnd.ace_cnt),
                                        str(rnd.eagle_cnt),
                                        str(rnd.score))
        self.score_list.SetupListItems(item_data)
        self.calc_button.Disable()
        self.commit_button.Enable()

    def Cancel(self, e):
        dprint("Cancel!")
        self.Close()

    def ListEditedEvent(self, evt):
        dprint("Our List has been Edited!!!")
        self.calc_button.Enable()
        self.commit_button.Disable()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class RoundsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(RoundsFrame, self).__init__(*args, **kwargs)
        self.SetSize(wx.Size(500, 300))
        self.InitUI()

    def SetRounds(self, rnd_list):
        self.round_list.SetupListItems(rnd_list)

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
        self.round_list.SetupListHdr(['Date', 'Course', 'Players'])
        item_data = {}
        for c in rdb.RoundList.iterkeys():
            rnd = rdb.RoundList[c]
            course_name = rdb.CourseList[rnd.course_num].name
            dprint("Searching for players for round number: %d" % rnd.num)
            player_cnt = 0
            for round_detail in rdb.RoundDetailList:
                dprint("Looking for round %d in:" % rnd.num, round_detail)
                if round_detail.round_num == rnd.num:
                    player_cnt += 1
            item_data[c] = (rnd.rdate, course_name, str(player_cnt))
        self.SetRounds(item_data)
        hbox2.Add(self.round_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListSelected,
                  source=self.round_list, id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ListDeselected,
                  source=self.round_list, id=wx.ID_ANY)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.quit_button = wx.Button(panel, id=wx.ID_EXIT, label='Quit')
        self.show_button = wx.Button(panel, id=wx.ID_EDIT, label='Show Round')
        self.new_button = wx.Button(panel, id=wx.ID_NEW, label='New Round')
        self.show_button.Disable()
        self.Bind(wx.EVT_BUTTON, self.OnNewRound, source=self.new_button)
        self.Bind(wx.EVT_BUTTON, self.OnQuit, source=self.quit_button)
        self.Bind(wx.EVT_BUTTON, self.OnShow, source=self.show_button)
        hbox3.AddSpacer(10)
        hbox3.Add(self.quit_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.show_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.new_button)
        hbox3.AddSpacer(10)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################

    def ListSelected(self, e):
        dprint("List Selected")
        self.show_button.Enable()

    def ListDeselected(self, e):
        dprint("List Deselected")
        self.show_button.Disable()

    def OnNewRound(self, e):
        dprint("New Round!")
        SetupRoundFrame(self, title='Setup a New Round')

    def OnShow(self, e):
        dprint("Show an existing round: NOT YET IMPLEMENTED")
        # XXX get list of player numbers in this round
        pass

    def SetUpMenuBar(self):
        # create the 'File' menu and fill it in
        fmenu = wx.Menu()

        omi = wx.MenuItem(fmenu, wx.ID_OPEN, '&Open')
        fmenu.AppendItem(omi)
        self.Bind(wx.EVT_MENU, self.DBUpdate, omi, wx.ID_OPEN)

        smi = wx.MenuItem(fmenu, wx.ID_SAVE, '&Save')
        fmenu.AppendItem(smi)
        self.Bind(wx.EVT_MENU, self.DBUpdate, smi, wx.ID_SAVE)

        fmenu.AppendSeparator()

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
        # XXX Need to check for database modified here, with a popup?
        dprint("QUITing ...")
        self.Destroy()

    def OnAbout(self, e):
        dprint('About ... NOT YET IMPLEMENTED')

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
