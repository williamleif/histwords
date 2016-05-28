import os

from collections import Counter
from multiprocessing import Queue, Process
from Queue import Empty

from coha.cohastringutils import process_lemma_line
from ioutils import write_pickle, load_pickle

DATA = "/dfs/scratch0/COHA/COHA_word_lemma_pos/"
OUT = "/dfs/scratch0/COHA/"

def worker(proc_num, queue):
    while True:
        try:
            decade = str(queue.get(block=False))
        except Empty:
             break
        print "Proc:", proc_num, "Decade:", decade
        word_freqs = Counter()
        lemma_freqs = Counter()
        lemma_pos_freqs = Counter()
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
                    word_freqs[word] += 1
                    lemma_freqs[lemma] += 1
                    lemma_pos_freqs[lemma_pos] += 1
        write_pickle(word_freqs, OUT + "decade_freqs/" + decade + "-word.pkl") 
        write_pickle(lemma_freqs, OUT + "decade_freqs/" + decade + "-lemma.pkl") 
        write_pickle(lemma_pos_freqs, OUT + "decade_freqs/" + decade + "-lemma_pos.pkl") 

if __name__ == "__main__":
    queue = Queue()
    for decade in range(1810, 2010, 10):
        queue.put(decade)
    procs = [Process(target=worker, args=[i, queue]) for i in range(25)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print "Getting full freqs..."
    word_freqs = Counter()
    lemma_freqs = Counter()
    lemma_pos_freqs = Counter()
    for decade in range(1810, 2010, 10):
        decade = str(decade)
        print decade
        word_freqs += load_pickle(OUT + "decade_freqs/" + decade + "-word.pkl") 
        lemma_freqs += load_pickle(OUT + "decade_freqs/" + decade + "-lemma.pkl") 
        lemma_pos_freqs += load_pickle(OUT + "decade_freqs/" + decade + "-lemma_pos.pkl") 
    write_pickle(word_freqs, OUT + "full_freqs/word.pkl") 
    write_pickle(lemma_freqs, OUT + "full_freqs/lemma.pkl") 
    write_pickle(lemma_pos_freqs, OUT + "full_freqs/lemma_pos.pkl") 
