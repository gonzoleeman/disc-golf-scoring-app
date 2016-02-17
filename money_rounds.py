#!/usr/bin/python
"""
These are the classes and data for dealing with
'Money Rounds', where a Money Round is an instance of a group
of players playing 1, 2, or 3 rounds of Ace betting. Is
is matched 0-or-1-to-1 with a Round, i.e. a money round
implies a round, but a round does not necessarily
imply a money round.
"""

import wx
from wx.lib.pubsub import Publisher as pub

import rdb
from utils import dprint
from opts import opts
import listctrl as lc
import wxdate
import money


ROUND_CHOICE_ID_BASE = 1000



class MoneyRoundSetupFrame(wx.Frame):
    '''
    This frame is used to get all the information needed to set
    up a money round. That information is just the player list. It used
    to be more, but now that is all we need.

    This list is assumed to be the set of players that played the
    regular round, since it is assumed the money round players are
    a subset of the regular round players.
    '''
    def __init__(self, *args, **kwargs):
        super(MoneyRoundSetupFrame, self).__init__(*args, **kwargs)
        self.SetSize((wx.Size(200, 400)))
        self.Bind(wx.EVT_CLOSE, self.Quit)
        self.this_round = None
        self.this_mround = None
        self.players = []

    def MyCreate(self, this_round, this_mround, players):
        self.this_round = this_round
        self.this_mround = this_mround
        self.players = players
        self.InitUI()

    def SetUpPanel(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        ################################################################
        vbox = wx.BoxSizer(wx.VERTICAL)
        ################################################################
        vbox.AddSpacer(10)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        big_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        big_font.SetPointSize(14)
        st1 = wx.StaticText(panel, label='Money Round Setup')
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
        player_data = {p: rdb.PlayerList[p].name for p in self.players}
        self.player_list.SetupList('Choose Players', player_data)
        hbox2.Add(self.player_list, 1, wx.EXPAND|wx.LEFT, border=10)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPlayerListSelected,
                  source=self.player_list)
        pub.subscribe(self.OnCheckItem, "ITEM CHECK UPDATE")
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_EXIT, label='Cancel')
        self.start_button = wx.Button(panel, label='Start')
        self.Bind(wx.EVT_BUTTON, self.OnStartMoneyScoring,
                  source=self.start_button)
        self.Bind(wx.EVT_BUTTON, self.Quit, source=cancel_button)
        self.start_button.Disable()
        vbox.AddSpacer(10)
        hbox3.Add(cancel_button)
        hbox3.AddStretchSpacer(1)
        hbox3.Add(self.start_button)
        vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.SetNormalStatus("Please choose money players")
        ################################################################
        panel.SetSizer(vbox)

    def SetErrorStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.RED)

    def SetNormalStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def SetScoreButtonState(self):
        '''Set appropriate state for the "Score" Button'''
        dprint("%d players selected" % \
               self.player_list.item_check_count)
        if self.player_list.item_check_count > 0:
            self.start_button.Enable()
            self.SetNormalStatus("")
        else:
            self.start_button.Disable()
            self.SetNormalStatus("Please choose money players")

    def OnPlayerListSelected(self, e):
        dprint("Player[%d] Selected" % e.Index)
        self.player_list.Select(e.Index, False)
        self.player_list.ToggleItem(e.Index)
        self.SetScoreButtonState()

    def OnCheckItem(self, evt):
        dprint("High level check item")
        self.SetScoreButtonState()

    def OnStartMoneyScoring(self, e):
        dprint("*** 'Start' Money Round Start Button Pressed: players[%d]:" % \
               self.player_list.item_check_count,
               self.player_list.items_checked)
        ################################################################
        this_mround = rdb.MoneyRound(self.this_round.num)
        dprint("Created:", this_mround)
        mround_details = []
        for (k, v) in self.player_list.items_checked.iteritems():
            i = self.player_list.GetItemData(k)
            if not v:
                continue # this user not checked
            dprint("Found player[%d] (from checklist)" % i)
            mrd = rdb.MoneyRoundDetail(this_mround.round_num, i)
            mround_details.append(mrd)
            dprint("Created:", mrd)
        mround_details = sorted(mround_details, key=lambda mrd: mrd.player_num)
        ################################################################
        # popup a window to enter the scores for round then go away
        srf = MoneyRoundDetailsFrame(self.GetParent(), title='Score a Round')
        srf.MyCreate(self.this_round, this_mround, mround_details,
                     for_update=False)
        self.Destroy()

    def Quit(self, e):
        '''Either .... happened'''
        # Do we need to check for database modified here, with a popup?
        # (I do not think so)
        dprint("QUITing RoundSetupFrame")
        self.Destroy()

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)
        dprint("GUI Initialized")


class MoneyRoundDetailsFrame(wx.Frame):
    '''
    This is the window used to create or edit a Money Round
    and one or more Money Round Details.
    '''
    def __init__(self, *args, **kwargs):
        super(MoneyRoundDetailsFrame, self).__init__(*args, **kwargs)
        self.SetSize((375, 400))
        self.for_update = False
        self.this_round = None
        self.this_mround = None
        self.for_update = None
        self.mround_details = None
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        # this means something on the GUI has changed
        self.is_edited = False
        # this means our internal state matches the GUI
        self.data_from_form_up_to_date = False
        # our sortable form data
        self.item_data = {}

    def MyCreate(self, this_round, this_mround, mround_details,
                 for_update=False):
        dprint("Creating (filling in) %s " % self.__class__.__name__)
        self.for_update = for_update
        self.this_round = this_round
        self.this_mround = this_mround
        self.mround_details = sorted(mround_details,
                                     key=lambda rd: rd.player_num)
        self.num_players = len(self.mround_details)
        dprint("Added round:    ", this_round)
        dprint("and money round:", this_mround)
        dprint("With %d Money Round Details:" % self.num_players)
        for mrd in mround_details:
            dprint(mrd)
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
        st1 = wx.StaticText(panel, label='Money Round Scoring')
        st1.SetFont(big_font)
        hbox1.Add(st1, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(hbox1, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(10)
        sl = wx.StaticLine(panel, size=wx.Size(400, 1))
        vbox.Add(sl, flag=wx.CENTER|wx.ALIGN_CENTER)
        ################################################################
        vbox.AddSpacer(20)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        bold_font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        bold_font.SetWeight(wx.FONTWEIGHT_BOLD)
        st2 = wx.StaticText(panel, label='Round Date:')
        st2.SetFont(bold_font)
        st2_5 = wx.StaticText(panel,
                              label=self.this_round.rdate.strftime('%m/%d/%Y'))
        st3 = wx.StaticText(panel, label='Course Location:')
        st3.SetFont(bold_font)
        dprint("Getting course number from:", self.this_round.course_num)
        the_course = rdb.CourseList[self.this_round.course_num]
        st3_5 = wx.StaticText(panel, label=the_course.name)
        hbox2.AddSpacer(5)
        hbox2.Add(st2)
        hbox2.AddSpacer(5)
        hbox2.Add(st2_5)
        hbox2.AddStretchSpacer(2)
        hbox2.Add(st3)
        hbox2.AddSpacer(5)
        hbox2.Add(st3_5)
        hbox2.AddSpacer(10)
        vbox.Add(hbox2, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        vbox.AddSpacer(25)
        # 0 -> NotPlayed, 1-6 -> 1-6 tries, 7->MzKitty wins!
        choices = ['<NotPlayed>'] + \
                  [str(i) for i in range(1,7)] + \
                  ['<MzKitty>']
        # save which choice means "mz kitty"
        self.choice_mz_kitty = len(choices) - 1
        self.choice_none = 0
        dprint("==> Setting up round choices from this_mround:",
               self.this_mround)
        dprint("    to: 1st=%s, 2nd=%s, 3rd=%s" % \
               (self.this_mround.mrounds[0],
                self.this_mround.mrounds[1],
                self.this_mround.mrounds[2]))
        ### money round 1, 2, and 3
        self.mf = [0 for i in range(3)]
        self.mfk = [None for i in range(3)]
        for i in range(3):
            hbox11 = wx.BoxSizer(wx.HORIZONTAL)
            st11 = wx.StaticText(panel, label='Round %d Tries:' % (i+1))
            self.mf[i] = wx.Choice(panel, choices=choices,
                                   id=ROUND_CHOICE_ID_BASE+i)
            self.mf[i].Select(self.this_mround.mrounds[i])
            st21 = wx.StaticText(panel, label='MzKitty:')
            self.mfk[i] = wx.StaticText(panel, size=(40,10))
            hbox11.Add(st11)
            hbox11.AddSpacer(15)
            hbox11.Add(self.mf[i])
            hbox11.AddSpacer(20)
            hbox11.Add(st21)
            hbox11.AddSpacer(5)
            hbox11.Add(self.mfk[i])
            vbox.Add(hbox11, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
            self.Bind(wx.EVT_CHOICE,
                      self.OnMoneyRoundDetails,
                      source=self.mf[i])
        vbox.AddSpacer(25)
        ################################################################
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.money_list = lc.AutoWidthListEditCtrl(panel)
        self.hdg_items = ['Name', 'Round 1', 'Round 2', 'Round 3']
        self.money_list.SetupListHdr(self.hdg_items,
                                     [wx.LIST_FORMAT_LEFT] + \
                                     [wx.LIST_FORMAT_CENTER] * 3,
                                     ['%s', '%s', '%s', '%s'])
        self.MoneyRoundDetailsAsDict()
        self.money_list.SetupListItems(self.item_data)
        self.money_list.SetEditColumnOk([1, 2, 3])
        hbox3.Add(self.money_list, 1, wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
        ################################################################
        # now set mzkitty amounts based on real data
        self.SetMzKittyAmts()
        ################################################################
        self.Bind(lc.EVT_LIST_EDITED_EVT, self.OnListEdited,
                  source=self.money_list)
        ################################################################
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, id=wx.ID_CANCEL, label='Cancel')
        lab = ('Update' if self.for_update else 'Commit')
        self.commit_button = wx.Button(panel, id=wx.ID_SAVE, label=lab)
        self.SetCommitButtonState()
        self.Bind(wx.EVT_BUTTON, self.OnCancel, source=cancel_button)
        self.Bind(wx.EVT_BUTTON, self.OnCommit, source=self.commit_button)
        hbox4.AddSpacer(10)
        hbox4.Add(cancel_button)
        hbox4.AddStretchSpacer(1)
        hbox4.Add(self.commit_button)
        vbox.Add(hbox4, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        ################################################################
        panel.SetSizer(vbox)
        ################################################################
        self.status_bar = self.CreateStatusBar()
        self.SetNormalStatus("Please fill in the scores")

    def SetMzKittyAmts(self):
        '''Set the 3 mz kitty amounts, based on money round data'''
        # scan through the item list itself
        dprint("Setting MzKitty Amounts ...")
        player_cnt = self.money_list.GetItemCount()
        cost_per_round = money.Money(1) * player_cnt
        for i in range(3):
            choice_val = self.mf[i].GetSelection()
            dprint("Round %d has value %d" % (i, choice_val))
            dprint("Comparing mf[%d]=%d with %d" % \
                   (i, choice_val, self.choice_mz_kitty))
            if choice_val == self.choice_mz_kitty:
                m = cost_per_round
            else:
                m = money.Money(0)
            self.mfk[i].SetLabel(money.money_to_string(m))
            self.mfk[i].Enable(not m.IsZero())

    def SetCommitButtonState(self):
        dprint("Setting commit button state ...")
        self.commit_button.Enable(self.is_edited)

    def OnCommit(self, e):
        dprint("%s.OnCommit: %s Money Round DB requested" % \
               (self.__class__.__name__,
                'Update' if self.for_update else 'Commit'))
        dprint("DB State: edited=%s, form_up_to_date=%s, " % \
               (self.is_edited, self.data_from_form_up_to_date))
        # save the date of our current round, since it can
        # change when we get data from the frame
        if not self.GetDataFromFrameIfNeeded():
            dprint("XXX need to diplay error status here: data invalid!")
            return
        if not self.is_edited:
            raise Exception("Internal Error: Committing non-edited list?")
        if self.for_update:
            # XXX we should check for this round having the date of a round
            # already in the database (not counting this round)
            # NOT YET IMPLEMENTED
            dprint("Modifying an existing money round: %d" % \
                   self.this_mround.round_num)
            rdb.modify_money_round(self.this_mround, self.mround_details)
        else:
            # check for duplicate round
            dprint("Adding a new money round: %d" % \
                   self.this_mround.round_num)
            rdb.add_money_round(self.this_mround, self.mround_details)
        rdb.commit_db()
        dprint("Updating parent GUI ...")
        pub.sendMessage("MONEY ROUND UPDATE", self.this_round)
        self.is_edited = False
        self.Close()

    def OnMoneyRoundDetails(self, e):
        '''A change has been made in one of the 3 money round choices'''
        # get which round (1, 2, or 3) and what choice (0-7)
        choice_idx = e.GetInt()                # 0-7
        choice_id = e.GetId() - ROUND_CHOICE_ID_BASE # 0, 1, or 2
        dprint("*** OnMoneyRoundDetails: round %d choosen: %s" % \
               (choice_id, choice_idx))
        ####
        cur_val = self.this_mround.mrounds[choice_id]
        dprint("Current value:", cur_val)
        for choice_id_next in range(choice_id+1, 3):
            dprint("Also looking at next id: %d" % choice_id_next)
            if choice_id_next is not None:
                if choice_idx > 0:
                    # make sure next round option is available and configured
                    self.mf[choice_id_next].Enable()
                    self.mf[choice_id_next].Select(
                        self.this_mround.mrounds[choice_id_next])
                elif choice_idx == 0:
                    # no round2 if round1 was not played
                    self.mf[choice_id_next].Select(0)
                    self.mf[choice_id_next].Disable()
        ###
        if cur_val != choice_idx:
            dprint("Choice was changed from %d to %d" % (cur_val, choice_idx))
            self.is_edited = True
            self.data_from_form_up_to_date = False
            self.mfk[choice_id].Enable(choice_idx == self.choice_mz_kitty)
            self.SetCommitButtonState()
            self.SetMzKittyAmts()

    def MoneyRoundDetailsAsDict(self):
        dprint("Making Money Round Details into dictionary ...")
        self.item_data = {}
        for mrd in self.mround_details:
            dprint(mrd)
            player = rdb.PlayerList[mrd.player_num]
            self.item_data[player.num] = (player.name,
                                        mrd.moola_rnd[0],
                                        mrd.moola_rnd[1],
                                        mrd.moola_rnd[2])
            dprint("Set item_data[%d] to:" % player.num,
                   self.item_data[player.num])

    def SetErrorStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.RED)

    def SetNormalStatus(self, msg):
        self.status_bar.SetStatusText(msg)
        self.status_bar.SetBackgroundColour(wx.NullColour)

    def GetDataFromFrameIfNeeded(self):
        '''
        Get data from our score list into our self.round_details

        Return True if data was legal,
        Else return False and leave data partially updated
        '''
        dprint("*** GetDataFromFrameIfNeeded (money rounds): " + \
               "form_up_to_date=%s" % self.data_from_form_up_to_date)
        if self.data_from_form_up_to_date:
            return True
        ####
        # get data from list into
        ####        dprint("Before Update:", self.this_round)
        mr1 = self.mf[0].GetSelection()
        mr2 = self.mf[1].GetSelection()
        mr3 = self.mf[2].GetSelection()
        # Sanity Checks on Money round
        if mr1 == 0 and mr2 > 0:
            self.SetErrorStatus("Money Round 2 without Round 1?")
            return False
        if mr2 == 0 and mr3 > 0:
            self.SetErrorStatus("Money Round 3 without Round 2?")
            return False
        ####
        self.this_mround.mrounds = [mr1, mr2, mr3]
        ####
        cnt = self.money_list.GetItemCount()
        dprint("Round detail list has %d items for round %d:" % \
               (cnt, self.this_round.num))
        dprint("Updating round details: money round tries: %d, %d, %d" % \
               (self.this_mround.mrounds[0],
                self.this_mround.mrounds[1],
                self.this_mround.mrounds[2]))
        ####
        for c in range(cnt):
            dprint("Looking for mround_detail index %d" % c)
            pname = self.money_list.GetItemText(c)
            dprint("Item %d: %s" % (c, pname))
            try:
                mr1_cents = self.money_list.GetFieldMonetaryValue(c, 1)
                mr2_cents = self.money_list.GetFieldMonetaryValue(c, 2)
                mr3_cents = self.money_list.GetFieldMonetaryValue(c, 3)
            except ArithmeticError, e:
                dprint("Oh oh: error getting money item:", e, "args:", e.args)
                col_no = e.args[1]
                hdg = self.hdg_items[col_no]
                self.SetErrorStatus("%s's %s invalid" % (pname, hdg))
                return False
            # Sanity checks for money round -- XXX this could be a loop?
            if not mr1 and mr1_cents.AsCents():
                self.SetErrorStatus(\
                    "%s's can't have Round 1 money: Round Not Played" % \
                    pname)
                return False
            if not mr2 and mr2_cents.AsCents():
                self.SetErrorStatus(\
                    "%s's can't have Round 2 money: Round Not Played" % \
                    pname)
                return False
            if not mr3 and mr3_cents.AsCents():
                self.SetErrorStatus(\
                    "%s's can't have Bonus Round money: Round Not Played" % \
                    pname)
                return False
            ####
            self.mround_details[c].SetMoney([mr1_cents, mr2_cents, mr3_cents])
            self.SetNormalStatus("")
        ####
        self.data_from_form_up_to_date = True
        return True

    def OnCancel(self, e):
        dprint("Cancel!: Edited=%s" % self.is_edited)
        if self.is_edited:
            res = wx.MessageBox('Data Modified. Are you sure?',
                                'Question',
                                wx.YES_NO | wx.ICON_WARNING)
            dprint("Message result:", res)
            if res == wx.NO:
                return
            # since our calculate has modifed the rdb data, we
            # need to reload it :(
            rdb.init_rounds()
        self.Destroy()

    def OnListEdited(self, evt):
        dprint("OnListEdited: Col=%d: %s" % (evt.col, evt.message))
        # was editing in the front9/back9 columns?
        if evt.col in [1, 2]:
            dprint("XXX Need to update mzkitty amount(s)!!!")
        # but any change means we need to save the changes
        self.is_edited = True
        self.SetCommitButtonState()
        # flag that we need to update data from our form
        self.data_from_form_up_to_date = False

    def InitUI(self):
        self.SetUpPanel()
        self.Show(True)


