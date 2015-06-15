import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from datetime import date
from helpfunctions import setDateAsIndex

def plotData(path):
    df = pd.read_csv(path)
    df = setDateAsIndex(df)
    
    plot(df, 2011, 2012, 01, 01, 01 ,01, 'gas [m3]')
    plot(df, 2012, 2012, 02, 03, 01 ,01, 'gas [m3]')
    plot(df, 2013, 2013, 02, 02, 04 ,11, 'gas [m3]')
    
    plot2(df, 2012, 2012, 02, 03, 01 ,01, 'gas [m3]', 'T')
    
    compareCorrelation(df, 2012, 2012, 02, 04, 01 ,01, 'gas [m3]', 'T')
    compareCorrelation(df, 2012, 2012, 02, 04, 01 ,01, 'gas [m3]', 'Q')
    compareCorrelation(df, 2012, 2012, 02, 04, 01 ,01, 'gas [m3]', 'elektriciteit [kwh]')
    
def plot(df, y1, y2, m1, m2, d1, d2, var):
    # figsize=(15,7)
    subset = df[(df.Momentum > date(y1, m1, d1)) & (df.Momentum < date(y2, m2, d2))][var].plot(grid=False, legend=False)
    subset.set_ylabel(var)
    subset.set_xlabel("Time")
    plt.show()
    
def plot2(df, y1, y2, m1, m2, d1, d2, var1, var2):
    subset1 = df[(df.Momentum > date(y1, m1, d1)) & (df.Momentum < date(y2, m2, d2))]['gas [m3]'].plot(figsize=(10,7), grid=False, legend=True, colormap='gray')
    subset2 = df[(df.Momentum > date(y1, m1, d1)) & (df.Momentum < date(y2, m2, d2))]['T'].plot(figsize=(10,7), grid=False, colormap='gray', style='--', legend='T')
    plt.show()
    
def compareCorrelation(df, y1, y2, m1, m2, d1, d2, var1, var2):
    x = df[(df.Momentum > date(y1, m1, d1)) & (df.Momentum < date(y2, m2, d2))][var1]
    y = df[(df.Momentum > date(y1, m1, d1)) & (df.Momentum < date(y2, m2, d2))][var2]
    print 'pearson value and p-value between ' + var1 + 'and ' + var2
    print pearsonr(x.values, y.values)