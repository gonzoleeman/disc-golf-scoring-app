#!/usr/bin/python
'''
List Control Customizations
'''


from utils import dprint
from opts import opts

import wx
import wx.lib.mixins.listctrl as wxlc
import wx.lib.newevent as wxne
import re


__version__ = "1.0"
__author__ = "Lee Duncan"


ListEditedEvt, EVT_LIST_EDITED_EVT = wxne.NewCommandEvent()


class AutoWidthListEditCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                            wxlc.TextEditMixin, wxlc.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                            style=wx.LC_REPORT|wx.LC_SINGLE_SEL,
                             size=wx.Size(10,10))
        wxlc.ListCtrlAutoWidthMixin.__init__(self)
        wxlc.ColumnSorterMixin.__init__(self, 1)
        self.num_re = re.compile('[+-]?[0-9]+$')
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.CheckEditBegin)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.CheckEditEnd)
        self.num_columns = 0

    def SetupListHdr(self, itemHdr):
        self.num_columns = len(itemHdr)
        col_width = 100
        for col_idx in range(self.num_columns):
            dprint("Setting column %d hdr to %s" % (col_idx,
                                                    itemHdr[col_idx]))
            self.InsertColumn(col_idx, itemHdr[col_idx], width=col_width)
            col_width = 75
        self.SetColumnCount(self.num_columns)

    def SetupListItems(self, item_data):
        self.DeleteAllItems()
        self.item_data_map = item_data
        data_idx = 0
        for key, data in self.item_data_map.items():
            dprint("Filling in row %d with key=%d:" % (data_idx, key), data)
            self.InsertStringItem(data_idx, data[0])
            for col_idx in range(1, self.num_columns):
                self.SetStringItem(data_idx, col_idx, data[col_idx])
            self.SetItemData(data_idx, key)
            data_idx += 1
        wxlc.TextEditMixin.__init__(self)

    def GetListCtrl(self):
        return self

    def CheckEditBegin(self, evt):
        dprint("*** Checking edit (begin):", evt)
        dprint("Should we edit col=%d, text=%s" % (evt.m_col, evt.Text))
        if evt.m_col in (1, 2, 3, 4):
            dprint("ALLOWing edit of column %d" % evt.m_col)
            evt.Allow()
            self.before_edit = evt.Text
        else:
            dprint("VETOing edit of column %d" % evt.m_col)
            evt.Veto()

    def CheckEditEnd(self, evt):
        dprint("*** Checking edit (end):", evt)
        dprint("Finished editing col=%d, text=%s" % (evt.m_col, evt.Text))
        self.after_edit = evt.Text
        if self.before_edit != self.after_edit:
            dprint("Sending a a custom event: list edited!")
            new_evt = ListEditedEvt(self.GetId(),
                                    message='list edited',
                                    col=evt.m_col, row=evt.m_item)
            wx.PostEvent(self.GetParent(), new_evt)
        # allow all edits -- XXX probably not needed
        evt.Allow()

    def GetFieldNumericValue(self, row, col):
        '''
        Ensure the string is a valid number:
        * Starts with an optional PLUS or MINUS sign
        * Then a first digit, which is [1-9]
        * Then optional more digits, which are [0-9]
        * Number uses up the whole string
        '''
        field_str = self.GetItem(row, col).GetText()
        dprint("Found item[row=%d, col=%d] = '%s'" % (row, col, field_str))
        if not self.num_re.match(field_str):
            raise ArithmeticError(field_str, col)

        val = int(field_str)
        dprint("Found a number: '%s' -> %d" % (field_str, val))
        return val


class AutoWidthListCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                        wxlc.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.LC_SINGLE_SEL,
                             size=wx.Size(10,10))
        wxlc.ListCtrlAutoWidthMixin.__init__(self)

    def GetListCtrl(self):
        return self

    def SetupListHdr(self, itemHdr):
        self.num_columns = len(itemHdr)
        col_width = 100
        for col_idx in range(self.num_columns):
            dprint("Setting column %d hdr to %s" % (col_idx,
                                                    itemHdr[col_idx]))
            self.InsertColumn(col_idx, itemHdr[col_idx], width=col_width)
            col_width = 75
        self.SetColumnCount(self.num_columns)

    def SetupListItems(self, item_data):
        self.DeleteAllItems()
        self.item_data_map = item_data
        data_idx = 0
        for key, data in self.item_data_map.items():
            dprint("Filling in row %d with key=%d:" % (data_idx, key), data)
            self.InsertStringItem(data_idx, data[0])
            for col_idx in range(1, self.num_columns):
                self.SetStringItem(data_idx, col_idx, data[col_idx])
            self.SetItemData(data_idx, key)
            data_idx += 1


class AutoWidthCheckListCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                             wxlc.CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.CONTROL_CHECKED)
        wxlc.ListCtrlAutoWidthMixin.__init__(self)
        wxlc.CheckListCtrlMixin.__init__(self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnCheckItem)
        self.items_checked = {}
        self.item_check_count = 0

    def OnCheckItem(self, data, flag=None):
        if flag is None:
            dprint("Skipping item checked: no item!")
            return
        dprint("Setting items_checked[%d] = %s" % (data, flag))
        self.items_checked[data] = flag
        if flag:
            self.item_check_count += 1
        else:
            self.item_check_count -= 1

