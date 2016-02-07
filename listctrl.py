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
import operator


__version__ = "1.0"
__author__ = "Lee Duncan"


ListEditedEvt, EVT_LIST_EDITED_EVT = wxne.NewCommandEvent()

def d2s(f, d):
    '''
    Convert data "d" to a string using format "f", but return the
    string "None" if d has value None
    '''
    if d is None:
        return 'None'
    return f % d


class AutoWidthListEditCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                            wxlc.TextEditMixin, wxlc.ColumnSorterMixin):
    '''
    A List mixin where:
    * the last item in the list takes up all the remaining room,
    * You can edit the fields, and
    * You can sort the columns
    '''
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.LC_SINGLE_SEL,
                             size=wx.Size(10, 10))
        wxlc.ListCtrlAutoWidthMixin.__init__(self)
        self.num_re = re.compile('[+-]?[0-9]+$')
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.CheckEditBegin)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.CheckEditEnd)
        self.num_columns = 0
        self.itemColumnFmt = []

    def GetListCtrl(self):
        return self

    def SetupListHdr(self, itemHdr, itemFmt, itemColumnFmt):
        self.num_columns = len(itemHdr)
        wxlc.ColumnSorterMixin.__init__(self, self.num_columns)
        col_width = 100
        for col_idx in range(self.num_columns):
            item = itemHdr[col_idx]
            lformat = itemFmt[col_idx]
            dprint("Setting column %d hdr to %s" % (col_idx, item))
            self.InsertColumn(col_idx, item, width=col_width, format=lformat)
            col_width = 75
        self.SetColumnCount(self.num_columns)
        self.itemColumnFmt = itemColumnFmt

    def SetupListItems(self, item_data):
        self.DeleteAllItems()
        self.itemDataMap = item_data
        data_idx = 0
        # sort list by keys
        sorted_items = sorted(item_data.items(), key=operator.itemgetter(0))
        #for key, data in self.itemDataMap.items():
        for (key, data) in sorted_items:
            dprint("Edit List: Filling in row %d with key=%d:" % \
                   (data_idx, key), data)
            cfmt = self.itemColumnFmt[0]
            self.InsertStringItem(data_idx, d2s(cfmt, data[0]))
            for col_idx in range(1, self.num_columns):
                cfmt = self.itemColumnFmt[col_idx]
                self.SetStringItem(data_idx, col_idx,
                                   d2s(cfmt, data[col_idx]))
            self.SetItemData(data_idx, key)
            data_idx += 1
        wxlc.TextEditMixin.__init__(self)

    def CheckEditBegin(self, evt):
        dprint("*** Checking edit (begin):", evt)
        dprint("Should we edit col=%d, text=%s" % (evt.m_col, evt.Text))
        if evt.m_col in [1, 2, 4, 5]:
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
        #dprint("Found item[row=%d, col=%d] = '%s'" % (row, col, field_str))
        if not self.num_re.match(field_str):
            raise ArithmeticError(field_str, col)

        val = int(field_str)
        #dprint("Found a number: '%s' -> %d" % (field_str, val))
        return val


class AutoWidthListCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                        wxlc.ColumnSorterMixin):
    '''
    A List mixin where:
    * the last item in the list takes up all the remaining room, and
    * You can sort the columns
    '''
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.LC_SINGLE_SEL,
                             size=wx.Size(10, 10))
        wxlc.ListCtrlAutoWidthMixin.__init__(self)

    def GetListCtrl(self):
        return self

    def SetupListHdr(self, itemHdr, itemFmt, itemColumnFmt):
        self.num_columns = len(itemHdr)
        wxlc.ColumnSorterMixin.__init__(self, self.num_columns)
        col_width = 100
        for col_idx in range(self.num_columns):
            item = itemHdr[col_idx]
            lformat = itemFmt[col_idx]
            dprint("Setting column %d hdr to '%s'" % (col_idx, item))
            self.InsertColumn(col_idx, item, width=col_width, format=lformat)
            col_width = 75
        self.SetColumnCount(self.num_columns)
        self.itemColumnFmt = itemColumnFmt

    def SetupListItems(self, item_data):
        self.DeleteAllItems()
        self.itemDataMap = item_data
        data_idx = 0
        for key, data in self.itemDataMap.items():
            cfmt = self.itemColumnFmt[0]
            dprint("Width List: Filling in col=0 row=%d, key=%d, fmt=%s:" % \
                   (data_idx, key, cfmt), data)
            self.InsertStringItem(data_idx, d2s(cfmt, data[0]))
            for col_idx in range(1, self.num_columns):
                cfmt = self.itemColumnFmt[col_idx]
                dprint("Width List: Filling col=%d row=%d, key=%d, fmt=%s:" % \
                   (col_idx, data_idx, key, cfmt), data[col_idx])
                self.SetStringItem(data_idx, col_idx, d2s(cfmt, data[col_idx]))
            self.SetItemData(data_idx, key)
            data_idx += 1


class AutoWidthCheckListCtrl(wx.ListCtrl, wxlc.ListCtrlAutoWidthMixin,
                             wxlc.CheckListCtrlMixin, wxlc.ColumnSorterMixin):
    '''
    A List mixin where:
    * the last item in the list takes up all the remaining room,
    * Each item has a check box, and
    * You can sort the columns
    '''
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1,
                             style=wx.LC_REPORT|wx.CONTROL_CHECKED)
        wxlc.ListCtrlAutoWidthMixin.__init__(self)
        wxlc.CheckListCtrlMixin.__init__(self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnCheckItem)
        wxlc.ColumnSorterMixin.__init__(self, 1)
        self.items_checked = {}
        self.item_check_count = 0

    def GetListCtrl(self):
        return self

    def SetupList(self, hdr_str, item_data):
        dprint("SetupList: hdr=%s" % hdr_str)
        self.DeleteAllItems()
        self.itemDataMap = item_data
        self.InsertColumn(0, hdr_str, width=100)
        data_idx = 0
        for k, v in self.itemDataMap.items():
            dprint("check List: Filling in row %d with key=%d:" % \
                   (data_idx, k), v)
            self.InsertStringItem(data_idx, str(v))
            self.SetItemData(data_idx, k)
            data_idx += 1

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

