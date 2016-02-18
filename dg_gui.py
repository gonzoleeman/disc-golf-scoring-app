#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course

TO DO:
    - Add tracking "weather" (as a free-form string) for each round?
      Not really useful for the overall report, but might be good
      for historical reasons? -- or could have a few choices for weather,
      like "sunny/rainy", "temp", "wind"? Seems like a bit much.

    - ReportFrame needs a "done" button?

    - A Way to get directly to an existing money round, without having
      to go through the round?
    
    - Disallow selection of report list (for now), since it adds no
      value, and could be misleading. Some day, this might pop up details
      about that person?

    - Rename front 9 and back 9 fields to "strokes" instead of "score",
      for God sake

    - Disallow duplicate frames, e.g. for Round Scoring, choosing a round,
      money round scoring. more than one report frame should be ok

    - on Commit, if no money round, as AreYouSure?

    - when updating a round, if the date is changed, make sure
      the updated date does not match another record in the database.
      But of course if the date is not changed, it will match
      one and only one entry in the db, which corresponds to
      this round.

    - Question: For counting 9-s, 18-s, and 33-s, what if, for example,
      somebody ties on the front 9. Do both folks get 9-s?

    - update "Overall" column in RoundDetailsFrame when "Front 9"
      or "Back 9" updated for "Round Scoring" frame, in real time

    - Add "Notes" to round detail entry? (for stuff DB doesn not cover?)

    - Keep track of Aces, Eagles, and Ace-Eagles on a per-hole basis,
      e.g. have a drop-down radio-button list in the menu for each
      of the 18 hole -- hopefully not needed, except for by Gary

    - Add option to backup the DB. (Periodically, or on demand)

    - Allow update of DB any time, but warn user that "calc is needed"
      if they have updated a front or back 9 score

    - Sanity check; disallow new rounds in the future?
      What about too far in the past? Probably not needed.

    - Break main status window into 2 parts: the first is the file
      name of the database, and the 2nd is for error messages
      (for which frame(s)?)

    - As soon as any field changed in the Scoring GUI, update
      the status window to say "Edited"

    - handle "E" as the number "0" (i.e. "even") for score fields,
      and display "E" instead of "+0" (enhancement). Display it this
      way too? (Might require a new "type" of integer?)

    - display results graphically? Not sure what would be displayed yet.

    - quit guessing what new round number will be, and actually let
      the database decide

    - in general, use use the DB as the backend, with transactions,
      and never have to keep local copies of data? (may be slow?)
    - use DB transactions for changes, so we can just update the DB, then
      throw it away if they say "no"

    - make setup window become the scoring window for a round,
      instead of just replacing one window with the next (optimization)
      (and likewise for the setup-report->report transition)

    - consider RETURN key in main window like Show/Edit button hit
      (optimization) (i.e. Default?, Focus?)

    -------------------------------

    - Support alternate/new Database files (why?)

    - support DB modification for Courses and Players (some day),
      so I do not have to use sqlite3 directly, or write a program, to
      do this

    - support modifying a round to add or remove a player,
      or even to remove a round? (not needed, and possibly evil)

    - Properly package for distribution (for who?)

    - implement real help? (like what?)

    - preferences? not really needed yet: nothing to configure/prefer
      - e.g. which players are "usually there"
      - size of windows?

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
    versoin 1.8: all works but commit?
    version 1.9: all works but getting result data!!!
    version 1.10: Now displays results, but no graph
    version 1.11: Total score now a fraction. Round scores displayed
        as "+N", or "-N". Also, now displaying "overall" score
    version 1.12: Now tracking front/rear/overall score separately, per
        round played, for easier tracking of 9-s, 18-s, etc.
    version 1.13: Many changes, including handling money rounds, and
        displaying money won and best front and rear rounds. Also added
        new date ranges for reports
    version 1.14:
        * update report window if round(s) updated
        * cleaned up money parsing debugging
        * cleaned up money reporting bugs
    version 1.15:
        * Now displaying report date range and record counts
        * Date and course now saved/updated/displayed in scoring frame
    version 1.16:
        * Now keeps track of mz kitty, on report screen, which
          took quite a bit of re-arranging, including breaking
          the round table into two: round and money round, and
          doing the same for the round detail, now round detail and
          money round detail. Assume that mz kitty only ges money
          if the round try-number field is "7", and then assume
          the number of players is the number you find in the
          money round detail table for that money round.
'''


import sys
from optparse import OptionParser
import wx

import rdb
from utils import dprint
from opts import opts
import rounds



__author__ = "Lee Duncan"
__version__ = "1.16"


################################################################

def parse_options():
    parser = OptionParser(version='%prog ' + __version__,
                          usage='usage: %prog [options]',
                          description='Disc Golf Database, version ' + \
                              __version__)
    parser.add_option('-d', '--debug', action='store_true',
                      help='enter debug mode [%default]')
    (o, a) = parser.parse_args()
    opts.debug = o.debug


################################################################

def main():
    parse_options()
    rdb.init_db()
    app = wx.App()
    rounds.CurrentRoundsFrame(None, title='DGDB: The Disc Golf Database')
    app.MainLoop()


if __name__ == '__main__':
    main()
    sys.exit(0)
