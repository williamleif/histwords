import argparse
import ioutils

from cooccurrence.netstats import run_parallel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computes network-based statistics for each word.")
    parser.add_argument("dir", help="path to directory with nppmi data and year indexes")
    parser.add_argument("word_file", help="path to sorted word file(s).", default=None)
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--num-words", type=int, help="Number of words (of decreasing average frequency) to include. Must also specifiy word file and index.", default=-1)
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=1900)
    parser.add_argument("--end-year", type=int, help="start year (inclusive)", default=2000)
    parser.add_argument("--year-inc", type=int, help="year increment", default=1)
    parser.add_argument("--thresh", type=float, help="optional threshold", default=None)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    year_index_infos = ioutils.load_year_index_infos(args.dir, years, args.word_file, num_words=args.num_words)
    outpref ="/netstats/" + args.word_file.split("/")[-1].split(".")[0]
    if args.num_words != -1:
        outpref += "-top" + str(args.num_words)
    if args.thresh != None:
        outpref += "-" + str(args.thresh)
    ioutils.mkdir(args.dir + "/netstats")
    run_parallel(args.num_procs, args.dir + outpref, args.dir + "/", year_index_infos, args.thresh)       
