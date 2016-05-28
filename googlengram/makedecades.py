import argparse
import collections

from multiprocessing import Process, Queue
from Queue import Empty

from vecanalysis.representations.explicit import Explicit
from cooccurrence.matstore import export_mat_from_dict
from ioutils import mkdir, write_pickle, load_pickle

def get_index(merged_index, year_list, index):
    word = year_list[index] 
    if word in merged_index:
        new_index = merged_index[word]
    else:
        new_index = len(merged_index)
        merged_index[word] = new_index
    return new_index

def worker(proc_num, queue, out_dir, in_dir):
    while True:
        try:
            decade = queue.get(block=False)
        except Empty:
            break

        print "Processing decade", decade
        counts = collections.defaultdict(int)       
        for year in range(10):
            embed = Explicit.load(in_dir + str(decade + year) + ".bin", normalize=False)
            if year == 0:
                merged_index = embed.wi
            year_list = load_pickle(in_dir + str(decade + year) + "-list.pkl")
            mat = embed.m.tocoo()
            for i in xrange(len(mat.data)):
                if mat.data[i] == 0:
                    continue
                new_row = get_index(merged_index, year_list, mat.row[i])
                new_col = get_index(merged_index, year_list, mat.col[i])
                counts[(new_row, new_col)] += mat.data[i]
            print "Done year ", decade + year
        export_mat_from_dict(counts, decade, out_dir)
        write_pickle(merged_index, out_dir + str(decade) + "-index.pkl")
        write_pickle(list(merged_index), out_dir + str(decade) + "-list.pkl")

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
    parser.add_argument("out_dir", help="path to network data (also where output goes)")
    parser.add_argument("in_dir", help="path to network data (also where output goes)")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--start-year", type=int, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, help="end year (inclusive)")
    args = parser.parse_args()
    decades = range(args.start_year, args.end_year + 1, 10)
    decades.reverse()
    mkdir(args.out_dir)
    run_parallel(args.num_procs, args.out_dir + "/",  args.in_dir + "/", decades)       
