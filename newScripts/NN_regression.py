import pandas as pd
import numpy as np

def splitData(path, features):
    df = pd.read_csv(path, encoding="utf-8-sig", parse_dates=['Momentum'])
    df = df.set_index(['Momentum'], drop=False)
    df.index = df.index.tz_localize('UTC')
    
    print df.head()
    
    shuffling = True
    
    n = df['T'].count()
    df['datetime'] = df.index.date
    splitPoint = int(n*70/100)
    train = df.ix[:splitPoint]
    rest = df.ix[splitPoint:]
    if shuffling:
        train = shuffle(train)
        
    train[features].to_csv('train.csv', header=False, index=False)
    # Reset index
    rest = rest.reset_index(drop=True)

    n = rest['T'].count()
    splitPoint = int(n*50/100)
    valid = rest.ix[:splitPoint]
    test = rest.ix[splitPoint:]
    test.to_csv('testAllF.csv', index=False)
    test[features].to_csv('testY.csv', header=False, index=False)
    test[(features+['datetime'])].to_csv('testYDate.csv', header=False, index=False)
    featuresNoY = features[1:]
    test[featuresNoY].to_csv('test.csv', header=False, index=False)
    valid[features].to_csv('valid.csv', header=False, index=False)

    
    # C:\Users\laptop\Documents\AI\ml_project\pylearn2\pylearn2\scripts\train.py NN_static_MLSE_j.yaml
    
    
def shuffle(df, n=1, axis=1):
    df = df.copy()
    for _ in range(n):
        df.apply(np.random.shuffle, axis=axis)
    return df