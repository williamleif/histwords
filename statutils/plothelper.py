import matplotlib.pyplot as plt
import numpy as np
import scipy as sp

def trendline(xd, yd, order=1, c='r', alpha=1, plot_r=False, text_pos=None):
    """Make a line of best fit"""

    #Calculate trendline
    coeffs = np.polyfit(xd, yd, order)

    intercept = coeffs[-1]
    slope = coeffs[-2]
    if order == 2: power = coeffs[0]
    else: power = 0

    minxd = np.min(xd)
    maxxd = np.max(xd)

    xl = np.array([minxd, maxxd])
    yl = power * xl ** 2 + slope * xl + intercept

    #Plot trendline
    plt.plot(xl, yl, color=c, alpha=alpha)

    #Calculate R Squared
    r = sp.stats.pearsonr(xd, yd)[0]

    if plot_r == False:
        #Plot R^2 value
        if text_pos == None:
            text_pos = (0.9 * maxxd + 0.1 * minxd, 0.9 * np.max(yd) + 0.1 * np.min(yd),)
        plt.text(text_pos[0], text_pos[1], '$R = %0.2f$' % r)
    else:
        #Return the R^2 value:
        return r

def plot_nice_err(x, y, y_err, color='blue', ls='-', lw=1):
   plt.plot(x, y, color=color, ls=ls, lw=lw)
   plt.fill_between(x, y-y_err, y+y_err, alpha=0.1, color=color)

def plot_word_dist(info, words, start_year, end_year, one_minus=False, legend_loc='upper left'):
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    plot_info = {}
    for word in words:
        plot_info[word] = info[word]
    for title, data_dict in plot_info.iteritems():
        x = []; y = []
        for year, val in data_dict.iteritems():
            if year >= start_year and year <= end_year:
                x.append(year)
                if one_minus:
                    val = 1 - val
                y.append(val)
        color = colors.pop()
        plt.plot(x, smooth(np.array(y)), color=color)
        plt.scatter(x, y, marker='.', color=color)
    plt.legend(plot_info.keys(), loc=legend_loc)
    return plt

def get_ccdf(deg_hist, x_min=1):
    cum_counts = [0]
    degs = range(x_min, np.max(deg_hist.keys()))
    total_sum = 0
    for deg in degs:
        if deg in deg_hist:
            deg_count = deg_hist[deg]
        else:
            deg_count = 0
        total_sum += deg_count
        cum_counts.append((cum_counts[-1] + deg_count))
    return np.array(degs), 1 - np.array(cum_counts[1:]) / float(total_sum)

def plot_word_basic(info, words, start_year, end_year, datatype):
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    plot_info = {}
    for word in words:
        plot_info[word] = info[word]
    for title, data_dict in plot_info.iteritems():
        x = []; y = []
        for year, val in data_dict[datatype].iteritems():
            if year >= start_year and year <= end_year:
                x.append(year)
                y.append(val)
        color = colors.pop()
        plt.plot(x, smooth(np.array(y)), color=color)
        plt.scatter(x, y, marker='.', color=color)
    plt.legend(plot_info.keys())
    plt.show()
 
def plot_basic(plot_info, start_year, end_year):
    for title, data_dict in plot_info.iteritems():
        x = []; y = []
        for year, val in data_dict.iteritems():
            if year >= start_year and year <= end_year:
                x.append(year)
                y.append(val)
        plt.plot(x, y)
    plt.legend(plot_info.keys())
    plt.show()

def plot_smooth(x, y, color='blue', window_len=7, window='hanning', ax=None, lw=1.0, ls="-", **kwargs):
    if ax == None:
        _, ax = plt.subplots(1,1)
    ax.plot(x, smooth(np.array(y), window_len=window_len), color=color, lw=lw, ls=ls)
    ax.scatter(x, y, color=color, **kwargs)
    return ax

def smooth(x, window_len=7, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    y = y[(window_len/2 - 1):-(window_len/2 + 1)]
    return y
