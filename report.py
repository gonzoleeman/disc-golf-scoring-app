#!/usr/bin/python
"""
These are the classes and data for dealing with
reports for the Disc Golf database.
"""

import wx
from wx.lib.pubsub import pub
import subprocess

import wxdate
import money_rounds
import score
from money import Money
import rdb
from utils import dprint
from opts import opts
import listctrl as lc
from printer import MyPrintout


def format_table_line(items, hdg=False):
    '''take the 13 enties in "items" and return them formatted for out table'''
    dprint("*** format_table_line: items passed in (hdg=%s):" % hdg)
    dprint(items)
    # set up an array of heading vs regular format for each column
    line_fmt = [
        ('{:<10s}', '{:<10s}'),
        ('{:^7s}', '{:^7d}'),
        ('{:>9s}', '{:>9.2f}'),
        ('{:>9s}', '{:>9.2f}'),
        ('{:^6s}', '{:^6d}'),
        ('{:^7s}', '{:^7d}'),
        ('{:^10s}', '{:^10d}'),
        ('{:^5s}', '{:^5d}'),
        ('{:^5s}', '{:^5d}'),
        ('{:^5s}', '{:^5d}'),
        ('{:^8s}', '{:^+8d}'),
        ('{:^8s}', '{:^+8d}'),
        ('{:>6s}', '{:>6s}')]
    fmt_idx = 0 if hdg else 1
    for i in range(13):
        dprint("item[%d] (len %d):" % (i, len(str(items[i]))), items[i])
        dprint("format for item: '%s'" % line_fmt[i][fmt_idx])
    l = []
    for i in range(13):
        fmt_str = line_fmt[i][fmt_idx]
        l.append(fmt_str.format(items[i]))
    res = ''.join(l)
    dprint("Returning table line: /%s/" % res)
    return res

def format_table_dash_line(hdg_items):
    dprint("format_table_dash_line")
    hdg = []
    for h in hdg_items:
        hdg.append('-' * len(h))
    return format_table_line(hdg, hdg=True)

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
        self.mz_kitty_amt = Money(0)
        self.printout = MyPrintout(self)

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
        vbox.AddSpacer(20)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(25)
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
        matches_msg = "Players Found: %d" % self.match_count
        st3 = wx.StaticText(panel, label=matches_msg)
        rounds_msg = "Rounds Found: %s" % (self.round_count)
        st4 = wx.StaticText(panel, label=rounds_msg)
        st5 = wx.StaticText(panel, label=self.MzKittyMsg())
        hbox3.AddSpacer(15)
        hbox3.Add(st2)
        hbox3.AddSpacer(40)
        hbox3.Add(st3)
        hbox3.AddSpacer(40)
        hbox3.Add(st4)
        hbox3.AddSpacer(40)
        hbox3.Add(st5)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        #vbox.AddSpacer(15)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.results_list = lc.AutoWidthListCtrl(panel)
        self.my_headings = [
            'Name', 'Rounds', 'TtlPts', 'PPR',
            'Aces', 'Eagles', 'Ace-Eagles',
            '9-s', '18-s', '33-s', 'Best F9', 'Best B9', '$ Won']
        self.results_list.SetupListHdr(\
            self.my_headings,
            [wx.LIST_FORMAT_LEFT, wx.LIST_FORMAT_CENTER] + \
            [wx.LIST_FORMAT_RIGHT] * 10 + [wx.LIST_FORMAT_CENTER],
            ['%s', '%d', '%5.2f', '%5.2f'] + \
            ['%d'] * 6 + ['%+d'] * 2 + ['$%s'])
        # set up list based on previously-generated report data
        self.results_list.SetupListItems(self.item_data)
        hbox2.Add(self.results_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        vbox.AddSpacer(15)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        done_button = wx.Button(panel, label='Done')
        # XXX maybe this should be a menu option?
        print_button = wx.Button(panel, label='Print')
        self.Bind(wx.EVT_BUTTON, self.OnDone, source=done_button)
        self.Bind(wx.EVT_BUTTON, self.OnPrint, source=print_button)
        hbox3.AddSpacer(10)
        hbox3.Add(done_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(print_button)
        hbox3.AddSpacer(10)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################
        pub.subscribe(self.OnNewRoundExists, "ROUND UPDATE")
        pub.subscribe(self.OnNewRoundExists, "MONEY ROUND UPDATE")

    def MzKittyMsg(self):
        return "Amount for Mz Kitty: $%5s" % self.mz_kitty_amt

    def OnPrint(self, e):
        dprint("PRINT? Are you kidding?")
        lines = self.GetOurData()
        dprint("Calling print routine ...")
        self.printout.PrintText(lines, "some title not used")

    def GetOurData(self):
        # generate a list of lines, to be printed
        lines = []
        lines.append(' ' * 20 + '*** Disc Golf Score Results -- by LeeMan ***')
        lines.append('')
        lines.append('Scores for Date Range: %s to %s' % \
                     (self.start_rdate.strftime("%m/%d/%Y"),
                      self.stop_rdate.strftime("%m/%d/%Y")))
        lines.append('')
        lines.append('Players found: %d              Rounds Found: %s' % \
                     (self.match_count, self.round_count))
        lines.append('')
        lines.append(self.MzKittyMsg())
        lines.append('')

        lines.append(format_table_line(self.my_headings, hdg=True))
        lines.append(format_table_dash_line(self.my_headings))
        for data_item in self.item_data.itervalues():
            lines.append(format_table_line(data_item))
        return lines


    def OnDone(self, e):
        dprint("All done!")
        self.Close()

    def OnNewRoundExists(self, round_no):
        '''A "NEW ROUND" or "NEW MONEY ROUND" message has been received'''
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
        # make a dictionary of the entries in range, where the 'key'
        # is the player number, and the data is an instance of
        # SearchResult for that player
        matches_found = {k: rdb.SearchResult(v.num) \
                         for k,v in rdb.PlayerList.iteritems()}
        # also keep track of unique rounds seen, using a key of
        # the round number, and data of True
        round_numbers_seen = {}
        for rd in rdb.RoundDetailList:
            dprint("Results: Looking at:", rd)
            rnd = rdb.RoundList[rd.round_num]
            dprint("From:      ", rnd)
            if not (self.start_rdate <= rnd.rdate <= self.stop_rdate):
                continue
            dprint("Found a match, round no %d" % rd.round_num)
            matches_found[rd.player_num].AddRoundResults(rd)
            round_numbers_seen[rd.round_num] = True
        # now go through the money rounds, to add up money for each player,
        # and to keep track of the number of players per round
        players_per_round = {}
        for mrd in rdb.MoneyRoundDetailList:
            dprint("Results: Looking at:", mrd)
            round_num = mrd.round_num
            if round_num not in round_numbers_seen:
                dprint("Skipping this entry: round# not in range:", round_num)
                continue
            dprint("Found a match, round no %d" % rd.round_num)
            # increment the number of players for this round
            player_num = mrd.player_num
            cur_cnt = players_per_round.get(round_num, 0)
            players_per_round[round_num] = cur_cnt + 1
            dprint("Now players_per_round[%d] = %d" % \
                   (round_num, cur_cnt+1))
            # now add in the money data for this player
            matches_found[mrd.player_num].AddMoneyRoundResults(mrd)
        dprint("List of players per round:", players_per_round)
        # finally, get the total for mz kitty
        for round_num in round_numbers_seen:
            dprint("Scanning money round for round_num=%d" % round_num)
            mrnd = rdb.MoneyRoundList[round_num]
            dprint("Found:", mrnd)
            num_players = players_per_round[round_num]
            dprint("Found %d players for this round" % num_players)
            for try_no in mrnd.mrounds:
                # XXX 7? really? make a constant!
                if try_no == 7:
                    add_amt = Money(num_players)
                    dprint("*** Found Money for mz kitty, " + \
                           "round=%d, try=%d, amt=%s" % \
                           (round_num, try_no, add_amt))
                    self.mz_kitty_amt += add_amt
        # fill in item data for our GUI list: 1:1 from matches found
        self.item_data = {}
        for pnum,sr in matches_found.iteritems():
            dprint("Found match[player_num=%d]:" % pnum, sr)
            if sr.rnd_cnt <= 0:
                # this player did not play any rounds
                dprint("Skipping this player, since they did not play")
                continue
            pname = rdb.PlayerList[sr.pnum].name
            self.item_data[pnum] = (pname, sr.rnd_cnt,
                                    float(sr.TotalPoints()),
                                    float(sr.PointsPerRound()),
                                    sr.acnt, sr.ecnt, sr.aecnt,
                                    sr.won_9s, sr.won_18s,
                                    sr.won_33s,
                                    sr.best_fstrokes, sr.best_bstrokes,
                                    sr.money_won)
            dprint("Created data item:", self.item_data[pnum])
        # keep track of number of matches and number of rounds seen
        self.match_count = len(self.item_data)
        self.round_count = len(round_numbers_seen)
        dprint("=> Rounds seen (cnt=%d):" % self.round_count,
               round_numbers_seen)

    def Quit(self, e):
        dprint("Quit? Really?")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


class ReportSetupFrame(wx.Frame):
    '''
    Called when the main-frame menu item "reports" is chosen

    This lets us choose the parameters for our report, i.e.
    the date range.
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


