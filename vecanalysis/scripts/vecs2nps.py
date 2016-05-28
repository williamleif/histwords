import numpy as np
import os
from multiprocessing import Process, Lock

DATA_DIR = '/dfs/scratch0/google_ngrams/'
INPUT_DIR = DATA_DIR + '/vecs-svd/'
OUTPUT_DIR = DATA_DIR + '/vecs-svd-np/'
#CTX_INPUT_FILE = INPUT_DIR + '{year}-300ctxvecs'
W_INPUT_FILE = INPUT_DIR + '{year}-300vec.txt'
#CTX_OUTPUT_FILE = OUTPUT_DIR + '{year}-300ctxvecs'
W_OUTPUT_FILE = OUTPUT_DIR + '{year}-300vecs'

YEARS = range(2007,2008)
VOCAB_SIZE = 50000
DIM = 300
size = (VOCAB_SIZE, DIM)

def main(proc_num, lock):
    while True:
        lock.acquire()
        work_left = False
        for year in YEARS:
            dirs = set(os.listdir(OUTPUT_DIR))
            if (W_OUTPUT_FILE.format(year=year) + ".npy").split("/")[-1] in dirs:
                continue
            work_left = True
            print proc_num, "year", year
            fname = W_OUTPUT_FILE.format(year=year) + ".npy"
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
    write_vecs(W_INPUT_FILE.format(year=year), W_OUTPUT_FILE.format(year=year))
#    write_vecs(CTX_INPUT_FILE.format(year=year), CTX_OUTPUT_FILE.format(year=year))

def write_vecs(finname, foutname):
    fh=file(finname)
#    first=fh.next()
#    size=map(int,first.strip().split())

    wvecs=np.zeros((size[0],size[1]),float)
    vocab=[]
    for i,line in enumerate(fh):
        line = line.strip().split()
        vocab.append(line[0])
        wvecs[i,] = np.array(map(float,line[1:]))

    np.save(foutname+".npy",wvecs)
    with file(foutname+".vocab","w") as outf:
       print >> outf, " ".join(vocab)

def run_parallel(num_procs):
    lock = Lock()
    procs = [Process(target=main, args=[i, lock]) for i in range(num_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    run_parallel(30)
