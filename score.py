#!/usr/bin/python
'''
Python module to calculate score for a round
'''

__version__ = "1.0"
__author__ = "Lee Duncan"

from utils import dprint
from opts import opts

ROUND_SCORES = [9, 6, 3, 2, 1]
OVERALL_SCORES = [15, 10, 5, 3, 2]

def score_round(round_list):
    '''
    Given a list of round detail objects, return an updated round
    detail object list with scores filled in for the front9 round, the
    back9 round, andthe overall
    '''
    dprint("score_round: *** ENTERING ***")

    # get sorted round lists
    front_list = sorted(round_list, key=lambda rd: rd.fscore)
    front_score_list = sorted([rnd.fscore for rnd in front_list])
    front_score_results = calculate_score(front_score_list, ROUND_SCORES)
    # fill in front_list with front-9 totals
    back_list = sorted(round_list, key=lambda rd: rd.bscore)
    back_score_list = sorted([rnd.bscore for rnd in back_list])
    back_score_results = calculate_score(back_score_list, ROUND_SCORES)
    # fill in back_list with back-9 totals
    ttl_list = sorted(round_list, key=lambda rd: rd.Overall())
    ttl_score_list = sorted([rnd.Overall() for rnd in ttl_list])
    ttl_score_results = calculate_score(ttl_score_list, OVERALL_SCORES)
    # fill in ttl_list with overall totals

    # now add all three lists to get result
    dprint("score_round: *** 3-way Merge ***")
    for rnd in round_list:
        dprint("Scoring for:", rnd)
        idx = 0
        for frnd in front_list:
            dprint("Comparing against front round (idx=%d):" % idx, frnd)
            if rnd == frnd:
                break
            idx += 1
        # assume there *will* be a match
        rnd.score = front_score_results[idx]
        idx = 0
        for brnd in back_list:
            dprint("Comparing against back round (idx=%d):" % idx, brnd)
            if rnd == brnd:
                break
            idx += 1
        rnd.score += back_score_results[idx]
        idx = 0
        for trnd in ttl_list:
            dprint("Comparing against ttl (idx=%d):" % idx, trnd)
            if rnd == trnd:
                break
            idx += 1
        rnd.score += ttl_score_results[idx]
        dprint("Score for this round/player: %f" % rnd.score)

    #dprint("Returning overall results:", round_list)
    return round_list


def calculate_score(score_list, score_values):
    dprint("calculate_scores: score list:", score_list)
    dprint("                score_values:", score_values)
    scores_seen = {}
    for s in score_list:
        if not s in scores_seen.keys():
            scores_seen[s] = 0
        scores_seen[s] += 1
    dprint("scores seen:", scores_seen)
    #
    # time to do actual scoring -- start at place "1", and go until
    # we run out of places (5 of them) or score details (not enough
    # players)
    #
    dprint("calculate_score: *** SCORING ***")
    results = []
    idx = 0
    for k in scores_seen.iterkeys():
        dprint("Looking at place: %d" % (idx + 1))
        num_at_place = scores_seen[k]
        if num_at_place == 1:
            val = 0
            if idx < len(score_values):
                val = score_values[idx]
            dprint("No tie for this position: score=%d" % val)
        else:
            dprint("%d-way tie" % num_at_place)
            val = 0
            for plc_idx in range(num_at_place):
                new_idx = idx + plc_idx
                dprint("idx=%d + plc_idx=%d = %d" % (idx, plc_idx, new_idx))
                if new_idx < len(score_values):
                    val += score_values[new_idx]
            dprint("ttl pts=%f" % val)
        score_each = float(val) / num_at_place
        for plc_idx in range(num_at_place):
            results.append(score_each)
        idx += num_at_place

    dprint("returning results:", results)
    return results
