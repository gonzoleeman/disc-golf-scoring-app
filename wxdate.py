#!/usr/bin/python
'''
My own wx.DateTime class
'''

from wx import DateTime as wxdt
from wx import DateSpan as wxds
import copy

from opts import opts
from utils import dprint

#
# return a range for the specified range
#

DATE_RANGES = ['<Choose a Range>',
               'YTD',
               'MTD',
               'Last Year',
               'Last Month',
               'All Time']


def range_from_key(key):
    '''
    return a starting and ending wx.DateTime() for each known date range
    choice
    '''
    if key == DATE_RANGES[0]:
        raise Exception("Must supply a date range")
    if key not in DATE_RANGES:
        raise Exception("Date Range '%s' not legal" % key)
    if key == 'YTD':
        dprint("Using 1/1/THISYEAR to NOW")
        dt_end = wxdt.Today()
        dt_start = wxdt()
        dt_start.Set(1, 0, dt_end.GetYear())
    elif key == 'MTD':
        dprint("Using 1/1/THISMONTH to NOW")
        dt_end = wxdt.Today()
        dprint("Found end date (today) of:", dt_end)
        dt_start = wxdt()
        dt_start.Set(1, dt_end.GetMonth(), dt_end.GetYear())
    elif key == 'Last Year':
        dprint("Using 1/1/LASTYEAR to 12/31/LASTYEAR")
        last_yr = wxdt.Today().GetYear() - 1
        dt_start = wxdt()
        dt_start.Set(1, 0, last_yr)
        dt_end = wxdt()
        dt_end.Set(31, 11, last_yr)
    elif key == 'Last Month':
        dprint("Using Beginning to end of Last month")
        # get first day of this month
        fom = wxdt.Today()
        fom.SetDay(1)
        # get last day of last month
        dt_end = fom - wxds(days=1)
        dprint("Set end date:", dt_end)
        # now get firs day of last month
        dt_start = fom - wxds(days=1)
        dt_start.SetDay(1)
    elif key == 'All Time':
        dt_start = wxdt()
        dt_start.Set(1, 0, 1900)
        dt_end = wxdt()
        dt_end.Set(31,11,3000)
    else:
        raise Exception("Unknown date range: '%s'" % key)
    ################################################################
    dprint("Found start date of: %s" % dt_start)
    dprint("Found end date of: %s" % dt_end)
    return (dt_start, dt_end)
