import numpy as np
import time
import random

from sklearn.utils.extmath import randomized_svd
from multiprocessing import Queue, Process
from argparse import ArgumentParser

from vecanalysis.representations.explicit import Explicit
from ioutils import load_year_words, mkdir, write_pickle, words_above_count

INPUT_FORMAT = '{year:d}.bin'
OUT_FORMAT = '{year:d}'

def worker(proc_num, queue, out_dir, in_dir, count_dir, words, dim, num_words, min_count=100):
    while True:
        if queue.empty():
            break
        year = queue.get()
        print "Loading embeddings for year", year
        time.sleep(random.random() * 120)
        valid_words = set(words_above_count(count_dir, year, min_count))
        print len(valid_words)
        words = list(valid_words.intersection(words[year][:num_words]))
        print len(words)
        base_embed = Explicit.load((in_dir + INPUT_FORMAT).format(year=year), normalize=False)
        base_embed = base_embed.get_subembed(words, restrict_context=True)
#        print "Converting to CSC..."
#        mat = base_embed.m.tocsc()
        print "SVD for year", year
#        u, s, v = sparsesvd(mat, dim)
        u, s, v = randomized_svd(base_embed.m, n_components=dim, n_iter=5)
        print "Saving year", year
        np.save((out_dir + OUT_FORMAT).format(year=year, dim=dim) + "-u.npy", u)
        np.save((out_dir + OUT_FORMAT).format(year=year, dim=dim) + "-v.npy", v)
        np.save((out_dir + OUT_FORMAT).format(year=year, dim=dim) + "-s.npy", s)
        write_pickle(base_embed.iw, (out_dir + OUT_FORMAT).format(year=year, dim=dim) + "-vocab.pkl")

if __name__ == '__main__':
    parser = ArgumentParser("Run SVD on historical co-occurrence matrices")
    parser.add_argument("in_dir", help="Directory with PPMI data")
    parser.add_argument("count_dir", help="Directory with PPMI data")
    parser.add_argument("word_file", help="File containing sorted list of words to potentially include")
    parser.add_argument("--num-words", type=int, help="Number of words to include", default=1000000)
    parser.add_argument("--dim", type=int, default=300)
    parser.add_argument("--workers", type=int, default=50)
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=1990)
    parser.add_argument("--year-inc", type=int, default=10)
    parser.add_argument("--min-count", type=int, default=100)
    args = parser.parse_args()
    queue = Queue()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    years.reverse()
    for year in years:
        queue.put(year)
    out_dir = args.in_dir + "/svd/" + str(args.dim) + "/" + str(args.num_words) + "/" + str(args.min_count) + "/"
    mkdir(out_dir)
    words = load_year_words(args.word_file, years)
    procs = [Process(target=worker, args=[i, queue, out_dir, args.in_dir, args.count_dir, words, args.dim, args.num_words, args.min_count]) for i in range(args.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
