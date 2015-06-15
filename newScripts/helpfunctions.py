import pandas as pd

def save_file(df, path):
	df.to_csv(path, index=False)
    
def setDateAsIndex(df):
    df['Momentum'] = df['Momentum'].astype('datetime64')
    df = df.set_index('Momentum', drop=False)
    # convert to CET:
    df.index = df.index + pd.DateOffset(hours=1)
    del df['Momentum']
    df['Momentum'] = df.index
    return df