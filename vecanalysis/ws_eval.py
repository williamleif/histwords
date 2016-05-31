import ioutils
from argparse import ArgumentParser
from scipy.stats.stats import spearmanr

from representations.explicit import Explicit
from representations.embedding import SVDEmbedding, Embedding

def read_test_set(path):
    test = []
    with open(path) as f:
        for line in f:
            x, y, sim = line.strip().lower().split()
            test.append(((x.split("-")[0], y.split("-")[0]), sim))
    return test 

def evaluate(representation, data):
    results = []
    oov = 0
    for (x, y), sim in data:
        if representation.oov(x) or representation.oov(y):
            oov += 1
#           continue
            results.append((0, sim)) 
        else:
            results.append((representation.similarity(x, y), sim))
    actual, expected = zip(*results)
    print "OOV: ", oov
    return spearmanr(actual, expected)[0]


if __name__ == '__main__':
    parser = ArgumentParser("Run word similarity benchmark")
    parser.add_argument("vec_path", help="Path to word vectors")
    parser.add_argument("test_path", help="Path to test data")
    parser.add_argument("--word-path", help="Path to sorted list of context words", default="")
    parser.add_argument("--num-context", type=int, help="Number context words to use", default=-1)
    parser.add_argument("--type", default="PPMI")
    args = parser.parse_args()
    if args.type == "PPMI":
        year = int(args.vec_path.split("/")[-1].split(".")[0])
        if args.num_context != -1 and args.word_path == "":
            raise Exception("Must specify path to context word file if the context words are to be restricted!")
        elif args.word_path != "":
            _, context_words = ioutils.load_target_context_words([year], args.word_path, -1, args.num_context)
            context_words = context_words[year]
        else:
            context_words = None
        rep = Explicit.load(args.vec_path, restricted_context=context_words)
    elif args.type == "SVD":
        rep = SVDEmbedding(args.vec_path, eig=0.0)
    else:
        rep = Embedding.load(args.vec_path, add_context=False)
    data = read_test_set(args.test_path)
    correlation = evaluate(rep, data)
    print "Correlation: " + str(correlation)
