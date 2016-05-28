import numpy as np
import os
import ioutils
from cooccurrence import matstore

def save_matrix(f, m):
    np.savez_compressed(f, data=m.data, indices=m.indices, indptr=m.indptr, shape=m.shape)

def load_matrix(f, thresh=None):
    if not f.endswith('.bin'):
        f += ".bin"
    if thresh == None:
        return matstore.retrieve_mat_as_coo(f).tocsr()
    else:
        return matstore.retrieve_mat_as_coo_thresh(f, thresh).tocsr()

def save_vocabulary(path, vocab):
    with open(path, 'w') as f:
        for w in vocab:
            print >>f, w

def load_vocabulary(mat, path):
    if os.path.isfile(path.split(".")[0] + "-index.pkl"):
        path = path.split(".")[0] + "-index.pkl"
    else:
        print "Could not find local index. Attempting to load directory wide index..."
        path = "/".join(path.split("/")[:-1]) + "/index.pkl"
    index = ioutils.load_pickle(path)
    vocab = sorted(index, key = lambda word : index[word])
    iw = vocab[:mat.shape[0]]
    ic = vocab[:mat.shape[1]]
    return iw, ic

def save_count_vocabulary(path, vocab):
    with open(path, 'w') as f:
        for w, c in vocab:
            print >>f, w, c

def load_count_vocabulary(path):
    with open(path) as f:
        # noinspection PyTypeChecker
        vocab = dict([line.strip().split() for line in f if len(line) > 0])
    return vocab
