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
from myfraction import MyFraction

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
                 acnt=0, ecnt=0, aecnt=0,
                 calc_fscore=None, calc_bscore=None, calc_oscore=None):
        self.round_num = int(rnum)
        self.player_num = int(pnum)
        # these are the round score: front and back
        # (we allow these to be "None", meaning "not yet filled in")
        self.fscore = fscore
        self.bscore = bscore
        # ace, eagle, and ace-eagle counts
        self.acnt = acnt
        self.ecnt = ecnt
        self.aecnt = aecnt
        # CALCULATED fractional scores for front, back, and overall
        self.calc_fscore = MyFraction() if calc_fscore is None else calc_fscore
        self.calc_bscore = MyFraction() if calc_bscore is None else calc_bscore
        self.calc_oscore = MyFraction() if calc_oscore is None else calc_oscore

    def __cmp__(self, other):
        if self.round_num != other.round_num:
            dprint("compare round detail: round_num NOT EQUAL")
            return self.round_num - other.round_num
        if self.player_num != other.player_num:
            dprint("compare round detail: player_num NOT EQUAL")
            return self.player_num - other.player_num
        for fname in ['fscore', 'bscore']:
            s = getattr(self, fname)
            o = getattr(other, fname)
            if s != o:
                if s is None:
                    dprint("compare round detail: self.%s is None" % fname)
                    return o
                if o is None:
                    dprint("compare round detail: other.%s is None" % fname )
                    return s
                dprint("compare round detail: %s NOT EQUAL" % fname)
                return s - o
        for fname in ['acnt', 'ecnt', 'aecnt']:
            s = getattr(self, fname)
            o = getattr(other, fname)
            if s != o:
                dprint("compare round detail: %s NOT EQUAL" % fname)
                return s - o
        for fname in ['calc_fscore', 'calc_bscore', 'calc_oscore']:
            s = getattr(self, fname)
            o = getattr(other, fname)
            if s > o:
                dprint("compare round detail: %s (s>o) NOT EQUAL" % fname)
                return 1
            if s < o:
                dprint("compare round detail: %s (s<o) NOT EQUAL" % fname)
                return -1
        dprint("compare round detail: *** EQUAL ***")
        return 0

    def SetScore(self, fscore, bscore):
        self.fscore = int(fscore)
        self.bscore = int(bscore)

    def SetCounts(self, acnt, ecnt, aecnt):
        self.acnt = acnt
        self.ecnt = ecnt
        self.aecnt = aecnt

    def Overall(self):
        '''Return overall, assuming round has been scored'''
        if self.fscore is None or self.bscore is None:
            return None
        return self.fscore + self.bscore

    def CalcScore(self):
        '''The Total score: front+back+overall'''
        res = self.calc_fscore + self.calc_bscore + self.calc_oscore
        dprint("returning %s + %s + %s = %s" % \
               (self.calc_fscore, self.calc_bscore, self.calc_oscore, res))
        return res

    def CalcFrontScore(self):
        return self.calc_fscore

    def CalcBackScore(self):
        return self.calc_bscore

    def CalcOverallScore(self):
        return self.calc_oscore

    def SetFrontCalcScore(self, score):
        self.calc_fscore = score
        dprint("Set front score to %s" % score)

    def SetBackCalcScore(self, score):
        self.calc_bscore = score
        dprint("Set back score to %s" % score)

    def SetOverallCalcScore(self, score):
        self.calc_oscore = score
        dprint("Set overall score to %s" % score)

    def __str__(self):
        return "RoundDetail[]: round_num=%d, " % self.round_num + \
               "player_num=%d, fscore=%s, bscore=%s, " % \
               (self.player_num, self.fscore, self.bscore) + \
               "a/e/ae=%d/%d/%d => %s|%s|%s" % \
               (self.acnt, self.ecnt, self.aecnt,
                self.calc_fscore, self.calc_bscore, self.calc_oscore)

class SearchResult:
    '''
    Used to gather data about how each player did over a period of time.
    
    i.e. this is what each entry in the search results looks like
    '''
    def __init__(self, pnum):
        dprint("Creating empty Search Result for pnum=%d" % pnum)
        self.pnum = pnum
        self.rnd_cnt = 0
        self.front_pts = MyFraction()
        self.back_pts = MyFraction()
        self.overall_pts = MyFraction()
        self.acnt = 0
        self.ecnt = 0
        self.aecnt = 0
        self.rounds_won = 0
        self.overalls_won = 0

    def TotalPoints(self):
        return self.front_pts + self.back_pts + self.overall_pts

    def AddResults(self, rd):
        dprint("Adding in results for pnum=%d:" % self.pnum, rd)
        if self.pnum != rd.player_num:
            raise Exception("Internal Error: Player Number Mismatch")
        self.rnd_cnt += 1
        self.front_pts += rd.calc_fscore
        self.back_pts += rd.calc_fscore
        self.overall_pts += rd.calc_oscore
        self.acnt += rd.acnt
        self.ecnt += rd.ecnt
        self.aecnt += rd.aecnt
        f9_won = (rd.calc_fscore == MyFraction(9))
        b9_won = (rd.calc_bscore == MyFraction(9))
        if f9_won and b9_won:
            self.rounds_won += 2
            self.overalls_won += 1
        elif f9_won or b9_won:
            self.rounds_won += 1

    def PointsPerRound(self):
        return self.TotalPoints() / self.rnd_cnt

    def __str__(self):
        return "SearchResult[pnum=%d]: rnd_cnt=%d, front/rear/overall-pts=%s/%s/%s, a/e/ae=%d/%d/%d" % \
               (self.pnum, self.rnd_cnt,
                self.front_pts, self.back_pts, self.overall_pts,
                self.acnt, self.ecnt, self.aecnt)


DB_DIR = 'db'
DB_FILE = 'disc_golf.db'
DB_PATH = "%s/%s" % (DB_DIR, DB_FILE)

# our internal representation of a database, using dictionaries
CourseList = {}
PlayerList = {}
RoundList = {}
# the detail list is not indexed by a number, so it's an array
RoundDetailList = []

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


def get_max_round_no():
    global RoundList

    # try it an alternative way
    rnd_nos = [rnd.num for rnd in RoundList.itervalues()]
    max_rnd_no = max(rnd_nos)
    dprint("Max Round No: %d" % max_rnd_no)
    return max_rnd_no


def init_rounds():
    global DBc
    global RoundList
    global RoundDetailList

    dprint("Initializing Disc Golf Rounds ...")
    RoundList = {}
    for row in db_cmd_exec('SELECT * FROM rounds'):
        (round_num, course_num, rdate) = row[0:3]
        dprint("Adding round[%d]: course_num=%s, rnd_date=%s" % \
               (round_num, course_num, rdate))
        RoundList[round_num] = Round(round_num, course_num, rdate)
    dprint("Initializing Disc Golf Round Details ...")
    RoundDetailList = []
    for row in db_cmd_exec('SELECT * from round_details'):
        (round_num, player_num,
         fscore, bscore,
         acnt, ecnt, aecnt,
         fscore_num, fscore_den,
         bscore_num, bscore_den,
         oscore_num, oscore_den) = row[0:13]
        dprint("Adding round detail: " +
               "rnd_num=%d, p_num=%d, " % (round_num, player_num) +
               "fscore=%d, bscore=%d, " % (fscore, bscore) +
               "a/e/ae=%d/%d/%d, score=%d/%d|%d/%d|%d/%d" % \
               (acnt, ecnt, aecnt,
                fscore_num, fscore_den,
                bscore_num, bscore_den,
                oscore_num, oscore_den))
        rd = RoundDetail(round_num, player_num, fscore, bscore,
                         acnt, ecnt, aecnt,
                         MyFraction(fscore_num, fscore_den),
                         MyFraction(bscore_num, bscore_den),
                         MyFraction(oscore_num, oscore_den))
        RoundDetailList.append(rd)
        dprint("Added:", rd)


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
    '''Return what the next round number will probably be'''
    return get_max_round_no() + 1


def add_round(rnd, rd_list):
    '''Add the specified round and list of round details to the DB'''
    dprint("Adding to DB:", rnd)
    for rd in rd_list:
        dprint(rd)
    db_cmd_exec('''INSERT INTO rounds(course_num, rdate)
                   VALUES(%d,"%s")''' % \
                (rnd.course_num, rnd.rdate.strftime("%m/%d/%Y")))
    for rd in rd_list:
        db_cmd_exec('''INSERT INTO round_details(round_num, player_num,
                                                 fscore, bscore,
                                                 acnt, ecnt, aecnt,
                                                 calc_fscore_numerator,
                                                 calc_fscore_denominator,
                                                 calc_bscore_numerator,
                                                 calc_bscore_denominator,
                                                 calc_oscore_numerator,
                                                 calc_oscore_denominator)
                       VALUES(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)''' % \
                    (rd.round_num, rd.player_num,
                     rd.fscore, rd.bscore,
                     rd.acnt, rd.ecnt, rd.eacnt,
                     rd.calc_fscore.numerator, rd.calc_fscore.denominator,
                     rd.calc_bscore.numerator, rd.calc_bscore.denominator,
                     rd.calc_oscore.numerator, rd.calc_oscore.denominator))


def modify_round(rnd, rd_list):
    '''Modify the specified round and list of round details in the DB'''
    dprint("Modifying in DB:", rnd)
    for rd in rd_list:
        dprint(rd)
    for rd in rd_list:
        dprint("Trying to update DB for:", rd)
        db_cmd_exec('''UPDATE round_details
                       SET fscore=%d,bscore=%d,
                           acnt=%d,ecnt=%d,aecnt=%d,
                           calc_fscore_numerator=%d,
                           calc_fscore_denominator=%d,
                           calc_bscore_numerator=%d,
                           calc_bscore_denominator=%d,
                           calc_oscore_numerator=%d,
                           calc_oscore_denominator=%d
                       WHERE round_num=%d AND player_num=%d''' % \
                    (rd.fscore, rd.bscore,
                     rd.acnt, rd.ecnt, rd.aecnt,
                     rd.calc_fscore.numerator, rd.calc_fscore.denominator,
                     rd.calc_bscore.numerator, rd.calc_bscore.denominator,
                     rd.calc_oscore.numerator, rd.calc_oscore.denominator,
                     rd.round_num, rd.player_num))

def round_details_equal(rd_list1, rd_list2):
    dprint("comparing two round detail lists with %d items;" % len(rd_list1))
    for rd in rd_list1:
        dprint("rd_list1[]:", rd)
    for rd in rd_list2:
        dprint("rd_list2[]:", rd)
    rd_list1 = sorted(rd_list1, key=lambda rd: rd.player_num)
    rd_list2 = sorted(rd_list2, key=lambda rd: rd.player_num)
    if len(rd_list1) != len(rd_list2):
        raise Exception("Internal Error: Lists have different lengths")
    idx = 0
    max = len(rd_list1)
    while idx < max:
        rd1 = rd_list1[idx]
        rd2 = rd_list2[idx]
        dprint("Comparing:", rd1)
        dprint("With:     ", rd2)
        if rd1 != rd2:
            dprint("Item lists unequal", rd1, ", ", rd2)
            return False
        idx += 1
    dprint("Item lists equals!")
    return True
