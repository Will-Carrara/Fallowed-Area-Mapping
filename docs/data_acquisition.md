# Data Acquisition
>
>
> ## Introduction
> This [document](https://docs.google.com/document/d/1TTolXOjy3UQUG_UKBN5ror2HNB1JjmtVScBrJW-CjHo/edit#heading=h.jpm77k4o3md1) will guide you through the process of extracting the average NDVI of a given set of polygons of farm field boundaries, formatting the extracted files for analysis, and creating pivot tables. You will be using the Google Earth Engine Python API to do the extraction and Python to do the rest.
>
> The goal here is to obtain properly formatted NDVI timeseries data in multiple .csv files for the input. Once the extractions are completed there will be a series of files which look something like this:
>
> <img src="imgs/format.png" width="600"/>
>
> ## Directory Setup
> You will need to initially set up a directory structure in this format. Note this will vary for the years you
```bash
    .
    ├── docs
    ├── states                  # comment
    │   ├── California          # comment
    │   ├── Nevada              # comment
    │   └── Washington          # comment
    └── ...
```