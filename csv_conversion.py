import pandas as pd

#importing the quarterly csv files
Q1_16 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2016-01-02-03.csv')
Q2_16 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2016-04-05-06.csv')
Q3_16 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2016-07-08-09.csv')
Q4_16 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2016-10-11-12.csv')

Q1_17 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2017-01-02-03.csv')
Q2_17 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2017-04-05-06.csv')
Q3_17 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2017-07-08-09.csv')
Q4_17 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2017-10-11-12.csv')

Q1_18 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2018-01-02-03.csv')
Q2_18 = pd.read_csv('../2016-2018_metro_validations/BandedValidations2018-04-05-06.csv')
Q3_18 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2018-07-08-09.csv')
Q4_18 = pd.read_csv('../2016-2018_metro_validations/bandedvalidations2018-10-11-12.csv')

#creating one single dataframe
total = Q1_16.append(Q2_16).append(Q3_16).append(Q4_16)
total = total.append(Q1_17).append(Q2_17).append(Q3_17).append(Q4_17)
total = total.append(Q1_18).append(Q2_18).append(Q3_18).append(Q4_18)

#sorting and renaming the columns to work with the program
total.VALIDATION_DATE = pd.to_datetime(total['VALIDATION_DATE'], dayfirst =True)
total = total.sort_values(['VALIDATION_DATE']).reset_index(drop = True)
total = total.rename(columns={'BAND_BOARDINGS_FLOOR': 'USAGE', 'GTFS_ID':'stop_id'})
total.USAGE = total.USAGE + 4
del total['BAND_BOARDINGS']

#removing useless columns from the stop information dataset
stops = pd.read_csv('../stops.csv')

del stops['zone_id']
del stops['location_type']
del stops['stop_timezone']
del stops['wheelchair_boarding']

total.to_csv('2016-2018_Metro_sorted_removed_columns.csv', index = False)
stops.to_csv('stops_removed_columns.csv', index = False)