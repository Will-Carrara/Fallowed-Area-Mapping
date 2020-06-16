# Tutorial
>
>
> ## Python Implementation
> This approach is based on a decision tree classification algorithm which was created to assist with identifying fallow agricultural lands based on Normalized Difference Vegetation Index (NDVI) thresholds. This tutorial will walk you through running F.A.M. for the state of Washington. For future runs, you will need to provide your own inputs, however for this example the inputs are already provided. This implementation uses the pandas ecosystem with the use of Data Frames as the main storage container.
>
> If at any point you experience trouble with one of the functions you can use a `help()` command within the script for additional insight as shown here:
```python
help(name_of_function)
```
>
> ## Understanding the Algorithm
> Script modification will need to be made based on your specific inputs. The current format of the algorithm varies slightly state by state, however the fundamental structure is very similar. On a high level of abstraction the F.A.M. algorithm performs the following tasks sequentially:
> - Read and pre-process input data
> - Calculate NDVI maximums over a 5 year user-defined historical period
> - Make initial classification on data partitioned by season
> - Reclassify observations in post-processing
> - Export results
>
> This script is written in a functional programming style, where the main calls take place in the last few lines of code. To better help you understand the logic behind F.A.M., we will start at the beginning and work our way down.
>
```python
# field status                        cdl
crp = 5 # cropped                     -> 2
flw = 4 # fallow                      -> 10
prn = 3 # perennial, no crop yet      -> 15
pin = 2 # partially irrigated normal  -> 8
pop = 1 # partially irrigated poor    -> 9
```
> Here we are defining the dummy variables which we will use to encode our classes. These numbers are not chosen arbitrarily and their order is of consequence. F.A.M uses a hierarchical merging process in which classes with a higher weight take precedence. The intuition here is that if a subroutine classifies a field as cropped, it is possible that it may also be classified as partially irrigated by another subroutine. In such an event, the cropped status will take priority. This method is programmatically equivalent to running each classification on the residuals of each prior run.
>
```python
files = np.sort([x for x in glob.glob('input/*/*.csv')])
```
> `files` is a sorted list of the paths to the input csvs. **It is critical that you have followed the directory setup instructions in the [data acquisition tutorial](data_acquisition.md).** If this has been done incorrectly, your files will not be ordered properly and the F.A.M. results will be erroneous. In this example everything is already setup properly.
>
```python
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
    yr_2008 = process(list(filter(lambda x:'2008' in x, files)), 2008)
    yr_2009 = process(list(filter(lambda x:'2009' in x, files)), 2009)
    yr_2010 = process(list(filter(lambda x:'2010' in x, files)), 2010)
    yr_2013 = process(list(filter(lambda x:'2013' in x, files)), 2013)
    yr_2015 = process(list(filter(lambda x:'2015' in x, files)), 2015)
    yr_2016 = process(list(filter(lambda x:'2016' in x, files)), 2016)
    yr_2017 = process(list(filter(lambda x:'2017' in x, files)), 2017)
    yr_2018 = process(list(filter(lambda x:'2018' in x, files)), 2018)
    yr_2019 = process(list(filter(lambda x:'2019' in x, files)), 2019)
```
> We are going to run into a rather dense <i>try-catch</i> block here. F.A.M. uses historical data as part of the classification procedure (more on this later). The idea here is that when running for the current year you don't need to rerun for the past years. To save time and computing resources, we will cache our previously processed data. **Note: you will need to delete any year from the cache if you update the input data for that year.**
>
We are making calls to our <i>process</i> function here. Let's take a look to see what it does.
>
```python
def process(files, year):

    df = pd.concat([pd.read_csv(x, usecols=[1,2,3], parse_dates=[2], header=0,
        names=['ndvi', 'id', 'date']) for x in files])

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
```
> This function applies a series of operations to merge multiple .csv files together to uniformly format NDVI time series data across the state. Additionally, function linearly interpolates and constrains observations to 8 day intervals. Let's move on.
>
```python
# historic years
hist_years = [yr_2008, yr_2009, yr_2010, yr_2013, yr_2017]

# calculate 5 year maximums for smoothed ts
max_smooth_spring = np.array([smooth(df.iloc[:,8:19]).max(axis=1) for df in hist_years]).max(0)
max_smooth_overlap = np.array([smooth(df.iloc[:,12:23]).max(axis=1) for df in hist_years]).max(0)
max_smooth_summer = np.array([smooth(df.iloc[:,19:38]).max(axis=1) for df in hist_years]).max(0)

max_smooth_5yr = pd.DataFrame({'id': yr_2018.index.values, 'spring_ndvi_smoothed_5yr_max':
 max_smooth_spring,'overlap_ndvi_smoothed_5yr_max': max_smooth_overlap,
 'summer_ndvi_smoothed_5yr_max': max_smooth_summer}).set_index('id')
```
> As mentioned above, F.A.M. uses historical data as part of the classification procedure. Here we have defined 2008, 2009, 2010, 2013, and 2017 as our reference years. Internal testing showed five years is sufficient for accurate results, however you may add more if desired. This block is calculating a time series of maximum NDVI for these years to use as a retrospective reference.
>
```python
# variables to tune
ndvi_max_threshold = 0.55
ndvi_min_threshold = 0.4
ndvi_perc_historic_threshold1 = 0.7
ndvi_perc_historic_threshold2 = 0.5
perennial_date_threshold = 23

# crop type information for perennials (id's may change with alteration of field boundaries)
crop_type = pd.read_csv("input/crop_data/perennial.csv").set_index('id')
```
> Our testing showed that the above thresholds yield the highest accuracy, however these may not hold over time. The curators of F.A.M. will work to keep them updated. The `crop_type` variable stores information about which crop id's have known perennials. You may provide your own list if desired with the format is provided in this repository. Now lets look at the main algorithmic calls.
>
```python
years = [yr_2019, yr_2018, yr_2017, yr_2016, yr_2015, yr_2013, yr_2010]
for year in years:
    name = [x for x in globals() if globals()[x] is year][0]
    export(postProcess(year)[0],'output/Washington_Spring_'+name[3:7])
    export(postProcess(year)[1],'output/Washington_Summer_'+name[3:7])
```
> With list comprehension we will make our final calls using the the `postProcess()` function which immediately calls the `fallowMapping()` function. Let's begin here first.
>
```python
def fallowMapping(df, season):

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

```
> This function applies a series of rules to periods of the data partitioned by season. Rules perform vectorized operations and are detailed in the comments. Assigned field statuses are hierarchical and will later be converted to their respective cdl codes.
>
```python
def postProcess(yr_df):

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
```
> Our post-processing procedure compares the date of the maximum NDVI value with cropped observations in the overlap period to reclassify any missed observations as cropped. We then call a decoding function on encoded statuses to proper cdl standards.
>
> Now that these functions have been called, the `export()` function will output the results in the <i>outputs</i> folder.
