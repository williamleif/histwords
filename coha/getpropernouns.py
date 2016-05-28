from multiprocessing import Queue, Process
from Queue import Empty
import collections

from ioutils import write_pickle, load_pickle

DATA = "/dfs/scratch0/COHA/pos_tags/"
OUT = "/dfs/scratch0/COHA/proper_nouns/"

def worker(proc_num, queue):
    while True:
        try:
            decade = str(queue.get(block=False))
        except Empty:
             break
        print "Proc:", proc_num, "Decade:", decade
        proper_nouns = set([])
        pos_tags = load_pickle(DATA + str(decade) + "-pos-maj.pkl")
        for word, tag in pos_tags.iteritems():
            if tag == "np":
                proper_nouns.add(word)
        write_pickle(proper_nouns, OUT + str(decade) + "-proper_nouns.pkl")

if __name__ == "__main__":
    queue = Queue()
    for decade in range(1810, 2010, 10):
        queue.put(decade)
    procs = [Process(target=worker, args=[i, queue]) for i in range(25)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print "Getting full set..."
    proper_nouns = set([])
    pos_counts = {}
    print "Merging pos counts.."
    for decade in range(1810, 2010, 10):
        decade_pos_counts = load_pickle(DATA + str(decade) + "-pos-counts.pkl")
        for word, counts in decade_pos_counts.iteritems(): 
            if word not in pos_counts:
                pos_counts[word] = collections.Counter()
            for pos, count in counts.iteritems():
                pos_counts[word][pos] += count
    write_pickle(pos_counts, DATA + "all-pos-counts.pkl")
    pos_maj = {}
    proper_nouns = set([])
    for word, p_counts in pos_counts.iteritems():
        pos_maj[word] = sorted(p_counts, key = lambda t : -1*p_counts[t])[0]
        if pos_maj[word] == "np":
            proper_nouns.add(word)
    write_pickle(pos_maj, OUT + "all-pos-maj.pkl")
    write_pickle(proper_nouns, OUT + "proper_nouns.pkl")
