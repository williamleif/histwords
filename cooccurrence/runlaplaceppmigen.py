import argparse

import ioutils
from cooccurrence.laplaceppmigen import run_parallel

SMOOTH = 10
START_YEAR = 1900
END_YEAR = 2000

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Computed laplace smoothed normalized PPMI values.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    parser.add_argument("--conf-dir", help="optional file of restricted word set. NOT CURRENTLY SUPPORTED.", default=None)
    parser.add_argument("--start-year", type=int, help="start year (inclusive)", default=START_YEAR)
    parser.add_argument("--end-year", type=int, help="start year (inclusive)", default=END_YEAR)
    parser.add_argument("--year-inc", type=int, help="start year (inclusive)", default=1)
    parser.add_argument("--smooth", type=int, help="smoothing factor", default=SMOOTH)
    parser.add_argument("--normalize", action="store_true", help="normalized ppmi")
    parser.add_argument("--cds", action="store_true", help="normalized ppmi")
    parser.add_argument("--neg", type=int, default=1)
    args = parser.parse_args()
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    if args.smooth == 0:
        smooth = 0
    else:
        smooth = 10.0**(-1*float(args.smooth))
    out_dir = args.out_dir + "/lsmooth" + str(args.smooth) + "/n" + str(args.normalize) + "/neg" + str(args.neg) + "/cds" + str(args.cds)
    ioutils.mkdir(out_dir)
    run_parallel(args.num_procs,  out_dir + "/", args.in_dir + "/", years, smooth, args.conf_dir, args.normalize, args.cds, args.neg)       

