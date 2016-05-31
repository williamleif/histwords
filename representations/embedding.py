import heapq

import numpy as np
from sklearn import preprocessing

from util import load_pickle, lines

class Embedding:
    """
    Base class for all embeddings. SGNS can be directly instantiated with it.
    """

    def __init__(self, vecs, vocab, normalize=True, **kwargs):
        self.m = vecs
        self.dim = self.m.shape[1]
        self.iw = vocab
        self.wi = {w:i for i,w in enumerate(self.iw)}
        if normalize:
            self.normalize()

    def __getitem__(self, key):
        if self.oov(key):
            raise KeyError
        else:
            return self.represent(key)

    def __iter__(self):
        return self.iw.__iter__()

    def __contains__(self, key):
        return not self.oov(key)

    @classmethod
    def load(cls, path, normalize=True, add_context=True, **kwargs):
        mat = np.load(path + "-w.npy")
        if add_context:
            mat += np.load(path + "-c.npy")
        iw = load_pickle(path + "-vocab.pkl")
        return cls(mat, iw, normalize) 

    def get_subembed(self, word_list, **kwargs):
        word_list = [word for word in word_list if not self.oov(word)]
        keep_indices = [self.wi[word] for word in word_list]
        return Embedding(self.m[keep_indices, :], word_list, normalize=False)

    def reindex(self, word_list, **kwargs):
        new_mat = np.empty((len(word_list), self.m.shape[1]))
        valid_words = set(self.iw)
        for i, word in enumerate(word_list):
            if word in valid_words:
                new_mat[i, :] = self.represent(word)
            else:
                new_mat[i, :] = 0 
        return Embedding(new_mat, word_list, normalize=False)

    def get_neighbourhood_embed(self, w, n=1000):
        neighbours = self.closest(w, n=n)
        keep_indices = [self.wi[neighbour] for _, neighbour in neighbours] 
        new_mat = self.m[keep_indices, :]
        return Embedding(new_mat, [neighbour for _, neighbour in neighbours]) 

    def normalize(self):
        preprocessing.normalize(self.m, copy=False)

    def oov(self, w):
        return not (w in self.wi)

    def represent(self, w):
        if w in self.wi:
            return self.m[self.wi[w], :]
        else:
            print "OOV: ", w
            return np.zeros(self.dim)

    def similarity(self, w1, w2):
        """
        Assumes the vectors have been normalized.
        """
        sim = self.represent(w1).dot(self.represent(w2))
        return sim

    def closest(self, w, n=10):
        """
        Assumes the vectors have been normalized.
        """
        scores = self.m.dot(self.represent(w))
        return heapq.nlargest(n, zip(scores, self.iw))
    

class SVDEmbedding(Embedding):
    """
    SVD embeddings.
    Enables controlling the weighted exponent of the eigenvalue matrix (eig).
    Context embeddings can be created with "transpose".
    """
    
    def __init__(self, path, normalize=True, eig=0.0, **kwargs):
        ut = np.load(path + '-u.npy')
        s = np.load(path + '-s.npy')
        vocabfile = path + '-vocab.pkl'
        self.iw = load_pickle(vocabfile)
        self.wi = {w:i for i, w in enumerate(self.iw)}
 
        if eig == 0.0:
            self.m = ut
        elif eig == 1.0:
            self.m = s * ut
        else:
            self.m = np.power(s, eig) * ut

        self.dim = self.m.shape[1]

        if normalize:
            self.normalize()

class GigaEmbedding(Embedding):
    def __init__(self, path, words, dim=300, normalize=True, **kwargs):
        seen = []
        vs = {}
        for line in lines(path):
            split = line.split()
            w = split[0]
            if w in words:
                seen.append(w)
                vs[w] = np.array(map(float, split[1:]), dtype='float32')
        self.iw = seen
        self.wi = {w:i for i,w in enumerate(self.iw)}
        self.m = np.vstack(vs[w] for w in self.iw)
        if normalize:
            self.normalize()


