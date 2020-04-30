# Data Acquisition
>
>
> ## Introduction
> This [document](https://docs.google.com/document/d/1TTolXOjy3UQUG_UKBN5ror2HNB1JjmtVScBrJW-CjHo/edit?usp=sharing) will guide you through the process of extracting the average NDVI of a given set of polygons of farm field boundaries. You will be using the Google Earth Engine's Python API to do the extraction. The goal here is to obtain properly formatted NDVI timeseries data in multiple .csv files to use for the F.A.M. algorithm's input.
>
> **You only need to obtain the raw .csv outputs after completing step 5 in the document linked above.** F.A.M. contains routines to format and merge the extracted files in accordance to the algorithm's requirements. Once the extractions are completed there will be a series of files which look something like this:
>
> <img src="imgs/format.png" width="600"/>
>
> ## Directory Setup
> You will need to initially set up a directory structure in this format. Much of this will be completed after cloning the repository, however the input folders will need to be configured for your specific application as the years you intend to analyze may vary from others.
```bash
    .
    ├── docs                    # documentation
    └── states
        ├── California
        │   ├── input
        │   │   ├── 2008
        │   │   ├── ...         # a directory for each year of data
        │   │   ├── 2020
        │   │   └── crop_data   # perennial data to be stored here
        │   ├── output
        │   └── cache           # will be created automatically after initial run
        │
        ├── Nevada
        │   ├── input
        │   │   ├── 2008
        │   │   ├── ...
        │   │   └── 2020
        │   ├── output
        │   └── cache
        │
        └── Washington
            ├── input
            │   ├── 2008
            ├── ├── ...
            │   ├── 2020
            │   └── crop_data
            ├── output
            └── cache
```
> In the <i>input</i> directories within each folder labeled according its corresponding year, place the output files of the extractions. You will note that there is a folder named <i>crop_data</i>. This contains a .csv file which lists known perennial sites within the state. This information is provided for both Washington and California, the latter can be found [here](../states/California/sample_crop_data/).
>
> Now that everything is in place, we can proceed to [running](tutorial.md) F.A.M.