#!/usr/bin/python
'''
Test script to read from sqlite3 DB
'''

import os
import sys
import sqlite3

from opts import opts
from utils import dprint

DB_PATH = 'db/disc_golf.db'


def main():
    dprint("Opening DB ...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    dprint("Trying to read table: courses ...")
    for row in c.execute('''SELECT * FROM courses'''):
        print row


if __name__ == '__main__':
    opts.debug = True
    main()
    sys.exit(0)
