from ioutils import load_pickle, write_pickle

DIR = "/dfs/scratch0/COHA/decade_freqs/"
word = {}
lemma = {}
lemma_pos = {}
for year in range(1810, 2010, 10):
    word[year] = load_pickle(DIR + str(year) + "-word.pkl")
    lemma[year] = load_pickle(DIR + str(year) + "-lemma.pkl")
    lemma_pos[year] = load_pickle(DIR + str(year) + "-lemma_pos.pkl")

write_pickle(word, DIR + "word.pkl")
write_pickle(lemma, DIR + "lemma.pkl")
write_pickle(lemma_pos, DIR + "lemma_pos.pkl")
