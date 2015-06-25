import sys
#import os
from os import pardir
from os.path import abspath, dirname, join
import helpfunctions as h
import data_preparation as p
from dataset_cleaning import cleanData
from dataset_analysis import plotData
from split_data import splitData
from addFeatures import addAllFeatures
from results import getResults
from synthesize_data import createSyntheticData
from test import test

helpstring = 'python ' + sys.argv[0] + ' <building> <task>\n\
building: 740-NTH, 761-KMH, or 882-WBW\n\
task: p (preparation), c (cleaning), pl (plot), f (add features), \
sy (synthesize), s (split data), r (get results)'
 
# all buildings: 556-JWS, 729-DMH, 740-NTH, 750-FMB, 761-KMH, 762-BPH, 763-KSH,\
# 764-TTH, 766-LWB, 784-JBH, 882-WBW
 
if len(sys.argv) != 3:
    print(helpstring)
    sys.exit()
    
building = sys.argv[1]

saveFolder = 'datasetsForANNs'
unclean = building + '_elektriciteit_withWeather.csv'
clean = building + '_elektriciteit_withWeather_clean.csv'
allFeatures = building + '_elektricity_weather_clean_f.csv'
featuresFile = building + '_Features' + '_CV.csv'
data = 'unified.csv'
holidayDates = 'holidays.csv'
weatherData = 'KNMI_weatherdata[2008-2014].csv'
synthesized = 'synthesized.csv'

root = abspath(join(dirname( __file__ ), pardir))
datasets = join(root, 'datasets')
saveFolder = join(root, saveFolder)

features17 = ['gas [m3]', 'T', 'gas1HBefore', \
    'arima', 'arimaPeak5HBefore', \
    'gas [m3]_mean', 'residuals', 'residualsDays', \
    'weekDay2', \
    'gas [m3]_peak', 'gasPeak1DBefore', 'gas1DBefore', 'gas1WBefore']      
    
if sys.argv[2] == 'p':
    df = p.extractBuildingData(join(datasets, data), building)
    df = p.mergeWithHolidays(join(datasets, holidayDates), df)
    df = p.mergeWithForecasts(join(datasets, weatherData), df)
    h.save_file(df, join(datasets, unclean))
elif sys.argv[2] == 'c':
    df = cleanData(join(datasets, unclean), building)
    h.save_file(df, join(datasets, clean))
elif sys.argv[2] == 'pl':
    plotData(join(datasets, clean))
elif sys.argv[2] == 'f':
    df = addAllFeatures(join(datasets, clean))
    h.save_file(df, join(saveFolder, allFeatures))
    #h.save_features(df, featuresFile, features)
elif sys.argv[2] == 'sy':
    df = createSyntheticData(join(root, 'testAllF.csv'))
    h.save_file(df, join(saveFolder, synthesized))
elif sys.argv[2] == 's':
    splitData(join(saveFolder, allFeatures), features16)
elif sys.argv[2] == 'r':
    getResults(join(saveFolder, allFeatures), join(saveFolder, synthesized), #join(root, 'testAllF.csv'), 
    join(root, 'predict.csv'))
elif sys.argv[2] == 't':
    test(join(saveFolder, allFeatures))
else:
    print helpstring
    
    
# schrijf method om te detecteren welke outliers hij kan vinden