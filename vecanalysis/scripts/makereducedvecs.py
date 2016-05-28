import numpy as np
import os
from multiprocessing import Process, Lock

from vecanalysis.representations.embedding import Embedding

DATA_DIR = '/dfs/scratch0/google_ngrams/'
INPUT_DIR = DATA_DIR + '/sglove-vecs-smallrel-aligned-seq/'
INPUT_PATH = INPUT_DIR + '{year}-300vecs'
OUTPUT_DIR = DATA_DIR + '/sglove-small/'
OUTPUT_PATH = OUTPUT_DIR + '{year}-300vecs'
WORD_FILE = DATA_DIR + 'info/interestingwords.txt'

def get_top_words(word_file, k):
    word_fp = open(word_file)
    top_words = [] 
    for word_line in word_fp:
        top_words.append(word_line.split()[0].strip())
        if len(top_words) == k:
            break
    return top_words


YEARS = range(1900, 2001)
TOP_WORDS = get_top_words(WORD_FILE, 30000)

def main(proc_num, lock):
    while True:
        lock.acquire()
        work_left = False
        for year in YEARS:
            dirs = set(os.listdir(OUTPUT_DIR))
            if (OUTPUT_PATH.format(year=year) + ".npy").split("/")[-1] in dirs:
                continue
            work_left = True
            print proc_num, "year", year
            fname = OUTPUT_PATH.format(year=year) + ".npy"
            with open(fname, "w") as fp:
                fp.write("")
            fp.close()
            break
        lock.release()
        if not work_left:
            print proc_num, "Finished"
            break
        write_year(year)

def write_year(year):
    write_vecs(INPUT_PATH.format(year=year), OUTPUT_PATH.format(year=year))

def write_vecs(finname, foutname):
    og_embed = Embedding.load(finname, normalize=False)
    red_embed = og_embed.get_subembed(TOP_WORDS)
    np.save(foutname+".npy", red_embed.m)
    with file(foutname+".vocab","w") as outf:
       print >> outf, " ".join(red_embed.iw)

def run_parallel(num_procs):
    lock = Lock()
    procs = [Process(target=main, args=[i, lock]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
