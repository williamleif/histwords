import argparse
import numpy as np

from multiprocessing import Process, Queue
import collections
from Queue import Empty

from ioutils import mkdir, write_pickle, load_pickle

def worker(proc_num, queue, out_dir, in_dir):
    while True:
        try:
            decade = queue.get(block=False)
        except Empty:
            break

        print "Processing decade", decade
        for year in range(10):
            year_counts = load_pickle(in_dir + str(decade + year) + "-pos.pkl")
            if year == 0:
                merged_pos_counts = year_counts
            for word, pos_counts in year_counts.iteritems():
                for pos, count in pos_counts.iteritems():
                    if not word in merged_pos_counts:
                        merged_pos_counts[word] = collections.Counter()
                    merged_pos_counts[word][pos] += count
        maj_tags = {}
        for word, pos_counts in merged_pos_counts.iteritems():
            if len(pos_counts) < 1:
                continue
            max_label = sorted(pos_counts, key= lambda w : pos_counts[w], reverse=True)[0]
            if pos_counts[max_label] > 0.5 * np.sum(pos_counts.values()):
                maj_tags[word] = max_label
            else:
                maj_tags[word] = "AMB"
        write_pickle(merged_pos_counts, out_dir + str(decade) + "-pos_counts.pkl")
        write_pickle(maj_tags, out_dir + str(decade) + "-pos.pkl")

def run_parallel(num_procs, out_dir, in_dir, decades):
    queue = Queue()
    for decade in decades:
        queue.put(decade)
    procs = [Process(target=worker, args=[i, queue, out_dir, in_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merges years of raw 5gram data.")
    parser.add_argument("base_dir", help="base directoty. /pos should be a subdir")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--start-year", type=int, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, help="end year (inclusive)")
    args = parser.parse_args()
    decades = range(args.start_year, args.end_year+1, 10)
    decades.reverse()
    out_dir = args.base_dir + "/decades/pos/"
    mkdir(out_dir)
    run_parallel(args.num_procs, out_dir,  args.base_dir + "/pos/", decades)       
