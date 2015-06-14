import pandas as pd

def cleaning(df):
    df['Momentum'] = df['Momentum'].astype('datetime64')
    df = df.set_index('Momentum', drop=False)

    # There is an implicit conversion of timezone. I need to fix it.
    df.index = df.index + pd.DateOffset(hours=1)
    del df['Momentum']
    df['Momentum'] = df.index

    if(building == '761-KMH'):
        df = df[(df.Momentum >= datetime.date(2009,01,01)) & (df.Momentum < datetime.date(2013,9,1))]

    df = removeDuplicateRows(df)
        
    return df2
    
def removeDuplicateRows(df):
    idx = pd.date_range(df.Momentum.min(),df.Momentum.max(), freq="H")
    df["index"] = df.index
    df.drop_duplicates(cols='index', take_last=True, inplace=True)
    del df["index"]

    return df.reindex(idx)
    
def interpolateMissingRows(df):
    df[df['gas [m3]'].isnull()]
    df = df.interpolate()
    df['Momentum'] = df.index

    return df