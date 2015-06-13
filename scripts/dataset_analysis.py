import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from datetime import date
from helpFunctions import readData

building = '740-NTH' #'761-KMH' #'882-WBW'
df = readData(building, '_elektriciteit_withWeather_clean.csv')

df['Momentum'] = df['Momentum'].astype('datetime64')
df = df.set_index('Momentum', drop=False)

# There is an implicit conversion of timezone. I need to fix it.
df.index = df.index + pd.DateOffset(hours=1)
del df['Momentum']
df['Momentum'] = df.index

# one year:
df2 = df[(df.Momentum > date(2011, 01, 01)) & (df.Momentum < date(2012, 01, 01))]['gas [m3]']
df2.plot(figsize=(15,7))
plt.show()

# one month:
ax = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 03, 01))][['gas [m3]']].plot(figsize=(10,7), grid=False, legend=False, colormap='gray')
ax.set_ylabel("Gas (m$^3$)")
ax.set_xlabel("")
plt.show()

# compare with temperature:
ax = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 03, 01))]['gas [m3]'].plot(figsize=(10,7), grid=False, legend=True, colormap='gray')
ax = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 03, 01))]['T'].plot(figsize=(10,7), grid=False, colormap='gray', style='--', legend='T')
plt.show()

# one week:
ax = df[(df.Momentum > date(2013, 02, 04)) & (df.Momentum < date(2013, 02, 11))]['gas [m3]'].plot(figsize=(10,7), grid=False, colormap='gray')
ax.set_ylabel("Gas (m$^3$)")
plt.show()

# comparing two variables:
x = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['gas [m3]']
y = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['T']
print 'pearson value and p-value between gas and temperature'
print pearsonr(x.values, y.values)

x = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['gas [m3]']
y = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['Q']
print 'pearson value and p-value between gas and global radiation'
print pearsonr(x.values, y.values)

x = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['gas [m3]']
y = df[(df.Momentum > date(2012, 02, 01)) & (df.Momentum < date(2012, 04, 01))]['elektriciteit [kwh]']
print 'pearson value and p-value between gas and electricity'
print pearsonr(x.values, y.values)

