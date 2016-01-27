#!/usr/bin/python
'''
initialize the disc golf db using sqlite3

if the db exists, raise an error
'''

import os
import sys
import sqlite3

from opts import opts
from utils import dprint


_DB_DIR = 'db'
_DB_FILE = 'disc_golf.db'


def ensure_no_db():
    if not os.path.isdir(_DB_DIR):
        os.mkdir(_DB_DIR)
        return
    if os.path.isfile("%s/%s" % (_DB_DIR, _DB_FILE)):
        raise Exception("DB File already exists!")

def initialize_players(c):
    dprint("Creating DB Table: 'players' ...")
    c.execute('''CREATE TABLE players (
    			player_num SMALLINT PRIMARY KEY,
    			name CHAR(20),
                        full_name CHAR(40))''')
    players = [
        (1, "Gary", "Gary Rogers"),
        (2, "Pat", "Pat Olmstead"),
        (3, "Charlie", "Charlie Amacher"),
        (4, "Dick", "Dick Burdock"),
        (5, "Gabe", "Gabe Miller"),
        (6, "Dr Dave", "Dr Dave"),
        (7, "John J", "John J"),
        (8, "John U", "John U"),
        (9, "Jonathon", "Jonathon Williams"),
        (10, "Rick", "Rick Miller"),
        (11, "Lee", "Lee Duncan"),
        ]
    c.executemany('''INSERT INTO players VALUES(?,?,?)''',
                  players)

def initialize_courses(c):
    dprint("Creating DB Table: 'courses' ...")
    c.execute('''CREATE TABLE courses (
    				course_num SMALLINT PRIMARY KEY,
    				name CHAR(20))''')
    courses = [
        (1, "Dick's",),
        (2, "Charlie's",),
        (3, "Bill's",),
        (4, "Rick's",),
        (5, "Pat's",),
        ]
    c.executemany('''INSERT INTO courses VALUES (?,?)''', courses)

def initialize_rounds(c):
    dprint("Creating DB Table: 'rounds' ...")
    c.execute('''CREATE TABLE rounds (
    				round_number SMALLINT PRIMARY KEY,
    				course_id CHAR(20),
                                round_date DATE)''')
    c.execute('''INSERT INTO rounds VALUES (1, 1, "1/12/2015")''')
    c.execute('''CREATE TABLE round_details (
    				round_number INTEGER,
                                player_id SMALLINT,
                                fscore SMALLINT,
                                bscore SMALLINT,
                                acount SMALLINT,
                                ecount SMALLINT,
                                calc_score SMALLINT,
                                PRIMARY KEY (round_number, player_id))''')
    rounds = [
        (1, 1, -3, -2, 0, 0, 0),
        (1, 4, 1, 0, 0, 0, 0),
        (1, 3, -1, -2, 0, 0, 0)
        ]
    c.executemany('''INSERT INTO round_details VALUES (?,?,?,?,?,?,?)''',
                  rounds)

def initialize_db():
    dprint("Creating DB: %s/%s ..." % (_DB_DIR, _DB_FILE))
    conn = sqlite3.connect("%s/%s" % (_DB_DIR, _DB_FILE))
    c = conn.cursor()
    initialize_players(c)
    initialize_courses(c)
    initialize_rounds(c)
    dprint("Commiting new database ...")
    conn.commit()

def main():
    ensure_no_db()
    initialize_db()

if __name__ == '__main__':
    opts.debug = True
    main()
    sys.exit(0);
