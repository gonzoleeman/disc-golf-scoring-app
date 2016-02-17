#!/usr/bin/python
'''
Python module to calculate score for a round
'''

__version__ = "1.0"
__author__ = "Lee Duncan"

from utils import dprint
from opts import opts
from myfraction import MyFraction

ROUND_SCORES = [9, 6, 3, 2, 1]
OVERALL_SCORES = [15, 10, 5, 3, 2]

def score_round(rd_list):
    '''
    Given a list of round detail objects, RETURN an updated round
    detail object list with scores filled in for the front9 round, the
    back9 round, andthe overall
    '''
    dprint("score_round: *** ENTERING ***")

    # get sorted round lists
    front_list = sorted(rd_list, key=lambda rd: rd.fscore)
    front_score_list = sorted([rd.fscore for rd in front_list])
    front_score_results = calculate_score(front_score_list, ROUND_SCORES)

    # fill in front_list with front-9 totals
    back_list = sorted(rd_list, key=lambda rd: rd.bscore)
    back_score_list = sorted([rd.bscore for rd in back_list])
    back_score_results = calculate_score(back_score_list, ROUND_SCORES)

    # fill in back_list with back-9 totals
    ttl_list = sorted(rd_list, key=lambda rd: rd.Overall())
    ttl_score_list = sorted([rd.Overall() for rd in ttl_list])
    ttl_score_results = calculate_score(ttl_score_list, OVERALL_SCORES)

    # fill in ttl_list with overall totals by adding all 3 lists
    dprint("score_round: *** 3-way Merge ***")
    for rd in rd_list:
        dprint("Scoring for:", rd)
        idx = 0
        for frd in front_list:
            dprint("Comparing against front round (idx=%d):" % idx, frd)
            if rd == frd:
                break
            idx += 1
        # assume there *will* be a match
        rd.SetFrontCalcScore(front_score_results[idx])
        idx = 0
        for brd in back_list:
            dprint("Comparing against back round (idx=%d):" % idx, brd)
            if rd == brd:
                break
            idx += 1
        rd.SetBackCalcScore(back_score_results[idx])
        idx = 0
        for trd in ttl_list:
            dprint("Comparing against ttl (idx=%d):" % idx, trd)
            if rd == trd:
                break
            idx += 1
        rd.SetOverallCalcScore(ttl_score_results[idx])

    return rd_list


def calculate_score(score_list, score_values):
    '''
    Calculate scores for a list of scores and a list of
    values for those scores, both sorted in the same order.
    Either list can be shorter, i.e. you may have more
    positions than players, or more players than positions.
    Both input lists contain integers.

    Return a list of fractions that repesent the scores for
    each player, in the order of the score_list[] supplied.
    '''
    dprint("calculate_scores: score list:", score_list)
    dprint("                score_values:", score_values)
    scores_seen = {}
    for s in score_list:
        if not s in scores_seen.keys():
            scores_seen[s] = 0
        scores_seen[s] += 1
    dprint("scores seen:", scores_seen)
    # time to do actual scoring -- start at place "1", and go until
    # we run out of places (5 of them) or score details (not enough
    # players)
    dprint("calculate_score: *** SCORING ***")
    results = []
    idx = 0
    for score_val in sorted(scores_seen.keys()):
        dprint("calculate_score: score_val:", score_val)
        num_at_place = scores_seen[score_val]
        dprint("calculate_score: num_at_place:", num_at_place)
        dprint("Looking at score=%d,cnt=%s at place: %d" % \
               (score_val, num_at_place, (idx + 1)))
        if num_at_place == 1:
            if idx < len(score_values):
                # there are points for this finish
                val = MyFraction(score_values[idx])
            else:
                # this finish is out of the points
                val = MyFraction()
            dprint("No tie for this position: score=%s" % val)
        else:
            dprint("%d-way tie" % num_at_place)
            val = MyFraction()
            for plc_idx in range(num_at_place):
                new_idx = idx + plc_idx
                dprint("idx=%d + plc_idx=%d = %d" % (idx, plc_idx, new_idx))
                if new_idx < len(score_values):
                    val += score_values[new_idx]
            dprint("ttl pts=%s" % val)
        score_each = MyFraction(val, num_at_place)
        for plc_idx in range(num_at_place):
            dprint("Appending result[]: %s" % score_each)
            results.append(score_each)
        idx += num_at_place

    dprint("returning results:", results)
    return results
