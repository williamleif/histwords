import os
import collections

from multiprocessing import Queue, Process
from Queue import Empty

from coha.cohastringutils import process_lemma_line
from ioutils import write_pickle

DATA = "/dfs/scratch0/COHA/COHA_word_lemma_pos/"
OUT = "/dfs/scratch0/COHA/pos_tags/"

def worker(proc_num, queue):
    while True:
        try:
            decade = str(queue.get(block=False))
        except Empty:
             break
        print "Proc:", proc_num, "Decade:", decade
        pos_tags = collections.defaultdict(collections.Counter)
        for file in os.listdir(DATA + decade):
            with open(DATA + decade + "/" + file) as fp:
                print proc_num, file
                fp.readline()
                for line in fp:
                    word, lemma, lemma_pos, _ = process_lemma_line(line)
                    if word == None:
                        continue
                    if lemma_pos == None:
                        continue
                    pos_tags[word][lemma_pos.split("_")[1]] += 1
        write_pickle(pos_tags, OUT + str(decade) + "-pos-counts.pkl")
        pos_maj = {}
        for word, pos_counts in pos_tags.iteritems():
            pos_maj[word] = sorted(pos_counts, key = lambda t : -1*pos_counts[t])[0]
        write_pickle(pos_maj, OUT + str(decade) + "-pos-maj.pkl")

if __name__ == "__main__":
    queue = Queue()
    for decade in range(1810, 2010, 10):
        queue.put(decade)
    procs = [Process(target=worker, args=[i, queue]) for i in range(25)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
