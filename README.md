# disc-golf-scoring-app

# GENERAL

This Python program makes keeping track of disc golf
scoring easy!

It uses the Corn Valley Disc Golf socring System, which
is gives each player a score for the front 9, a score
for the back 9, and an overall score. This means that
each player gets a score that has 3 parts for each time
they play a "round" of disc golf.

# Scoring

The score is done thusly:

Scores for placing in the front or back 9:

	First place:	 9
	Second place:	 6
	Third place:	 3
	Fourth palce:	 2
	Fifth place:	 1

The scoring for the overall score is:

	First place:	15
	Second place:	10
	Third place:	 5
	Fourth palce:	 3
	Fifth place:	 2

This means that if a placer wins the front 9 and
the back 9, and hence the overall as well, they
will get 33 points (9+9+15).
\
In addition, Aces, Eagles, and Ace-Eagles are counted.

# Money

Also accounted for is 2 or 3 money rounds. (*more on this
later*)

# Prerequsites

If you'd like to use this stuff, you need a database. I
used sqlite3. Also used are the wxPython widgets, and
Python 2.7.

# Getting Started

To get started, you need to pre-load the database.

Use the devel/init_disc_golf_db.py script.
