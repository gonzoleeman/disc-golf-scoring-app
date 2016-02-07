#!/usr/bin/python
'''
initialize the disc golf db using sqlite3

if the db exists, raise an error

TODO:
* Add "force" option to remove existing DB?
'''

import os
import sys
from optparse import OptionParser
import sqlite3

from opts import opts
from utils import dprint


_DB_DIR = 'db'
_DB_FILE = 'disc_golf.db'


__author__ = "Lee Duncan"
__version__ = "1.0"


#
# data for preloading the database
#
players = [
    # fields:
    # 1. num -- autoincrement
    # 2. name
    # 3. full_name
    ("Gary", "Gary Rogers"),		# 1
    ("Pat", "Pat Olmstead"),	        # 2
    ("Charlie", "Charlie Amacher"),     # 3
    ("Dick", "Dick Burdock"),           # 4
    ("Gabe", "Gabe Miller"),            # 5
    ("Dr Dave", "Dr Dave"),             # 6
    ("John J", "John J"),               # 7
    ("John U", "John U"),               # 8
    ("Jonathon", "Jonathon Williams"),  # 9
    ("Rick", "Rick Miller"),            # 10
    ("Lee", "Lee Duncan"),              # 11
    ("Bill", "Bill ???"),               # 12
    ]

courses = [
    # fields:
    # 1. num -- autoincrement
    # 2. course_name
    ("Dick's",),
    ("Charlie's",),
    ("Bill's",),
    ("Rick's",),
    ("Pat's",),
    ]


#
# optional (debugging) data for creating round info
#
rounds = [
    # fields:
    # 1. num -- autoincrement
    # 2. course_num (join from course.num)
    # 3. rdate
    (1, "1/12/2016"),                   # Dick's: 8 players
    (5, "1/19/2016"),                   # Pat's: 6 players
    ]

round_details = [
    # fields:
    # round_num (join from rounds.num)
    #  player_num (join from player.num)
    #   fscore
    #    bscore
    #     acnt
    #      ecnt
    #       calc_score_numerator
    #        calc_score_denomiator
    ################################################################
    # for round 1: At Dicks's on 1/12/2016: 8 players
    (1,  2, +1, +2, 1, 0,  1, 1),       # Pat
    (1,  1, -1, -1, 0, 0, 12, 1),       # Gary
    (1,  4, +1, +4, 0, 0,  5, 1),       # Dick
    (1,  3, +2, +2, 0, 0,  1, 2),       # Charlie
    (1, 12, +1,  0, 0, 0,  1, 2),       # Bill
    (1, 11,  0,  0, 0, 0,  1, 2),       # Lee
    (1,  7, +6, +4, 0, 0,  1, 2),       # John J
    (1,  9, -1, +1, 0, 0,  1, 2),       # Jonathon
    ################################################################
    # for round 2 - At Pat's on 1/19/2016: 6 players
    (2,  2,  0, -3, 0, 0, 33, 1),       # Pat
    (2,  4,  0, +1, 0, 0,  1, 4),       # Dick
    (2,  3, +4, -1, 0, 0, 11, 1),       # Charlie
    (2, 12, -2, -1, 0, 0,  4, 3),       # Bill
    (2, 11, -2, -2, 0, 0,  5, 3),       # Lee
    ]


def ensure_no_db():
    if not os.path.isdir(_DB_DIR):
        os.mkdir(_DB_DIR)
        return
    if os.path.isfile("%s/%s" % (_DB_DIR, _DB_FILE)):
        raise Exception("DB File already exists!")

def initialize_players(c):
    global players
    
    dprint("Creating DB Table: 'players' ...")
    c.execute('''CREATE TABLE players (
    			num INTEGER PRIMARY KEY AUTOINCREMENT,
    			name CHAR(20),
                        full_name CHAR(40))''')
    dprint("Initializing DB Table: 'players' ...")
    c.executemany('''INSERT INTO players(name, full_name) VALUES(?,?)''',
                  players)

def initialize_courses(c):
    global courses

    dprint("Creating DB Table: 'courses' ...")
    c.execute('''CREATE TABLE courses (
    				num INTEGER PRIMARY KEY AUTOINCREMENT,
    				name CHAR(20))''')
    dprint("Initializing DB Table: 'courses' ...")
    c.executemany('''INSERT INTO courses(name) VALUES (?)''', courses)

def initialize_rounds(c):
    global rounds
    global round_details

    dprint("Creating DB Table: 'rounds' ...")
    c.execute('''CREATE TABLE rounds (
    				num INTEGER PRIMARY KEY AUTOINCREMENT,
    				course_num INTEGER,
                                rdate DATE)''')
    c.execute('''CREATE TABLE round_details (
    				round_num INTEGER,
                                player_num INTEGER,
                                fscore SMALLINT,
                                bscore SMALLINT,
                                acnt SMALLINT,
                                ecnt SMALLINT,
                                calc_score_numerator SMALLINT,
                                calc_score_denominator SMALLINT,
                                PRIMARY KEY (round_num, player_num))''')
    dprint("Initializing DB Table: 'rounds' ...")
    c.executemany(
        '''INSERT INTO rounds(course_num, rdate) VALUES (?,?)''',
        rounds)
    dprint("Initializing DB Table: 'round_details' ...")
    c.executemany('''INSERT INTO round_details VALUES (?,?,?,?,?,?,?,?)''',
                  round_details)


def initialize_db():
    dprint("Creating DB: %s/%s ..." % (_DB_DIR, _DB_FILE))
    conn = sqlite3.connect("%s/%s" % (_DB_DIR, _DB_FILE))
    c = conn.cursor()
    initialize_players(c)
    initialize_courses(c)
    initialize_rounds(c)
    dprint("Commiting new database ...")
    conn.commit()


def parse_options():
    parser = OptionParser(version='%prog ' + __version__,
                          usage='usage: %prog [options]',
                          description='Disc Golf Database, version ' + \
                              __version__)
    parser.add_option('-d', '--debug', action='store_true',
                      help='enter debug mode [%default]')
    (o, a) = parser.parse_args()
    opts.debug = o.debug

def main():
    parse_options()
    ensure_no_db()
    initialize_db()

if __name__ == '__main__':
    main()
    sys.exit(0);
