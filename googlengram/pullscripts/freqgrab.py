import requests
import urllib2
import re
import os
import subprocess
import argparse

import ioutils

VERSION = '20120701'
TYPE = '1gram'
YEARS = range(1800, 2001)


def main(out_dir, source):
    page = requests.get("http://storage.googleapis.com/books/ngrams/books/datasetsv2.html")
    pattern = re.compile('href=\'(.*%s-%s-%s-.*\.gz)' % (source, TYPE, VERSION))
    urls = pattern.findall(page.text)
    del page

    year_freqs = {}
    for year in YEARS:
        year_freqs[year] = {}

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
                    word = split[0].decode('utf-8').lower()
                    word = word.strip("\"")
                    word = word.split("\'s")[0]
                    year = int(split[1])
                    count = int(split[2])
                    doc_count = int(split[3])
                    if not year in YEARS:
                        continue
                    if not word in year_freqs[year]:
                        year_freqs[year][word] = (count, doc_count)
                    else:
                        old_counts = year_freqs[year][word]
                        year_freqs[year][word] = (old_counts[0] + count, old_counts[1] + count)
                except UnicodeDecodeError:
                     pass

        print "Deleting", name
        try:
            os.remove(out_dir + name)
            os.remove(out_dir + name + '.gz')
        except:
            pass

    print "Writing..."
    for year in YEARS:
        ioutils.write_pickle(year_freqs[year], out_dir + str(year) + "-freqs.pkl")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pulls and saves unigram data.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("source", help="source dataset to pull from (must be available on the N-Grams website")
    args = parser.parse_args()
    main(args.out_dir + "/", args.source) 
