#!/usr/bin/python
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - Finish creating the "Show" window
      - Ensure that only one window per course can be popped up
        (should it be modal?)
    - Check for options (e.g. "--debug|-d") at startup
    - Put support stuff in library files?
    - Properly package for distribution
    - Figure out how to save state when quitting, i.e.
      the "current" DB, course, hole, and perhaps other
      preferences -- might need a ~/.dg file?
    - Add "Are you sure" popup if DB is modified
    - Add catching window close event
    - DB: persist in a real file
    - Add pictures to DB some day?

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
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import rdb
from utils import dprint
from opts import opts


__author__ = "Lee Duncan"
__version__ = "1.2"


QUIT_BIND_ID = 1
DB_SAVE_BIND_ID = 2
DB_OPEN_BIND_ID = 3
DB_NEW_BIND_ID = 4
COURSE_ADD_BIND_ID = 5
COURSE_EDIT_BIND_ID = 6
COURSE_DELETE_BIND_ID = 7
COURSE_SHOW_BIND_ID = 8


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class DBMainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(DBMainFrame, self).__init__(*args, **kwargs)
        self.SetSize((700, 300))
        self.InitUI()

    def SetUpMenuBar(self):
        '''
        Set up the menu bar
        '''
        menubar = wx.MenuBar()

        ############################################

        fileMenu = wx.Menu()

        ndbmi = wx.MenuItem(fileMenu, wx.ID_NEW, '&New DB')
        fileMenu.AppendItem(ndbmi)
        self.Bind(wx.EVT_MENU, self.OnDBNew, ndbmi, DB_NEW_BIND_ID)

        odbmi = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Open DB')
        fileMenu.AppendItem(odbmi)
        self.Bind(wx.EVT_MENU, self.OnDBOpen, odbmi, DB_OPEN_BIND_ID)

        self.SaveDBMenuItem = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save DB')
        fileMenu.AppendItem(self.SaveDBMenuItem)
        self.Bind(wx.EVT_MENU, self.OnDBSave, self.SaveDBMenuItem,
                  DB_SAVE_BIND_ID)
        self.SetSaveDBMenuState()

        fileMenu.AppendSeparator()

        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit')
        fileMenu.AppendItem(qmi)
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi, QUIT_BIND_ID)

        menubar.Append(fileMenu, 'DB &File')
        
        ############################################
        
        editMenu = wx.Menu()

        self.itemMenuItems = []

        acmi = wx.MenuItem(editMenu, wx.ID_ADD, 'Add Course')
        editMenu.AppendItem(acmi)
        self.Bind(wx.EVT_MENU, self.OnCourseAdd, acmi, COURSE_ADD_BIND_ID)
        self.itemMenuItems.append(acmi)

        ecmi = wx.MenuItem(editMenu, wx.ID_EDIT, 'Edit Course')
        editMenu.AppendItem(ecmi)
        self.itemMenuItems.append(ecmi)

        dcmi = wx.MenuItem(editMenu, wx.ID_DELETE, 'Delete Course')
        editMenu.AppendItem(dcmi)
        self.itemMenuItems.append(dcmi)

        menubar.Append(editMenu, '&Edit')

        ############################################

        helpMenu = wx.Menu()
        menubar.Append(helpMenu, '&Help')
        
        accel_tbl = wx.AcceleratorTable([\
                (wx.ACCEL_CTRL, ord('Q'), QUIT_BIND_ID),
                (wx.ACCEL_CTRL, ord('N'), DB_NEW_BIND_ID),
                (wx.ACCEL_CTRL, ord('O'), DB_OPEN_BIND_ID),
                (wx.ACCEL_CTRL, ord('S'), DB_SAVE_BIND_ID),
                ])
        self.SetAcceleratorTable(accel_tbl)

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
        self.Bind(wx.EVT_BUTTON, self.OnCourseAdd, abutton, COURSE_ADD_BIND_ID)
        ebutton = wx.Button(panel, label='Edit', size=(70, 30))
        hbox3.Add(ebutton)
        self.Bind(wx.EVT_BUTTON, self.OnCourseEdit, ebutton,
                  COURSE_EDIT_BIND_ID)
        dbutton = wx.Button(panel, label='Delete', size=(70, 30))
        hbox3.Add(dbutton)
        self.Bind(wx.EVT_BUTTON, self.OnCourseDelete, dbutton,
                  COURSE_DELETE_BIND_ID)
        self.ShowButton = wx.Button(panel, label='Show', size=(70, 30))
        hbox3.Add(self.ShowButton)
        self.Bind(wx.EVT_BUTTON, self.OnCourseShow, self.ShowButton,
                  COURSE_SHOW_BIND_ID)

        self.itemButtons = [ebutton, dbutton, self.ShowButton]
        self.SetCourseSelectedState(False)

        vbox.Add(hbox3, flag=wx.CENTER|wx.ALIGN_CENTER, border=10)

        panel.SetSizer(vbox)

    def SetSaveDBMenuState(self):
        '''
        Set the "Save DB" Menu item state, based on whether
        our DB is modified or not
        '''
        if rdb.DiscGolfCourseListModified:
            self.SaveDBMenuItem.Enable(True)
        else:
            self.SaveDBMenuItem.Enable(False)

    def SetCourseSelectedState(self, st):
        for i in self.itemButtons:
            if st:
                i.Enable()
            else:
                i.Disable()
        for i in self.itemMenuItems:
            i.Enable(st)

    def ListSelected(self, e):
        dprint("List Item Selected, Index=%d" % e.Index)
        self.SetCourseSelectedState(True)

    def ListDeselected(self, e):
        dprint("List Item Deselected, Index=%d" % e.Index)
        self.SetCourseSelectedState(False)

    def ListActivated(self, e):
        dprint("List Activated, Index=%d" % e.Index)

    def InitUI(self):
        self.SetUpMenuBar()
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")

    def OnQuit(self, e):
        dprint("'QUIT' event")
        self.Close()

    def OnDBNew(self, e):
        dprint("'NEW DB' event (NYI) ...")

    def OnDBOpen(self, e):
        dprint("'OPEN DB' event (NYI) ...")

    def OnDBSave(self, e):
        dprint("'SAVE DB' event (NYI) ...")

    def OnCourseAdd(self, e):
        dprint("'ADD COURSE' event (NYI) ...")

    def OnCourseEdit(self, e):
        dprint("'EDIT COURSE' event (NYI) ...")

    def OnCourseDelete(self, e):
        dprint("'DELETE COURSE' event (NYI) ...")

    def OnCourseShow(self, e):
        dprint("'SHOW COURSE' event")
        CourseShowFrame(self, title='Show Course')


class CourseShowFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(CourseShowFrame, self).__init__(*args, **kwargs)
        self.SetSize((700, 300))
        self.InitUI()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("'COURSE SHOW' Window Initialized")

    def SetUpPanel(self):
        panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(10)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.AddSpacer(10)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Holes On Course')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)

        vbox.AddSpacer(10)

        panel.SetSizer(vbox)


def main():
    rdb.InitDB()
    app = wx.App()
    DBMainFrame(None, title='Disc Golf DB')
    app.MainLoop()


if __name__ == '__main__':
    opts.debug = True
    main()
