import os
import time
import random
import argparse

from multiprocessing import Process, Queue

import ioutils
from vecanalysis import alignment
from vecanalysis.representations.representation_factory import create_representation

def get_cosine_deltas(base_embeds, delta_embeds, words, type):
    deltas = {}
    if type == "PPMI":
        base_embeds, delta_embeds = alignment.explicit_intersection_align(base_embeds, delta_embeds)
    else:
        base_embeds, delta_embeds = alignment.intersection_align(base_embeds, delta_embeds)
    print base_embeds.m.shape, delta_embeds.m.shape
    for word in words:
        if base_embeds.oov(word) or delta_embeds.oov(word):
            deltas[word] = float('nan')
        else:
            delta = base_embeds.represent(word).dot(delta_embeds.represent(word).T)
            if type == "PPMI":
                delta = delta[0,0]
            deltas[word] = delta
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

def worker(proc_num, queue, out_pref, in_dir, target_lists, context_lists, displacement_base, thresh, year_inc, type):
    time.sleep(10*random.random())
    while True:
        if queue.empty():
            print proc_num, "Finished"
            break
        year = queue.get()
        print proc_num, "Loading matrices..."
        base = create_representation(type, in_dir + str(year-year_inc),  thresh=thresh, restricted_context=context_lists[year], normalize=True, add_context=False)
        delta = create_representation(type, in_dir + str(year),  thresh=thresh, restricted_context=context_lists[year], normalize=True, add_context=False)
        print proc_num, "Getting deltas..."
        year_vols = get_cosine_deltas(base, delta, target_lists[year], type)
        year_disp = get_cosine_deltas(displacement_base, delta, target_lists[year], type)
        print proc_num, "Writing results..."
        ioutils.write_pickle(year_vols, out_pref + str(year) + "-vols.pkl")
        ioutils.write_pickle(year_disp, out_pref + str(year) + "-disps.pkl")

def run_parallel(num_procs, out_pref, in_dir, years, target_lists, context_lists, displacement_base, thresh, year_inc, type):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, out_pref, in_dir, target_lists, context_lists, displacement_base, thresh, year_inc, type]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print "Merging"
    full_word_set = set([])
    for year_words in target_lists.itervalues():
        full_word_set = full_word_set.union(set(year_words))
    merge(out_pref, years, list(full_word_set))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computes semantic change statistics for words.")
    parser.add_argument("dir", help="path to network data (also where output goes)")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("word_file", help="path to sorted word file")
    parser.add_argument("--target-words", type=int, help="Number of words (of decreasing average frequency) to analyze", default=-1)
    parser.add_argument("--context-words", type=int, help="Number of words (of decreasing average frequency) to include in context. -2 means all regardless of word list", default=-1)
    parser.add_argument("--context-word-file")
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=1800)
    parser.add_argument("--year-inc", type=int, help="year increment", default=10)
    parser.add_argument("--type", default="PPMI")
    parser.add_argument("--end-year", type=int, help="end year (inclusive)", default=2000)
    parser.add_argument("--disp-year", type=int, help="year to measure displacement from", default=2000)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    target_lists, context_lists = ioutils.load_target_context_words(years, args.word_file, args.target_words, -1)
    if args.context_word_file != None:
        print "Loading context words.."
        _ , context_lists = ioutils.load_target_context_words(years, args.word_file, -1, args.context_words)
    target_lists, context_lists = ioutils.load_target_context_words(years, args.word_file, args.target_words, args.context_words)
    outpref = args.dir + "/volstats/" + args.word_file.split("/")[-1].split(".")[0].split("-")[1]
    if args.context_words != -1:
        outpref += "/c" + str(args.context_words) + "/"
    if args.target_words != -1:
        outpref += "/t" + str(args.target_words) + "/"
    ioutils.mkdir(outpref)
    displacement_base = create_representation(args.type, args.dir + "/" +  str(args.disp_year), restricted_context=context_lists[args.disp_year], normalize=True, add_context=False)
    run_parallel(args.num_procs, outpref, args.dir + "/", years[1:], target_lists, context_lists, displacement_base, 0, args.year_inc, args.type)       
