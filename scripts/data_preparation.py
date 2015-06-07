import os
import pandas as pd
import numpy as np
import time
import datetime
from pylearn2.utils.track_version import LibVersion

def mergeWithHolidays(s):
    dateString = "%04d-%02d-%02d" % (s['Momentum'].year, s['Momentum'].month, s['Momentum'].day)
    weekday = 6
    if dateString not in holidays:
        weekday = s['Momentum'].weekday()
    s['weekDay'] = weekday
    
    return s
    
def mergeWithForecasts(s):
    dateString = "%04d%02d%02d" % (s['Momentum'].year, s['Momentum'].month, s['Momentum'].day)
    selected = ff[(ff.YYYYMMDD == dateString) & (ff.HH == s['Momentum'].hour)]
    
    s['T'] = selected['T'].values[0]
    s['FH'] = selected['FH'].values[0]
    # the humidity is percentual
    s['U'] = selected['U'].values[0]/100
    s['N'] = selected['N'].values[0]
    s['Q'] = selected['Q'].values[0]
    
    return s

# pc info:
#libv = LibVersion()
#libv.print_versions()
#libv.print_exp_env_info()

t = time.time()

data = 'test.csv'
path = os.path.dirname( __file__ )
path = os.path.abspath(os.path.join(path, os.pardir))
df = pd.read_csv(os.path.join(path, 'datasets/' + data).replace('\\', '/'))

building = '740-NTH' # select only one building

df = df[(df.filename == building) & ((df['gas [m3]'].notnull()) | (df['elektriciteit [kwh]'].notnull()))]

columnsToRemove = ['-1 tot 1e verdieping [m3]', '2 tot 6e verdieping [m3]', 'warmtemeter [kwh]', 'warmte aeq [m3]', 'warmtemeter [m3]', 'elektriciteit liander [kwh]', 'hvi-1 trafo 1 [kwh]', 'hvi-2 trafo 2 [kwh]', 'k1-3 keuken [kwh]', 'k1-4 repro [kwh]', 'koelmachine airco [kwh]', 'koelmachine mer [kwh]', 'kwh-meter [kwh]', 'lk04-mer bg [kwh]', 'ovi parkeergarage [kwh]', 'schoolgebouw [m3]', 'weesperzijde 190 [kwh]', 'totaal', 'rk5 - lbk nw [kwh]', 'rk4 - lbk zw - zonnecollectoren [kwh]', 'rk3 - lbk no - zo [kwh]', 'rk2 - lbk keuken, rest. [kwh]', 'rk-1 stadsverwarming [kwh]', 'parkeergarage [m3]', 'parkeergarage (tot mei 2013) [kwh]']
df = df.drop(columnsToRemove, 1)
df = df.rename(columns={'Unnamed: 0': 'Momentum'})
df = df[df['Momentum'].notnull()]
df['Momentum'] = df['Momentum'].astype('datetime64')
df = df.set_index('Momentum', drop=False)

# There is an implicit conversion of timezone. I need to fix it.
df.index = df.index + pd.DateOffset(hours=1)
del df['Momentum']
df['Momentum'] = df.index

df = df.resample('H',how='sum') # look at hourly data
df['Momentum'] = df.index
df['elektriciteit [kwh]'] = df['elektriciteit [kwh]'].shift(1) # consumption of the last hour
df = df[df['gas [m3]'].notnull()][['Momentum', 'gas [m3]', 'elektriciteit [kwh]']]


### Holidays implementation
df['weekDay'] = 0
data2 = 'holidays.csv'
holidays = pd.read_csv(os.path.join(path, 'datasets/' + data2).replace('\\', '/')).values

df = df.apply(mergeWithHolidays, 1)

### Weather forecasts implementation
data3 = 'KNMI_weatherdata[2008-2014].csv'
ff = pd.read_csv(os.path.join(path, 'datasets/' + data3).replace('\\', '/'), sep=';')

columns = ff.columns
columns = [x.strip() for x in columns]
ff.columns = columns
ff = ff[['YYYYMMDD', 'HH', 'FH', 'T', 'U', 'N', 'Q']]
ff[['YYYYMMDD']] = ff[['YYYYMMDD']].astype(str)
ff[['U']] = ff[['U']].astype(float)
#HH is from 1 to 24
ff['HH'] = ff['HH']-1
#humidity is in percentage
ff.head()

df['T'] = 0
df['FH'] = 0
df['U'] = 0
df['N'] = 0
df['Q'] = 0

df = df.apply(mergeWithForecasts, 1)


newFile = os.path.join(path, 'datasets/' + building + '_holidayTest.csv').replace('\\', '/')
df[df['elektriciteit [kwh]'].notnull()].to_csv(newFile, index=False)

print time.time() - t