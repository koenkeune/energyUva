import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
from scipy import stats
from datetime import date, timedelta, datetime
from dataset_analysis import plot
import matplotlib.pyplot as plt


def getResults(path1, path2, path3):
    df = pd.read_csv(path1, parse_dates=['Momentum'])
    df = df.set_index(['Momentum'], drop=False)
    
    test = pd.read_csv(path2)
    rr = pd.read_csv(path3, names=["predicted"])
    rr['actual'] = test['gas [m3]'].values
    rr['Momentum'] = test['Momentum'].values
    rr = rr.set_index('Momentum', drop=False)

    print "MAPE: ", mape(rr['actual'].values, rr['predicted'].values)
    print "RMSE: ", sqrt(mean_squared_error(rr['actual'].values, rr['predicted'].values))
    print "MAE: ", mean_absolute_error(rr['actual'].values, rr['predicted'].values) 
    
    r = calculateSimularity(df, rr)
    
    rr = rr.apply(contro, axis=1, args=[r])
    
    plot(df, 2008, 2008, 3, 3, 17, 22, 'gas [m3]')
    
    outliers = findOutliers(rr)
    
    plotOutliers(outliers, 5)

def mape(actual, predicted):
    actual, predicted = nonZeroValues(actual, predicted)
    return np.mean(np.divide(np.abs(np.array(actual) - np.array(predicted)), np.array(actual))) * 100
    
def nonZeroValues(actual, predicted):
    actual = np.array(actual)
    indexes = np.where(actual == 0)[0]

    actual = [v for i,v in enumerate(actual) if i not in frozenset(indexes)]
    predicted = [v for i,v in enumerate(predicted) if i not in frozenset(indexes)] 
    
    return (actual, predicted)    
    
def calculateSimularity(df, dfR):
    dfR['outlier'] = 0
    rmse = sqrt(mean_squared_error(dfR['actual'].values, dfR['predicted'].values))

    n = df['gas [m3]'].count()
    n = dfR['actual'].count()
    c1, c2 = stats.chi2.ppf([0.025,1-0.025],n)
    l = sqrt(n/c2)*rmse
    r = sqrt(n/c1)*rmse

    err = sqrt(mean_squared_error(dfR['actual'].values, dfR['predicted'].values))

    print l, " ", r, " err:", err, " ", c1, " ", c2
    
    return r
    
def contro(s, r):
    if abs(s['predicted']-s['actual']) > r*4.0:
        s['outlier'] = s['actual']
    else:
        s['outlier'] = -1
    return s
    
def findOutliers(df):
    df['Momentum'] = df['Momentum'].astype('datetime64')
    foundOutliers = df[df.outlier > -1]
    
    outliers = []
    for index, outlier in foundOutliers.iterrows():
        d_from = outlier['Momentum'] - timedelta(days=2)
        d_to = outlier['Momentum'] + timedelta(days=2)
        df_o = df[(df.Momentum > d_from) & (df.Momentum < d_to)].copy()
        outliers.append(df_o)
        
    print 'outliers found: ' + str(len(foundOutliers))
    
    return outliers
    
def plotOutliers(outliers, max):
    if len(outliers) > max:
        end = max
    else:
        end = len(outliers)
    
    for i in xrange(0, end):
        outlierIndex = []
        for j in xrange(len(outliers[i]['outlier'])):
            if outliers[i]['outlier'][j] > -1:
                outlierIndex.append(j)
                
        
        predictedValues = outliers[i]['predicted']
        actualValues = outliers[i]['actual']

        time = outliers[i]['Momentum'].index.values.astype('datetime64')
        time = time.astype(datetime)
        
        plt.plot(time, predictedValues, '--')
        plt.plot(time, actualValues, 'k-')
        
        outlierPoints = outliers[i]['outlier'].iloc[outlierIndex]
        timePoints = outliers[i]['outlier'].iloc[outlierIndex].index.values.astype('datetime64')
        timePoints = timePoints.astype(datetime)
        
        plt.plot(timePoints, outlierPoints, 'o')
        
        plt.show()