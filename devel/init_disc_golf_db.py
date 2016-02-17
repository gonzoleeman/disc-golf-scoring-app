#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
initialize the disc golf db using sqlite3

if the db exists, raise an error

TODO:
* Add "force" option to remove existing DB?

Versions:
1.1: all the beginning stuff
1.2: * Breaking money rounds out as two new tables
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
__version__ = "1.2-wip"


#
# data for preloading the database
#
players_preload_list = [
    # fields:
    # 1. num -- autoincrement			** KEY **
    # 2. name
    # 3. full_name
    (1, "Gary", "Gary Rogers"),           # 1
    (2, "Pat", "Pat Olmstead"),           # 2
    (3, "Charlie", "Charlie Amacher"),    # 3
    (4, "Dick", "Dick Burdock"),          # 4
    (5, "Gabe", "Gabe Miller"),           # 5
    (6, "Dr Dave", "Dr Dave"),            # 6
    (7, "John J", "John J"),              # 7
    (8, "John U", "John U"),              # 8
    (9, "Jonathon", "Jonathon Williams"), # 9
    (10, "Rick", "Rick Miller"),          # 10
    (11, "Lee", "Lee Duncan"),            # 11
    (12, "Bill", "Bill ???"),             # 12
    ]

courses_preload_list = [
    # fields:
    # 1. num -- autoincrement			** KEY **
    # 2. course_name
    (1, "Dick's",),                     # 1
    (2, "Charlie's",),                  # 2
    (3, "Bill's",),                     # 3
    (4, "Rick's",),                     # 4
    (5, "Pat's",),                      # 5
    ]


#
# optional data for creating round info
#
rounds_preload_list = [
    # fields:
    # 1. num -- autoincrement			** KEY **
    # 2.  course_num (join from course.num)
    # 3.   rdate
    (1, 1, "1/10/2016"),                # Round 1: at Dick's
    (2, 5, "1/24/2016"),                # Round 2: Pat's
    ]

money_rounds_preload_list = [
    # fields:
    # 1.  round_num (JOIN from rounds.num)	** KEY **
    # 3.   mround1				- $ round 1 won on which pass?
    # 4.    mround2				- $ round 2 won on which pass?
    # 5.     mround3				- $ round 3 won on which pass?
    (1, 1, 3, 0),               # Money Round At Round 1: [1, 3, None]
    (2, 6, 7, 0),               # Money Round at Round 2: [6, 7, None]
    ]

round_details_preload_list = [
    # fields:
    # 1. round_num (JOIN from rounds.num)	\_ ** KEY **
    # 2.  player_num (JOIN from player.num)	/
    # 3.   fscore					- front score over/under
    # 4.    bscore					- back score over/under
    # 5.     acnt					- ace count
    # 6.      ecnt					- eagle count
    # 7.       aecnt				- ace-eagle count
    # 8.        calc_fscore_numerator
    # 9.         calc_fscore_denomiator
    # 10.         calc_bscore_numerator
    # 11.          calc_bscore_denomiator
    # 12.           calc_oscore_numerator
    # 13.            calc_oscore_denomiator
    ################################################################
    # for round 1: At Dicks's on 1/12/2016: 8 players
    (1,  2, +1, +2, 1, 0, 0,  1, 1, 0, 1, 0, 1), # Pat
    (1,  1, -1, -1, 0, 0, 0, 12, 1, 0, 1, 0, 1), # Gary
    (1,  4, +1, +4, 0, 0, 0,  5, 1, 0, 1, 0, 1), # Dick
    (1,  3, +2, +2, 0, 0, 0,  1, 2, 0, 1, 0, 1), # Charlie
    (1, 12, +1,  0, 0, 0, 0,  1, 2, 0, 1, 0, 1), # Bill
    (1, 11,  0,  0, 0, 0, 0,  1, 2, 0, 1, 0, 1), # Lee
    (1,  7, +6, +4, 0, 0, 0,  1, 2, 0, 1, 0, 1), # John J
    (1,  9, -1, +1, 0, 0, 0,  1, 2, 0, 1, 0, 1), # Jonathon
    ################################################################
    # for round 2 - At Pat's on 1/19/2016: 6 players
    (2,  2,  0, -3, 0, 0, 0, 33, 1, 0, 1, 0, 1), # Pat
    (2,  4,  0, +1, 0, 0, 0,  1, 4, 0, 1, 0, 1), # Dick
    (2,  3, +4, -1, 0, 0, 0, 11, 1, 0, 1, 0, 1), # Charlie
    (2, 12, -2, -1, 0, 0, 0,  4, 3, 0, 1, 0, 1), # Bill
    (2, 11, -2, -2, 0, 0, 0,  5, 3, 0, 1, 0, 1), # Lee
    ]


money_round_details_preload_list = [
    # fields:
    # round_num (JOIN from round.num) 		\_ ** KEY **
    #  player_num (JOIN from player.num)	/
    #   money_rnd1_winnings
    #    money_rnd2_winnings
    #     money_rnd3_winnings
    ################################################################
    # for money round 1: At Dicks's on 1/12/2016: all 8 players
    (1,  2,   0,   0, 0),               # Pat
    (1,  1,   0, 400, 0),               # Gary
    (1,  4, 400, 400, 0),               # Dick
    (1,  3, 400,   0, 0),               # Charlie
    (1, 12,   0,   0, 0),               # Bill
    (1, 11,   0,   0, 0),               # Lee
    (1,  7,   0,   0, 0),               # John J
    (1,  9,   0,   0, 0),               # Jonathon
    ################################################################
    # for money round 2 - At Pat's on 1/19/2016: all 6 players
    (2,  2, 500, 0, 0),                 # Pat
    (2,  4,   0, 0, 0),                 # Dick
    (2,  3, 500, 0, 0),                 # Charlie
    (2, 12,   0, 0, 0),                 # Bill
    (2, 11,   0, 0, 0),                 # Lee
    ]

def ensure_no_db(force_db_rm_first=False):
    '''
    Make sure there is no DB file

    Raise an exception on error, else just return
    '''
    if not os.path.isdir(_DB_DIR):
        dprint("Yikes: The DB directory doesn't even exist, so creating it")
        os.mkdir(_DB_DIR)
        # there can be no DB if we had to make the directory
        return
    db_file = "%s/%s" % (_DB_DIR, _DB_FILE)
    if not os.path.isfile(db_file):
        # no file means no db, so we are done
        return
    # there is a db file -- shoold we remove it?
    if not force_db_rm_first:
        # user does not want to remove the file first, so bail
        raise Exception("DB File already exists: %s" % db_file)
    # try to remove the db first, then check again
    dprint("Forcing removal of DB file, as requested")
    os.remove(db_file)
    if os.path.isfile(db_file):
        raise Exception("Can't remove existing DB File: %s" % db_file)


def db_cmd_exec(c, cmd):
    dprint("sqlite3 cmd: %s" % cmd)
    c.execute(cmd)

def db_cmd_exec_many(c, cmd, data):
    for d in data:
        db_cmd_exec(c, cmd % d)

def initialize_players(c, create_empty=False):
    global players_preload_list
    
    dprint("Creating DB Table: 'players' ...")
    db_cmd_exec(c, '''CREATE TABLE players (
    			num INTEGER PRIMARY KEY AUTOINCREMENT,
    			name CHAR(20),
                        full_name CHAR(40))''')
    if create_empty:
        return
    dprint("Initializing DB Table: 'players' ...")
    db_cmd_exec_many(c, '''INSERT INTO players VALUES(%d, \"%s\",\"%s\")''',
                     players_preload_list)

def initialize_courses(c, create_empty=False):
    global courses_preload_list

    dprint("Creating DB Table: 'courses' ...")
    db_cmd_exec(c, '''CREATE TABLE courses (
    				num INTEGER PRIMARY KEY AUTOINCREMENT,
    				name CHAR(20))''')
    if create_empty:
        return
    dprint("Initializing DB Table: 'courses' ...")
    db_cmd_exec_many(c, '''INSERT INTO courses VALUES (%d, \"%s\")''',
                     courses_preload_list)

def initialize_rounds(c, create_empty=False):
    global rounds_preload_list
    global money_rounds_preload_list
    global round_details_preload_list
    global money_round_details_preload_list

    dprint("Creating DB Table: 'rounds' ...")
    db_cmd_exec(c, '''CREATE TABLE rounds (
    				  num INTEGER PRIMARY KEY AUTOINCREMENT,
    				  course_num INTEGER,
                                  rdate DATE)''')
    db_cmd_exec(c, '''CREATE TABLE money_rounds (
                                  round_num INTEGER PRIMARY KEY,
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
                                    PRIMARY KEY (round_num, player_num))''')
    db_cmd_exec(c, '''CREATE TABLE money_round_details (
    				  round_num INTEGER,
                                  player_num INTEGER,
                                  money_rnd1_winnings SMALLINT,
                                  money_rnd2_winnings SMALLINT,
                                  money_rnd3_winnings SMALLINT,
                                    PRIMARY KEY (round_num, player_num))''')
    ####
    if create_empty:
        return
    ####
    dprint("Initializing DB Table: 'rounds' ...")
    db_cmd_exec_many(c, '''INSERT INTO rounds
                           VALUES (%d,%d,\"%s\")''',
                     rounds_preload_list)
    ####
    dprint("Initializing DB Table: 'money_rounds' ...")
    db_cmd_exec_many(c, '''INSERT INTO money_rounds
                           VALUES(%d,%d,%d,%d)''',
                     money_rounds_preload_list)
    ####
    dprint("Initializing DB Table: 'round_details' ...")
    db_cmd_exec_many(c, '''INSERT INTO round_details
                           VALUES (%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)''',
                     round_details_preload_list)
    ####
    dprint("Initializing DB Table: 'money_round_details' ...")
    db_cmd_exec_many(c, '''INSERT INTO money_round_details
                           VALUES (%d,%d,%d,%d,%d)''',
                     money_round_details_preload_list)


def initialize_db(skip_preload_flag):
    dprint("Creating DB: %s/%s ..." % (_DB_DIR, _DB_FILE))
    conn = sqlite3.connect("%s/%s" % (_DB_DIR, _DB_FILE))
    c = conn.cursor()
    initialize_players(c, skip_preload_flag)
    initialize_courses(c, skip_preload_flag)
    initialize_rounds(c, skip_preload_flag)
    dprint("Commiting new database ...")
    conn.commit()


def parse_options():
    parser = OptionParser(version='%prog ' + __version__,
                          usage='usage: %prog [options]',
                          description='Disc Golf Database, version ' + \
                              __version__)
    parser.add_option('-d', '--debug', action='store_true',
                      help='enter debug mode [%default]')
    parser.add_option('-n', '--no-preload', action='store_true',
                      dest='no_preload',
                      help='do NOT preload data [%default]')
    parser.add_option('-f', '--force-db-rm-first', action='store_true',
                      dest='force_db_rm_first',
                      help='force DB removal, if needed, to start [%default]')
    (o, a) = parser.parse_args()
    opts.debug = o.debug
    opts.no_preload = o.no_preload
    opts.force_db_rm_first = o.force_db_rm_first

def main():
    parse_options()
    ensure_no_db(opts.force_db_rm_first)
    initialize_db(opts.no_preload)

if __name__ == '__main__':
    main()
    sys.exit(0)
