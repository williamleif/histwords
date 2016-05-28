import argparse
import os
import random
import collections
from Queue import Empty 
from multiprocessing import Process, Queue

from nltk.corpus import stopwords

import ioutils
from cooccurrence import matstore

def merge(years, out_pref, out_dir):
    word_freqs = collections.defaultdict(dict)
    word_lists = {}
    word_set = set([])
    for year in years:
        word_lists[year] = ioutils.load_pickle(out_dir + str(year) + "tmp.pkl")
        word_set = word_set.union(set(word_lists[year]))
        os.remove(out_dir + str(year) + "tmp.pkl")
    for year in years:
        year_freqs= ioutils.load_pickle(out_dir + str(year) + "freqstmp.pkl")
        for word in word_set:
            if word not in year_freqs:
                word_freqs[word][year] = float('nan')
            else:
                word_freqs[word][year] = year_freqs[word]
        os.remove(out_dir + str(year) + "freqstmp.pkl")

    ioutils.write_pickle(word_freqs, out_pref + "-freqs.pkl")
    ioutils.write_pickle(word_lists, out_pref + ".pkl")

def main(proc_num, queue, out_pref, out_dir, in_dir, index, freq_thresh, lang):
    random.shuffle(years)
    print proc_num, "Start loop"
    while True:
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        stop_set = set(stopwords.words(lang))
        word_freqs = {}
        print "Loading mat for year", year
        year_mat = matstore.retrieve_mat_as_coo(in_dir + str(year) + ".bin")
        year_mat = year_mat.tocsr()
        year_mat = year_mat / year_mat.sum()
        print "Processing data for year", year
        for word_i in xrange(year_mat.shape[0]):
            word = index[word_i]
            if not word.isalpha() or word in stop_set or len(word) == 1:
                continue
            year_freq = year_mat[word_i, :].sum()
            word_freqs[word] = year_freq
        print "Writing data"
        sorted_list = sorted(word_freqs.keys(), key = lambda key : word_freqs[key], reverse=True)
        sorted_list = [word for word in sorted_list 
                    if word_freqs[word] > freq_thresh]
        ioutils.write_pickle(sorted_list, out_dir + str(year) + "tmp.pkl")
        ioutils.write_pickle(word_freqs, out_dir + str(year) + "freqstmp.pkl")

def run_parallel(num_procs, years, out_pref, out_dir, in_dir, index, freq_thresh, lang):
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_pref, out_dir, in_dir, index, freq_thresh, lang]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    merge(years, out_pref, out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get yearly sorted by-frequency list of (non-stop) words and dicts with their frequencies")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("in_dir", help="directory with 5 grams and index")
    parser.add_argument("num_procs", type=int, help="num procs")
    parser.add_argument("--start-year", type=int, default=1900, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2000, help="end year (inclusive)")
    parser.add_argument("--freq-thresh", type=int, default=7, help="frequency threshold (neg. power of 10)")
    parser.add_argument("--lang", type=str, default="english", help="language")
    args = parser.parse_args()

    years = range(args.start_year, args.end_year + 1)
    index = ioutils.load_pickle(args.in_dir + "/merged_list.pkl")
    out_pref = args.out_dir + "/freqnonstop_peryear-" + str(years[0]) + "-" + str(years[-1]) + "-"  + str(args.freq_thresh)
    freq_thresh = 10.0 ** (-1.0 * float(args.freq_thresh))
    run_parallel(args.num_procs, years, out_pref , args.out_dir + "/", args.in_dir + "/", index, freq_thresh, args.lang)
