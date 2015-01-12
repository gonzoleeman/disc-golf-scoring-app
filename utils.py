#!/usr/bin/python
'''
Python ride database class

TO DO:
    - throw exception of we write over a hole on a course
'''

__version__ = "1.0"
__author__ = "Lee Duncan"


import sys
from opts import opts


def dprint(*args):
    global opts
    if opts.debug:
        print >>sys.stderr, 'DEBUG:',
        for arg in args:
            print >>sys.stderr, arg,
        print >>sys.stderr

