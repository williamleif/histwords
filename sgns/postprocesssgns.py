import numpy as np
from multiprocessing import Queue, Process
from argparse import ArgumentParser

from ioutils import load_pickle, write_pickle

def worker(proc_num, queue, dir, count_dir, min_count):
    while True:
        if queue.empty():
            break
        year = queue.get()
        print "Loading data..", year
#        time.sleep(120 * random.random())
        freqs = load_pickle(count_dir + str(year) + "-counts.pkl")
        iw = []
        with open(dir + str(year) + "-w.txt") as fp:
            info = fp.readline().split()
            vocab_size = int(info[0])
            dim = int(info[1])
            w_mat = np.zeros((vocab_size, dim))
            for i, line in enumerate(fp):
                line = line.strip().split()
                iw.append(line[0].decode("utf-8"))
                if freqs[iw[-1]] >= 500:
                    w_mat[i,:] = np.array(map(float, line[1:]))
        c_mat = np.zeros((vocab_size, dim))
        with open(dir + str(year) + "-c.txt") as fp:
            fp.readline()
            for i, line in enumerate(fp):
                line = line.strip().split()
                if freqs[line[0]] >= min_count:
                    c_mat[i,:] = np.array(map(float, line[1:]))
        np.save(dir + str(year) + "-w.npy", w_mat)
        np.save(dir + str(year) + "-c.npy", c_mat)
        write_pickle(iw, dir + str(year) + "-vocab.pkl")

if __name__ == "__main__":
    parser = ArgumentParser("Post-processes SGNS vectors to easier-to-use format. Removes infrequent words.")
    parser.add_argument("dir")
    parser.add_argument("count_dir", help="Directory with count data.")
    parser.add_argument("--workers", type=int, help="Number of processes to spawn", default=20)
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    parser.add_argument("--min-count", type=int, default=500)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    queue = Queue()
    for year in years:
        queue.put(year)
    procs = [Process(target=worker, args=[i, queue, args.dir, args.count_dir, args.min_count]) for i in range(args.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
