import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt
import pickle

def SmoothSpline(x, y, s=240):
	sp = UnivariateSpline(x, y, s=s)
	return sp(x)

def SaveTimeSeries(t, v, filename):
    with open(filename, 'wb') as f:
        pickle.dump((t,v), f, 0)

def LoadTimeSeries(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

x,y = LoadTimeSeries('brightness.pkl')
plt.plot(x, y,'o')
spli = SmoothSpline(x, y)
SaveTimeSeries(x, spli, 'brightness_spline.pkl')
plt.plot(x, spli)

plt.show()

