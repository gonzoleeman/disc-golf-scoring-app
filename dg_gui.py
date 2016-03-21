#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Python script to present a Disc Golf GUI, that allows
us to keep track of courses and holes on that course


'''


import sys
from optparse import OptionParser
import wx

import rdb
from utils import dprint
from opts import opts
import rounds



__author__ = "Lee Duncan"
__version__ = "1.18"


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
