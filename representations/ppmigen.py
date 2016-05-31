import numpy as np
import ioutils as util
from argparse import ArgumentParser

from representations.representation_factory import create_representation
from scipy.sparse import coo_matrix

def make_ppmi_mat(old_mat, row_probs, col_probs, smooth, neg=1, normalize=False):
    prob_norm = old_mat.sum() + (old_mat.shape[0] * old_mat.shape[1]) * smooth
    old_mat = old_mat.tocoo()
    row_d = old_mat.row
    col_d = old_mat.col
    data_d = old_mat.data
    neg = np.log(neg)
    for i in xrange(len(old_mat.data)):
        if data_d[i] == 0.0:
            continue
        joint_prob = (data_d[i] + smooth) / prob_norm
        denom = row_probs[row_d[i], 0] * col_probs[0, col_d[i]]
        if denom == 0.0:
            data_d[i] = 0
            continue
        data_d[i] = np.log(joint_prob /  denom)
        data_d[i] = max(data_d[i] - neg, 0)
        if normalize:
            data_d[i] /= -1*np.log(joint_prob)
    return coo_matrix((data_d, (row_d, col_d)))

def run(count_path, out_path, smooth=0, cds=True, normalize=False, neg=1):
    counts = create_representation("Explicit", count_path, normalize=False)
    old_mat = counts.m
    index = counts.wi
    smooth = old_mat.sum() * smooth

    # getting marginal probs
    row_probs = old_mat.sum(1) + smooth
    col_probs = old_mat.sum(0) + smooth
    if cds:
        col_probs = np.power(col_probs, 0.75)
    row_probs = row_probs / row_probs.sum()
    col_probs = col_probs / col_probs.sum()

    # building PPMI matrix
    ppmi_mat = make_ppmi_mat(old_mat, row_probs, col_probs, smooth, neg=neg, normalize=normalize)
    import pyximport
    pyximport.install(setup_args={"include_dirs": np.get_include()})
    from representations import sparse_io
    sparse_io.export_mat_eff(ppmi_mat.row, ppmi_mat.col, ppmi_mat.data, out_path + ".bin")
    util.write_pickle(index, out_path + "-index.pkl")

if __name__ == "__main__":
    parser = ArgumentParser("Generates PPMI matrix from count matrix")
    parser.add_argument("count_path", help="Path to count matrix.")
    parser.add_argument("out_path", help="Output path prefix (no extension)")
    parser.add_argument("--cds", action='store_true', help="Whether to use context distribution scaling")
    parser.add_argument("--neg", type=int, help="Number of negative samples to substract.", default=1)
    parser.add_argument("--smooth", type=int, help="Laplace smoothing factor (as relative frequency for joint events.)", default=0)
    parser.add_argument("--normalize", action='store_true', help="Whether to normalize PPMI values by inverse log-prob")
    args = parser.parse_args()
    run(args.count_path, args.out_path, args.smooth, args.cds, args.normalize, args.neg)

