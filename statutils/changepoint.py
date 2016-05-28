import operator
import numpy as np
import scipy as sp
import statsmodels.api as sm
import collections

FREQ_FILE = "/dfs/scratch0/google_ngrams/info/relevantwords.txt"

def make_area_seres(year_series):
    inc_series = sorted(year_series.items(), key=operator.itemgetter(0))
    baseline = min(year_series.values())
    area_series = []
    for i in range(len(inc_series) - 1):
        year, val = inc_series[i]
        next_year, next_val = inc_series[i + 1]
        area_series.add((year, 0.5 * max(val - next_val, next_val - val) + min(val, next_val) - baseline)) 
    return area_series
        

def is_area_change_point(area_series, year, thresh):
    start_year = area_series[0][0]
    change_point = year - start_year
    area_array = np.array([val for val, _ in area_series])
    ratio = np.sum(area_array[0:change_point]) / np.sum(area_array[change_point:])
    if ratio > thresh:
        return 1
    elif ratio < thresh ** -1:
        return -1
    else:
        return 0

def mean_shift(year_series, bootstrap_samples=1000, start_year=1900, end_year=2000, p_value_thresh=0.01):
    array_series = np.array([val for year, val in sorted(year_series.items(), key=operator.itemgetter(0)) if year >= start_year and year <= end_year])
    bootstrapped = np.empty((bootstrap_samples, array_series.shape[0]))
    for i in xrange(bootstrap_samples):
        bootstrapped[i, :] = np.random.permutation(array_series)
    p_values = np.ones(array_series.shape[0] - 1) * bootstrap_samples
    shifts = np.empty(array_series.shape[0] - 1)
    for i in xrange(array_series.shape[0] - 1):
        shifts[i] = array_series[i+1:].mean() - array_series[0:i+1].mean()
        for j in xrange(bootstrapped.shape[0]):
            if abs(bootstrapped[j,i+1:].mean() - bootstrapped[j, 0:i+1].mean()) < abs(shifts[i]):
                p_values[i] -= 1
        p_values[i] /= float(bootstrap_samples)
    max_ind = -1
    max_val = 0
    for i in xrange(len(shifts)):
        if p_values[i] < p_value_thresh and abs(shifts[i]) > max_val:
            max_ind = i
            max_val = shifts[i]
    return max_ind, shifts[max_ind], p_values[max_ind]
