#!/usr/bin/python
'''
My own wx.DateTime class
'''

from wx import DateTime as wxdt
from wx import DateSpan as wxds
import datetime as dt

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

def wxdt_create(day=None, month=None, year=None):
    res = wxdt()
    if day is not None:
        res.SetDay(day)
    if month is not None:
        res.SetMonth(month)
    if year is not None:
        res.SetYear(year)
    return res

def wxdt_to_date_str(wxdt_dt):
    '''Return "%m/%d/%Y" for a wxdt date'''
    return "%d/%d/%d" % (wxdt_dt.GetMonth()+1,
                         wxdt_dt.GetDay(),
                         wxdt_dt.GetYear())

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
        dt_start = wxdt_create(1, 0)
    elif key == 'MTD':
        dprint("Using 1/1/THISMONTH to NOW")
        dt_end = wxdt.Today()
        dt_start = wxdt_create(1)
    elif key == 'Last Year':
        dprint("Using 1/1/LASTYEAR to 12/31/LASTYEAR")
        last_yr = wxdt.Today().GetYear() - 1
        dt_start = wxdt_create(1, 0, last_year)
        dt_end = wxdt_create(31, 11, last_yr)
    elif key == 'Last Month':
        dprint("Using Beginning to end of Last month")
        # get first day of this month
        fom = wxdt_create(1)
        # get last day of last month
        dt_end = fom - wxds(days=1)
        dprint("Set end date:", dt_end)
        # now get first day of last month
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


def wxdt_to_dt(wxdt_dt):
    '''
    return a wx.datetime for the supplied datetime
    '''
    dt_dt = dt.datetime(wxdt_dt.GetYear(),
                        wxdt_dt.GetMonth()+1,
                        wxdt_dt.GetDay())
    dprint("Converted wx:", wxdt_dt, "to dt:", dt_dt)
    return dt_dt

def dt_to_wxdt(dt_dt):
    '''
    return a datetime for the wx.DateTime supplied
    '''
    if dt_dt is None:
        dt_dt = dt.datetime.today()
    wxdt_dt = wxdt_create(dt_dt.day,
                          dt_dt.month-1,
                          dt_dt.year)
    dprint("Converted dt: %s to wxdt: %s" % \
           (dt_dt.strftime("%m/%d/%Y"), wxdt_to_date_str(wxdt_dt)))
    return wxdt_dt
