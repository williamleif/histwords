import os

from coha.cohastringutils import process_lemma_line
from ioutils import write_pickle

DATA = "/dfs/scratch0/COHA/COHA_word_lemma_pos/"
OUT = "/dfs/scratch0/COHA/info/"

def process_file(fp, word_dict, lemma_dict, lemma_pos_dict):
    fp.readline()
    for line in fp:
        word, lemma, lemma_pos, _ = process_lemma_line(line)
        if word == None:
            continue
        if lemma_pos == None:
            continue
        if word not in word_dict:
            id = len(word_dict)
            word_dict[word] = id
        if lemma not in lemma_dict:
            id = len(lemma_dict)
            lemma_dict[lemma] = id
        if lemma_pos not in lemma_pos_dict:
            id = len(lemma_pos_dict)
            lemma_pos_dict[lemma_pos] = id

if __name__ == "__main__":
    word_dict = {}
    lemma_dict = {}
    lemma_pos_dict = {}
    for decade in range(1810, 2010, 10):
        folder = str(decade)
        print "Processing decade...", folder
        for file in os.listdir(DATA + folder):
            with open(DATA + folder + "/" + file) as fp:
                print "Processing file..", folder + "/" + file
                process_file(fp, word_dict, lemma_dict, lemma_pos_dict)
    write_pickle(word_dict, OUT + "word-dict.pkl") 
    write_pickle(lemma_dict, OUT + "lemma-dict.pkl") 
    write_pickle(lemma_pos_dict, OUT + "lemma-pos-dict.pkl") 
