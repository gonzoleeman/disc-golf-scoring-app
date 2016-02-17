#!/usr/bin/python
"""
These are the classes and data for dealing with
reports for the Disc Golf database.
"""

import wx
from wx.lib.pubsub import Publisher as pub

import rdb
from utils import dprint
from opts import opts
import listctrl as lc
import wxdate
import money_rounds
import score
import money


class ScoreResultsFrame(wx.Frame):
    '''
    This is the report frame, where results over a period of time are
    shown.
    '''
    def __init__(self, *args, **kwargs):
        super(ScoreResultsFrame, self).__init__(*args, **kwargs)
        self.SetSize((1100, 250))
        self.start_rdate = None
        self.stop_rdate = None
        self.match_count = 0
        self.round_count = 0

    def MyStart(self, start_rdate, stop_rdate):
        dprint("ScoreResultsFrame:MyStart(%s, %s): entering" % \
               (start_rdate, stop_rdate))
        self.start_rdate = wxdate.wxdt_to_dt(start_rdate)
        self.stop_rdate = wxdate.wxdt_to_dt(stop_rdate)
        dprint("Report on reults from", start_rdate, "to", stop_rdate)
        self.GenerateResultsList()
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
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        dprint("Setting up message on date ranges")
        dprint("Start:", self.start_rdate)
        dprint("Stop: ", self.stop_rdate)
        #
        # XXX this needs to be cleaned up, for form readability
        #
        date_range_msg = "Report for Date Range: %s to %s" % \
                         (self.start_rdate.strftime("%m/%d/%Y"),
                          self.stop_rdate.strftime("%m/%d/%Y"))
        st2 = wx.StaticText(panel, label=date_range_msg)
        matches_msg = "Records Found: %d" % self.match_count
        st3 = wx.StaticText(panel, label=matches_msg)
        rounds_msg = "Rounds Found: %s" % (self.round_count)
        st4 = wx.StaticText(panel, label=rounds_msg)
        mz_kitty_msg = "Amount for Mz Kitty: $%5s" % money.Money(0)
        st5 = wx.StaticText(panel, mz_kitty_msg)
        hbox3.Add(st2)
        hbox3.AddSpacer(40)
        hbox3.Add(st3)
        hbox3.AddSpacer(40)
        hbox3.Add(st4)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(st5)
        vbox.Add(hbox3)
        ################################################################
        vbox.AddSpacer(15)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.results_list = lc.AutoWidthListCtrl(panel)
        self.results_list.SetupListHdr(\
            ['Name', 'Rounds', 'TtlPts', 'PPR',
             'Aces', 'Eagles', 'Ace-Eagles',
             '9-s', '18-s', '33-s', 'Best F9', 'Best B9', '$ Won'],
            [wx.LIST_FORMAT_LEFT, wx.LIST_FORMAT_CENTER] + \
            [wx.LIST_FORMAT_RIGHT] * 10 + [wx.LIST_FORMAT_CENTER],
            ['%s', '%d', '%5.2f', '%5.2f'] + \
            ['%d'] * 6 + ['%+d'] * 2 + ['$%s'])
        # set up list based on previously-generated report data
        self.results_list.SetupListItems(self.item_data)
        hbox2.Add(self.results_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################
        pub.subscribe(self.OnNewRoundExists, "ROUND UPDATE")
        pub.subscribe(self.OnNewRoundExists, "MONEY ROUND UPDATE")

    def OnNewRoundExists(self, message):
        '''A "NEW ROUND" message has been received'''
        dprint("ScoreResultsFrame: A 'NEW ROUND' Message we received!")
        # re-read the database rounds and round_details into our
        # internal structures, since they have changed
        rdb.init_rounds()
        # re-generate our report results and data, then display them
        self.GenerateResultsList()
        self.results_list.SetupListItems(self.item_data)
        self.Show(True)

    def GenerateResultsList(self):
        '''Set up our report list items base on current data'''
        dprint("***SetResultsList: Generating report for dates from:", \
               self.start_rdate, ", to:", self.stop_rdate)
        dprint("Report Starting Date (as datetime):", self.start_rdate)
        dprint("Report Ending Date (as datetime):  ", self.stop_rdate)
        # make a dictionary of the entries in range
        matches_found = {k: rdb.SearchResult(v.num) \
                         for k,v in rdb.PlayerList.iteritems()}
        self.item_data = {}
        # also keep track of unique rounds seen
        rounds_seen = {}
        for rd in rdb.RoundDetailList:
            dprint("Looking at:", rd)
            rnd = rdb.RoundList[rd.round_num]
            dprint("From:      ", rnd)
            if not (self.start_rdate <= rnd.rdate <= self.stop_rdate):
                continue
            dprint("Found a match, round no %d" % rd.round_num)
            matches_found[rd.player_num].AddResults(rd)
            rounds_seen[rd.round_num] = True
        # fill in data for our GUI list
        for pnum,sr in matches_found.iteritems():
            dprint("Found match[%d]:" % pnum, sr)
            if sr.rnd_cnt > 0:
                pname = rdb.PlayerList[sr.pnum].name
                self.item_data[pnum] = (pname, sr.rnd_cnt, sr.TotalPoints(),
                                        sr.PointsPerRound(),
                                        sr.acnt, sr.ecnt, sr.aecnt,
                                        sr.won_9s, sr.won_18s,
                                        sr.won_33s,
                                        sr.best_fscore, sr.best_bscore,
                                        sr.money_won)
                dprint("Created data item:", self.item_data[pnum])
        # keep track of number of matches
        self.match_count = len(self.item_data)
        self.round_count = len(rounds_seen)
        dprint("=> Rounds seen (cnt=%d):" % self.round_count, rounds_seen)

    def Quit(self, e):
        dprint("Quit? Really?")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class ReportSetupFrame(wx.Frame):
    '''
    Called when the main-frame menu item "reports" is chosen
    '''
    def __init__(self, *args, **kwargs):
        super(ReportSetupFrame, self).__init__(*args, **kwargs)
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
        self.date_range_choices = wxdate.DATE_RANGES
        self.cbox = wx.ComboBox(panel, id=wx.ID_ANY,
                                value=self.date_range_choices[0],
                                choices=self.date_range_choices,
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
        self.SetNormalStatus("Please choose a Date Range")
        ################################################################
        panel.SetSizer(vbox)

    def SetErrorStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.RED)

    def SetNormalStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def DateChanged(self, e):
        dprint("One of our dates has changed!", e)
        if self.DateRangeValid():
            self.results_button.Enable()
            self.SetNormalStatus("")
        else:
            self.results_button.Disable()

    def DateRangeChoosen(self, e):
        dprint("A pre-canned Date range has been choosen", e)
        dprint("Choice String: %s" % e.GetString())
        canned_choice = e.GetString()
        if canned_choice == self.date_range_choices[0]:
            dprint("No choice made! Bailing")
            return
        (dt_start, dt_end) = wxdate.range_from_key(canned_choice)
        dprint("Frame: Starting Date Range:", dt_start)
        dprint("Frame: Stopping Date Range:", dt_end)
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
        df = ScoreResultsFrame(self.GetParent(), title="Where's The Beef?")
        df.MyStart(self.start_rdate.GetValue(),
                   self.stop_rdate.GetValue())
        self.Close()

    def Quit(self, e):
        dprint("Quit? Really?")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)

