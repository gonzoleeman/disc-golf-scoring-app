#!/usr/bin/python
"""
My own Fraction Class -- Like Fraction(), but smart enough to
know that '4/3' is really '1 1/3'
"""

import fractions
import sys
import os


class MyFraction(fractions.Fraction):
    """Like a Fraction, but can print out more rationally (LOL)"""
    def __init__(self, numerator=0, denominator=1):
        super(MyFraction, self).__init__(numerator, denominator)

    def __str__(self):
        if self.numerator < self.denominator:
            return super(MyFraction, self).__str__()
        whole_number = self.numerator / self.denominator
        numerator = self.numerator - (whole_number * self.denominator)
        if numerator == 0:
            return "%d" % whole_number
        return "%d %d/%d" % (whole_number, numerator, self.denominator)

    def __repr__(self):
        return 'MyFraction(%d, %d)' % (self.numerator, self.denominator)

    def __add__(self, other):
        res = super(MyFraction, self).__add__(other)
        return MyFraction(res.numerator, res.denominator)

    def __sub__(self, other):
        res = super(MyFraction, self).__sub__(other)
        return MyFraction(res.numerator, res.denominator)

    def __mul__(self, other):
        res = super(MyFraction, self).__mul__(other)
        return MyFraction(res.numerator, res.denominator)

    def __div__(self, other):
        res = super(MyFraction, self).__div__(other)
        return MyFraction(res.numerator, res.denominator)

    def __neg__(self):
        return MyFraction(-self.numerator, self.denominator)


