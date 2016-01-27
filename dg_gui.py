#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - Create Menu items:
      - File -- to change DB file open, save, and Quit
      - Help -- empty for now
    - Check for options (e.g. "--debug|-d") at startup
    - support DB modification for Courses
    - implement real help?

    - Figure out how to save state when quitting, i.e.
      the "current" DB, course, hole, and perhaps other
      preferences -- might need a ~/.dg file?

    - Add catching window close event
    - Add pictures to DB some day? (e.g. for start screen?)
    - Properly package for distribution

    - implement windows for:
      * scoring a round
      * looking at a round (same?)
      * looking at results (with graph(s)?)

    - make setup window go away when scoring a round (use
      same window, with tabs or something?)

History:
    Version 1.0: menu bar present, hooked up, but on
        Quit works
    Version 1.1: Now using a better list, with columns, and
        faking out a ride database
    Version 1.2: Now under git control. Added list selection
        detection, list edit buttons, and button enable/disable
    version 1.3: trynig to get it arranged correctly
    version 1.4: getting closer: setting up a round correctly now
'''

import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin

import rdb
from utils import dprint
from opts import opts


__author__ = "Lee Duncan"
__version__ = "1.4"



class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(10,10))
        ListCtrlAutoWidthMixin.__init__(self)

class AutoWidthCheckListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin,
                             CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.CONTROL_CHECKED)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnCheckItem)
        self.items_checked = {}
        self.item_check_count = 0

    def OnCheckItem(self, data, flag):
        dprint("Setting items_checked[%d] = %s" % (data, flag))
        self.items_checked[data] = flag
        if flag:
            self.item_check_count = self.item_check_count + 1
        else:
            self.item_check_count = self.item_check_count - 1


class SetupRoundFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SetupRoundFrame, self).__init__(*args, **kwargs)
        self.SetSize((400, 300))
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the GUI
        '''
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.AddSpacer(10)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Round Setup')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)

        vbox.AddSpacer(10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.player_list = AutoWidthCheckListCtrl(panel)
        self.player_list.InsertColumn(0, 'Choose Players', width=100)
        for k in rdb.PlayerList.iterkeys():
            p = rdb.PlayerList[k]
            dprint("Setting up:", p)
            index = self.player_list.InsertStringItem(sys.maxint, p.name)
            dprint("Inserted %s in list, index=%d" % (p, index))
            self.player_list.SetItemData(index, k)
        hbox2.Add(self.player_list, 1, wx.EXPAND|wx.LEFT, border=10)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.PlayerListSelected,
                  source=self.player_list,
                  id=wx.ID_ANY)

        hbox2.AddSpacer(15)

        self.course_list = AutoWidthListCtrl(panel)
        self.course_list.InsertColumn(0, 'Choose a Course', width=100)
        for k in rdb.CourseList.iterkeys():
            c = rdb.CourseList[k]
            index = self.course_list.InsertStringItem(sys.maxint, c.name)
            dprint("Inserted %s in list, index=%d" % (c, index))
            self.course_list.SetItemData(index, k)
        hbox2.Add(self.course_list, 1, wx.EXPAND|wx.RIGHT, border=10)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.CourseListSelected,
                  source=self.course_list,
                  id=wx.ID_ANY)

        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)

        vbox.AddSpacer(10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        date_label = wx.StaticText(panel, label='Date')

        self.round_date = wx.DatePickerCtrl(panel, size=wx.Size(110,20))

        self.score_button = wx.Button(panel, label='Score a Round')
        self.Bind(wx.EVT_BUTTON, self.ButtonPressed,
                  source=self.score_button)
        self.score_button.Disable()

        hbox3.Add(date_label)
        hbox3.AddSpacer(5)
        hbox3.Add(self.round_date)
        hbox3.AddStretchSpacer(2)
        hbox3.Add(self.score_button)

        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)

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

    def ButtonPressed(self, e):
        dprint("Button Pressed: %d players selected:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        player_numbers = []
        for (k, v) in self.player_list.items_checked.iteritems():
            i = self.player_list.GetItemData(k)
            if v:
                dprint("Saving player number: %d" % i)
                player_numbers.append(i)
        dprint("Player number list:", player_numbers)
        i = self.course_list.GetFirstSelected()
        course_number = self.course_list.GetItemData(i)
        dprint("Course number: %d" % course_number)
        rdate = self.round_date.GetValue()
        dprint("round date:", rdate)
        self.ScoreRound(course_number, rdate, player_numbers)

    def ScoreRound(self, course_number, rdate, player_numbers):
        '''popup a window to enter the scores for round'''
        dprint("ScoreRound: NOT YET IMPLEMENTED")

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


def main():
    rdb.initDB()
    app = wx.App()
    SetupRoundFrame(None, title='Disc Golf Database')
    app.MainLoop()


if __name__ == '__main__':
    opts.debug = True
    main()
