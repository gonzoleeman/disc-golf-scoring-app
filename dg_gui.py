#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - Figure out how to save state when quitting, i.e.
      the "current" course, and perhaps other preferences

History:
    Version 1.0: menu bar present, hooked up, but on
        Quit works
    Version 1.1: Now using a better list, with columns, and
        faking out a ride database
'''

import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import rdb
from utils import dprint
from opts import opts


__author__ = "Lee Duncan"
__version__ = "1.2"


QUIT_BIND_ID = 1
SAVE_BIND_ID = 2
OPEN_BIND_ID = 3
NEW_BIND_ID = 4

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MyFrame, self).__init__(*args, **kwargs)
        self.SetSize((700, 300))
        self.InitUI()

    def SetUpMenuBar(self):
        '''
        Set up the menu bar
        '''
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        nmi = wx.MenuItem(fileMenu, wx.ID_NEW, '&New')
        fileMenu.AppendItem(nmi)
        self.Bind(wx.EVT_MENU, self.OnNew, nmi, NEW_BIND_ID)
        omi = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Open')
        fileMenu.AppendItem(omi)
        self.Bind(wx.EVT_MENU, self.OnOpen, omi, OPEN_BIND_ID)
        smi = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save')
        fileMenu.AppendItem(smi)
        self.Bind(wx.EVT_MENU, self.OnSave, smi, SAVE_BIND_ID)
        fileMenu.AppendSeparator()
        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit')
        fileMenu.AppendItem(qmi)
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi, QUIT_BIND_ID)
        accel_tbl = wx.AcceleratorTable([\
                (wx.ACCEL_CTRL, ord('Q'), QUIT_BIND_ID),
                (wx.ACCEL_CTRL, ord('N'), NEW_BIND_ID),
                (wx.ACCEL_CTRL, ord('O'), OPEN_BIND_ID),
                (wx.ACCEL_CTRL, ord('S'), SAVE_BIND_ID),
                ])
        self.SetAcceleratorTable(accel_tbl)
        menubar.Append(fileMenu, '&File')
        
        editMenu = wx.Menu()
        menubar.Append(editMenu, '&Edit')
        nmi = wx.MenuItem(editMenu, wx.ID_UNDO, '&Undo')
        editMenu.AppendItem(nmi)

        helpMenu = wx.Menu()
        menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(menubar)

    def SetUpPanel(self):
        '''
        Set up the main (panel) window of the GUI
        '''
        panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)

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
        self.list.InsertColumn(0, 'Name', width=100)
        self.list.InsertColumn(1, 'Location', width=150)
        self.list.InsertColumn(2, 'Holes', wx.LIST_FORMAT_CENTER, width=50)
        self.list.InsertColumn(3, 'Par', wx.LIST_FORMAT_CENTER, width=50)
        self.list.InsertColumn(4, 'Description', width=90)
        for c in rdb.DiscGolfCourseList:
            index = self.list.InsertStringItem(sys.maxint, c.cname)
            self.list.SetStringItem(index, 1, c.loc)
            self.list.SetStringItem(index, 2, "%d" % c.NumHoles())
            self.list.SetStringItem(index, 3, "%d" % c.GetCoursePar())
            self.list.SetStringItem(index, 4, c.desc)
        hbox2.Add(self.list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ListSelected,
                  source=self.list,
                  id=wx.ID_ANY)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.ListDeselected,
                  source=self.list,
                  id=wx.ID_ANY)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ListActivated,
                  source=self.list,
                  id=wx.ID_ANY)

        # lastly, set up bottom row: buttons
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        abutton = wx.Button(panel, label='Add', size=(70, 30))
        hbox3.Add(abutton)
        ebutton = wx.Button(panel, label='Edit', size=(70, 30))
        hbox3.Add(ebutton)
        dbutton = wx.Button(panel, label='Delete', size=(70, 30))
        hbox3.Add(dbutton)
        sbutton = wx.Button(panel, label='Show', size=(70, 30))
        self.itemButtons = [ebutton, dbutton, sbutton]
        self.SetItemButtonsState(False)
        hbox3.Add(sbutton)
        vbox.Add(hbox3, flag=wx.CENTER|wx.ALIGN_CENTER, border=10)

        panel.SetSizer(vbox)

    def SetItemButtonsState(self, st):
        for i in self.itemButtons:
            if st:
                i.Enable()
            else:
                i.Disable()

    def ListSelected(self, e):
        '''
        A list item is highlighed/selected
        '''
        dprint("List Item Selected, Index=%d" % e.Index)
        self.SetItemButtonsState(True)

    def ListDeselected(self, e):
        '''
        A List item that was selected is deselected
        '''
        dprint("List Item Deselected, Index=%d" % e.Index)
        self.SetItemButtonsState(False)

    def ListActivated(self, e):
        '''
        Double Click on a list item
        '''
        dprint("List Activated, Index=%d" % e.Index)

    def InitUI(self):
        '''
        Initialize the GUI
        '''
        self.SetUpMenuBar()
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")

    def OnQuit(self, e):
        '''
        Handle a "quit" menu choice
        '''
        dprint("'QUIT' event")
        self.Close()

    def OnNew(self, e):
        '''
        Handle a "new" menu choice -- this should
        throw away current changes (after asking), then
        start with an empty slate
        '''
        # popup a "new file" dialog
        # create the database file
        dprint("'NEW' event (NYI) ...")

    def OnOpen(self, e):
        '''
        Handle a "open" menu choice -- this should
        throw away current changes (after asking), then
        read the database from a file
        '''
        # popup a "open file" dialog
        # populate the database
        dprint("'OPEN' event (NYI) ...")

    def OnSave(self, e):
        '''
        Handle a "save" menu choice -- this should
        save the current database as a file, then
        mark the database as unmodified
        '''
        # popup a "save file" dialog
        # create the database file
        dprint("'SAVE' event (NYI) ...")


def main():
    rdb.InitDB()
    app = wx.App()
    MyFrame(None, title='Disc Golf DB')
    app.MainLoop()


if __name__ == '__main__':
    opts.debug = True
    main()
