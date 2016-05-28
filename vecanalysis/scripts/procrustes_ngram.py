import os
import numpy as np
from multiprocessing import Lock, Process

from vecanalysis import alignment, embeddings

DATA_DIR = '/dfs/scratch0/google_ngrams/'
INPUT_DIR = DATA_DIR + '/vecs-interesting-np/'
OUTPUT_DIR = DATA_DIR + '/vecs-interesting-aligned/'
INPUT_FILE = INPUT_DIR + '{year}-200vecs.npy'
OUTPUT_FILE = OUTPUT_DIR + '{year}-200vecs'

YEARS = range(1850, 2009)
BASE_YEAR = 2005
BASE_EMBED = embeddings.Embeddings.load(INPUT_FILE.format(year=BASE_YEAR))

def align_year(year):
    year_embed = embeddings.Embeddings.load(INPUT_FILE.format(year=year))
    year_embed, base_embed = alignment.intersection_align(year_embed, BASE_EMBED)
    aligned_embed = alignment.procrustes_align(base_embed, year_embed)
    foutname = OUTPUT_FILE.format(year=year)
    np.save(foutname+".npy",aligned_embed._vecs)
    with file(foutname+".vocab","w") as outf:
       print >> outf, " ".join(aligned_embed._vocab)
    print "Finished year:", year

def main(proc_num, lock):
    while True:
        lock.acquire()
        work_left = False
        for year in YEARS:
            dirs = set(os.listdir(OUTPUT_DIR))
            if (OUTPUT_FILE.format(year=year) + ".npy").split("/")[-1] in dirs:
                continue
            work_left = True
            print proc_num, "year", year
            fname = OUTPUT_FILE.format(year=year) + ".npy"
            with open(fname, "w") as fp:
                fp.write("")
            fp.close()
            break
        lock.release()
        if not work_left:
            print proc_num, "Finished"
            break
        align_year(year)

def run_parallel(num_procs):
    lock = Lock()
    procs = [Process(target=main, args=[i, lock]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

