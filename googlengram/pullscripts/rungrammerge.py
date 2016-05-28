import argparse
from googlengram.pullscripts.runmerge import run_parallel

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merges years of raw 5gram data.")
    parser.add_argument("out_dir", help="directory where data will be stored")
    parser.add_argument("in_dir", help="path to unmerged data")
    parser.add_argument("num_procs", type=int, help="number of processes to spawn")
    args = parser.parse_args()
    run_parallel(args.num_procs, args.out_dir, args.in_dir)       

