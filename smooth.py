import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt
import statsmodels.api as sm  # deprecated: used by SmoothLowess() only
import numpy.polynomial.polynomial as poly
from utility import LoadTimeSeries

def smoothWithMovingWindow(x,window_len=11,window='hanning'):  # used by SmoothHanning() etc.
        if x.ndim != 1:
                raise ValueError, "smooth only accepts 1 dimension arrays."
        if x.size < window_len:
                raise ValueError, "Input vector needs to be bigger than window size."
        if window_len<3:
                return x
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
        if window == 'flat': #moving average
                w=np.ones(window_len,'d')
        else:  
                w=eval('np.'+window+'(window_len)')  # todo: useful to choose a function based on a string
        y=np.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]

WL = 15

def SmoothHanning (x,y):
    smoothed = smoothWithMovingWindow(np.array(y),window_len=WL, window='hanning')
    return smoothed

def SmoothHamming (x,y):
    smoothed = smoothWithMovingWindow(np.array(y),window_len=WL, window='hamming')
    return smoothed

def SmoothBartlett (x,y):
    smoothed = smoothWithMovingWindow(np.array(y),window_len=WL, window='bartlett')
    return smoothed

def SmoothBlackman (x,y):
    smoothed = smoothWithMovingWindow(np.array(y),window_len=WL, window='blackman')
    return smoothed

def SmoothFlat (x,y):
    smoothed = smoothWithMovingWindow(np.array(y),window_len=WL, window='flat')
    return smoothed

def SmoothPoly(x, y):
    coefs = poly.polyfit(x, y, 4)  # no change with >4
    return poly.polyval(x, coefs)

def SmoothLowess(x, y):
    lowess = sm.nonparametric.lowess(y, x, frac=.3)
    lowess_x = list(zip(*lowess))[0]
    lowess_y = list(zip(*lowess))[1]
    return (lowess_x, lowess_y)

def SmoothGauss(x, y):
	b = gaussian(19, 20)
	return filters.convolve1d(y, b/b.sum())

def SmoothWiener(x, y):
	return wiener(y, mysize=15, noise=1000000)

def SmoothSpline(x, y):
	sp = UnivariateSpline(x, y, s=240)  # 4240
	return sp(x)

'''
x,y = LoadTimeSeries('time-series.pkl')
plt.plot(x, y,'o')

plt.plot(x, SmoothSpline(x, y))
(lx,ly) = SmoothLowess(x, y)
plt.plot(lx, ly)
plt.plot(x, SmoothPoly(x, y))
plt.plot(x, SmoothHanning(x, y))
plt.plot(x, SmoothHamming(x, y))
plt.plot(x, SmoothBlackman(x, y))
plt.plot(x, SmoothBartlett(x, y))
plt.plot(x, SmoothFlat(x, y))
plt.plot(x, SmoothGauss(x, y))
plt.plot(x, SmoothWiener(x, y))

plt.show()
'''
