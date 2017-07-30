from representations.sequentialembedding import SequentialEmbedding

"""
Let's examine the closest neighbors for a word over time
"""

import collections
from sklearn.manifold import TSNE


import numpy as np
import matplotlib.pyplot as plt

# this is based on embedding.py get_time_sims
def get_time_sims(self, word1):
    time_sims = collections.OrderedDict()
    lookups = {}
    nearests = {}
    sims = {}
    for year, embed in self.embeds.iteritems():
        nearest = []
        nearests["%s|%s" % (word1, year)]= nearest
        time_sims[year] = []

        for sim, word in embed.closest(word1, n=20):
            ww = "%s|%s" % (word, year)
            nearest.append((sim, ww))
            if sim > 0.35:
                time_sims[year].append((sim, ww))
                lookups[ww] = embed.represent(word)
                sims[ww] = sim

    return time_sims, lookups, nearests, sims

def get_cmap(n, name='Greys'):
    return plt.cm.get_cmap(name, n)

word1 = "gay"
# TODO: color the words based on the decade, instead of appending to the word
if __name__ == "__main__":
    fiction_embeddings = SequentialEmbedding.load("embeddings/eng-all_sgns", range(1900, 2000, 10))
    time_sims, lookups, nearests, sims = get_time_sims(fiction_embeddings, word1)

    words = []
    meanings = []
    for word in lookups.keys():
        if word.split("|")[0] != word1:
            words.append(word)
        else:
            meanings.append(word)

    values = [ lookups[word] for word in words ]
    mat = np.array(values)
    model = TSNE(n_components=2, random_state=None, learning_rate=150, early_exaggeration=1)
    fitted = model.fit_transform(mat)

    # TODO: remove this and just set the plot axes directly
    plt.scatter(fitted[:,0], fitted[:,1], alpha=0)

    annotations = []
    positions = {}

    cmap = get_cmap(len(meanings))
    # plot the word meanings without our destination word
    # make sure to record every word's position
    for i in xrange(len(words)):
        pt = fitted[i] 
        positions[words[i]] = pt

        ww,decade = [w.strip() for w in words[i].split("|")]
        color = cmap((int(decade) - 1900) / 10)
        word = ww
        if ww == word1:
            annotations.append((ww, decade, pt))
            word = words[i]
            color = 'black'

        sizing = sims[words[i]] * 30
        print "SIZING", sizing

        plt.text(pt[0], pt[1], word, color=color, size=int(sizing))

    import math
    # TODO: we don't have a model.transform, so lets use nearest neighbors!
    for m in meanings:
        px = 0
        py = 0
        wt = 0
        for word in meanings:
            neighbors = nearests[word]
            for sim, n in nearests[word]:
                if n not in positions:
                    continue

                pt = positions[n]
                px += 4 * sim * pt[0]
                py += 4 * sim * pt[1]
                wt += 4 * sim

            ww,decade = [w.strip() for w in word.split("|")]
            color = cmap((int(decade) - 1900) / 10)
#            annotations.append((ww,decade,(px/wt, py/wt)))
#            plt.text(px / wt, py / wt, word, color=color)

    if annotations:
        annotations.sort(key=lambda w: w[1], reverse=True)
        prev = annotations[0][-1]
        for ww, decade, ann in annotations[1:]:
            plt.annotate('', xy=prev, xytext=ann, 
                arrowprops=dict(facecolor='blue', shrink=0.1, alpha=0.3,width=2, headwidth=15))
            print prev, ann
            prev = ann

    plt.show()
    for year, sim in time_sims.iteritems():
        print year, sim

