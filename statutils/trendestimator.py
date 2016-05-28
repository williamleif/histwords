import operator
import numpy as np
import scipy as sp
import statsmodels.api as sm

def trend_estimate(year_series, start_year=1900, end_year=2000, min_obs=1):
    y = np.array([val for year, val in sorted(year_series.items(), key=operator.itemgetter(0)) if year >= start_year and year <= end_year])
    y = np.nan_to_num(y)
    zeros = np.where(y==0)[0]
    if len(zeros) == 0:
        start = 0
    else:
        start = zeros[-1] + 1
    y = y[start:]
    if len(y) <= min_obs:
        return None
    X = np.arange(len(y))
    X = sm.add_constant(X)
    mod = sm.OLS(y, X)
    res = mod.fit()
    return res

def trend_estimate_arr(y, start_year=1900, end_year=2000):
    zeros = np.where(y==0)[0]
    if len(zeros) == 0:
        start = 0
    else:
        start = zeros[-1] + 1
    y = y[start:]
    if len(y) <= 1:
        return None
    X = np.arange(len(y))
    X = sm.add_constant(X)
    mod = sm.OLS(y, X)
    res = mod.fit()
    return res


def get_trend_estimates(word_series, start_year=1900, end_year=2000, min_obs=10):
    res_series = {}
    for word, year_series in word_series.iteritems():
        trend_est = trend_estimate(year_series, start_year=start_year, end_year=end_year, min_obs=min_obs)
        if not trend_est == None:
            res_series[word] = trend_est
    return res_series

def get_high_entry_trs(word_series, start_year=1900, end_year=2000, not_present_min=0.25, not_present_max=0.50,  slope_thresh=10**(-8)):
    entry_series = {}
    for word, year_series in word_series.iteritems():
        eff_series = {year:entry for year,entry in year_series.items() if entry != float('nan') and entry != 0}
        eff_len = len(eff_series)
        not_present_prop =  1 - float(eff_len) / (end_year - start_year) 
        if not_present_prop > not_present_min and not_present_prop < not_present_max:
            entry_series[word] = eff_series
    trend_estimates = get_trend_estimates(entry_series, start_year=start_year, end_year=end_year)
    processed = process_trend_estimates(trend_estimates, slope_thresh=slope_thresh)
    return sort_trend_infos(processed["increasing"], "slope")

def get_new_words_by_range(word_series, start_year=1925, end_year=1950, not_present_min=0.25, not_present_max=0.75):
    return {word for word, year in get_new_words(word_series, start_year=1900, end_year=2000, not_present_min=not_present_min, not_present_max=not_present_max).iteritems()
            if year >= start_year and year < end_year}

def get_successful_new_words(word_series, start_year=1900, end_year=2000, not_present_min=0.25, not_present_max=0.75, s_buff=10, e_buff=10, shift=1):
#    trend_estimates = get_trend_estimates(word_series, start_year=start_year, end_year=end_year)
#    processed = process_trend_estimates(trend_estimates)
#    inc_words = set(processed["increasing"].keys())
    years = range(start_year, end_year)
    new_words = {}
    for word, year_series in word_series.iteritems():
        last_not_pres = -1
        num_not_pres = 0
        pres = []
        for year in years:
            if not year in year_series or year_series[year] <= 0.0 or year_series[year] == float('nan'):
                last_not_pres = max(year, last_not_pres)
                num_not_pres += 1
            else:
                pres.append(year)
        if (float(num_not_pres)/len(years) > not_present_min and float(num_not_pres)/len(years) < not_present_max 
                and last_not_pres < end_year - e_buff and np.min(pres) > start_year + s_buff):
#            pres = [point for point in pres if point <= last_not_pres + 1]
            new_words[word] = np.min(pres)
               # new_words[word] = int((np.min(pres) + last_not_pres + 1) / 2.0)
#            new_words[word] = len(pres)
    return new_words


def get_unsuccessful_new_words(word_series, start_year=1900, end_year=2000, not_present_min=0.25, not_present_max=0.99, s_buff=10, e_buff=10, shift=1):
#    trend_estimates = get_trend_estimates(word_series, start_year=start_year, end_year=end_year)
#    processed = process_trend_estimates(trend_estimates)
#    inc_words = set(processed["increasing"].keys())
    years = range(start_year, end_year)
    new_words = {}
    for word, year_series in word_series.iteritems():
        last_not_pres = -1
        num_not_pres = 0
        pres = []
        for year in years:
            if not year in year_series or year_series[year] <= 0.0 or year_series[year] == float('nan'):
                last_not_pres = max(year, last_not_pres)
                num_not_pres += 1
            else:
                pres.append(year)
        if float(num_not_pres)/len(years) > not_present_min and float(num_not_pres)/len(years) < not_present_max and max(pres) < end_year - e_buff and np.min(pres) > start_year + s_buff:# and word in inc_words:
#            pres = [point for point in pres if point <= last_not_pres + 1]
            new_words[word] = np.min(pres)
    return new_words

def get_dying_words(word_series, start_year=1900, end_year=2000, not_present_min=0.25, not_present_max=0.75, buffer=10):
    trend_estimates = get_trend_estimates(word_series, start_year=start_year, end_year=end_year)
    processed = process_trend_estimates(trend_estimates)
    dec_words = set(processed["decreasing"].keys())
    years = range(start_year, end_year)
    old_words = {}
    for word, year_series in word_series.iteritems():
        last_pres = -1
        num_not_pres = 0
        for year in years:
            if not year in year_series or year_series[year] == 0.0 or year_series[year] == float('nan'):
                num_not_pres += 1
            else:
                last_pres = max(year, last_pres)
        if float(num_not_pres)/len(years) > not_present_min and float(num_not_pres)/len(years) < not_present_max and word in dec_words and last_pres <= end_year - buffer:
            old_words[word] = last_pres
    return old_words

                
def process_trend_estimates(trend_estimates, freq_dict=None, p_value_thresh=0.001, slope_thresh = 0, min_obs = 20):
    narrowing = {}
    broadening = {}
    nochange = {}
    for word, res in trend_estimates.iteritems():
        if res.nobs < min_obs:
            continue
        if freq_dict != None:
            if word in freq_dict:
                freq = freq_dict[word]
            else:
                freq = 0
        else:
            freq = None
        word_info = {"slope" : res.params[1], 
                "intercept" : res.params[0],
                "r2" : res.rsquared,
                "pvalue" : res.pvalues[1],
                "fpvalue" : res.f_pvalue,
                "freq" : freq}
        if word_info["pvalue"] < p_value_thresh and abs(word_info["slope"]) > slope_thresh:
            if word_info["slope"] > 0:
                narrowing[word] = word_info
            else:
                broadening[word] = word_info
        else:
            nochange[word] = word_info

    return {"decreasing" : broadening, "increasing" : narrowing, "nochange" : nochange}

def prune_trend_infos(trend_infos, stat, descending, thresh):
    if stat == None:
        return trend_infos
    if descending:
        mod = 1
    else:
        mod = -1
    return [(word, word_info) for (word, word_info) in trend_infos if word_info[stat]*mod > mod*thresh] 

def sort_trend_infos(trend_infos, stat, descending=True, freq_thresh=None, r2_thresh=0):
    pruned = prune_trend_infos(trend_infos.items(), "r2", True, r2_thresh)
    if freq_thresh != None:
        pruned = prune_trend_infos(pruned, "freq", True, freq_thresh)
    return sorted(pruned, key= lambda (word, word_info) : word_info[stat], reverse=descending)

def get_densefreq_corr(density_trends_p, freq_trends_p, p_value_thresh = 0.001):
    a = []
    b = []
    density_trends = {}
    freq_trends = {}
    for word in density_trends_p:
        if word in freq_trends_p:
            density_trends[word] = density_trends_p[word]
            freq_trends[word] = freq_trends_p[word]
    get_sig_slope = lambda info : info.params[1] if info.pvalues[1] < p_value_thresh else 0
    for word in density_trends.keys(): 
        if density_trends[word].nobs < 20 or freq_trends[word].nobs < 20:
            continue
        a.append(-1 * get_sig_slope(density_trends[word]))
        b.append(get_sig_slope(freq_trends[word]))
    return {"spearman" : sp.stats.spearmanr(a, b), "kendall" : sp.stats.kendalltau(a, b), "pearson" : sp.stats.pearsonr(a, b)}

