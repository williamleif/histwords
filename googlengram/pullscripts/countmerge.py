import sys
import argparse
from Queue import Empty 
from multiprocessing import Process, Queue

from googlengram import indexing
from representations import sparse_io
import ioutils

YEARS = range(1900, 2001)

def main(proc_num, queue, out_dir, in_dir):
    merged_index = ioutils.load_pickle(out_dir + "merged_index.pkl") 
    print proc_num, "Start loop"
    while True:
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        print proc_num, "Fixing counts for year", year
        fixed_counts = {}
        old_mat = sparse_io.retrieve_mat_as_dict(in_dir + str(year) + ".bin")
        old_index = ioutils.load_pickle(in_dir + str(year) + "-list.pkl") 
        for pair, count in old_mat.iteritems():
            try:
                i_word = old_index[pair[0]]
            except IndexError:
                print pair
                sys.exit(0)
            c_word = old_index[pair[1]]
            new_pair = (indexing.word_to_static_id(i_word, merged_index), 
                    indexing.word_to_static_id(c_word, merged_index))
            fixed_counts[new_pair] = count
        
        print proc_num, "Writing counts for year", year
        sparse_io.export_mats_from_dicts({str(year) : fixed_counts}, out_dir)

def run_parallel(num_procs, out_dir, in_dir):
    queue = Queue()
    for year in YEARS:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_dir, in_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts yearly counts to have merged index.")
    parser.add_argument("out_dir", help="directory where the consolidated data will be stored. Must also contain merged index.")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    args = parser.parse_args()
    run_parallel(args.num_procs, args.out_dir + "/", args.in_dir + "/")       

