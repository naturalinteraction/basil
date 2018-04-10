import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy.polynomial.polynomial as poly
from utility import LoadTimeSeries

def smooth(x,window_len=11,window='hanning'):
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
                w=eval('np.'+window+'(window_len)')
        y=np.convolve(w/w.sum(),s,mode='same')
        return y[window_len:-window_len+1]

WL = 15

def testHanning (x,y):
    smoothed = smooth(np.array(y),window_len=WL, window='hanning')
    plt.plot(x, smoothed, '-')

def testHamming (x,y):
    smoothed = smooth(np.array(y),window_len=WL, window='hamming')
    plt.plot(x, smoothed, '-')

def testBartlett (x,y):
    smoothed = smooth(np.array(y),window_len=WL, window='bartlett')
    plt.plot(x, smoothed, '-')

def testBlackman (x,y):
    smoothed = smooth(np.array(y),window_len=WL, window='blackman')
    plt.plot(x, smoothed, '-')

def testFlat (x,y):
    smoothed = smooth(np.array(y),window_len=WL, window='flat')
    plt.plot(x, smoothed, '-')

def testPoly(x, y):
    coefs = poly.polyfit(x, y, 4)
    ffit = poly.polyval(x, coefs)
    plt.plot(x, ffit, '-')

def testLowess(x, y):
    lowess = sm.nonparametric.lowess(y, x, frac=.3)
    lowess_x = list(zip(*lowess))[0]
    lowess_y = list(zip(*lowess))[1]
    plt.plot(lowess_x, lowess_y, '-')

def testGauss(x, y):
	b = gaussian(19, 20)
	ga = filters.convolve1d(y, b/b.sum())
	plt.plot(x, ga, '-')

def testWiener(x, y):
	wi = wiener(y, mysize=15, noise=1000000)
	plt.plot(x, wi, '-')

def testSpline(x, y):
	sp = UnivariateSpline(x, y, s=4240)
	plt.plot(x, sp(x), '-')

x,y = LoadTimeSeries('time-series.pkl')

plt.plot(x,y,'o')

testSpline(x, y)
'''
testGauss(x, y)
testWiener(x, y)
testSpline(x, y)
testLowess(x, y)
testHanning(x, y)
testHamming(x, y)
testBlackman(x, y)
testBartlett(x, y)
testFlat(x, y)
testPoly(x, y)
'''
plt.show()

