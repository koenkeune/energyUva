import os
import pandas as pd


def readData(building, file):
    data = building + file
    path = os.path.dirname( __file__ )
    path = os.path.abspath(os.path.join(path, os.pardir))
    
    return pd.read_csv(os.path.join(path, 'datasets/' + data).replace('\\', '/'))