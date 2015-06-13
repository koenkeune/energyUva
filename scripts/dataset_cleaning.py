import pandas as pd
import time
import os

t = time.time()

building = '740-NTH' #'761-KMH' #'882-WBW'
data = building + '_elektriciteit_withWeather.csv'
path = os.path.dirname( __file__ )
path = os.path.abspath(os.path.join(path, os.pardir))
df = pd.read_csv(os.path.join(path, 'datasets/' + data).replace('\\', '/'))

df['Momentum'] = df['Momentum'].astype('datetime64')
df = df.set_index('Momentum', drop=False)

# There is an implicit conversion of timezone. I need to fix it.
df.index = df.index + pd.DateOffset(hours=1)
del df['Momentum']
df['Momentum'] = df.index

if(building == '761-KMH'):
    df = df[(df.Momentum >= datetime.date(2009,01,01)) & (df.Momentum < datetime.date(2013,9,1))]

# Fix duplicated and missing rows to make ARIMA possible
idx = pd.date_range(df.Momentum.min(),df.Momentum.max(), freq="H")

df["index"] = df.index
df.drop_duplicates(cols='index', take_last=True, inplace=True)
del df["index"]

df2 = df.reindex(idx)

df2[df2['gas [m3]'].isnull()]
# apply linear interpolation for the missing rows
df2 = df2.interpolate()
df2['Momentum'] = df2.index

newFile = os.path.join(path, 'datasets/' + building + '_elektriciteit_withWeather_clean.csv').replace('\\', '/')
df2.to_csv(newFile, index=False)

print time.time() - t