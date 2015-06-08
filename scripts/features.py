import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
#matplotlib inline

def normalizeColumns(df, columns):
    for column in columns:
        '''max_X = df[column].max()
        min_X = df[column].min()
        
        midrange = (max_X+min_X)/2
        Xrange = (max_X-min_X)
        
        df[column] = (df[column] - midrange) / (Xrange/2)'''
        df[column] = (df[column] - df[column].mean())/df[column].std()
    return df

building = '740-NTH' # '761-KMH' #'882-WBW' #'740-NTH'
data = building + '_elektriciteit_withWeather_clean.csv'
path = os.path.dirname( __file__ )
path = os.path.abspath(os.path.join(path, os.pardir))
path = os.path.join(path, 'datasets/' + data).replace('\\', '/')

df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Momentum']) 
df = df.set_index(['Momentum'], drop=False)
df.index = df.index.tz_localize('UTC')#.tz_convert('Europe/Rome')

df['nextDay'] = df['weekDay'].shift(24)

timeFeatures = ['hour', 'weekDay', 'month', 'year', 'dayOfYear', 'nextDay']

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
    
df['gas1HBefore'] = df['gas [m3]'].shift(1)
df['gas2HBefore'] = df['gas [m3]'].shift(2)
df['Tdiff1'] = df['T']-df['T'].shift(1)
df['gasPeak5HBefore'] = pd.stats.moments.rolling_max(df['gas [m3]'].shift(1),5,min_periods=5)
df['gasSum5HBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),5,min_periods=5)
df['gasPeak1DBefore'] = pd.stats.moments.rolling_max(df['gas [m3]'].shift(1),24,min_periods=24)
df['gasSum1DBefore'] = pd.stats.moments.rolling_sum(df['gas [m3]'].shift(1),24,min_periods=24)

df2 = pd.read_csv('datasets/ARIMA_forecast.csv', encoding="utf-8-sig", parse_dates=['Index']) #, names=['Momentum', 'arima', 'arimaHi']
df2.rename(columns={'Index': 'Momentum', 'predicted': 'arima'}, inplace=True)
df2 = df2.set_index('Momentum', drop=False)
df2.index = df2.index.tz_localize('UTC')#.tz_convert('Europe/Rome')

df = df.join(df2[['arima', 'predictedHi']])
df = pd.concat([df[df.arima.notnull()]])
df = df[df.arima.notnull()].sort_index()

# residuals
resid = pd.read_csv('datasets/residuals_year.csv', encoding="utf-8-sig", parse_dates=['Index'])
resid.rename(columns={'Index': 'Momentum', 'remainder': 'residuals'}, inplace=True)
resid = resid.set_index('Momentum', drop=False)
resid.index = resid.index + pd.DateOffset(hours=1)
resid.index = resid.index.tz_localize('UTC')#.tz_convert('Europe/Rome')

df = df.join(resid[['residuals', 'trend']], how="inner", sort=True)
df = df[(df.weekDay.notnull()) & (df.arima.notnull())]
df["index"] = df.index
df.drop_duplicates(cols='index', take_last=True, inplace=True)
del df["index"]

#residuals 3
resid = pd.read_csv('datasets/residuals_day.csv', encoding="utf-8-sig", parse_dates=['Index'])
resid.rename(columns={'Index': 'Momentum', 'remainder':'residualsDays', 'trend': 'trendDays'}, inplace=True)
resid = resid.set_index('Momentum', drop=False)
resid.index = resid.index + pd.DateOffset(hours=1)
resid.index = resid.index.tz_localize('UTC')#.tz_convert('Europe/Rome')

df = df.join(resid[['residualsDays', 'trendDays']])
df = df[(df.weekDay.notnull()) & (df.arima.notnull())]

#residuals electricity
resid = pd.read_csv('datasets/residuals_electricity_day.csv', encoding="utf-8-sig", parse_dates=['Index'])
resid.rename(columns={'Index': 'Momentum', 'remainder':'residualsElectricity'}, inplace=True)
resid = resid.set_index('Momentum', drop=False)
resid.index = resid.index + pd.DateOffset(hours=1)
resid.index = resid.index.tz_localize('UTC')#.tz_convert('Europe/Rome')

df = df.join(resid[['residualsElectricity']])
df = df[(df.weekDay.notnull()) & (df.arima.notnull())]

# memories
df['arimaPeak5HBefore'] = pd.stats.moments.rolling_max(df['arima'].shift(1),5,min_periods=5)
df['arimaSum5HBefore'] = pd.stats.moments.rolling_sum(df['arima'].shift(1),5,min_periods=5)

backtrack = ['elektriciteit [kwh]', 'T', 'gas [m3]']
names = [x+"_peak" for x in backtrack]
for f in backtrack:
    df[f+"_peak"] = pd.stats.moments.rolling_max(df[f].shift(1),5, min_periods=5)
   
toNormalize = ['elektriciteit [kwh]', 'nextDay', 'weekDay', 'month', 'T', 'FH', 'gas1HBefore', 'gas2HBefore', 'arima', 'residuals', 'Tdiff1', 'gasPeak5HBefore', 'gasSum5HBefore','arimaPeak5HBefore','arimaSum5HBefore', 'gasSum1DBefore', 'gasPeak1DBefore', 'residualsDays', 'residuals']
toNormalize.extend(names)
df = normalizeColumns(df, toNormalize)
print df.head()