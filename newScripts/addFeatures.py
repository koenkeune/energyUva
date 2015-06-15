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
    resElecPath = os.path.join(root, 'datasets', 'residuals_electricity_day.csv')
    
    df = addTimeFeatures(df)
    df = addGasFeatures(df)
    df = addArima(df, arimaPath)
    df = addResidualsYear(df, resYearPath)
    df = addResidualsDay(df, resDayPath)
    df = addResidualsElectricity(df, resElecPath)
    df = addArimaHistory(df)
    df, peakColumns = addPeaks(df)
    
    toNormalize = ['elektriciteit [kwh]', 'nextDay', 'weekDay', 'month', 'T', \
    'FH', 'gas1HBefore', 'gas2HBefore', 'arima', 'residuals', 'Tdiff1', \
    'gasPeak5HBefore', 'gasSum5HBefore','arimaPeak5HBefore','arimaSum5HBefore'\
    , 'gasSum1DBefore', 'gasPeak1DBefore', 'residualsDays', 'residuals']
    
    toNormalize.extend(peakColumns)
    df = normalizeColumns(df, toNormalize)
    df = normalizeColumns(df,['hour', 'weekDay', 'month', 'dayOfYear', 'nextDay'])
    
    return df


def addTimeFeatures(df): # missing date feature compared to Marco's
    timeFeatures = ['hour', 'weekDay', 'month', 'year', 'dayOfYear', 'nextDay']
    
    df['nextDay'] = df['weekDay'].shift(24)
    
    for tf in timeFeatures:
        if tf != 'weekDay' and tf != 'nextDay':
            df[tf] = 0
            
        df['sin' + tf.title()] = 0
        df['cos' + tf.title()] = 0
        
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayOfYear'] = df.index.dayofyear

    for tf in timeFeatures:
        maximum = df[tf].max()
        df['sin' + tf.title()] = np.sin(2*np.pi*df[tf]/maximum)
        df['cos' + tf.title()] = np.cos(2*np.pi*df[tf]/maximum)
    
    return df
    
def addGasFeatures(df):
    df['gas1HBefore'] = df['gas [m3]'].shift(1)
    df['gas2HBefore'] = df['gas [m3]'].shift(2)
    df['Tdiff1'] = df['T']-df['T'].shift(1)
    df['gasPeak5HBefore'] = pd.stats.moments.rolling_max(df['gas [m3]'].shift(1),5,min_periods=5)
    df['gasSum5HBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),5,min_periods=5)
    df['gasPeak1DBefore'] = pd.stats.moments.rolling_max(df['gas [m3]'].shift(1),24,min_periods=24)
    df['gasSum1DBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),24,min_periods=24)
    
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
    
def addResidualsElectricity(df, path):
    resid = pd.read_csv('datasets/residuals_electricity_day.csv', encoding="utf-8-sig", parse_dates=['Index'])
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
    backtrack = ['elektriciteit [kwh]', 'T', 'gas [m3]']
    names = [x+"_peak" for x in backtrack]
    for f in backtrack:
        df[f+"_peak"] = pd.stats.moments.rolling_max(df[f].shift(1),5, min_periods=5)
    
    return df
    
def addPeaks(df):
    backtrack = ['elektriciteit [kwh]', 'T', 'gas [m3]']
    peakColumns = [x+"_peak" for x in backtrack]
    for f in backtrack:
        df[f+"_peak"] = pd.stats.moments.rolling_max(df[f].shift(1),5, min_periods=5)
        
    return df, peakColumns

def normalizeColumns(df, columns):
    for column in columns:
        df[column] = (df[column] - df[column].mean())/df[column].std()
    
    return df