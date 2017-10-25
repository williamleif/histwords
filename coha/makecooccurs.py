import os

from collections import Counter
from multiprocessing import Queue, Process
from Queue import Empty
from argparse import ArgumentParser

from coha.cohastringutils import process_lemma_line
from ioutils import load_pickle, mkdir
import pyximport
pyximport.install(setup_args={"include_dirs": np.get_include()})
from representations.sparse_io import export_mat_from_dict

DATA = "/dfs/scratch0/COHA/COHA_word_lemma_pos/"
DICT = "/dfs/scratch0/COHA/info/{type}-dict.pkl"
OUT = "/dfs/scratch0/COHA/cooccurs/{type}/{window_size:d}/"

def worker(proc_num, queue, window_size, type, id_map):
    while True:
        try:
            decade = str(queue.get(block=False))
        except Empty:
             break
        print "Proc:", proc_num, "Decade:", decade
        pair_counts = Counter()
        for file in os.listdir(DATA + decade):
            with open(DATA + decade + "/" + file) as fp:
                print proc_num, file
                fp.readline()
                context = []
                for line in fp:
                    word, lemma, lemma_pos, _ = process_lemma_line(line)
                    if type == "word":
                        item = word
                    elif type == "lemma":
                        item = lemma
                    elif type == "lemma_pos":
                        item = lemma_pos
                    else:
                        raise Exception("Unknown type {}".format(type))
                    if item == None:
                        continue
                    context.append(id_map[item])
                    if len(context) > window_size * 2 + 1:
                        context.pop(0)
                    pair_counts = _process_context(context, pair_counts, window_size)
        export_mat_from_dict(pair_counts, decade, OUT.format(type=type, window_size=window_size))

def _process_context(context, pair_counts, window_size):
    if len(context) < window_size + 1:
        return pair_counts
    target = context[window_size]
    indices = range(0, window_size)
    indices.extend(range(window_size + 1, 2 * window_size + 1))
    for i in indices:
        if i >= len(context):
            break
        pair_counts[(target, context[i])] += 1
    return pair_counts

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("type")
    parser.add_argument("window_size", type=int)
    parser.add_argument("--workers", type=int, default=25)
    args = parser.parse_args()
    mkdir(OUT.format(type=args.type, window_size=args.window_size))
    queue = Queue()
    for decade in range(1810, 2010, 10):
        queue.put(decade)
    id_map = load_pickle(DICT.format(type=args.type))
    procs = [Process(target=worker, args=[i, queue, args.window_size, args.type, id_map]) for i in range(args.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
