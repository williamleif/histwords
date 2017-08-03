import helpers
import sys


"""
Let's examine the closest neighbors for a word over time
"""

import numpy as np
import matplotlib.pyplot as plt


# We accept a list of words from command line
# to generate graphs for.

WORDS = helpers.get_words()


if __name__ == "__main__":
    embeddings = helpers.load_embeddings()
    all_lookups = {}
    all_sims = {}
    WORDS.sort()
    wordchain = "_".join(WORDS)

    helpers.clear_figure()
    for word1 in WORDS:
        time_sims, lookups, nearests, sims = helpers.get_time_sims(embeddings, word1)

        all_lookups.update(lookups)
        all_sims.update(sims)




    words = all_lookups.keys()
    values = [ all_lookups[word] for word in words ]
    fitted = helpers.fit_tsne(values)

    # draw the words onto the graph
    cmap = helpers.get_cmap(len(time_sims))

    # TODO: split the annotations up
    annotations = helpers.plot_words(WORDS, words, fitted, cmap, all_sims)
    if annotations:
        helpers.plot_annotations(annotations)

    helpers.savefig("%s_chain.png" % wordchain)


