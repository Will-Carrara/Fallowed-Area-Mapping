# Tutorial
>
>
> ## Python Implementation
> This approach is based on a decision tree classification algorithm which was created to assist with identifying fallow agricultural lands based on Normalized Difference Vegetation Index (NDVI) thresholds. This tutorial will walk you through running F.A.M. for the state of Washington. For future runs, you will need to provide your own inputs, however for this example the inputs are already provided.
>
> If at any point you experience trouble with one of the functions you can use a help command within the script for additional insight.
```python
help(name_of_function)
```
>
> ## Understanding the Algorithm
> Script modification will need to be made based on your specific inputs. The current format of the algorithm varies slightly state by state, however the fundamental structure is very similar. On a high level of abstraction the F.A.M. algorithm preforms these tasks in order:
> - Read and pre-process input data
> - Calculate NDVI maximums over a 5 year user-defined historical period
> - Make initial classification on data partitioned by season
> - Reclassify observations in post-processing
> - Export results
>
> This script is written in a functional programming style, where the main calls take place in the last few lines of code. To help you understand the logic will start at the beginning and work our way down.
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
> <i>files</i> is a sorted list of the paths to the input csvs. **It is critical that you have followed the directory setup instructions in the [data acquisition tutorial](data_acquisition.md).** If this has been done incorrectly, you files will not be ordered properly and the F.A.M. results will be erroneous. In this example everything is already setup properly so you don't need to worry.
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
    yr_2008 = process(files[0:24], 2008)
    yr_2009 = process(files[24:48], 2009)
    yr_2010 = process(files[48:72], 2010)
    yr_2013 = process(files[72:96], 2013)
    yr_2015 = process(files[96:120], 2015)
    yr_2016 = process(files[120:144], 2016)
    yr_2017 = process(files[144:168], 2017)
    yr_2018 = process(files[168:192], 2018)
    yr_2019 = process(files[192:216], 2019)

    export(yr_2008, "cache/yr_2008")
    export(yr_2009, "cache/yr_2009")
    export(yr_2010, "cache/yr_2010")
    export(yr_2013, "cache/yr_2013")
    export(yr_2015, "cache/yr_2015")
    export(yr_2016, "cache/yr_2016")
    export(yr_2017, "cache/yr_2017")
    export(yr_2018, "cache/yr_2018")
    export(yr_2019, "cache/yr_2019")
```
> We are going to run into a rather dense <i>try-catch</i> block here. F.A.M. uses historical data as part of the classification procedure (more on this later). When running for the current year you don't need to rerun for the past years. To save time and computing resources, we will cache our previously processed data. **Note: you will need to delete any year from the cache if you update the input data for that year.**
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

    print("Processed:", df.shape)
    print("\n")

    return df
```
> This function Uses a series operations to merge multiple .csv files together to uniformly format ndvi time series data across the state. Additionally, function linearly interpolates and constrains observations to 8 day intervals. Let's move on.
>
```python
# historic years
years = [yr_2008, yr_2009, yr_2010, yr_2013, yr_2017]

# calculate 5 year maximums for smoothed ts
max_smooth_spring = np.array([smooth(df.iloc[:,8:19]).max(axis=1) for df in years]).max(0)
max_smooth_overlap = np.array([smooth(df.iloc[:,12:23]).max(axis=1) for df in years]).max(0)
max_smooth_summer = np.array([smooth(df.iloc[:,19:38]).max(axis=1) for df in years]).max(0)

max_smooth_5yr = pd.DataFrame({'id': yr_2018.index.values, 'spring_ndvi_smoothed_5yr_max':
 max_smooth_spring,'overlap_ndvi_smoothed_5yr_max': max_smooth_overlap,
 'summer_ndvi_smoothed_5yr_max': max_smooth_summer}).set_index('id')
```
> As mentioned above, F.A.M. uses historical data as part of the classification procedure. Here we have defined 2008, 2009, 2010, 2013, and 2017 as our reference years. Internal testing showed five years is sufficient for accurate results, however you may add more if desired. This block is calculating a maximum ndvi time series for these year to use as a retrospective reference.
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
> Our testing showed that the above thresholds yield the highest accuracy, however these may not hold over time. The curators of F.A.M. will work to keep them updated. The <i>crop_type</i> variable stores information about which crop ids have known perennials. You can provided your own list if desired and the format is provided in this repository.
>
```python
years = [yr_2019, yr_2018, yr_2017, yr_2016, yr_2015, yr_2013, yr_2010]
for year in years:
    name = [x for x in globals() if globals()[x] is year][0]
    export(postProcess(year)[0],'output/Washington_Spring_'+name[3:7])
    export(postProcess(year)[1],'output/Washington_Summer_'+name[3:7])

print("Post-processing & exports completed at",snapshot(start),"minutes.\n")

# end script time
end = time.time()
print("Total time to run script:", str(round((end-start)/60,3)), "minutes.\n")
```
> Here are the main algorithmic calls.