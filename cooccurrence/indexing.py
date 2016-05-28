import numpy as np

def word_to_id(word, index):
    word = word.decode('utf-8').lower()
    word = word.strip("\"")
    word = word.split("\'s")[0]
    try:
        return index[word]
    except KeyError:
        id_ = len(index)
        index[word] = id_
        return id_

def word_to_cached_id(word, index):
    try:
        return index[word]
    except KeyError:
        id_ = len(index)
        index[word] = id_
        return id_

def word_to_static_id(word, index):
    return index[word]

def word_to_static_id_pass(word, index):
    try:
        return index[word]
    except KeyError:
        return -1;

def get_word_indices(word_list, index):
    common_indices = []
    new_word_list = []
    for word in word_list:
        try:
            common_indices.append(index[word])
            new_word_list.append(word)
        except KeyError:
            print "Unmapped word!"
    return new_word_list, np.array(common_indices)

def get_full_word_list(year_indexinfo):
    word_set = set([])
    for info in year_indexinfo.values():
        word_set.update(info["list"])
    return list(word_set)
