import random
import os
import argparse
import collections
from Queue import Empty 
from multiprocessing import Process, Queue
from scipy.sparse import coo_matrix
import time

import ioutils
from cooccurrence import matstore

import numpy as np
cimport numpy as np

DYTPE = np.float64
ctypedef np.float64_t DTYPE_t

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

def worker(proc_num, queue, out_dir, in_dir, smooth, conf_dir, normalize, cds, neg):
    cdef int i
    cdef np.ndarray data_d
    cdef np.ndarray row_d, col_d
    cdef float prob_norm
    print proc_num, "Start loop"
    time.sleep(200*random.random())
    while True:
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break

        print proc_num, "Making PPMIs for year", year
        # loading matrix 
        old_mat = matstore.retrieve_mat_as_coo(in_dir + str(year) + ".bin")
        old_mat = old_mat.tocsr()
        if "index.pkl" in os.listdir(in_dir):
            index = ioutils.load_pickle(in_dir + "/index.pkl")
        else:
            index = ioutils.load_pickle(in_dir + str(year) + "-index.pkl")
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
        print proc_num, "Writing counts for year", year
        matstore.export_mat_eff(ppmi_mat.row, ppmi_mat.col, ppmi_mat.data, year, out_dir)
        ioutils.write_pickle(index, out_dir + str(year) + "-index.pkl")


def run_parallel(num_procs, out_dir, in_dir, years, smooth, conf_dir, normalize, cds, neg):
    queue = Queue()
    years.reverse()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_dir, in_dir, smooth, conf_dir, normalize, cds, neg]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
