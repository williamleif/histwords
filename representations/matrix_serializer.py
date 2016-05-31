import numpy as np
import os
import ioutils as util

def load_matrix(f):
    if not f.endswith('.bin'):
        f += ".bin"
    import pyximport
    pyximport.install(setup_args={"include_dirs": np.get_include()})
    from representations import sparse_io
    return sparse_io.retrieve_mat_as_coo(f).tocsr()

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
    index = util.load_pickle(path)
    vocab = sorted(index, key = lambda word : index[word])
    iw = vocab[:mat.shape[0]]
    ic = vocab[:mat.shape[1]]
    return iw, ic
