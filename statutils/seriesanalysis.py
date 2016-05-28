import numpy as np
from scipy.stats import ranksums, ttest_ind, spearmanr

def series_corr(word_year_series_1, word_year_series_2, i_year_words, start_year=1900, end_year=2000, series_1_norms=None, series_2_norms=None):
    """
    Gets the per-year correlation between the two word time series.
    Words are included even if they have values missing for a year, but there missing values are excluded from the year in question.
    """
    year_corrs = []
    year_ps = []
    years = range(start_year, end_year + 1)
    if start_year not in i_year_words:
        i_year_words = {year:i_year_words for year in years}
    if series_1_norms == None:
        series_1_norms = ([0 for year in years], [1 for year in years])
    if series_2_norms == None:
        series_2_norms = ([0 for year in years], [1 for year in years])
    for i in xrange(len(years)):
        year = years[i]
        s1 = []
        s2 = []
        for word in i_year_words[year]:
            if word in word_year_series_1 and word in word_year_series_2:
                if not np.isnan(word_year_series_1[word][year]) and not np.isnan(word_year_series_2[word][year]):
                    s1.append((word_year_series_1[word][year] - series_1_norms[0][i]) / series_1_norms[1][i])
                    s2.append((word_year_series_2[word][year] - series_2_norms[0][i]) / series_2_norms[1][i])
        corr, p = spearmanr(s1, s2)
        year_corrs.append(corr)
        year_ps.append(p)
    return year_corrs, year_ps

def get_series_median(words_time_series, words, one_minus=False, start_year=1900, end_year=2000, year_inc=10, exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words in the set words for the specified years 
    """
    i_year_words = {year:words for year in range(start_year, end_year+1, year_inc)}
    return get_series_median_peryear(words_time_series, i_year_words, one_minus, start_year, end_year, year_inc, exclude_partial_missing)

def get_series_median_peryear(word_time_series, i_year_words, one_minus=False, start_year=1900, end_year=2000, year_inc=10, exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words specified per year in i_year_words for specified years 
    """
    medians = []
    r_word_time_series = {}
    if exclude_partial_missing:
        for word, time_series in word_time_series.iteritems():
            if not np.isnan(np.sum(time_series.values())):
                r_word_time_series[word] = time_series
    else:
        r_word_time_series = word_time_series
    for year in xrange(start_year, end_year + 1, year_inc):
        word_array = np.array([r_word_time_series[word][year] for word in i_year_words[year] 
            if word in r_word_time_series and not np.isnan(r_word_time_series[word][year]) and not r_word_time_series[word][year] == 0])
        if len(word_array) == 0:
            continue
        if one_minus:
            word_array = 1 - word_array
        medians.append(np.median(word_array))
    return np.array(medians)


def get_series_mean_std(words_time_series, words, one_minus=False, start_year=1900, end_year=2000, year_inc=1, exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words in the set words for the specified years 
    """
    i_i_year_words = {year:words for year in range(start_year, end_year+1, year_inc)}
    return get_series_mean_std_peryear(words_time_series, i_i_year_words, one_minus, start_year, end_year, year_inc, exclude_partial_missing)

def get_series_mean_std_peryear(word_time_series, i_year_words, one_minus=False, start_year=1900, end_year=2000, year_inc=1, exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words specified per year in i_year_words for specified years 
    """
    means = []
    stderrs = []
    r_word_time_series = {}
    if exclude_partial_missing:
        for word, time_series in word_time_series.iteritems():
            if not np.isnan(np.sum(time_series.values())):
                r_word_time_series[word] = time_series
    else:
        r_word_time_series = word_time_series
    for year in xrange(start_year, end_year + 1, year_inc):
        word_array = np.array([r_word_time_series[word][year] for word in i_year_words[year] 
            if word in r_word_time_series and not np.isnan(r_word_time_series[word][year]) and not np.isinf(r_word_time_series[word][year])])
        if len(word_array) == 0:
            continue
        if one_minus:
            word_array = 1 - word_array
        means.append(word_array.mean())
        stderrs.append(word_array.std())
    return np.array(means), np.array(stderrs)

def get_series_mean_stderr(words_time_series, words, one_minus=False, start_year=1900, end_year=2000, year_inc=1, exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words in the set words for the specified years 
    """
    i_year_words = {year:words for year in range(start_year, end_year+1)}
    return get_series_mean_stderr_peryear(words_time_series, i_year_words, one_minus, start_year, end_year, year_inc, exclude_partial_missing)

def get_series_mean_stderr_peryear(word_time_series, i_year_words, one_minus=False, start_year=1900, end_year=2000, year_inc=1,  exclude_partial_missing=False):
    """
    Return the mean and stderr arrays for the values of the words specified per year in i_year_words for specified years 
    """
    means = []
    stderrs = []
    r_word_time_series = {}
    if exclude_partial_missing:
        for word, time_series in word_time_series.iteritems():
            time_series = {year:val for year, val in time_series.iteritems() if year >= start_year and year <= end_year}
            if not np.isnan(np.sum(time_series.values())):
                r_word_time_series[word] = time_series
    else:
        r_word_time_series = word_time_series
    for year in xrange(start_year, end_year + 1, year_inc):
        word_array = np.array([r_word_time_series[word][year] for word in i_year_words[year] 
            if word in r_word_time_series and not np.isnan(r_word_time_series[word][year])])
        if one_minus:
            word_array = 1 - word_array
        means.append(word_array.mean())
        stderrs.append(word_array.std() / len(word_array))
    return np.array(means), np.array(stderrs)

def get_set_dev(series, words, one_minus=False, start_year=1900, end_year=2000, method='diff'):
    """
    Gets the mean relative deviation of the words in words vs. the full series.
    Only words with valid values throughout the series are included.
    """
    base_mat = _make_series_mat(series, series.keys(), one_minus=one_minus, start_year=start_year, end_year=end_year)
    word_mat =  _make_series_mat(series, words, one_minus=one_minus, start_year=start_year, end_year=end_year)
    if method == 'diff':
        word_mat = word_mat - base_mat.mean(0)
    elif method == 'ratio':
        word_mat = word_mat / base_mat.mean(0)
    else:
        raise RuntimeError("Unknown deviation method. Use diff or ratio.")
    return word_mat.mean(0), word_mat.std(0) / np.sqrt(len(words))

def get_yearly_set_dev(series, i_year_words, one_minus=False, start_year=1900, end_year=2000, method='diff'):
    """
    Gets the mean relative deviation of the words in words vs. the full series.
    """
    base_mat = _make_series_mat(series, series.keys(), one_minus=one_minus, start_year=start_year, end_year=end_year)
    means = []
    stderrs = []
    r_word_time_series = series
    for year in xrange(start_year, end_year + 1):
        word_array = np.array([r_word_time_series[word][year] for word in i_year_words[year] 
            if word in r_word_time_series and not np.isnan(r_word_time_series[word][year])])
        if one_minus:
            word_array = 1 - word_array
        if method == 'diff':
            word_array = word_array - base_mat.mean(0)[year-start_year]
        elif method == 'ratio':
            word_array = word_array / base_mat.mean(0)[year-start_year]
        else:
            raise RuntimeError("Unknown deviation method. Use diff or ratio.")
        means.append(word_array.mean())
        stderrs.append(word_array.std() / len(word_array))
    return np.array(means), np.array(stderrs)

def _make_series_mat(words_time_series, words, one_minus=True, start_year=1900, end_year=2000):
    series_list = []
    for word in words:
        if word not in words_time_series:
            continue
        word_array = np.array([value for year, value in words_time_series[word].items() if year >= start_year and year <=end_year])
        if word_array.min() < 0:
            continue
        if one_minus:
            word_array = 1 - word_array
        if np.isnan(word_array.sum()):
            continue
        series_list.append(word_array)
    series_mat = np.array(series_list)
    return series_mat

# BELOW HERE POSSIBLY DEPRECATED

def get_series_mean_conf_clust(clust_series, deg_mean_series, start_year=1900, end_year=2000):
    series_mat = _make_series_mat(clust_series, clust_series.keys(), one_minus=False, start_year=start_year, end_year=end_year)
    means = series_mat.mean(0)
    rand_clust = np.array(deg_mean_series) / float(len(clust_series.keys()))
    std_errs = series_mat.std(0) / np.sqrt(len(clust_series.keys()))
    return means, std_errs, rand_clust

def get_power_series(word_degree_series, words, year=1999):
    series_mat = _make_series_mat(word_degree_series, words, one_minus=False, start_year=year, end_year=year)
    degs = []
    probs = []
    sum = series_mat.sum()
    for i in range(1, series_mat.max() + 1):
        count = (series_mat == i).sum()
        if count != 0:
            probs.append(float(count) / float(sum))
            degs.append(i)
    return degs, probs

def p_value_series(words_time_series, word_set1, word_set2,  one_minus=True):
    series_mat1 = _make_series_mat(words_time_series, word_set1, one_minus=True)
    series_mat2 = _make_series_mat(words_time_series, word_set2, one_minus=True)
    assert series_mat1.shape[1] == series_mat2.shape[1]
    p_series = np.empty(series_mat1.shape[1])
    for timepoint in xrange(series_mat1.shape[1]):
        _, p_series[timepoint] = ttest_ind(series_mat1[timepoint,:], series_mat2[timepoint,:], equal_var=False)
    return p_series

def series_mean_ranksums(word_set1, word_set2, words_time_series, one_minus=True):
    word_means1 = np.array(get_word_means(words_time_series, word_set1).values())
    word_means2 = np.array(get_word_means(words_time_series, word_set2).values())
    if one_minus:
        word_means1 = 1 - word_means1
        word_means2 = 1 - word_means2
    z,p = ranksums(word_means1, word_means2)
    return {"z" : z, 
            "p" : p, 
            "set1_size" : len(word_means1), 
            "set2_size" : len(word_means2), 
            "set1_med" : np.median(word_means1),
            "set2_med" : np.median(word_means2)}

def get_word_means(words_time_series, words, transform = lambda x : x):
    word_means = {}
    for word in words:
        if word not in words_time_series:
            continue
        word_mean = np.array([transform(value) for value in words_time_series[word].values() if value != 0]).mean()
        if np.isnan(word_mean):
            continue
        word_means[word] = word_mean 
    return word_means
