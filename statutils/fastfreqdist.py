from nltk.probability import FreqDist, MLEProbDist
import numpy as np

class CachedFreqDist(FreqDist):
    """
    A read only version of nltk's FreqDist that caches the sample size for speed.
    DO NOT UPDATE COUNTS OF THIS OBJECT, resulting frequencies will not sum to one.
    """
    def __init__(self, freqdist):
        FreqDist.__init__(self, freqdist)
        self._N = np.sum(self.values())

    def N(self):
        return self._N

    # slightly odd nomenclature freq() if FreqDist does counts and ProbDist does probs,
    # here, freq() does probs
    def freq(self, sample):
        if self.N() == 0:
            return 0
        return float(self[sample]) / self.N()

class MultiGenMLEProbDist(MLEProbDist):
    """
    An extension of nltk's MLEProbDist that allows for fast sampling for larger sample sizes
    """

    def __init__(self, freqdist, bins=None):
        MLEProbDist.__init__(self, freqdist, bins)
        self._probarray = np.zeros((len(freqdist),))
        self._probmap = {}
        for i, item in enumerate(freqdist.keys()):
            self._probarray[i] = freqdist.freq(item)
            self._probmap[i] = item

    def generate_many(self, n):
        return {self._probmap[i]:count for i, count in 
                enumerate(np.random.multinomial(n, self._probarray)) if count != 0}
