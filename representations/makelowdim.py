import numpy as np

from sklearn.utils.extmath import randomized_svd
import util
from representations.explicit import Explicit

def run(in_file, out_path, dim=300): 
        base_embed = Explicit.load(in_file, normalize=False)
        u, s, v = randomized_svd(base_embed.m, n_components=dim, n_iter=5)
        np.save(out_path + "-u.npy", u)
        np.save(out_path + "-v.npy", v)
        np.save(out_path + "-s.npy", s)
        util.write_pickle(base_embed.iw, out_path  + "-vocab.pkl")

if __name__ == '__main__':
    run("/lfs/madmax3/0/stock/ppmi.bin", "/lfs/madmax3/0/stock/svd-vecs")
    
