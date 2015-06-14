# reading and cleaning should be optional

import sys
import os
import data_preparation
import dataset_cleaning
import dataframe_saver as s

helpstring = 'python ' + sys.argv[0] + ' <building>\n\
choose between: 556-JWS, 729-DMH, 740-NTH, 750-FMB, 761-KMH, 762-BPH, 763-KSH,\
 764-TTH, 766-LWB, 784-JBH, 882-WBW'
 
if len(sys.argv) != 2:
    print(helpstring)
    sys.exit()
    
building = sys.argv[1]

dataFolder = 'datasets'
saveFolder = 'datasetsForANNs'
savedFile = building + '_elektriciteit_withWeather.csv' # with weather should be optional
data = 'unified.csv'
holidayDates = 'holidays.csv'
weatherData = 'KNMI_weatherdata[2008-2014].csv'
root = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir))
path = os.path.join(root, 'datasets', data)
path2 = os.path.join(root, 'datasets', holidayDates)
path3 = os.path.join(root, 'datasets', weatherData)

df = data_preparation.extractBuildingData(path, building)
df = data_preparation.mergeWithHolidays(path2, df)
df = data_preparation.mergeWithForecasts(path3, df)

s.save_file(df, os.path.join(root, saveFolder, savedFile))

df = pd.read_csv(os.path.join(root, saveFolder, savedFile))
df = dataset_cleaning(path, df)
s.save_file(df, os.path.join(root, saveFolder, building + '_elektriciteit_withWeather_clean.csv'))  