import requests
import urllib2
import re
import os
import subprocess
import argparse
from multiprocessing import Process, Queue

import ioutils

VERSION = '20120701'
TYPE = '5gram'
POS = re.compile('.*_[A-Z]+\s.*')
LINE_SPLIT = 100000000
EXCLUDE_PATTERN = re.compile('.*_[A-Z]+[_,\s].*')

def split_main(proc_num, queue, download_dir):
    print proc_num, "Start loop"
    while True:
        if queue.empty():
            break
        url = queue.get()
        name = re.search('%s-(.*).gz' % VERSION, url).group(1)
        dirs = set(os.listdir(download_dir))
        if name in [file.split("-")[0] for file in dirs]:
            continue

        print proc_num, "Name", name
        loc_dir = download_dir + "/" + name + "/"
        ioutils.mkdir(loc_dir)

        print proc_num, "Downloading", name
        success = False
        while not success:
            with open(loc_dir + name + '.gz', 'w') as f:
                try:
                    f.write(urllib2.urlopen(url, timeout=60).read())
                    success = True
                except:
                    print "Fail!!"
                    continue

        print proc_num, "Unzipping", name
        subprocess.call(['gunzip', '-f', loc_dir + name + '.gz', '-d'])
        print proc_num, "Splitting", name
        subprocess.call(["split", "-l", str(LINE_SPLIT), loc_dir + name, download_dir + "/" +  name + "-"])
        os.remove(loc_dir + name)
        os.rmdir(loc_dir)

def run_parallel(num_processes, out_dir, source):
    page = requests.get("http://storage.googleapis.com/books/ngrams/books/datasetsv2.html")
    pattern = re.compile('href=\'(.*%s-%s-%s-.*\.gz)' % (source, TYPE, VERSION))
    urls = pattern.findall(page.text)
    del page
    queue = Queue()
    for url in urls:
        queue.put(url)
    ioutils.mkdir(out_dir + '/' + source + '/raw')
    download_dir = out_dir + '/' + source + '/raw/'
    ioutils.mkdir(download_dir)
    procs = [Process(target=split_main, args=[i, queue, download_dir]) for i in range(num_processes)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pulls and unzips raw 5gram data")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("source", help="source dataset to pull from (must be available on the N-Grams website")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    args = parser.parse_args()
    run_parallel(args.num_procs, args.out_dir, args.source) 
