from ioutils import load_pickle, write_pickle
from nltk.corpus import stopwords

FREQS = "/dfs/scratch0/COHA/cooccurs/{type}/avg_freqs.pkl"
OUT = "/dfs/scratch0/COHA/word_lists/full-{type}-{cond}.pkl"
PROPER_NOUNS = "/dfs/scratch0/COHA/proper_nouns/proper_nouns.pkl"
STOPWORDS = set(stopwords.words("english"))

def make_word_list(type):
    process_word = lambda word : word if type != "lemma_pos" else word.split("_")[0]
    freqs = load_pickle(FREQS.format(type=type))
    word_lists = {}
    nstop_lists = {}
    nproper_lists = {}
    nstop_nproper_lists = {}
    print "Processing type: ", type
    proper_nouns = load_pickle(PROPER_NOUNS)
    word_lists = [word for word in sorted(freqs, key = lambda val : -1*freqs[val]) if word != "" and word.isalnum()]
    nstop_lists = [word for word in sorted(freqs, key = lambda val : -1*freqs[val]) if not process_word(word) in STOPWORDS if word != "" and word.isalnum()]
    nproper_lists = [word for word in sorted(freqs, key = lambda val : -1*freqs[val]) if not process_word(word) in proper_nouns if word != "" and word.isalnum()]
    nstop_nproper_lists = [word for word in sorted(freqs, key = lambda val : -1*freqs[val]) if not process_word(word) in proper_nouns and not process_word(word) in STOPWORDS if word != "" and word.isalnum()]
    write_pickle(word_lists, OUT.format(type=type, cond="all"))
    write_pickle(nstop_lists, OUT.format(type=type, cond="nstop"))
    write_pickle(nproper_lists, OUT.format(type=type, cond="nproper"))
    write_pickle(nstop_nproper_lists, OUT.format(type=type, cond="nstop_nproper"))

if __name__ == '__main__':
    for type in ["word", "lemma"]:
        make_word_list(type)
    
    
