#!/usr/bin/python
"""
My own money class :(
"""

from opts import opts
from utils import dprint


__author__ = 'Lee Duncan'
__version__ = '1.0'



MONEY_STR_WIDTH=5


class Money:
    def __init__(self, dollars=0, cents=0):
        d = int(dollars)
        c = int(cents)
        if (d < 0 and c > 0) or (d > 0 and c < 0):
            #dprint("c:", c)
            #dprint("d:", d)
            raise Exception("Signs of Dollars and Cents must match")
        while c >= 100:
            #dprint("moving plus cents to plus dollars")
            d += 1
            c -= 100
        while c <= -100:
            #dprint("moving minus cents to plus dollars")
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
        return "%d.%02d" % (self.dollars, self.cents)

    def __cmp__(self, other):
        return self.AsCents() - other.AsCents()

    def AsCents(self):
        return (100 * self.dollars) + self.cents

    def IsZero(self):
        return self.dollars == 0 and self.cents == 0



def money_from_string(money_str):
    if money_str[0] == '$':
        money_str = money_str[1:]
        #dprint("Stripped dollar sign from front of amount:", money_str)
    if '.' in money_str:
        (d_str, c_str) = money_str.split('.')
    else:
        # assume we have only dollars
        d_str = money_str
        c_str = '0'
    d = int(d_str) if len(d_str) else 0
    c = int(c_str) if len(c_str) else 0
    res = Money(d, c)
    dprint("Money string '%s' -> $%s" % (money_str, res))
    return res

def money_to_string(m):
    money_str_fmt = '$%%%ds' % MONEY_STR_WIDTH
    res = money_str_fmt % m
    dprint("Money '%s' to Money String '%s'" % (m, res))
    return res
