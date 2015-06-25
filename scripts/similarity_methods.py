import pandas as pd
import numpy as np
from math import sqrt
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error

def getPredResults(df):
    mapeR = mape(df['actual'].values, df['predicted'].values)
    RMSE = sqrt(mean_squared_error(df['actual'].values, df['predicted'].values))
    MAE = mean_absolute_error(df['actual'].values, df['predicted'].values)
    
    return mapeR, RMSE, MAE
    
def getOutliers(df, rr):
    r = calculateSimularity(df, rr)
    
    rr = rr.apply(contro, axis=1, args=[r])
    rr['Momentum'] = rr['Momentum'].astype('datetime64')
    
    return rr

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