import random
import os
import time
import argparse
from Queue import Empty
from multiprocessing import Process, Queue
from scipy.sparse import coo_matrix

import ioutils
from cooccurrence import matstore
from cooccurrence.indexing import get_full_word_list

import numpy as np 
cimport numpy as np

NAN = float('nan')
STATS = ["deg", "sum", "bclust", "wclust"]

def compute_word_stats(mat, word, word_index, index_set = None, stats=STATS):
    if not word in word_index:
        return {stat:NAN for stat in stats}
    word_i = word_index[word] 
    if index_set != None and not word_i in index_set:
        return {stat:NAN for stat in stats}
    if word_i >= mat.shape[0]: 
        return {stat:NAN for stat in stats}
    vec = mat[word_i, :]
    indices = vec.nonzero()[1]
    vec = vec[:, indices]
    # only compute clustering if we have too..
    if "bclust" in stats or "wclust" in stats:
        if len(indices) >= 2:
            weights = vec/vec.sum()
            reduced = mat[indices, :]
            reduced = reduced[:, indices]
            reduced.eliminate_zeros()
            weighted = (weights * reduced).sum() / (float(len(indices)) - 1)
            binary = float(reduced.nnz) / (len(indices) * (len(indices) - 1)) 
        else:
            weighted = binary = 0
    deg = len(indices)
    sum = vec.sum()
    vals = {}
    if "deg" in stats:
        vals["deg"] = deg
    if "sum" in stats:
        vals["sum"] = sum
    if "bclust" in stats:
         vals["bclust"] = binary
    if "wclust" in stats:
         vals["wclust"] = weighted
    return vals

def get_year_stats(mat, year_index, word_list, index_set=None, stats=STATS):
    mat.setdiag(0)
    mat = mat.tocsr()
    year_stats = {stat:{} for stat in stats}
    for i, word in enumerate(word_list):
        single_word_stats = compute_word_stats(mat, word, year_index, index_set=index_set, stats=["sum", "deg", "bclust", "wclust"])
        if i % 1000 == 0:
            print "Done ", i
        for stat in single_word_stats:
            year_stats[stat][word] = single_word_stats[stat]
    return year_stats

def merge(out_pref, years, full_word_list):
    merged_word_stats = {}
    for stat in STATS:
        merged_word_stats[stat] = {}
        for word in full_word_list:
            merged_word_stats[stat][word] = {}
    for year in years:
        year_stats = ioutils.load_pickle(out_pref + str(year) + "-tmp.pkl")
        for stat, stat_vals in year_stats.iteritems():
            for word in full_word_list:
                if not word in stat_vals:
                    merged_word_stats[stat][word][year] = NAN
                else:
                    merged_word_stats[stat][word][year] = stat_vals[word]
        os.remove(out_pref + str(year) + "-tmp.pkl")
    ioutils.write_pickle(merged_word_stats, out_pref +  ".pkl")

def worker(proc_num, queue, out_pref, in_dir, year_index_infos, thresh):
    print proc_num, "Start loop"
    time.sleep(10 * random.random())
    while True:
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break

        print proc_num, "Retrieving mat for year", year
        if thresh != None:
            mat = matstore.retrieve_mat_as_coo_thresh(in_dir + str(year) + ".bin", thresh)
        else:
            mat = matstore.retrieve_mat_as_coo(in_dir + str(year) + ".bin", min_size=5000000)
        print proc_num, "Getting stats for year", year
        year_stats = get_year_stats(mat, year_index_infos[year]["index"], year_index_infos[year]["list"], index_set = set(year_index_infos[year]["indices"]))

        print proc_num, "Writing stats for year", year
        ioutils.write_pickle(year_stats, out_pref + str(year) + "-tmp.pkl")

def run_parallel(num_procs, out_pref, in_dir, year_index_infos, thresh):
    queue = Queue()
    years = year_index_infos.keys()
    random.shuffle(years)
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_pref, in_dir, year_index_infos, thresh]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print "Merging"
    merge(out_pref, years, get_full_word_list(year_index_infos))
