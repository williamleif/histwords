import heapq

import numpy as np
from sklearn import preprocessing

from ioutils import load_pickle

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
    
    def __init__(self, path, normalize=True, eig=0.0, transpose=False, **kwargs):
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
