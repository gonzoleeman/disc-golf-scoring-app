#!/usr/bin/python
"""
My own money class :(
"""

__author__ = 'Lee Duncan'
__version__ = '1.0'


class Money:
    def __init__(self, dollars=0, cents=0):
        d = int(dollars)
        c = int(cents)
        if (d < 0 and c > 0) or (d > 0 and c < 0):
            print "DEBUG: c:", c
            print "DEBUG: d:", d
            raise Exception("Signs of Dollars and Cents must match")
        while c >= 100:
            print "moving plus cents to plus dollars"
            d += 1
            c -= 100
        while c <= -100:
            print "moving minus cents to plus dollars"
            d -= 1
            c += 100
        self.dollars = d
        self.cents = c

    def __add__(self, other):
        return Money(self.dollars + other.dollars,
                     self.cents + other.cents)

    def __mul__(self, multiplier):
        if not isinstance(multiplier, int):
            raise Exception(
                "unsupported operator types for '*': Money and (not int)")
        return Money(multiplier * self.dollars,
                     multiplier * self.cents)

    def __div__(self, divisor):
        if not isinstance(divisor, int):
            raise Exception(
                "unsupported operator types for '*': Money and (not int)")
        res_cents = self.AsCents() / divisor
        return Money(cents=res_cents)

    def __sub__(self, other):
        return Money(self.dollars - other.dollars,
                     self.cents - other.cents)

    def __neg__(self):
        return Money(-self.dollars, -self.cents)

    def __repr__(self):
        return "Money(%d,%d)" % (self.dollars, self.cents)

    def __str__(self):
        return "$%d.%02d" % (self.dollars, self.cents)

    def AsCents(self):
        return (100 * self.dollars) + self.cents



if __name__ == '__main__':
    m = Money(3,45)
    x = m * 3
