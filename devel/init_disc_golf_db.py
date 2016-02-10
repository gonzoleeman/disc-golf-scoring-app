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
players_preload_list = [
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

courses_preload_list = [
    # fields:
    # 1. num -- autoincrement
    # 2. course_name
    ("Dick's",),                        # 1
    ("Charlie's",),                     # 2
    ("Bill's",),                        # 3
    ("Rick's",),                        # 4
    ("Pat's",),                         # 5
    ]


#
# optional (debugging) data for creating round info
#
rounds_preload_list = [
    # fields:
    # 1. num -- autoincrement
    # 2.  course_num (join from course.num)
    # 3.   rdate
    # 4.    mround1				- $ round 1 won on which pass?
    # 5.     mround2				- $ round 2 won on which pass?
    # 6.      mround3				- $ round 3 won on which pass?
    (1, "1/10/2016", 1, 3, 0),          # Dick's
    (5, "1/24/2016", 6, 4, 0),          # Pat's
    ]

round_details_preload_list = [
    # fields:
    # round_num (join from rounds.num)
    #  player_num (join from player.num)
    #   fscore					- front score over/under
    #    bscore					- back score over/under
    #     acnt					- ace count
    #      ecnt					- eagle count
    #       aecnt				- ace-eagle count
    #        calc_fscore_numerator
    #         calc_fscore_denomiator
    #          calc_bscore_numerator
    #           calc_bscore_denomiator
    #            calc_oscore_numerator
    #             calc_oscore_denomiator
    #              money_rnd1_winnings
    #               money_rnd2_winnings
    #                money_rnd3_winnings
    ################################################################
    # for rouxsnd 1: At Dicks's on 1/12/2016: 8 players
    (1,  2, +1, +2, 1, 0, 0,  1, 1, 0, 1, 0, 1, 0, 0, 0), # Pat
    (1,  1, -1, -1, 0, 0, 0, 12, 1, 0, 1, 0, 1, 0, 400, 0), # Gary
    (1,  4, +1, +4, 0, 0, 0,  5, 1, 0, 1, 0, 1, 400, 400, 0), # Dick
    (1,  3, +2, +2, 0, 0, 0,  1, 2, 0, 1, 0, 1, 400, 0, 0), # Charlie
    (1, 12, +1,  0, 0, 0, 0,  1, 2, 0, 1, 0, 1, 0, 0, 0), # Bill
    (1, 11,  0,  0, 0, 0, 0,  1, 2, 0, 1, 0, 1, 0, 0, 0), # Lee
    (1,  7, +6, +4, 0, 0, 0,  1, 2, 0, 1, 0, 1, 0, 0, 0), # John J
    (1,  9, -1, +1, 0, 0, 0,  1, 2, 0, 1, 0, 1, 0, 0, 0), # Jonathon
    ################################################################
    # for round 2 - At Pat's on 1/19/2016: 6 players
    (2,  2,  0, -3, 0, 0, 0, 33, 1, 0, 1, 0, 1, 500, 0, 0), # Pat
    (2,  4,  0, +1, 0, 0, 0,  1, 4, 0, 1, 0, 1, 0, 0, 0), # Dick
    (2,  3, +4, -1, 0, 0, 0, 11, 1, 0, 1, 0, 1, 0, 500, 0), # Charlie
    (2, 12, -2, -1, 0, 0, 0,  4, 3, 0, 1, 0, 1, 0, 0, 0), # Bill
    (2, 11, -2, -2, 0, 0, 0,  5, 3, 0, 1, 0, 1, 0, 0, 0), # Lee
    ]


def ensure_no_db():
    if not os.path.isdir(_DB_DIR):
        os.mkdir(_DB_DIR)
        return
    if os.path.isfile("%s/%s" % (_DB_DIR, _DB_FILE)):
        raise Exception("DB File already exists!")

def db_cmd_exec(c, cmd):
    dprint("sqlite3 cmd: %s" % cmd)
    c.execute(cmd)

def db_cmd_exec_many(c, cmd, data):
    for d in data:
        db_cmd_exec(c, cmd % d)

def initialize_players(c):
    global players_preload_list
    
    dprint("Creating DB Table: 'players' ...")
    db_cmd_exec(c, '''CREATE TABLE players (
    			num INTEGER PRIMARY KEY AUTOINCREMENT,
    			name CHAR(20),
                        full_name CHAR(40))''')
    dprint("Initializing DB Table: 'players' ...")
    db_cmd_exec_many(c, '''INSERT INTO players(name, full_name)
                           VALUES(\"%s\",\"%s\")''',
                     players_preload_list)

def initialize_courses(c):
    global courses_preload_list

    dprint("Creating DB Table: 'courses' ...")
    db_cmd_exec(c, '''CREATE TABLE courses (
    				num INTEGER PRIMARY KEY AUTOINCREMENT,
    				name CHAR(20))''')
    dprint("Initializing DB Table: 'courses' ...")
    db_cmd_exec_many(c, '''INSERT INTO courses(name) VALUES (\"%s\")''',
                     courses_preload_list)

def initialize_rounds(c):
    global rounds_preload_list
    global round_details_preload_list

    dprint("Creating DB Table: 'rounds' ...")
    db_cmd_exec(c, '''CREATE TABLE rounds (
    				  num INTEGER PRIMARY KEY AUTOINCREMENT,
    				  course_num INTEGER,
                                  rdate DATE,
                                  mround1 SMALLINT,
                                  mround2 SMALLINT,
                                  mround3 SMALLINT)''')
    db_cmd_exec(c, '''CREATE TABLE round_details (
    				  round_num INTEGER,
                                  player_num INTEGER,
                                  fscore SMALLINT,
                                  bscore SMALLINT,
                                  acnt SMALLINT,
                                  ecnt SMALLINT,
                                  aecnt SMALLINT,
                                  calc_fscore_numerator SMALLINT,
                                  calc_fscore_denominator SMALLINT,
                                  calc_bscore_numerator SMALLINT,
                                  calc_bscore_denominator SMALLINT,
                                  calc_oscore_numerator SMALLINT,
                                  calc_oscore_denominator SMALLINT,
                                  money_rnd1_winnings SMALLINT,
                                  money_rnd2_winnings SMALLINT,
                                  money_rnd3_winnings SMALLINT,
                                    PRIMARY KEY (round_num, player_num))''')
    dprint("Initializing DB Table: 'rounds' ...")
    db_cmd_exec_many(c, '''INSERT INTO rounds(course_num,
                                              rdate,
                                              mround1,
                                              mround2,
                                              mround3)
                        VALUES (%d,\"%s\",%d,%d,%d)''',
                     rounds_preload_list)
    dprint("Initializing DB Table: 'round_details' ...")
    db_cmd_exec_many(c, '''INSERT INTO round_details
                    VALUES (%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)''',
                     round_details_preload_list)


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
