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


from utils import dprint
from opts import opts
import sqlite3

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
        self.num = rnum
        self.course_num = cnum
        self.rdate = rdate

    def __str__(self):
        return "Round[%d]: course=%d, %s" % \
               (self.num, self.course_num, self.rdate)

class RoundDetail:
    '''
    One entry for one person for one round (which is one course on one day)
    '''
    def __init__(self, rnum, pnum, fscore, bscore, acnt=0, ecnt=0):
        self.round_num = rnum
        self.player_num = pnum
        self.front_score = fscore
        self.back_score = bscore
        self.ace_cnt = acnt
        self.eagle_cnt = ecnt

    def __str__(self):
        return "Round[%d]: player=%d, score=%d/%d, a/e=%d/%d" % \
               (self.round_num, self.player_num,
                self.front_score, self.back_score,
                self.ace_cnt, self.eagle_cnt)

DB_DIR = 'db'
DB_FILE = 'disc_golf.db'
DB_PATH = "%s/%s" % (DB_DIR, DB_FILE)

CourseList = {}
PlayerList = {}
RoundList = {}
RoundDetailList = {}

#
# database routines (use a 'class'?)
#
def init_db():
    global CourseList
    global PlayerList
    global RoundList
    global RoundDetailList
    
    '''Initialize the DG Database'''
    dprint("Initializing the Database (%s) ..." % DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # now read our DB tables into Python objects
    dprint("Initializing Disc Golf Courses ...")
    for row in c.execute('''SELECT * FROM courses'''):
        course_num = row[0]
        dprint("Adding course[%d]: %s" % (course_num, row[1]))
        CourseList[course_num] = Course(course_num, row[1])
    for row in c.execute('''SELECT * FROM players'''):
        player_num = row[0]
        dprint("Adding player[%d]: %s (%s)" % (player_num, row[1], row[2]))
        PlayerList[player_num] = Player(player_num, row[1], row[2])
    for row in c.execute('''SELECT * FROM rounds'''):
        round_num =row[0]
        course_num = row[1]
        dprint("Adding round[%d]: Course=%s, %s" % \
               (round_num, course_num, row[2]))
        RoundList[round_num] = Round(player_num, course_num, row[2])
