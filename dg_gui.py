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

    - Figure out how to save state when quitting, i.e.
      the "current" DB, course, hole, and perhaps other
      preferences -- might need a ~/.dg file?

    - Add catching window close event
    - Add pictures to DB some day? (e.g. for start screen?)
    - Properly package for distribution

History:
    Version 1.0: menu bar present, hooked up, but on
        Quit works
    Version 1.1: Now using a better list, with columns, and
        faking out a ride database
    Version 1.2: Now under git control. Added list selection
        detection, list edit buttons, and button enable/disable
'''

import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin

import rdb
from utils import dprint
from opts import opts


__author__ = "Lee Duncan"
__version__ = "1.3"



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
        self.itemsChecked = {}

    def OnCheckItem(self, data, flag):
        dprint("data:", data)
        dprint("flag", flag)
        self.itemsChecked[data] = flag

class ChooseCourseFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ChooseCourseFrame, self).__init__(*args, **kwargs)
        self.SetSize((400, 200))
        self.InitUI()
        self.course_select = False

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the GUI
        '''
        panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(14)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.AddSpacer(10)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Disc Golf Courses')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)

        vbox.AddSpacer(10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.list = AutoWidthListCtrl(panel)
        self.list.InsertColumn(0, 'Choose a Course', width=100)
        for k in rdb.CourseList.iterkeys():
            c = rdb.CourseList[k]
            dprint("Setting up:", c)
            index = self.list.InsertStringItem(sys.maxint, c.name)
            dprint("Inserted in list, index=%d" % index)
            self.list.SetItemData(index, k)
        hbox2.Add(self.list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListSelected,
                  source=self.list,
                  id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ListActivated,
                  source=self.list,
                  id=wx.ID_ANY)

        # lastly, add a button at the bottom for setting up the round
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.play_button = wx.Button(panel, label='Setup a Round',
                                     size=(150, 30))
        self.Bind(wx.EVT_BUTTON, self.ButtonPressed,
                  source=self.play_button, id=wx.ID_ANY)
        self.play_button.Disable()
        hbox3.Add(self.play_button)
        vbox.Add(hbox3, flag=wx.CENTER|wx.ALIGN_CENTER, border=10)

        panel.SetSizer(vbox)

    def ListSelected(self, e):
        dprint("List Item [%d] Selected" % e.Index)
        self.play_button.Enable()

    def ListActivated(self, e):
        dprint("List Item [%d] Activated" % e.Index)
        self.SetupRound(e.Index)

    def ButtonPressed(self, e):
        dprint("Button Pressed")
        self.SetupRound(self.list.GetFirstSelected())

    def SetupRound(self, i):
        '''play a round on course[i]'''
        dprint("Play a round on course, list index=%d, index=%d" % \
               (i, self.list.GetItemData(i)))
        c = rdb.CourseList[self.list.GetItemData(i)]
        dprint("Playing at:", c)
        r = SetupRoundFrame(self,
                            title='Setup a Round at %s' % c.name)
        r.Show(True)

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("Window Initialized")


class SetupRoundFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(SetupRoundFrame, self).__init__(*args, **kwargs)
        self.SetSize((400, 300))
        self.InitUI()

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the GUI
        '''
        panel = wx.Panel(self)

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

        hbox15 = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(panel, label='Course:')
        hbox15.Add(st)
        #sc = wx.SpinCtrl(panel, )

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.list = AutoWidthCheckListCtrl(panel)
        self.list.InsertColumn(0, 'Choose Players', width=150)
        for k in rdb.PlayerList.iterkeys():
            p = rdb.PlayerList[k]
            dprint("Setting up:", p)
            self.list.InsertStringItem(sys.maxint, p.name)
        self.list.OnCheckItem(0, True)
        hbox2.Add(self.list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListSelected,
                  source=self.list,
                  id=wx.ID_ANY)

        # lastly, add a button at the bottom for playing a round
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.play_button = wx.Button(panel, label='Play a Round',
                                     size=(150, 30))
        self.Bind(wx.EVT_BUTTON, self.ButtonPressed,
                  source=self.play_button, id=wx.ID_ANY)
        #self.play_button.Disable()
        hbox3.Add(self.play_button)
        vbox.Add(hbox3, flag=wx.CENTER|wx.ALIGN_CENTER, border=10)

        panel.SetSizer(vbox)

    def ListSelected(self, e):
        dprint("List Item [%d] Selected" % e.Index)
        self.list.Select(e.Index, False)
        self.list.ToggleItem(e.Index)
        #self.list.CheckItem(e.Index, not self.list.IsChecked(e.Index))
        #self.play_button.Enable()

    def ButtonPressed(self, e):
        dprint("Button Pressed")
        # need to get a list of all players selected
        #self.PlayRound(player_list)
        dprint("list of selection:", self.list.itemsChecked)

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


def main():
    rdb.initDB()
    app = wx.App()
    ChooseCourseFrame(None, title='Disc Golf DB')
    app.MainLoop()

if __name__ == '__main__':
    opts.debug = True
    main()
