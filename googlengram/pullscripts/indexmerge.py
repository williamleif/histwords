import collections
import argparse

from googlengram import indexing

YEARS = range(1800, 2001)

def run(out_dir, in_dir):
    index = collections.OrderedDict()
    for year in YEARS:
        print "Merging year", year
        year_list = ioutils.load_pickle(in_dir + str(year) + "-list.pkl")
        i = 0
        for i in xrange(len(year_list)):
            word = year_list[i]
            indexing.word_to_cached_id(word, index)

    ioutils.write_pickle(index, out_dir + "merged_index.pkl") 
    ioutils.write_pickle(list(index), out_dir + "merged_list.pkl") 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Makes merged index for cooccurrence data")
    parser.add_argument("out_dir", help="directory where merged index will be stored")
    parser.add_argument("in_dir", help="path to unmerged data")
    args = parser.parse_args()
    run(args.out_dir + "/", args.in_dir + "/")       
