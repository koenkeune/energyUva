import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def sinDayAndHour(s):
    s['hour'] = s['Momentum'].hour
    return s
    
def normalizeColumns(df, columns):
    for column in toNormalize:
        max_X = df[column].max()
        min_X = df[column].min()
        
        midrange = (max_X+min_X)/2
        Xrange = (max_X-min_X)
        
        df[column] = (df[column] - midrange) / (Xrange/2)
    return df
  
building = '740-NTH' #'882-WBW'
data = building + '_elektriciteit_withWeather_clean.csv'
path = os.path.dirname( __file__ )
path = os.path.abspath(os.path.join(path, os.pardir))

df = pd.read_csv(os.path.join(path, 'datasets/' + data).replace('\\', '/'))  

df['Momentum'] = df['Momentum'].astype('datetime64')
df = df.set_index('Momentum', drop=False)

# There is an implicit conversion of timezone. I need to fix it.
df.index = df.index + pd.DateOffset(hours=1)
del df['Momentum']
df['Momentum'] = df.index

# add sinusoidal time feature
df['hour'] = 0
df['sinHour'] = 0
df['cosHour'] = 0
df['sinWeekDay'] = 0
df['cosWeekDay'] = 0
    
df = df.apply(sinDayAndHour, 1)
df['sinHour'] = np.sin(2*np.pi*df['hour']/23)
df['sinWeekDay'] = np.sin(2*np.pi*df['weekDay']/6)
df['cosHour'] = np.cos(2*np.pi*df['hour']/23)
df['cosWeekDay'] = np.cos(2*np.pi*df['weekDay']/6)

# normalize weather columns
df['T_noNorm'] = df['T']

toNormalize = ['elektriciteit [kwh]', 'T', 'FH', 'U', 'N', 'Q']
df = normalizeColumns(df, toNormalize)

features = ['gas [m3]','elektriciteit [kwh]', 'T', 'FH', 'U', 'N', 'Q', 'sinHour', 'cosHour', 'sinWeekDay', 'cosWeekDay']
#newFile = os.path.join(path, 'filteredDatasets/'+building+'_NN_10F.csv').replace('\\', '/')
newFile = os.path.join(path, 'trainCV.csv').replace('\\', '/')
df[features].to_csv(newFile, index=False)


#rr = pd.read_csv(newFile)
#rr.plot()
#rr['actual'].tail(80).plot()
#rr['predicted'].tail(80).plot()

#plt.show()