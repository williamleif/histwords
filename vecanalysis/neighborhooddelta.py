import os
import time
import random
import argparse
import numpy as np
from scipy.spatial import distance
from scipy import sparse
import collections

from multiprocessing import Process, Queue

import ioutils
from vecanalysis.representations.representation_factory import create_representation
from vecanalysis.representations.embedding import Embedding
NUM_NEIGH=26

def make_second_order(embed, embed_c):
    new_mat = embed.m.dot(embed_c.m.T)
    if type(new_mat) == sparse.csr.csr_matrix:
        new_mat = np.asarray(new_mat.todense())
    return Embedding(new_mat, embed.iw, normalize=False)

def get_cosine_deltas(base_embeds, delta_embeds, words, rep_type, sim_words):
    deltas = {}
    base_t = base_embeds.get_subembed(words, restrict_context=False)
    delta_t = delta_embeds.get_subembed(words, restrict_context=False)
    print "Reindexing..."
    base_s = base_embeds.reindex(sim_words, restrict_context=False, normalize=False)
    delta_s = delta_embeds.reindex(sim_words, restrict_context=False, normalize=False)
    print base_s.m.shape, delta_s.m.shape
    print "Making second orders..."
    base_embeds = make_second_order(base_t, base_s)
    delta_embeds = make_second_order(delta_t, delta_s)
    for i, word in enumerate(words):
        if base_embeds.oov(word) or delta_embeds.oov(word):
            deltas[word] = float('nan')
        else:
            base_inds = np.argsort(base_embeds.represent(word))[-NUM_NEIGH:-1]
            delta_inds = np.argsort(delta_embeds.represent(word))[-NUM_NEIGH:-1]
            inds = np.union1d(base_inds, delta_inds)
            deltas[word] = 1 - distance.cosine(base_embeds.represent(word)[inds], delta_embeds.represent(word)[inds])
    return deltas

def merge(out_pref, years, word_list):
    vol_yearstats = {}
    disp_yearstats = {}
    for word in word_list:
        vol_yearstats[word] = {}
        disp_yearstats[word] = {}
    for year in years:
        vol_yearstat = ioutils.load_pickle(out_pref + str(year) + "-vols.pkl")
        disp_yearstat = ioutils.load_pickle(out_pref + str(year) + "-disps.pkl")
        for word in word_list:
            if word not in vol_yearstat:
                vol = float('nan')
            else:
                vol = vol_yearstat[word]
            if word not in disp_yearstat:
                disp = float('nan')
            else:
                disp = disp_yearstat[word]
            vol_yearstats[word][year] = vol
            disp_yearstats[word][year] = disp
        os.remove(out_pref + str(year) + "-vols.pkl")
        os.remove(out_pref + str(year) + "-disps.pkl")
    ioutils.write_pickle(vol_yearstats, out_pref + "vols.pkl")
    ioutils.write_pickle(disp_yearstats, out_pref + "disps.pkl")

def worker(proc_num, queue, out_pref, in_dir, target_lists, context_lists, displacement_base, disp_words, min_count, year_inc, rep_type, count_dir):
    time.sleep(10*random.random())
    while True:
        if queue.empty():
            print proc_num, "Finished"
            break
        year = queue.get()
        print proc_num, "Loading matrices..."
        base = create_representation(rep_type, in_dir + str(year-year_inc), restricted_context=context_lists[year], normalize=True, add_context=False)
        delta = create_representation(rep_type, in_dir + str(year), restricted_context=context_lists[year], normalize=True, add_context=False)
        base_words = set(ioutils.words_above_count(count_dir, year - year_inc, min_count))
        delta_words = set(ioutils.words_above_count(count_dir, year, min_count))
        common_words = list(base_words.union(delta_words))
        print proc_num, "Getting deltas..."
        year_vols = get_cosine_deltas(base, delta, target_lists[year], rep_type, common_words)
        common_words = list(delta_words.union(disp_words))
        year_disp = get_cosine_deltas(displacement_base, delta, target_lists[year], rep_type, common_words)
        print proc_num, "Writing results..."
        ioutils.write_pickle(year_vols, out_pref + str(year) + "-vols.pkl")
        ioutils.write_pickle(year_disp, out_pref + str(year) + "-disps.pkl")

def run_parallel(num_procs, out_pref, in_dir, years, target_lists, context_lists, displacement_base, disp_words, min_count, year_inc, rep_type, count_dir):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_pref, in_dir, target_lists, context_lists, displacement_base, disp_words, min_count, year_inc, rep_type, count_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print "Merging"
    full_word_set = set(target_lists[years[0]])
    for year_words in target_lists.itervalues():
        full_word_set = full_word_set.union(set(year_words))
    merge(out_pref, years, list(full_word_set))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computes semantic change statistics for words.")
    parser.add_argument("dir", help="path to word vector data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("word_file", help="path to sorted word file")
    parser.add_argument("count_dir", help="path to directory with word count data")
    parser.add_argument("out_dir", help="Output directory")
    parser.add_argument("--target-words", type=int, help="Number of words (of decreasing average frequency) to analyze", default=-1)
    parser.add_argument("--context-words", type=int, help="Number of words (of decreasing average frequency) to include in context. -2 means all regardless of word list", default=0)
    parser.add_argument("--context-word-file", help="path to sorted word file")
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=1800)
    parser.add_argument("--year-inc", type=int, help="year increment", default=1)
    parser.add_argument("--min-count", type=int, help="year increment", default=500)
    parser.add_argument("--rep-type", default="PPMI")
    parser.add_argument("--end-year", type=int, help="end year (inclusive)", default=2000)
    parser.add_argument("--disp-year", type=int, help="year to measure displacement from", default=2000)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    target_words = ioutils.load_pickle(args.word_file)
    target_lists = collections.defaultdict(lambda : target_words[:args.target_words])
    if args.context_word_file != None:
        print "Loading context word file..."
        context_words = ioutils.load_pickle(args.context_word_file)[:args.context_words]
    else:
        context_words = None
    context_lists = collections.defaultdict(lambda : context_words)
    ioutils.mkdir(args.out_dir)
    displacement_base = create_representation(args.rep_type, args.dir + "/" +  str(args.disp_year), restricted_context=context_lists[args.disp_year], normalize=True, add_context=False)
    disp_words = ioutils.words_above_count(args.count_dir, args.disp_year, args.min_count)
    run_parallel(args.num_procs, args.out_dir, args.dir + "/", years[1:], target_lists, context_lists, displacement_base, disp_words, args.min_count, args.year_inc, args.rep_type, args.count_dir)       
