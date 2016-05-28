import argparse

import ioutils
from cooccurrence import matstore
from cooccurrence.indexing import get_word_indices

START_YEAR = 1900
END_YEAR = 2000

INDEX_FILE = "/dfs/scratch0/googlengrams/2012-eng-fic/5grams/merged_index.pkl"

def run(out_file, in_dir, years, year_indices):
    samplesizes = {}
    for year in years:
        print "Processing year", year
        indices = year_indices[year]
        mat = matstore.retrieve_mat_as_coo(in_dir + str(year) + ".bin")
        mat = mat.tocsr()
        mat = mat[indices, :]
        mat = mat[:, indices]
        samplesizes[year] = mat.sum()
    ioutils.write_pickle(samplesizes, out_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="get sample sizes")
    parser.add_argument("out_file", help="output file")
    parser.add_argument("in_dir", help="input directory")
    parser.add_argument("--word-file", help="path to sorted word file(s). Must also specify index.", default=None)
    parser.add_argument("--num-words", type=int, help="Number of words (of decreasing average frequency) to include. Must also specifiy word file and index.", default=-1)
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=START_YEAR)
    parser.add_argument("--end-year", type=int, help="start year (inclusive)", default=END_YEAR)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1)
    index = ioutils.load_pickle(INDEX_FILE)
    word_pickle = ioutils.load_pickle(args.word_file)
    word_info = {}
    if not args.start_year in word_pickle:
        word_pickle = word_pickle[:args.num_words]
        year_word_info = get_word_indices(word_pickle, index)[1] 
        for year in years:
            word_info[year] = year_word_info
    else:
        for year in years:
            word_info[year] = get_word_indices(word_pickle[year][:args.num_words], index)[1]
    run(args.out_file, args.in_dir + "/", years, word_info)
