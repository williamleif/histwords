import subprocess

from argparse import ArgumentParser
from ioutils import mkdir

VOCAB_FILE = "{year:d}.vocab"
INPUT_FILE = "{year:d}.txt"
SAVE_FILE = "{year:d}"

def train_years(years, in_dir, out_dir, dim, workers, sequential):
    for i, year in enumerate(years):
        print "Running year", year
        if i == 0 or not sequential:
            subprocess.call(['./sgns/hyperwords/word2vecf/word2vecf', 
                    '-output', out_dir + SAVE_FILE.format(year=year) + "-w",
                    '-dumpcv', out_dir + SAVE_FILE.format(year=year) + "-c",
                    '-threads', str(workers), 
                    '-train', in_dir + INPUT_FILE.format(year=year),
                    '-size', str(dim),
                    '-sample', '0',
                    '-negative', '5',
                    '-wvocab', in_dir + VOCAB_FILE.format(year=year),
                    '-cvocab', in_dir + VOCAB_FILE.format(year=year),
                    '-verbose', '2'])
        else:
            subprocess.call(['./sgns/hyperwords/word2vecf/word2vecf', 
                    '-output', out_dir + SAVE_FILE.format(year=year) + "-w",
                    '-dumpcv', out_dir + SAVE_FILE.format(year=year) + "-c",
                    '-w-init-file', out_dir + SAVE_FILE.format(year=years[i-1]) + "-w.bin",
                    '-c-init-file', out_dir + SAVE_FILE.format(year=years[i-1]) + "-c.bin",
                    '-threads', str(workers), 
                    '-train', in_dir + INPUT_FILE.format(year=year),
                    '-size', str(dim),
                    '-sample', '0',
                    '-negative', '5',
                    '-wvocab', in_dir + VOCAB_FILE.format(year=year),
                    '-cvocab', in_dir + VOCAB_FILE.format(year=year),
                    '-verbose', '2'])

if __name__ == "__main__":
    parser = ArgumentParser("Runs sequential Glove embeddings for years")
    parser.add_argument("in_dir", help="Directory with cooccurrence information and vocab.")
    parser.add_argument("out_dir")
    parser.add_argument("--dim", type=int, default=300)
    parser.add_argument("--workers", type=int, default=50)
    parser.add_argument("--start-year", type=int, default=1800)
    parser.add_argument("--end-year", type=int, default=2000)
    parser.add_argument("--year-inc", type=int, default=1)
    parser.add_argument("--sequential", action="store_true")
    args = parser.parse_args()
    if not args.sequential:
        out_dir = args.out_dir + "/noinit/"
    else:
        out_dir = args.out_dir
    out_dir = out_dir + "/" + str(args.dim) + "/"
    mkdir(out_dir)
    years = range(args.start_year, args.end_year + 1, args.year_inc)
    train_years(years, args.in_dir + "/", out_dir, args.dim, args.workers, args.sequential)

