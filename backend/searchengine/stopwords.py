"""English stop-word list used by the tokenizer.

A fairly standard set of high-frequency function words. Terms here are dropped
during tokenization so they never enter the index or a query. Contractions are
listed in the apostrophe-stripped form the tokenizer produces (``don't`` -> ``dont``).
"""

STOP_WORDS: frozenset[str] = frozenset(
    """
    a about above after again against all also am an and any are as at
    be because been before being below between both but by
    can cannot could
    did do does doing done down during
    each few for from further
    had has have having he her here hers herself him himself his how
    i if in into is it its itself
    just
    me more most my myself
    no nor not now
    of off on once only or other others our ours ourselves out over own
    same she should so some such
    than that the their theirs them themselves then there these they this those
    through to too
    under until up
    very
    was we were what when where which while who whom why will with would
    you your yours yourself yourselves

    arent cant couldnt didnt doesnt dont hadnt hasnt havent hes im isnt its ive
    lets shant shes shouldnt thats theres theyd theyll theyre theyve wasnt werent
    weve whats wheres whos wont wouldnt youd youll youre youve
    """.split()
)
