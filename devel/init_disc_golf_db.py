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
import csv

from opts import opts
from utils import dprint


_DB_DIR = 'db'
_DB_FILE = 'disc_golf.db'


__author__ = "Lee Duncan"
__version__ = "1.2-wip"


#
# data for preloading the database
#


#
# optional data for creating round info
#


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
    dprint("sqlite3 cmd: '%s'" % cmd)
    c.execute(cmd)

def db_cmd_execd(c, cmd, data):
    dprint("sqlite3 cmd: '%s' with data:" % cmd, data)
    c.execute(cmd, data)


def initialize_players(c, create_empty=False):
    if True:
        db_cmd_exec(c, '''CREATE TABLE players (
    			num INTEGER PRIMARY KEY,
    			name CHAR(20),
                        full_name CHAR(40))''')
    else:
        db_cmd_exec(c, '''CREATE TABLE players (
    			num INTEGER PRIMARY KEY AUTOINCREMENT,
    			name CHAR(20),
                        full_name CHAR(40))''')
    if create_empty:
        return
    with open('preload/players.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONNUMERIC)
        for r in dr:
            t = (int(r['num']), r['name'], r['full_name'])
            db_cmd_execd(c, "INSERT INTO players VALUES(?,?,?)", t)


def initialize_courses(c, create_empty=False):
    dprint("Creating DB Table: 'courses' ...")
    db_cmd_exec(c, '''CREATE TABLE courses (
    				num INTEGER PRIMARY KEY,
    				name CHAR(20))''')
    if create_empty:
        return
    with open('preload/courses.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONNUMERIC)
        for r in dr:
            #dprint("Dict Result Row:", r)
            t = (int(r['num']), r['course_name'])
            db_cmd_execd(c, "INSERT INTO courses VALUES(?,?)", t)

def initialize_rounds(c, create_empty=False):
    db_cmd_exec(c, '''CREATE TABLE rounds (
    				  num INTEGER PRIMARY KEY,
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
                                  fstrokes SMALLINT,
                                  bstrokes SMALLINT,
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
    with open('preload/rounds.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONNUMERIC)
        for r in dr:
            t = (int(r['num']), int(r['course_num']), r['rdate'])
            dprint("setting up 'rounds' tupple:", t)
            db_cmd_execd(c, "INSERT INTO rounds VALUES(?,?,?)", t)
    ####
    with open('preload/money_rounds.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONNUMERIC)
        for r in dr:
            t = (int(r['round_num']),
                 int(r['mround1']), int(r['mround2']), int(r['mround3']))
            db_cmd_execd(c, "INSERT INTO money_rounds VALUES(?,?,?,?)", t)
    ####
    with open('preload/round_details.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONNUMERIC)
        for r in dr:
            t = (int(r['round_num']), int(r['player_num']),
                 int(r['fstrokes']), int(r['bstrokes']),
                 int(r['acnt']), int(r['ecnt']), int(r['aecnt']),
                 int(r['calc_fscore_numerator']),
                 int(r['calc_fscore_denominator']),
                 int(r['calc_bscore_numerator']),
                 int(r['calc_bscore_denominator']),
                 int(r['calc_oscore_numerator']),
                 int(r['calc_bscore_denominator']))
            db_cmd_execd(c, "INSERT INTO round_details " + \
                         "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", t)
    ####
    with open('preload/money_round_details.csv', 'rb') as fin:
        dr = csv.DictReader(fin,
                            skipinitialspace=True,
                            quoting=csv.QUOTE_NONE)
        for r in dr:
            t = (int(r['round_num']), int(r['player_num']),
                 int(r['money_rnd1_winnings']),
                 int(r['money_rnd2_winnings']),
                 int(r['money_rnd3_winnings']))
            db_cmd_execd(c, "INSERT INTO money_round_details " + \
                         "VALUES(?,?,?,?,?)", t)


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
