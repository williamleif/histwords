import helpers
import sys
from representations.sequentialembedding import SequentialEmbedding

"""
Let's examine the closest neighbors for a word over time
"""

import collections
from sklearn.manifold import TSNE


import numpy as np
import matplotlib.pyplot as plt

WORDS = helpers.get_words()
if __name__ == "__main__":
    embeddings = helpers.load_embeddings()

    for word1 in WORDS:
        time_sims, lookups, nearests, sims = helpers.get_time_sims(embeddings, word1)

        helpers.clear_figure()

        # we remove word1 from our words because we just want to plot the different
        # related words
        words = filter(lambda word: word.split("|")[0] != word1, lookups.keys())

        values = [ lookups[word] for word in words ]
        fitted = helpers.fit_tsne(values)
        if not len(fitted):
            print "Couldn't model word", word1
            continue

        cmap = helpers.get_cmap(len(time_sims))
        annotations = helpers.plot_words(word1, words, fitted, cmap, sims)

        helpers.savefig("%s_shaded" % word1)
        for year, sim in time_sims.iteritems():
            print year, sim

