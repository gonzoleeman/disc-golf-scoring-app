#!/usr/bin/python
'''
Python ride database class

TO DO:
    - throw exception of we write over a hole on a course
'''

__version__ = "1.0"
__author__ = "Lee Duncan"


from utils import dprint
from opts import opts


__DB_MODIFIED__ = False


class DiscGolfHole:
    '''
    Represents one hole on one Disc Golf Course
    '''
    def __init__(self, hnum, hpar, hlen=None, hdesc=None):
        self.hnum = hnum
        self.hpar = hpar
        self.hlen = hlen
        self.hdesc = hdesc

    def __str__(self):
        fstr = "Hole %d: par=%d" % (self.hnum, self.hpar)
        if self.hlen:
            fstr += ", len=%d" % self.hlen
        if self.hdesc:
            fstr += ", desc=\"%s\"" % self.hdesc
        return fstr


class DiscGolfCourse:
    '''
    Each one of these represents a Disc Golf Course IRW
    (In the Real World)
    '''
    def __init__(self, cname, loc=None, desc=None):
        self.cname = cname
        self.loc = loc
        self.desc = desc
        self.holes = {}
        self.course_no = -1

    def __str__(self):
        fstr = "Course: %s" % self.cname
        if self.loc:
            fstr += ", Loc: %s" % self.loc
        if self.desc:
            fstr += ", Desc: %s" % self.desc
        return fstr

    def AddHole(self,  hnum, hpar, hlen=None, hdesc=None):
        '''
        Convenience method to add a new hole
        '''
        self.holes[hnum] = DiscGolfHole(hnum, hpar, hlen, hdesc)

    def GetCoursePar(self):
        ttl_par = 0
        for ch in self.holes:
            ttl_par += self.holes[ch].hpar
        return ttl_par

    def NumHoles(self):
        return len(self.holes)


DiscGolfCourseList = []

DiscGolfCourseListModified = False

def AddDiscGolfCourse(*args, **kwargs):
    '''
    Add a Disc Golf Course
    '''
    course = DiscGolfCourse(*args, **kwargs)
    DiscGolfCourseList.append(course)
    dprint("Creating DB Course ...")
    return course
    

def InitDB():
    '''
    Initialized the Database
    '''

    #
    # fake out some data for our courses
    #

    c = AddDiscGolfCourse("Pat's House", loc="Near Corvallis",
                          desc="Lot's of Cow Poo")
    c.AddHole(1, 3,
              hdesc="From water trough to bucket on barn wall, over garage")
    c.AddHole(2, 2, hdesc="From big tree to corner of yard, under branches")
    c.AddHole(3, 3, hdesc="Short corner-to-corner along road fence, easy 3")
    c.AddHole(4, 3, hdesc="Long, over the garden throw, Garden OB")

    c = AddDiscGolfCourse("Dick's House", loc="Near Corvallis",
                          desc="Can be wet, is mostly flat")
    c.AddHole(1, 3, hdesc="Over hedge, from garage to front corner")
    c.AddHole(2, 2, hdesc="From corner to near driveway")
    c.AddHole(3, 3, hdesc="From driveway to far front corner")
    c.AddHole(4, 3, hdesc="From far front corner to front of driveway")
    c.AddHole(5, 3, hdesc="Can't remember this hole!")
