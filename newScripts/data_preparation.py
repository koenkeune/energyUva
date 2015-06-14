import pandas as pd
import numpy as np
import datetime

def extractBuildingData(path, building):
    df = pd.read_csv(path)
    # only extract the electricity and the gas usage of a building
    df = df[(df.filename == building) & ((df['gas [m3]'].notnull()) | (df['elektriciteit [kwh]'].notnull()))]
    
    columnsToRemove = list(df.columns.values)
    columnsToKeep = ['Unnamed: 0', 'gas [m3]', 'elektriciteit [kwh]', 'totaal [kwh]', 'water [m3]', 'filename']
    [columnsToRemove.remove(i) for i in columnsToKeep]
    
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

    return df[df['gas [m3]'].notnull()][['Momentum', 'gas [m3]', 'elektriciteit [kwh]']]

def mergeWithHolidays(path, df):
    df['weekDay'] = 0
    holidays = pd.read_csv(path).values
    
    return df.apply(assignDayOfTheWeek(holidays), 1)
    
def assignDayOfTheWeek(holidays):
    def assignDayOfTheWeekPerRow(row):
        dateString = "%04d-%02d-%02d" % (row['Momentum'].year, row['Momentum'].month, row['Momentum'].day)
        weekday = 6
        if dateString not in holidays:
            weekday = row['Momentum'].weekday()
        row['weekDay'] = weekday
        
        return row
    return assignDayOfTheWeekPerRow
    
def mergeWithForecasts(path,df):
    weather = pd.read_csv(path, sep=';')

    columns = weather.columns
    columns = [x.strip() for x in columns]
    weather.columns = columns
    weather = weather[['YYYYMMDD', 'HH', 'FH', 'T', 'U', 'N', 'Q']]
    weather[['YYYYMMDD']] = weather[['YYYYMMDD']].astype(str)
    weather[['U']] = weather[['U']].astype(float)
    weather['HH'] = weather['HH'] - 1 #HH is from 1 to 24

    df['T'] = 0
    df['FH'] = 0
    df['U'] = 0
    df['N'] = 0
    df['Q'] = 0

    df = df.apply(assignForecasts(weather), 1)
    
    return df[df['elektriciteit [kwh]'].notnull()]
    
def assignForecasts(weather):
    def assignForecastsPerRow(row):
        dateString = "%04d%02d%02d" % (row['Momentum'].year, row['Momentum'].month, row['Momentum'].day)
        selected = weather[(weather.YYYYMMDD == dateString) & (weather.HH == row['Momentum'].hour)]
        
        row['T'] = selected['T'].values[0]
        row['FH'] = selected['FH'].values[0]
        row['U'] = selected['U'].values[0]/100 # the humidity is a percentage
        row['N'] = selected['N'].values[0]
        row['Q'] = selected['Q'].values[0]
    
        return row
    return assignForecastsPerRow