import collections
import copy

import pandas as pd
import statsmodels.api as sm
import scipy as sp
import numpy as np

def make_data_frame(words, years, feature_dict):
    """
    Makes a pandas dataframe for word, years, and dictionary of feature funcs.
    Each feature func should take (word, year) and return feature value.
    Constructed dataframe has flat csv style structure and missing values are removed.
    """

    temp = collections.defaultdict(list)
    feature_dict["word"] = lambda word, year : word
    feature_dict["year"] = lambda word, year : year
    for word in words:
        for year in years:
            for feature, feature_func in feature_dict.iteritems():
                temp[feature].append(feature_func(word, year))
    df = pd.DataFrame(temp)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    return df

def run_lmm(formula, df, reml=False, **kwargs):
    """
    Wrapper for running a linear mixed model with given formula.
    Inputs defined by statsmodels.
    """
    model = sm.MixedLM.from_formula(formula, df, **kwargs)
    return model.fit(reml=reml)

def marginal_r2(res):
    e_f = np.std(res.model.predict(res.fe_params)) ** 2.0
    e_other = np.std(res.fittedvalues - res.model.endog) ** 2.0
    return e_f / (e_f + e_other)

def like_ratio(null_model, alt_model, df=1):
    """
    Compute the likelihood ratio statistic and corresponding p value btw nested models.
    Really should only be used for single parameter tests.
    """
    D = -2 * (null_model.llf - alt_model.llf)
    return {"D" : D, "p_val" : 1 - sp.stats.chi2.cdf(D, df)}

def simple_slope_percentiles(res, df, target, varying, percs=[25, 50, 75]):
    exog = {}
    for param in res.fe_params.index:
        if len(param.split(":")) != 1:
            continue
        if param == "Intercept":
            exog[param] = 1.0
        else:
            exog[param] = np.median(df[param])
    ret_vals = collections.OrderedDict()
    for varying_perc in percs:
        exog[varying] = np.percentile(df[varying], varying_perc)
        ret_vals[exog[varying]] = collections.defaultdict(list)
        for target_perc in [25, 75]:
            exog[target] = np.percentile(df[target], target_perc)
            exog_arr = np.array([exog[param] if len(param.split(":")) == 1 else exog[param.split(":")[0]] * exog[param.split(":")[1]]
                for param in res.fe_params.index])
            ret_vals[exog[varying]]["endog"].append(res.model.predict(res.fe_params, exog=exog_arr))
            ret_vals[exog[varying]]["target"].append(exog[target])
    return ret_vals

def simple_slope_categories(res, df, target, cat, cats):
    exog = {}
    for param in res.fe_params.index:
        if len(param.split(":")) != 1:
            continue
        if param == "Intercept":
            exog[param] = 1.0
        elif param in cats:
            exog[param] = 0
        else:
            exog[param] = np.mean(df[param])
    if cat != None:
        exog[cat] = 1
    x_points = []
    y_points = []
    for target_perc in [10, 90]:
        exog[target] = np.percentile(df[target], target_perc)
#        exog[target] = target_perc
        exog_arr = np.array([exog[param] if len(param.split(":")) == 1 else exog[param.split(":")[0]] * exog[param.split(":")[1]]
            for param in res.fe_params.index])
        y_points.append(res.model.predict(res.fe_params, exog=exog_arr))
        x_points.append(exog[target])
    return x_points, y_points

def get_marginal_effects(res, df, targets):
    exog = collections.OrderedDict()
    stderrs = collections.OrderedDict()
    stderr_arr = np.sqrt(np.diag(res.cov_params()[0:res.k_fe])) 
    for i, param in enumerate(res.fe_params.index):
        if len(param.split(":")) != 1:
            continue
        if param == "Intercept":
            exog[param] = 1.0
        else:
            exog[param] = np.mean(df[param])
        stderrs[param] = stderr_arr[i]
    ret_vals = {}
    stderr_vals = collections.defaultdict(float)
    for target in targets:
        exog_temp = copy.deepcopy(exog)
        exog_temp[target] = 0
        exog_arr = np.array([exog_temp[param] if len(param.split(":")) == 1 else exog_temp[param.split(":")[0]] * exog_temp[param.split(":")[1]]
            for param in res.fe_params.index])
        at_zero = res.model.predict(res.fe_params, exog=exog_arr)
        exog_temp[target] = 1
        exog_arr = np.array([exog_temp[param] if len(param.split(":")) == 1 else exog_temp[param.split(":")[0]] * exog_temp[param.split(":")[1]]
            for param in res.fe_params.index])
        at_one = res.model.predict(res.fe_params, exog=exog_arr)
        ret_vals[target] = at_one - at_zero
        for param in res.fe_params.index:
            if len(param.split(":")) > 1 and target in param:
                t_params = param.split(":")
                other = t_params[0] if t_params[1] == target else t_params[1]
                stderr_vals[target] += exog[other] * stderrs[other]
        stderr_vals[target] += stderrs[target]
    return ret_vals, stderr_vals

def get_marginal_effect_points(res, df, targets, percentiles=(10, 90)):
    exog = {}
    stderrs = {}
    stderr_arr = np.sqrt(np.diag(res.cov_params()[0:res.k_fe])) 
    for i, param in enumerate(res.fe_params.index):
        if len(param.split(":")) != 1:
            continue
        if param == "Intercept":
            exog[param] = 1.0
        else:
            exog[param] = np.mean(df[param])
        stderrs[param] = stderr_arr[i]
    ret_vals = {}
    stderr_vals = collections.defaultdict(float)
    for target in targets:
        exog_temp = copy.deepcopy(exog)
        exog_arr = np.array([exog_temp[param] if len(param.split(":")) == 1 else exog_temp[param.split(":")[0]] * exog_temp[param.split(":")[1]]
            for param in res.fe_params.index])
        at_zero = res.model.predict(res.fe_params, exog=exog_arr)
        exog_temp[target] = 1
        exog_arr = np.array([exog_temp[param] if len(param.split(":")) == 1 else exog_temp[param.split(":")[0]] * exog_temp[param.split(":")[1]]
            for param in res.fe_params.index])
        at_one = res.model.predict(res.fe_params, exog=exog_arr)
        ret_vals[target] = at_one - at_zero
        for param in res.fe_params.index:
            if len(param.split(":")) > 1 and target in param:
                t_params = param.split(":")
                other = t_params[0] if t_params[1] == target else t_params[1]
                stderr_vals[target] += exog[other] * stderrs[other]
        stderr_vals[target] += stderrs[target]
    return ret_vals, stderr_vals


def get_slopes_stderrs(res):
    stderr_arr = np.sqrt(np.diag(res.cov_params()[0:res.k_fe])) 
    slopes = {}
    stderrs = {}
    for i, param in enumerate(res.fe_params.index):
        slopes[param] = res.fe_params[param]
        stderrs[param] = stderr_arr[i]
    return slopes, stderrs
