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
> ## Step 1
> Script modification will need to be made based on your specific inputs. The current format of the algorithm varies slightly state by state, however the fundamental structure is very similar.
>
> This script is written in a functional programming style, where the main calls take place in the last few lines of code. To help you understand the logic will start at the beginning.
```python
# field status                        cdl
crp = 5 # cropped                     -> 2
flw = 4 # fallow                      -> 10
prn = 3 # perennial, no crop yet      -> 15
pin = 2 # partially irrigated normal  -> 8
pop = 1 # partially irrigated poor    -> 9

```
> Here we are defining the dummy variables which we will use to encode our classes. These numbers are not chosen arbitrarily and their order is of consequence. F.A.M uses a hierarchical merging process in which classes with a higher weight take precedence. The intuition here, is that if the routine classifies a field as cropped, it is possible that it may also be classified as partially irrigated. In such an event, the cropped status will take priority. This method is programmatically equivalent to running the sub-classifications on the residuals of each prior run.
```python
files = np.sort([x for x in glob.glob('input/*/*.csv')])
```
<i>files</i> is sorted list of the paths to the input csvs. **It is critical that you have followed the directory setup instructions in the [Data Acquisition](data_acquisition.md) tutorial.** If this has been done incorrectly, you files will not be ordered properly and the F.A.M. results will be inaccurate. In this example, everything is already setup properly.















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
> The F.A.M. algorithm uses a lot of list comprehension. If you are not familiar with this, you can find more information [here]("https://www.geeksforgeeks.org/comprehensions-in-python/").