import pandas as pd
import numpy as np
import os

def addAllFeatures(path):
    df = pd.read_csv(path, parse_dates=['Momentum'])
    df = df.set_index(['Momentum'], drop=False)
    df.index = df.index.tz_localize('UTC')
    
    root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir))
    arimaPath = os.path.join(root, 'datasets', 'ARIMA_forecast.csv')
    resYearPath = os.path.join(root, 'datasets', 'residuals_year.csv')
    resDayPath = os.path.join(root, 'datasets', 'residuals_day.csv')
    resWeekPath = os.path.join(root, 'datasets', 'residuals_week.csv')
    resElecPath = os.path.join(root, 'datasets', 'residuals_electricity_day.csv')
    
    df['T_noNorm'] = df['T']
    
    df = addTimeFeaturesBasic(df)
    df = addTimeFeatures(df)
    df = addTimeFeatures2(df)    
    df = addGasFeatures(df)
    df = addArima(df, arimaPath)
    df = addResidualsYear(df, resYearPath)
    df = addResidualsDay(df, resDayPath)
    df = addResidualsWeek(df, resWeekPath)
    df = addResidualsElectricity(df, resElecPath)
    df = addArimaHistory(df)
    df, peakColumns = addPeaks(df)
    df, meanColumns = addMeans(df)
    
    toNormalize = ['elektriciteit [kwh]', 'nextDay', 'weekDay', 'month', 'T', \
    'FH', 'gas1HBefore', 'gas2HBefore', 'arima', 'residuals', 'Tdiff1', \
    'gas1DBefore', 'gasSum5HBefore','arimaPeak5HBefore','arimaSum5HBefore'\
    , 'gasSum1DBefore', 'gasPeak1DBefore', 'residualsDays', 'residuals', \
    'gasMean15DBefore', 'gas1WBefore']
    
    toNormalize.extend(peakColumns)
    toNormalize.extend(meanColumns)
    df = normalizeColumns(df, toNormalize)
    #df = normalizeColumns(df,['hour', 'weekDay', 'month', 'dayOfYear', 'nextDay'])
    
    return df[(df['gas [m3]'].notnull()) & (df["T_noNorm_mean"].notnull()) & \
    (df['nextDay'].notnull()) & (df['arimaPeak5HBefore'].notnull()) & (df.\
    residualsWeekDays.notnull()) & (df.residuals.notnull()) & (df\
    ['gasMean15DBefore'].notnull()) & (df['gas1WBefore'].notnull())]
    
def addTimeFeaturesBasic(df):
    df['date'] = df.index.date   
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayOfYear'] = df.index.dayofyear
    df['nextDay'] = df['weekDay'].shift(24)   
    df['weekDay2'] = df['weekDay']
    df = df.apply(convertToOnes, axis=1)
    
    return df

def convertToOnes(s):
    if s['weekDay2'] > 1:
        s['weekDay2'] = 1
    return s    
    
def addTimeFeatures(df):
    timeFeatures = ['hour', 'weekDay', 'month', 'year', 'dayOfYear', 'nextDay']
    
    for tf in timeFeatures:
        maximum = df[tf].max()
        df['sin' + tf.title()] = np.sin(2*np.pi*df[tf]/maximum)
        df['cos' + tf.title()] = np.cos(2*np.pi*df[tf]/maximum)
    
    return df
    
    # calculates hottest moment
def addTimeFeatures2(df): # per year would be better
    maxDay = df['dayOfYear'].max()
    maxMonth = df['month'].max()
    maxHour = df['hour'].max()
    peakDay = df['dayOfYear'][df['T'].idxmax()]
    peakMonth = maxDay * maxMonth / maxDay
    peakHour = 18
    
    df['cosDayOfYear2'] = np.cos(2*np.pi* df['dayOfYear'] / maxDay - (2*np.pi*(peakDay+1) / maxDay))
    df['cosMonth2'] = np.cos(2*np.pi* df['month'] / maxMonth - (2*np.pi*(peakMonth+1) / maxMonth))
    df['cosHour2'] = np.cos(2*np.pi* df['hour'] / maxHour - (2*np.pi*peakHour / maxHour))
    
    return df
    
def addGasFeatures(df):
    df['gas1HBefore'] = df['gas [m3]'].shift(1)
    df['gas2HBefore'] = df['gas [m3]'].shift(2)
    df['gas1DBefore'] = df['gas [m3]'].shift(24)
    df['gas1WBefore'] = df['gas [m3]'].shift(168)
    df['Tdiff1'] = df['T']-df['T'].shift(1)
    df['gasSum5HBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),5,min_periods=5)
    df['gasPeak1DBefore'] = pd.stats.moments.rolling_max(df['gas [m3]'].shift(1),24,min_periods=24)
    df['gasSum1DBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),24,min_periods=24)
    df['gasMean15DBefore'] = pd.stats.moments.rolling_mean(df['gas [m3]'].shift(1),360,min_periods=360)
    
    return df
    
def addArima(df, path):
    df2 = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Index'])
    df2.rename(columns={'Index': 'Momentum', 'predicted': 'arima'}, inplace=True)
    df2 = df2.set_index('Momentum', drop=False)
    df2.index = df2.index.tz_localize('UTC')

    df = df.join(df2[['arima', 'predictedHi']])
    df = pd.concat([df[df.arima.notnull()]])
    
    return df[df.arima.notnull()].sort_index()
    
def addResidualsYear(df, path):
    resid = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Index'])
    resid.rename(columns={'Index': 'Momentum', 'remainder': 'residuals'}, inplace=True)
    resid = resid.set_index('Momentum', drop=False)
    resid.index = resid.index + pd.DateOffset(hours=1)
    resid.index = resid.index.tz_localize('UTC')

    df = df.join(resid[['residuals', 'trend']], how="inner", sort=True)
    df = df[(df.weekDay.notnull()) & (df.arima.notnull())]
    df["index"] = df.index
    df.drop_duplicates(subset='index', take_last=True, inplace=True)
    del df["index"]
    
    return df
    
def addResidualsDay(df, path):
    resid = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Index'])
    resid.rename(columns={'Index': 'Momentum', 'remainder':'residualsDays', 'trend': 'trendDays'}, inplace=True)
    resid = resid.set_index('Momentum', drop=False)
    resid.index = resid.index + pd.DateOffset(hours=1)
    resid.index = resid.index.tz_localize('UTC')

    df = df.join(resid[['residualsDays', 'trendDays']])
    
    return df[(df.weekDay.notnull()) & (df.arima.notnull())]
    
def addResidualsWeek(df, path):
    resid = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Index'])
    resid.rename(columns={'Index': 'Momentum', 'remainder':'residualsWeekDays', 'trend': 'trendWeekDays'}, inplace=True)
    resid = resid.set_index('Momentum', drop=False)
    resid.index = resid.index + pd.DateOffset(hours=1)
    resid.index = resid.index.tz_localize('UTC')

    df = df.join(resid[['residualsWeekDays', 'trendWeekDays']])
    
    return df[(df.weekDay.notnull()) & (df.arima.notnull())]
    
def addResidualsElectricity(df, path):
    resid = pd.read_csv('datasets/residuals_electricity_day2.csv', encoding="utf-8-sig", parse_dates=['Index'])
    resid.rename(columns={'Index': 'Momentum', 'remainder':'residualsElectricity'}, inplace=True)
    resid = resid.set_index('Momentum', drop=False)
    resid.index = resid.index + pd.DateOffset(hours=1)
    resid.index = resid.index.tz_localize('UTC')
    
    df = df.join(resid[['residualsElectricity']])
        
    return df[(df.weekDay.notnull()) & (df.arima.notnull())]
    
def addArimaHistory(df):
    df['arimaPeak5HBefore'] = pd.stats.moments.rolling_max(df['arima'].shift(1),5,min_periods=5)
    df['arimaSum5HBefore'] = pd.stats.moments.rolling_sum(df['arima'].shift(1),5,min_periods=5)
    
    return df
    
def addPeaks(df):
    backtrack = ['elektriciteit [kwh]', 'T', 'gas [m3]', 'T_noNorm']
    peakColumns = [x+"_peak" for x in backtrack]
    for f in backtrack:
        df[f+"_peak"] = pd.stats.moments.rolling_max(df[f].shift(1),5, min_periods=5)
        
    return df, peakColumns
    
def addMeans(df):
    backtrack = ['elektriciteit [kwh]', 'T', 'gas [m3]', 'T_noNorm']
    meanColumns = [x+"_mean" for x in backtrack]
    for f in backtrack:
        df[f+"_mean"] = pd.stats.moments.rolling_mean(df[f].shift(1),5, min_periods=5)
        
    return df, meanColumns

def normalizeColumns(df, columns):
    for column in columns:
        df[column] = (df[column] - df[column].mean())/df[column].std()
    
    return df