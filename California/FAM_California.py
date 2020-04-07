# ___________________________________________ NASA AMES RESEARCH CENTER ___________________________________________
# title           : FAM_California.py
# description     : Working in collaboration with the California Department of Water Resources, scientists
#                   at NASA Ames Research Center (ARC), the U.S. Geological Survey (USGS), the U.S. Department
#                   of Agriculture (USDA), and California State University Monterey Bay (CSUMB) have demonstrated
#                   the feasibility of using satellite imagery to track the extent of fallowed land in the Central
#                   Valley of California on a monthly basis.
#
# author          : Will Carrara
# date            : 02-12-2019
# version         : 0.7
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
crp = 5 # cropped                     -> 2
flw = 4 # fallow                      -> 10
prn = 3 # perennial, no crop yet      -> 15
pin = 2 # partially irrigated normal  -> 8
pop = 1 # partially irrigated poor    -> 9

files = np.sort([x for x in glob.glob('input/*/*.csv')])

# export .csv file
export = lambda df, name: df.to_csv(name + '.csv', header=True)

# smoothing filter
smooth = lambda df: df.rolling(window=5,min_periods=0,axis=1,center=True).mean()

# create time stamp
snapshot = lambda start: str(round((time.time() - start)/60,3))


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

    # perennials cannot be partially irrigated (summer only)
    field_status = np.where(field_status == prn, 2, field_status)

    return field_status

def process(files, year):
    """Reads, formats, and restructures data.

    Uses a series operations to merge multiple .csv files together to format ndvi
    time series data across the state of California. Additionally, function linearly
    interpolates, and constrains observations to 8 day intervals.

    Args:
        files (list): A list of .csv files.

        year (int): Corresponding year to input data.

    Returns:
        DataFrame: A pandas object with properly formatted times series data.
    """
    df = pd.concat([pd.read_csv(x, usecols=[1,2,3], parse_dates=[2], header=0,
        names=['ndvi', 'id', 'date']) for x in files])

    print(year, df.shape)

    # create any missing observations on 8 day interval for each id
    dates = pd.date_range("1-01-"+str(year), freq='8D', periods=46)
    dates = pd.Series(dates.format()).tolist()
    df = df.append(pd.DataFrame({'ndvi':np.nan,'id':1,'date':dates}), ignore_index=True)

    # merge, sort, and keep max duplicate
    df = df.sort_values(['id','date','ndvi'])
    df = df.drop_duplicates(subset=['id','date'], keep='last').iloc[1:]

    # pivot shape for increased efficiency
    df = df.pivot(index='id', columns='date', values='ndvi')

    # linearly interpolate by id
    df.interpolate(method='linear', axis=1, limit_direction='both', inplace=True)

    # constrain data to 8 day intervals
    df = df[dates].dropna()

    return df

print("Processing initiated at",snapshot(start),"minutes.\n")

try:
    yr_2008 = pd.read_csv("cache/yr_2008.csv").set_index('id')
    yr_2009 = pd.read_csv("cache/yr_2009.csv").set_index('id')
    yr_2010 = pd.read_csv("cache/yr_2010.csv").set_index('id')
    yr_2013 = pd.read_csv("cache/yr_2013.csv").set_index('id')
    yr_2015 = pd.read_csv("cache/yr_2015.csv").set_index('id')
    yr_2016 = pd.read_csv("cache/yr_2016.csv").set_index('id')
    yr_2017 = pd.read_csv("cache/yr_2017.csv").set_index('id')
    yr_2018 = pd.read_csv("cache/yr_2018.csv").set_index('id')
    yr_2019 = pd.read_csv("cache/yr_2019.csv").set_index('id')

except:
    print("Exception: year not found.")
    yr_2008 = process(files[0:50], 2008)
    yr_2009 = process(files[50:100], 2009)
    yr_2010 = process(files[100:150], 2010)
    yr_2013 = process(files[150:200], 2013)
    yr_2015 = process(files[200:250], 2015)
    yr_2016 = process(files[250:300], 2016)
    yr_2017 = process(files[300:350], 2017)
    yr_2018 = process(files[350:400], 2018)
    yr_2019 = process(files[400:450], 2019)

    export(yr_2008, "cache/yr_2008")
    export(yr_2009, "cache/yr_2009")
    export(yr_2010, "cache/yr_2010")
    export(yr_2013, "cache/yr_2013")
    export(yr_2015, "cache/yr_2015")
    export(yr_2016, "cache/yr_2016")
    export(yr_2017, "cache/yr_2017")
    export(yr_2018, "cache/yr_2018")
    export(yr_2019, "cache/yr_2019")

test = [yr_2008, yr_2009, yr_2010, yr_2013, yr_2015, yr_2016, yr_2017, yr_2018, yr_2019]
[print(yr.shape) for yr in test]
quit()

def reduce (df):
    common = df.index.intersection(yr_2008.index)
    df = df.loc[common]

    common = df.index.intersection(yr_2018.index)
    df = df.loc[common]

    common = df.index.intersection(yr_2009.index)
    df = df.loc[common]

    common = df.index.intersection(yr_2013.index)
    df = df.loc[common]

    return df.loc[common]

yr_2008 = reduce(yr_2008)
yr_2009 = reduce(yr_2009)
yr_2010 = reduce(yr_2010)
yr_2013 = reduce(yr_2013)
yr_2015 = reduce(yr_2015)
yr_2016 = reduce(yr_2016)
yr_2017 = reduce(yr_2017)
yr_2018 = reduce(yr_2018)
yr_2019 = reduce(yr_2019)



print("Processing completed at",snapshot(start),"minutes.\n")

print("Historic calculations initiated at",snapshot(start),"minutes.\n")

# historic years
years = [yr_2008, yr_2009, yr_2010, yr_2013, yr_2017]

# calculate 5 year maximums for smoothed ts
max_smooth_spring = np.array([smooth(df.iloc[:,8:19]).max(axis=1) for df in years]).max(0)
max_smooth_overlap = np.array([smooth(df.iloc[:,12:23]).max(axis=1) for df in years]).max(0)
max_smooth_summer = np.array([smooth(df.iloc[:,19:38]).max(axis=1) for df in years]).max(0)

max_smooth_5yr = pd.DataFrame({'id': yr_2018.index.values, 'spring_ndvi_smoothed_5yr_max':
 max_smooth_spring,'overlap_ndvi_smoothed_5yr_max': max_smooth_overlap,
 'summer_ndvi_smoothed_5yr_max': max_smooth_summer}).set_index('id')

print("Historic calculations completed at",snapshot(start),"minutes.\n")

# variables to tune
ndvi_max_threshold = 0.55
ndvi_min_threshold = 0.4
ndvi_perc_historic_threshold1 = 0.7
ndvi_perc_historic_threshold2 = 0.5
perennial_date_threshold = 23

# crop type information for perennials (id's may change with alteration of field boundaries)
crop_type = pd.read_csv("input/crop_data/perennial.csv").set_index('id')

crop_type = reduce(crop_type)

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


def fallowMapping(df, season):
    """Performs initial classification results by season.

    Applies a series rules to periods of the data partitioned by season. Rules
    perform vectorized operations and are detailed in the comments. Assigned
    field statuses are hierarchical in nature and must be later converted to
    their respective cdl codes.

    Args:
        df (DataFrame): A pandas object which contains formatted ndvi time
                        series data.

        season (str): A season either "spring", "summer", or "overlap".

    Returns:
        DataFrame: A pandas object with classified times series data.
    """
    if(season == 'spring'):
        df = df.iloc[:,8:19]
        hist_season = 'spring_ndvi_smoothed_5yr_max'

    elif(season == 'overlap'):
        df = df.iloc[:,12:23]
        hist_season = 'overlap_ndvi_smoothed_5yr_max'

    elif(season == 'summer'):
        df = df.iloc[:,19:38]
        hist_season = 'summer_ndvi_smoothed_5yr_max'

    df_smooth = pd.DataFrame(np.sort(smooth(df).values, axis=1), index=df.index, columns=df.columns)
    df_sorted = pd.DataFrame(np.sort(df.values, axis=1), index=df.index, columns=df.columns)

    # highest ndvi values from the original linearly interpolated ts
    ndvi_max1 = df_sorted.iloc[:,-1]
    ndvi_max4 = df_sorted.iloc[:,-4]

    # highest ndvi values from the smoothed ts
    ndvi_smoothed_max1 = df_smooth.iloc[:,-1]

    # check cropped
    rule1 = np.where(ndvi_max4 >= ndvi_max_threshold, crp, -9999)

    # mask for perennial croptype (summer only)
    rule2 = np.where(crop_type['crop_group'].notnull(), prn, -9999)

    # check fallow
    rule3 = np.where(ndvi_max1 < ndvi_min_threshold, flw, -9999)

    # check fields between 0.4 and 0.7 relative to historic average
    rule4 = np.where(ndvi_smoothed_max1 >= (ndvi_perc_historic_threshold1
     * max_smooth_5yr[hist_season]), pin, -9999)

    # check for partially irrigated
    rule5 = np.where(ndvi_smoothed_max1 >= (ndvi_perc_historic_threshold2
     * max_smooth_5yr[hist_season]), pop, -9999)

    # check for fields that are less than 50% of historical average
    rule6 = np.where(ndvi_smoothed_max1 < (ndvi_perc_historic_threshold2
     * max_smooth_5yr[hist_season]), flw, -9999)

    # calculate percent 5 year average
    pnorm = np.where(True,round(ndvi_smoothed_max1/max_smooth_5yr[hist_season],4)*100,-9999)

    # classify field status via hierarchical merge
    if(season == 'summer'):
        field_status = np.maximum.reduce([rule1, rule2, rule3, rule4, rule5, rule6])
    else:
        field_status = np.maximum.reduce([rule1, rule3, rule4, rule5, rule6])

    # add classifications & historical averages
    df.insert(0,'field_status',field_status)
    df.insert(0,'percent_5yr_Avg',pnorm)

    return df


def postProcess(yr_df):
    """Performs final classification on results.

    Compares the date of the max ndvi value with cropped observations in the overlap
    period to reclassify observations as cropped. Calls decoding function to encoded
    statuses to proper cdl standards. Calls fallowMapping for initial classifications.

    Args:
        yr_df (DataFrame): A pandas object which contains formatted ndvi time
                           series data.

    Returns:
        list: Contains two pandas DataFrame objects by season with final classified
              results.
    """
    print("Initial classifications initiated at",snapshot(start),"minutes.\n")

    # initial classifications
    df_spring = fallowMapping(yr_df,'spring')
    df_overlap = fallowMapping(yr_df,'overlap')
    df_summer = fallowMapping(yr_df,'summer')

    print("Initial classifications completed at",snapshot(start),"minutes.\n")

    # mask of cropped observations in overlap period
    mask_ov = np.where(df_overlap['field_status'] == crp,7,-1)

    # date of max ndvi
    a = list(smooth(yr_df).idxmax(axis=1))
    # spring date columns
    b = list(yr_df.iloc[:,0:19].columns)
    # summer date columns
    c = list(yr_df.iloc[:,19:].columns)

    # check if max ndvi value is in season
    mask_sp = [7 if i in b else 0 for i in a]
    mask_su = [7 if i in c else 0 for i in a]

    # max ndvi observation and cropped in overlap period
    df_spring['field_status'] = decode(np.where(mask_sp == mask_ov, crp, df_spring['field_status']))
    df_summer['field_status'] = decode(np.where(mask_su == mask_ov, crp, df_summer['field_status']))

    # mask for early season perennials (spring only)
    df_spring['field_status'] = np.where(crop_type['crop_group'].notnull(), 15, df_spring['field_status'])

    return [df_spring, df_summer]


print("Post-processing initiated at",snapshot(start),"minutes.\n")

years = [yr_2019, yr_2018, yr_2017, yr_2016, yr_2015, yr_2013, yr_2010]
for year in years:
    name = [x for x in globals() if globals()[x] is year][0]
    export(postProcess(year)[0],'output/California_Spring_'+name[3:7])
    export(postProcess(year)[1],'output/California_Summer_'+name[3:7])

print("Post-processing & exports completed at",snapshot(start),"minutes.\n")

# end script time
end = time.time()
print("Total time to run script:", str(round((end-start)/60,3)), "minutes.\n")