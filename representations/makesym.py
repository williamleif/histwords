import random
import argparse
from Queue import Empty 
from multiprocessing import Process, Queue

from cooccurrence import matstore

START_YEAR = 1900
END_YEAR = 2000

def main(proc_num, queue, out_dir, in_dir):
    random.shuffle(years)
    print proc_num, "Start loop"
    while True:
        try: 
            year = queue.get(block=False)
        except Empty:
            print proc_num, "Finished"
            break
        print proc_num, "Loading  matrix", year
        coo_mat = matstore.retrieve_mat_as_coo(in_dir + str(year) + ".bin", min_size=10**6)
        csr_mat = coo_mat.tocsr()
        sum_mat = (csr_mat + csr_mat.T) 
        sum_mat = sum_mat.tocoo()
        for i in xrange(len(sum_mat.data)):
            sum_mat.data[i] = max(csr_mat[sum_mat.row[i], sum_mat.col[i]], csr_mat[sum_mat.col[i], sum_mat.row[i]])
        
        print proc_num, "Writing counts for year", year
        matstore.export_mat_eff(sum_mat.row, sum_mat.col, sum_mat.data, year, out_dir)
            

def run_parallel(num_procs, out_dir, in_dir, years):
    queue = Queue()
    for year in  years:
        queue.put(year)
    procs = [Process(target=main, args=[i, queue, out_dir, in_dir]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get sorted list of words according to average relative frequency")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("in_dir", help="directory with 5 grams")
    parser.add_argument("num_procs", type=int, help="index file")
    parser.add_argument("--start-year", type=int, default=START_YEAR, help="start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=END_YEAR, help="end year (inclusive)")
    args = parser.parse_args()

    years = range(args.start_year, args.end_year + 1)
    run_parallel(args.num_procs, args.out_dir + "/", args.in_dir + "/", years) 
