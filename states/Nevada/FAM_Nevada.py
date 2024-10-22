# ___________________________________________ NASA AMES RESEARCH CENTER ___________________________________________
# title           : FAM_Nevada.py
# description     : Working in collaboration with the California Department of Water Resources, scientists
#                   at NASA Ames Research Center (ARC), the U.S. Geological Survey (USGS), the U.S. Department
#                   of Agriculture (USDA), and California State University Monterey Bay (CSUMB) have demonstrated
#                   the feasibility of using satellite imagery to track the extent of fallowed land in the State
#                   of Nevada on a monthly basis.
#
# author          : Will Carrara
# date            : 06-16-2020
# version         : 1.2
# notes           : Further project details can be found at: https://github.com/Will-Carrara/Fallowed-Area-Mapping
# python_version  : 3.*
# _________________________________________________________________________________________________________________

import time
import glob

import numpy as np
import pandas as pd

# warning handling
pd.options.mode.chained_assignment = None

# start script time
start = time.time()

# field status                        cdl
crp = 4 # cropped                     -> 2
flw = 3 # fallow                      -> 10
pin = 2 # partially irrigated normal  -> 8
pop = 1 # partially irrigated poor    -> 9

# input data paths
files = [x for x in glob.glob('input/*/*.csv')]

# export csv file
export = lambda df, name: df.to_csv(name + '.csv', header=True)

# smoothing filter
smooth = lambda df: df.rolling(window=5,min_periods=0,axis=1,center=True).mean()

# create time stamp
snapshot = lambda start: str(round((time.time() - start)/60,3))

# convert to standard cdl codes
def decode(field_status):
    """Maps field status to standard cdl code.

    Uses a series of vectorized operations to sequentially map input to
    corresponding cdl code.

    Args:
        field_status (ndarray): An array object containing hierarchical
        field codes.

    Returns:
        ndarray: Mapped values to corresponding cdl code.
    """
    field_status = np.where(field_status == pin, 8, field_status)
    field_status = np.where(field_status == pop, 9, field_status)
    field_status = np.where(field_status == flw, 10, field_status)
    field_status = np.where(field_status == crp, 2, field_status)

    return field_status


def process(files, year):
    """Reads, formats, and restructures data.

    Uses a series operations to merge multiple .csv files together to format ndvi
    time series data across the state of Nevada. Additionally, function linearly
    interpolates, and constrains observations to 8 day intervals.

    Args:
        files (list): A list of .csv files.

        year (int): Corresponding year to input data.

    Returns:
        DataFrame: A pandas object with properly formatted times series data.
    """
    df = pd.concat([pd.read_csv(x, usecols=[1,2,3], parse_dates=[2], header=0,
        names=['ndvi', 'id', 'date']) for x in files])

    # create any missing observations on 8 day interval for single id
    dates = pd.date_range("1-01-"+str(year), freq='8D', periods=46)
    dates = pd.Series(dates.format()).tolist()
    df = df.append(pd.DataFrame({'ndvi':np.nan,'id':1,'date':dates}), ignore_index=True)

    # merge, sort, and keep max duplicate
    df = df.sort_values(['id','date','ndvi'])
    df = df.drop_duplicates(subset=['id','date'], keep='last').iloc[1:]

    # pivot shape for increased efficiency
    df = df.pivot(index='id', columns='date', values='ndvi')

    # linearly interpolate by grouped id
    df.interpolate(method='linear',axis=1,limit_direction='both',inplace=True)

    # constrain data to 8 day intervals
    df = df[dates].dropna()

    return df

print("Processing initiated at",snapshot(start),"minutes.\n")

yr_2006 = process(list(filter(lambda x:'2006' in x, files)), 2006)
yr_2008 = process(list(filter(lambda x:'2008' in x, files)), 2008)
yr_2009 = process(list(filter(lambda x:'2009' in x, files)), 2009)
yr_2010 = process(list(filter(lambda x:'2010' in x, files)), 2010)
yr_2011 = process(list(filter(lambda x:'2011' in x, files)), 2011)
yr_2013 = process(list(filter(lambda x:'2013' in x, files)), 2013)
yr_2014 = process(list(filter(lambda x:'2014' in x, files)), 2014)
yr_2015 = process(list(filter(lambda x:'2015' in x, files)), 2015)
yr_2016 = process(list(filter(lambda x:'2016' in x, files)), 2016)
yr_2017 = process(list(filter(lambda x:'2017' in x, files)), 2017)
yr_2018 = process(list(filter(lambda x:'2018' in x, files)), 2018)
yr_2019 = process(list(filter(lambda x:'2019' in x, files)), 2019)

print("Processing completed at",snapshot(start),"minutes.\n")

print("Historic calculations initiated at",snapshot(start),"minutes.\n")

# all years
years = [yr_2006, yr_2008, yr_2009, yr_2010, yr_2011, yr_2013, yr_2015, yr_2014, yr_2016, yr_2017, yr_2018, yr_2019]

# historic years
hist_years = [yr_2006, yr_2008, yr_2009, yr_2010, yr_2017]

# calculate 5 year maximums for smoothed ts
max_smooth = np.array([smooth(df).max(axis=1) for df in hist_years]).max(0)
max_smooth_5yr = pd.DataFrame({'id':yr_2018.index.values,'ndvi_smooth_5yr_max':max_smooth})

print("Historic calculations completed at",snapshot(start),"minutes.\n")

# variables to tune
ndvi_max_threshold = 0.55
ndvi_min_threshold = 0.4
ndvi_perc_historic_threshold1 = 0.7
ndvi_perc_historic_threshold2 = 0.5

# ________________________________________DATE CONVERSION_________________________________________
#|01-01|01-09|01-17|01-25|02-02|02-10|02-18|02-26|03-06|03-14|03-22|03-30|04-07|04-15|04-23|05-01|
#|  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  |  10 |  11 |  12 |  13 |  14 |  15 |
#|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|
#|05-09|05-17|05-25|06-02|06-10|06-18|06-26|07-04|07-12|07-20|07-28|08-05|08-13|08-21|08-29|09-06|
#|  16 |  17 |  18 |  19 |  20 |  21 |  22 |  23 |  24 |  25 |  26 |  27 |  28 |  29 |  30 |  31 |
#|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|
#|09-14|09-22|09-30|10-08|10-16|10-24|11-01|11-09|11-17|11-25|12-03|12-11|12-19|12-27|     |     |
#|  32 |  33 |  34 |  35 |  36 |  37 |  38 |  39 |  40 |  41 |  42 |  43 |  44 |  45 |     |     |
#|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|


def fallowMapping(df):
    """Performs initial classification results by season.

    Applies a series rules to periods of partitioned data. Rules perform
    vectorized operations and are detailed in the comments. Assigned field
    statuses are hierarchical in nature and must be converted to their
    respective cdl codes.

    Args:
        df (DataFrame): A pandas object which contains formatted ndvi time
                        series data.

        season (str): A season either "spring", "summer", or "overlap".

    Returns:
        DataFrame: A pandas object with classified times series data.
    """
    df = df.iloc[:,8:38]

    df_smooth = pd.DataFrame(np.sort(smooth(df).values, axis=1), columns=df.columns)
    df_sorted = pd.DataFrame(np.sort(df.values, axis=1), columns=df.columns)

    # highest ndvi values from the original, linearly interpolated ts
    ndvi_max1 = df_sorted.iloc[:,-1]
    ndvi_max4 = df_sorted.iloc[:,-4]

    # highest ndvi values from the smoothed ts
    ndvi_smoothed_max1 = df_smooth.iloc[:,-1]

    # check cropped
    rule1 = np.where(ndvi_max4 >= ndvi_max_threshold, crp, -9999)

    # check fallow
    rule3 = np.where(ndvi_max1 < ndvi_min_threshold, flw, -9999)

    # check fields between 0.4 and 0.6 relative to historic average
    rule4 = np.where(ndvi_smoothed_max1 >= (ndvi_perc_historic_threshold1*max_smooth_5yr['ndvi_smooth_5yr_max']), pin, -9999)

    # check for partially irrigated
    rule5 = np.where(ndvi_smoothed_max1 >= (ndvi_perc_historic_threshold2*max_smooth_5yr['ndvi_smooth_5yr_max']), pop, -9999)

    # check for fields that are less than 50% of historical average
    rule6 = np.where(ndvi_smoothed_max1 < (ndvi_perc_historic_threshold2*max_smooth_5yr['ndvi_smooth_5yr_max']), flw, -9999)

    # calculate percent 5 year average
    pnorm = np.where(True, round(ndvi_smoothed_max1/max_smooth_5yr['ndvi_smooth_5yr_max'], 4)*100, -9999)

    # classify field status via hierarchical merge
    field_status = decode(np.maximum.reduce([rule1, rule3, rule4, rule5, rule6]))

    # add classifications & historical averages
    df.insert(0, 'percent_5yr_Avg', pnorm)
    df.insert(0, 'field_status', field_status)

    return df

print("Classifications initiated at",snapshot(start),"minutes.\n")

for year in years:
    name = [x for x in globals() if globals()[x] is year][0]
    export(fallowMapping(year),'output/Nevada_'+name[3:7])

print("Classifications & exports completed at",snapshot(start),"minutes.\n")

# end script time
end = time.time()
print("Total time to run script:", str(round((end-start)/60,3)), "minutes.\n")