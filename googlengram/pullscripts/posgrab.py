import requests
import urllib2
import re
import os
import subprocess
import argparse
import collections

import ioutils

VERSION = '20120701'
TYPE = '1gram'
POS = re.compile('[^_]+_[A-Z]+')

def main(out_dir, source, years):
    page = requests.get("http://storage.googleapis.com/books/ngrams/books/datasetsv2.html")
    pattern = re.compile('href=\'(.*%s-%s-%s-.*\.gz)' % (source, TYPE, VERSION))
    urls = pattern.findall(page.text)
    del page

    year_counts = {}
    year_doc_counts = {}
    year_pos = {}
    for year in years:
        year_pos[year] = {}
        year_counts[year] = {}
        year_doc_counts[year] = {}

    print "Start loop"
    for url in urls:
        name = re.search('%s-(.*).gz' % VERSION, url).group(1)
        print  "Downloading", name

        success = False
        while not success:
            with open(out_dir + name + '.gz', 'w') as f:
                try:
                    f.write(urllib2.urlopen(url, timeout=60).read())
                    success = True
                except:
                    continue

        print  "Unzipping", name
        subprocess.call(['gunzip', '-f', out_dir + name + '.gz', '-d'])

        print  "Going through", name
        with open(out_dir + name) as f:
            for l in f:
                try:
                    split = l.strip().split('\t')
                    if not POS.match(split[0]):
                        continue
                    count = int(split[2])
                    if count < 10:
                        continue
                    word_info = split[0].split("_") 
                    pos = word_info[-1]
                    word = word_info[0].decode('utf-8').lower()
                    word = word.strip("\"")
                    word = word.split("\'s")[0]
                    year = int(split[1])
                    doc_count = int(split[3])
                    if not year in years:
                        continue
                    if not word in year_counts[year]:
                        year_counts[year][word] = 0
                        year_doc_counts[year][word] = 0
                        year_pos[year][word] = collections.Counter() 
                    year_counts[year][word] += count 
                    year_doc_counts[year][word] += doc_count 
                    year_pos[year][word][pos] += count
                except UnicodeDecodeError:
                     pass

        print "Deleting", name
        try:
            os.remove(out_dir + name)
            os.remove(out_dir + name + '.gz')
        except:
            pass

    print "Writing..."
    for year in years:
        ioutils.write_pickle(year_counts[year], out_dir + str(year) + "-counts.pkl")
        ioutils.write_pickle(year_doc_counts[year], out_dir + str(year) + "-doc_counts.pkl")
        ioutils.write_pickle(year_pos[year], out_dir + str(year) + "-pos.pkl")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pulls and saves unigram data.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("source", help="source dataset to pull from (must be available on the N-Grams website")
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1)
    ioutils.mkdir(args.out_dir)
    main(args.out_dir + "/", args.source, years) 
