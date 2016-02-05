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
    ("Gary", "Gary Rogers"),
    ("Pat", "Pat Olmstead"),
    ("Charlie", "Charlie Amacher"),
    ("Dick", "Dick Burdock"),
    ("Gabe", "Gabe Miller"),
    ("Dr Dave", "Dr Dave"),
    ("John J", "John J"),
    ("John U", "John U"),
    ("Jonathon", "Jonathon Williams"),
    ("Rick", "Rick Miller"),
    ("Lee", "Lee Duncan"),
    ("Bill", "Bill ???"),
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
    # 3. round_date
    (2, "1/12/2015"),	# Charlie's on Jan 12, 2015
    (1, "1/19/2015"),	# Dick's on Jan 19, 2015
    ]

round_details = [
    # fields:
    # round_num (join from rounds.num)
    # player_num (join from player.num)
    # fscore
    # bscore
    # acount
    # ecount
    # calc_score -- NOTE that scores are wrong on purpose
    (1, 3, 1, 0, 0, 0, 1.0),	# Dicks's on 1/12/2015, Charlie
    (1, 2, 2, 0, 0, 0, 12.0),	# Dicks's on 1/12/2015, Pat
    (1, 5, 3, 0, 0, 0, 5.0),	# Dicks's on 1/12/2015, Gabe
    (1, 7, 4, 0, 0, 0, 0.5),	# Dicks's on 1/12/2015, John J
    (1, 11, 0, 0, 0, 0, 2.33333),	# Dicks's on 1/12/2015, Lee
    (2, 3, 1, 0, 0, 0, 33.0),	# Charlie's on 1/19/2015, Charlie
    (2, 9, 4, 0, 0, 0, 4.50),	# Charlie's on 1/19/2015, Jonathon
    (2, 2, 2, 0, 0, 0, 0.25),	# Charlie's on 1/19/2015, Pat
    (2, 5, 3, 0, 0, 0, 10.99999),	# Charlie's on 1/19/2015, Gabe
    (2, 11, 0, 0, 0, 0, 3.1415),	# Charlie's on 1/19/2015, Lee
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
                                round_date DATE)''')
    c.execute('''CREATE TABLE round_details (
    				round_num INTEGER,
                                player_num INTEGER,
                                fscore SMALLINT,
                                bscore SMALLINT,
                                acount SMALLINT,
                                ecount SMALLINT,
                                calc_score DOUBLE,
                                PRIMARY KEY (round_num, player_num))''')
    dprint("Initializing DB Table: 'rounds' ...")
    c.executemany(
        '''INSERT INTO rounds(course_num, round_date) VALUES (?,?)''',
        rounds)
    dprint("Initializing DB Table: 'round_details' ...")
    c.executemany('''INSERT INTO round_details VALUES (?,?,?,?,?,?,?)''',
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
