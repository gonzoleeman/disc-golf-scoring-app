#!/usr/bin/python
'''
Python ride database class

TO DO:
    - throw exception of we write over a hole on a course
'''

__version__ = "1.0"
__author__ = "Lee Duncan"

class Opts:
    def __init__(self, debug=False):
        self.debug = debug

opts = Opts()

