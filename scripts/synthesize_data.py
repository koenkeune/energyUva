import pandas as pd
from datetime import timedelta, datetime

def createSyntheticData(path, anomalies):
    df = pd.read_csv(path, parse_dates=['Momentum'])
    df = df.set_index(['Momentum'], drop=False)
    
    
    #anomalies = [(2013,5,21,4), (2013,7,6,19), (2013,8,23,6), 
    #(2013,11,13,01), (2013,12,25,14), (2014,1,20,17)]
    for i in xrange(len(peakDates)):
        df = addPeak(df, peakDates[i], 50)
    
    # for i in xrange(len(peakDates)):
        # df = addPeak(df, peakDates[i], -50)
    
    
    #df = addReturningPeaks(df, (2008, 01, 21, 06), 'years', 2, 1, 10)
    #df = addPeakExtendedTime(df, (2008, 01, 21, 06), 'weeks', 2, 10)
    #df = addLinearFunction(df, (2008, 01, 21, 06), 'weeks', 2, 0.1)
    
    return df

def addTransition(df, (y1, m1, d1, h1), (y2, m2, d2, h2), transitionTime):
    
    division = transitionTime + 1
    
    for i in xrange(1, division):
        addPeak(df, (y1, m1, d1, h1 - i), x/division)
        addPeak(df, (y2, m2, d2, h2 + i), x/division)
    
def addPeak(df, startDate, x):

    return synthesize(df, startDate, 'hours', 1, 1, x, False)
    
def addPeakExtendedTime(df, (y, m, d, h), timeUnit, timePeriod, x):
    timePeriod = calcHours((y, m, d, h), timeUnit, timePeriod)

    return synthesize(df, (y, m, d, h), 'hours', timePeriod, 1, x, False)

def addReturningPeaks(df, startDate, timeUnit, numberOfTimes, stepSize, x):

    return synthesize(df, startDate, timeUnit, numberOfTimes, stepSize, x, False)
    
def addLinearFunction(df, (y, m, d, h), timeUnit, numberOfTimes, a):
    numberOfTimes = calcHours((y, m, d, h), timeUnit, numberOfTimes)
    synthesize(df, (y, m, d, h), 'hours', numberOfTimes, 1, a, True)

    return df
    
def calcHours((y, m, d, h), timeUnit, timePeriod):
    
    if timeUnit == 'years':
        numberOfHours = (datetime(y+timePeriod, m, d, h) - datetime(y, m, d, h)).days * 24
    elif timeUnit == 'weeks':
        numberOfHours = timePeriod * 24 * 7
    elif timeUnit == 'days':
        numberOfHours = timePeriod * 24
        
    return numberOfHours
    
def synthesize(df, (y, m, d, h), timeUnit, numberOfTimes, stepSize, x, linear):
    date = datetime(y, m, d, h)
    
    for i in xrange(numberOfTimes):
        print date
        print df['gas [m3]'][date]
        df['gas [m3]'][date]
        if linear:
            df['gas [m3]'][date] += i * x
        else:
            df['gas [m3]'][date] += x
        if df['gas [m3]'][date] < 0:
            df['gas [m3]'][date] = 0
        print df['gas [m3]'][date]
        
        if timeUnit == 'years':
            y += 1
            date = datetime(y, m, d, h)
        elif timeUnit == 'weeks':
            date += timedelta(weeks = stepSize)
        elif timeUnit == 'days':
            date += timedelta(days = stepSize)
        elif timeUnit == 'hours':
            date += timedelta(hours = stepSize)

    return df