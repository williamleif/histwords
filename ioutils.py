import os
import collections
import cPickle as pickle
from cooccurrence.indexing import get_word_indices

def words_above_count(count_dir, year, min_count):
    counts = load_pickle(count_dir + str(year) + "-counts.pkl")
    words = sorted([word for word, count in counts.iteritems() if count >= min_count], key = lambda word : -1*counts[word])
    return words

def load_target_context_words(years, word_file, num_target, num_context):
    if num_context == 0:
        num_context = None
    if num_target == -1:
        num_target = num_context
    elif num_context == -1:
        num_context = num_target
    if num_target > num_context and num_context != None:
        raise Exception("Cannot have more target words than context words")
    word_lists = load_year_words(word_file, years)
    target_lists = {}
    context_lists = {}
    if num_context != -1:
        for year in years:
            context_lists[year] = word_lists[year][:num_context]
            target_lists[year] = word_lists[year][:num_target]
    else:
        context_lists = target_lists = word_lists
    return target_lists, context_lists

def load_year_indexes(dir, years):
    if "index.pkl" in os.listdir(dir):
        index = load_pickle(dir + "/index.pkl")
        year_indexes = {year:index for year in years}
    else:
        year_indexes = {}
        for year in years:
            year_indexes[year] = load_pickle(dir + str(year) + "-index.pkl")
    return year_indexes

def load_year_index_infos(index_dir, years, word_file, num_words=-1):
    """
    Returns dictionary mapping year to:
        "index": word->id index for that year.
        "list": word_list for that year
        "indices": set of valid indices corresponding to the word list
    Assumes that each year is indexed seperately.
    """
    if "index.pkl" in os.listdir(index_dir):
        return load_year_index_infos_common(load_pickle(index_dir + "index.pkl"),
                years, word_file, num_words=num_words)
    year_index_infos = collections.defaultdict(dict)
    word_lists = load_year_words(word_file, years)
    for year, word_list in word_lists.iteritems():
        year_index = load_pickle(index_dir + "/" + str(year) + "-index.pkl") 
        year_index_infos[year]["index"] = year_index
        if num_words != -1:
            word_list = word_list[:num_words]
        word_list, word_indices = get_word_indices(word_list, year_index)
        year_index_infos[year]["list"] = word_list
        year_index_infos[year]["indices"] = word_indices
    return year_index_infos

def load_year_index_infos_common(common_index, years, word_file, num_words=-1):
    """
    Returns dictionary mapping year to:
        "index": word->id index for that year.
        "list": word_list for that year
        "indices": set of valid indices corresponding to the word list
    Assumes that each year is indexed seperately.
    """
    year_index_infos = collections.defaultdict(dict)
    word_lists = load_year_words(word_file, years)
    for year, word_list in word_lists.iteritems():
        year_index = common_index
        year_index_infos[year]["index"] = year_index
        if num_words != -1:
            word_list = word_list[:num_words]
        word_list, word_indices = get_word_indices(word_list, year_index)
        year_index_infos[year]["list"] = word_list
        year_index_infos[year]["indices"] = word_indices
    return year_index_infos

def load_year_words(word_file, years):
    word_pickle = load_pickle(word_file)
    word_lists = {}
    if not years[0] in word_pickle:
        if type(word_pickle) == dict or type(word_pickle) == collections.Counter:
            word_pickle = sorted(word_pickle, key = lambda word : word_pickle[word], reverse=True) 
        for year in years:
            word_lists[year] = word_pickle
    else:
        for year in years:
            word_list = word_pickle[year]
            if type(word_list) == dict or type(word_list) == collections.Counter:
                word_list = sorted(word_list.keys(), key = lambda word : word_list[word], reverse=True) 
            word_lists[year] = word_list
    return word_lists

def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory) 

def write_pickle(data, filename):
    fp = open(filename, "wb")
    pickle.dump(data, fp)

def load_pickle(filename):
    fp = open(filename, "rb")
    return pickle.load(fp)

def load_word_list(filename):
    fp = open(filename, "r")
    words = []
    for line in fp:
        words.append(line.strip())
    fp.close()
    return words


