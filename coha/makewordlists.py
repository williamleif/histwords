from ioutils import load_pickle, write_pickle
from nltk.corpus import stopwords

FREQS = "/dfs/scratch0/COHA/decade_freqs/{type}.pkl"
OUT = "/dfs/scratch0/COHA/word_lists/{type}-{cond}.pkl"
PROPER_NOUNS = "/dfs/scratch0/COHA/proper_nouns/{year:d}-proper_nouns.pkl"
STOPWORDS = set(stopwords.words("english"))

def make_word_list(type):
    process_word = lambda word : word if type != "lemma_pos" else word.split("_")[0]
    freqs = load_pickle(FREQS.format(type=type))
    word_lists = {}
    nstop_lists = {}
    nproper_lists = {}
    nstop_nproper_lists = {}
    print "Processing type: ", type
    for year, year_freqs in freqs.iteritems():
        proper_nouns = load_pickle(PROPER_NOUNS.format(year=year))
        word_lists[year] = [word for word in sorted(year_freqs, key = lambda val : -1*year_freqs[val]) if word != "" and word.isalnum()]
        nstop_lists[year] = [word for word in sorted(year_freqs, key = lambda val : -1*year_freqs[val]) if not process_word(word) in STOPWORDS and not word == "" and word.isalnum()]
        nproper_lists[year] = [word for word in sorted(year_freqs, key = lambda val : -1*year_freqs[val]) if not process_word(word) in proper_nouns and not word == "" and word.isalnum()]
        nstop_nproper_lists[year] = [word for word in sorted(year_freqs, key = lambda val : -1*year_freqs[val]) if not process_word(word) in proper_nouns 
                and not process_word(word) in STOPWORDS and not word == "" and word.isalnum()]
        print "Finished year: ", year
    write_pickle(word_lists, OUT.format(type=type, cond="all"))
    write_pickle(nstop_lists, OUT.format(type=type, cond="nstop"))
    write_pickle(nproper_lists, OUT.format(type=type, cond="nproper"))
    write_pickle(nstop_nproper_lists, OUT.format(type=type, cond="nstop_nproper"))

if __name__ == '__main__':
    for type in ["word", "lemma", "lemma_pos"]:
        make_word_list(type)
    
    
