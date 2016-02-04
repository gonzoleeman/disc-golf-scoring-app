#!/usr/bin/python
'''
Python ride database class

 these classes represent the
 the disc golf course database

 There are three classes:
 * Course,
 * Player, and
 * Round

 Which will populate 3 dictionary tables:
 * CourseList,
 * PlayerList, and
 * RoundList

Designed to use a plugable backend (using classes), but using
a file backend to start
'''

__version__ = "1.0"
__author__ = "Lee Duncan"


import sqlite3
from dateutil.parser import parse as parse_date
import datetime as dt

from utils import dprint
from opts import opts


class Course:
    '''
    A single Disc Golf Course
    '''
    def __init__(self, cnum, cname):
        self.num = cnum
        self.name = cname

    def __str__(self):
        return "Course[%d]: %s" % (self.num, self.name)

class Player:
    '''
    A Disc Golf Player
    '''
    def __init__(self, pnum, sname, lname):
        self.num = pnum
        self.name = sname
        self.long_name = lname

    def __str__(self):
        return "Player[%d]: %s (%s)" % \
               (self.num, self.long_name, self.name)


class Round:
    '''
    One round, not counting the individual scores
    '''
    def __init__(self, rnum, cnum, rdate):
        self.num = int(rnum)
        self.course_num = int(cnum)
        self.rdate = parse_date(rdate)

    def __str__(self):
        return "Round[%d]: course=%d, %s" % \
               (self.num, self.course_num, self.rdate)

class RoundDetail:
    '''
    One entry for one person for one round (which is one course on one day)
    '''
    def __init__(self, rnum, pnum, fscore=None, bscore=None,
                 acnt=0, ecnt=0, score=0.0):
        self.round_num = int(rnum)
        self.player_num = int(pnum)
        self.fscore = (None if fscore is None else int(fscore))
        self.bscore = bscore
        if self.bscore is not None:
            self.bscore = int(self.bscore)
        self.acnt = acnt
        self.ecnt = ecnt
        # this is the CALCULATED *FLOATING POINT* score
        self.score = float(score)

    def __eq__(self, other):
        return self.round_num == other.round_num and \
               self.player_num == other.player_num

    def SetScore(self, fscore, bscore):
        self.fscore = int(fscore)
        self.bscore = int(bscore)

    def Overall(self):
        '''Return overall, assuming round has been scored'''
        return self.fscore + self.bscore

    def __str__(self):
        return "RoundDetail[round=%d]: " % self.round_num + \
               "pnum=%d, score=%s/%s, a/e=%d/%d => %f" % \
               (self.player_num, self.fscore, self.bscore,
                self.acnt, self.ecnt, self.score)


DB_DIR = 'db'
DB_FILE = 'disc_golf.db'
DB_PATH = "%s/%s" % (DB_DIR, DB_FILE)

# our internal representation of a database, using dictionaries
CourseList = {}
PlayerList = {}
RoundList = {}
# the detail list is not indexed by a number, so it's an array
RoundDetailList = []

RoundNumberMax = 0

#
# database routines (use a 'class'?)
#
def init_db():
    '''Initialize the DG Database'''

    global CourseList
    global PlayerList
    global RoundList
    global RoundDetailList
    global RoundNumberMax

    dprint("Initializing the Database (%s) ..." % DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # now read our DB tables into Python objects
    dprint("Initializing Disc Golf Courses ...")
    for row in c.execute('''SELECT * FROM courses'''):
        course_num = row[0]
        course_name = row[1]
        dprint("Adding course[%d]: name=%s" % (course_num, course_name))
        CourseList[course_num] = Course(course_num, course_name)
    dprint("Initializing Disc Golf Players ...")
    for row in c.execute('''SELECT * FROM players'''):
        (player_num, player_name, player_full_name) = row[0:3]
        dprint("Adding player[%d]: name=%s full_name=%s" % (player_num,
                                                            player_name,
                                                            player_full_name))
        PlayerList[player_num] = Player(player_num,
                                        player_name,
                                        player_full_name)
    dprint("Initializing Disc Golf Rounds ...")
    for row in c.execute('''SELECT * FROM rounds'''):
        (round_num, course_num, round_date) = row[0:3]
        dprint("Adding round[%d]: course_num=%s, rnd_date=%s" % \
               (round_num, course_num, round_date))
        RoundList[round_num] = Round(round_num, course_num, round_date)
        if round_num > RoundNumberMax:
            RoundNumberMax = round_num
    dprint("Initializing Disc Golf Round Details ...")
    for row in c.execute('''SELECT * from round_details'''):
        (round_num, player_num, fscore, bscore, acnt, ecnt, score) = row[0:7]
        dprint("Adding round detail: rnd_num=%s, p_num=%s, fscore=%s, bscore=%s, a/e-cnt=%s/%s, score=%s" % \
               (round_num, player_num, fscore, bscore, acnt, ecnt, score))
        rd = RoundDetail(round_num, player_num, fscore, bscore,
                         acnt, ecnt, score)
        RoundDetailList.append(rd)
    dprint("Round Number max seen: %d" % RoundNumberMax)

def next_round_num():
    global RoundNumberMax

    RoundNumberMax += 1
    return RoundNumberMax
