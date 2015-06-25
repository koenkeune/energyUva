import pandas as pd
from datetime import timedelta, datetime
#from dataset_analysis import plot2, plot
import matplotlib.pyplot as plt
from similarity_methods import getPredResults, getOutliers
import numpy as np
from operator import methodcaller

def getResults(dfPath, testPath, predictionPath):
    df = pd.read_csv(dfPath, parse_dates=['Momentum'])
    df = df.set_index(['Momentum'], drop=False)
    
    test = pd.read_csv(testPath)
    
    rows = np.random.choice(test.index.values, 3)
    sampled_df = df.ix[rows]
    
    
    y = df.ix[rows[0]]['Momentum'].year
    m = df.ix[rows[0]]['Momentum'].month
    d = df.ix[rows[0]]['Momentum'].day
    h = df.ix[rows[0]]['Momentum'].hour
    
    #print (y,m,d,h)
    
    rr = pd.read_csv(predictionPath, names=["predicted"])
    rr['actual'] = test['gas [m3]'].values
    rr['Momentum'] = test['Momentum'].values
    rr = rr.set_index('Momentum', drop=False)
    
    
    
    (mape, rmse, mae) = getPredResults(rr)
    print "MAPE: ", mape
    print "RMSE: ", rmse
    print "MAE: ", mae
    
    rr  = getOutliers(df, rr)
    
    
    anomalyDates = []
    
    for i in xrange(len(rows)):
        anomalyDates.append(rows[i]))
    
    
    plotOutliers(rr, anomalyDates, 10)
    
    
    
    #plot2(rr, 2014, 2014, 2, 2, 3, 10, 'predicted' ,'actual')
    
    #rr.to_csv('rr.csv')
    
    # peakDates = [(2013,5,21,4), (2013,7,6,19), (2013,8,23,6), 
    # (2013,11,13,01), (2013,12,25,14), (2014,1,20,17)]
    # anomalyDates = []
    
    # for i in xrange(len(peakDates)):
        # (y,m,d,h) = peakDates[i]
        # anomalyDates.append(pd.tseries.tools.to_datetime(datetime(y,m,d,h)))

    
        
def findOutlierDates(df, anomalyDates):
    if anomalyDates:
        foundOutliers = df[df.Momentum == anomalyDates[0]]
        if len(anomalyDates) > 1:
            for i in xrange(1, len(anomalyDates)):
                foundOutlierRow = df[df.Momentum == anomalyDates[i]]
                foundOutliers = foundOutliers.append(foundOutlierRow)
    else:
        foundOutliers = df[df.outlier > -1]
        
    if anomalyDates:
        print 'anomalies found: ' + str(len(foundOutliers)) + ' out of ' + \
        str(len(anomalyDates))
    else:
        print 'outliers found: ' + str(len(foundOutliers))
    
    return foundOutliers
    
def findOutliersTimeFrame(df, anomalyDates):

    foundOutliers = findOutlierDates(df, anomalyDates)
    
    outliersTimeFrame = []
    for _, outlier in foundOutliers.iterrows():
        d_from = outlier['Momentum'] - timedelta(days=2)
        d_to = outlier['Momentum'] + timedelta(days=2)
        df_o = df[(df.Momentum > d_from) & (df.Momentum < d_to)]
        outliersTimeFrame.append(df_o)
    
    return outliersTimeFrame
    
def plotOutliers(rr, anomalyDates, max):
    outliersTF = findOutliersTimeFrame(rr, anomalyDates)

    if len(outliersTF) > max:
        end = max
    else:
        end = len(outliersTF)
    
    for i in xrange(0, end):
        outlierIndices = []
        
        for j in xrange(len(outliersTF[i]['outlier'])):
            if outliersTF[i]['outlier'][j] > -1:
                outlierIndices.append(j)
                
        predictedValues = outliersTF[i]['predicted']
        actualValues = outliersTF[i]['actual']

        time = outliersTF[i]['Momentum'].index.values.astype('datetime64')
        time = time.astype(datetime)
        
        plt.plot(time, predictedValues, '--')
        plt.plot(time, actualValues, 'k-')
        
        outlierPoints = outliersTF[i]['outlier'].iloc[outlierIndices]
        timePoints = outliersTF[i]['outlier'].iloc[outlierIndices].index.values.astype('datetime64')
        
        
        ax = plt.plot(timePoints, outlierPoints, 'o')
        plt.ylabel('Gas [m3]')
        plt.xlabel('Time (in hours)')
        plt.title(str(anomalyDates[i])) # only if plotting outliers
        #plt.show()