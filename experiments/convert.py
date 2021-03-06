import pickle

def LoadTimeSeries(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def ConvertPickleToCSV(name):
    x,y = LoadTimeSeries(name + '.pkl')
    file = open(name + '.csv', 'w')
    file.write('minutes,' + 'values' + '\n')
    for i in range(len(x)):
        file.write(str(x[i]) + ',' + str(y[i]) + '\n')
    file.close()

# ConvertPickleToCSV('biomass')
ConvertPickleToCSV('brightness')
ConvertPickleToCSV('brightness_spline')

