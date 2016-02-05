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
import itertools as it

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
        self.full_name = lname

    def __str__(self):
        return "Player[%d]: %s (%s)" % \
               (self.num, self.full_name, self.name)


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
        self.fscore = None if fscore is None else int(fscore)
        self.bscore = None if bscore is None else int(bscore)
        self.acnt = acnt
        self.ecnt = ecnt
        # this is the CALCULATED *FLOATING POINT* score
        self.calc_score = float(score)

#    def __eq__(self, other):
#        dprint("Comparing EQUALity of %d/%d and %d/%d" % \
#               (self.round_num, self.player_num,
#                other.round_num, other.player_num))
#        return self.round_num == other.round_num and \
#               self.player_num == other.player_num

    def __cmp__(self, other):
        #dprint("__cmp__('%s', '%s')" % (self, other))
        if self.round_num != other.round_num:
            return self.round_num - other.round_num
        if self.player_num != other.player_num:
            return self.player_num - other.player_num
        if self.fscore != other.fscore:
            if self.fscore is None:
                return other.fscore
            if other.fscore is None:
                return self.fscore
            return self.fscore - other.fscore
        if self.bscore != other.bscore:
            if self.score is None:
                return other.bscore
            if other.bscore is None:
                return self.bscore
            return self.bscore - other.bscore
        if self.acnt != other.acnt:
            return self.acnt - other.acnt
        if self.ecnt != other.ecnt:
            return self.ecnt - other.ecnt
        if self.calc_score != other.calc_score:
            return self.calc_score - other.calc_score
        #dprint("rounds match!!!")
        return 0

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
                self.acnt, self.ecnt, self.calc_score)


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

DBConn = None
DBc = None


#
# database routines
#

def db_cmd_exec(cmd):
    global DBc

    dprint("sqlite3 cmd: %s" % cmd)
    return DBc.execute(cmd)


def init_courses():
    global DBc
    global CourseList
    
    dprint("Initializing Disc Golf Courses ...")
    CourseList = {}
    for row in db_cmd_exec('SELECT * FROM courses'):
        course_num = row[0]
        course_name = row[1]
        dprint("Adding course[%d]: name=%s" % (course_num, course_name))
        CourseList[course_num] = Course(course_num, course_name)


def init_players():
    global DBc
    global PlayerList

    dprint("Initializing Disc Golf Players ...")
    PlayerList = {}
    for row in db_cmd_exec('SELECT * FROM players'):
        (player_num, player_name, player_full_name) = row[0:3]
        dprint("Adding player[%d]: name=%s full_name=%s" % (player_num,
                                                            player_name,
                                                            player_full_name))
        PlayerList[player_num] = Player(player_num,
                                        player_name,
                                        player_full_name)


def init_rounds():
    global DBc
    global RoundList
    global RoundDetailList
    global RoundNumberMax

    dprint("Initializing Disc Golf Rounds ...")
    RoundList = {}
    RoundNumberMax = 0
    for row in db_cmd_exec('SELECT * FROM rounds'):
        (round_num, course_num, rdate) = row[0:3]
        dprint("Adding round[%d]: course_num=%s, rnd_date=%s" % \
               (round_num, course_num, rdate))
        RoundList[round_num] = Round(round_num, course_num, rdate)
        if round_num > RoundNumberMax:
            RoundNumberMax = round_num
    dprint("Initializing Disc Golf Round Details ...")
    RoundDetailList = []
    for row in db_cmd_exec('SELECT * from round_details'):
        (round_num, player_num, fscore, bscore, acnt, ecnt, score) = row[0:7]
        dprint("Adding round detail: " +
               "rnd_num=%s, p_num=%s, " % (round_num, player_num) +
               "fscore=%s, bscore=%s, " % (fscore, bscore) +
               "a/e-cnt=%s/%s, score=%s" % (acnt, ecnt, score))
        rd = RoundDetail(round_num, player_num, fscore, bscore,
                         acnt, ecnt, score)
        RoundDetailList.append(rd)
        dprint("Added:", rd)
    dprint("Round Number max seen: %d" % RoundNumberMax)


def init_db():
    '''Initialize the DG Database'''

    global DBConn
    global DBc

    dprint("Initializing the Database (%s) ..." % DB_PATH)
    DBConn = sqlite3.connect(DB_PATH)
    DBc = DBConn.cursor()
    # now read our DB tables into Python objects
    init_courses()
    init_players()
    init_rounds()


def commit_db():
    '''Commit the Database'''
    dprint("Commiting the database ...")
    DBConn.commit()


def next_round_num():
    global RoundNumberMax

    RoundNumberMax += 1
    return RoundNumberMax


def add_round(rnd, rd_list):
    '''Add the specified round and list of round details to the DB'''
    dprint("Adding to DB:", rnd)
    for rd in rd_list:
        dprint(rd)
    db_cmd_exec('''INSERT INTO rounds(course_num, rdate)
                   VALUES(%d,"%s")''' % \
                (rnd.course_num, rnd.rdate.strftime("%m/%d/%Y")))
    for rd in rd_list:
        db_cmd_exec('''INSERT INTO round_details
                       VALUES(%d,%d,%d,%d,%d,%d,%f)''' % \
                    (rd.round_num, rd.player_num,
                     rd.fscore, rd.bscore,
                     rd.acnt, rd.ecnt,
                     rd.calc_score))


def modify_round(rnd, rd_list):
    '''Modify the specified round and list of round details in the DB'''
    dprint("Adding to DB:", rnd)
    for rd in rd_list:
        dprint(rd)
    for rd in rd_list:
        dprint("Trying to update DB for:", rd)
        db_cmd_exec('''UPDATE round_details
                       SET fscore=%d,bscore=%d,
                           acnt=%d,ecnt=%d,
                           calc_score=%f
                       WHERE round_num=%d AND player_num=%d''' % \
                    (rd.fscore, rd.bscore,
                     rd.acnt, rd.ecnt,
                     rd.calc_score,
                     rd.round_num, rd.player_num))

def round_details_equal(rd_list1, rd_list2):
    dprint("comparing two round detail lists ...")
    for rd in rd_list1:
        dprint("rd_list1[]:", rd)
    for rd in rd_list2:
        dprint("rd_list2[]:", rd)
    rd_list1 = sorted(rd_list1, key=lambda rd: rd.player_num)
    rd_list2 = sorted(rd_list2, key=lambda rd: rd.player_num)
    if len(rd_list1) != len(rd_list2):
        dprint("lists have different lengths")
        return False
    idx = 0
    max = len(rd_list1)
    while idx < max:
        rd1 = rd_list1[idx]
        rd2 = rd_list2[idx]
        dprint("Comparing:", rd1)
        dprint("With:     ", rd2)
        if rd1 != rd2:
            dprint("items unequal", rd1, ", ", rd2)
            return False
        idx += 1
    dprint("Item lists equals!")
    return True
