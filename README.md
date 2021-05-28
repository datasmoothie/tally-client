# Tally Python client
The Tally Python client is a wrapper for Datasmoothie's Tally API for market research and survey data. It's a RESTful
API that leverages Quantipy and other techologies to give users access to all the data processing, aggregation and
exporting functions they need.

# Quick start
Tally is compatible with both SPSS (.sav) files and Quantipy files.

```
ds = tally.DataSet(api_token=[your_token])
ds.use_spss('my_spss_file.sav')

pandas_dataframe = ds.crosstab(x=['q1', 'q2'], y=['gender', ['locality'], sig_level=[0.05]])

ds.build_powerpoint(filename='my_powerpoint.pptx',
                    powerpoint_template='My_Branded_Template.pptx', 
                    x=['q1', 'q2', 'q3'], 
                    y=['gender', 'locality']
                    )

ds.build_excel(filename='my_tables.xlsx',
               powerpoint_template='My_Branded_Template.pptx', 
               x=['q1', 'q2', 'q3'], 
               y=['gender', 'locality'],
               sig_level[0.05,  0.1]
               )

```
## Supported file formats and data sources
Tally supports SPSS fiels, Quantipy files. It also supports external datasources, such as Datasmoothie (with more on the way).

```
#datasmoothie (remote storage of data)
ds.use_datasmoothie(datasmoothie_token=[my_datasmoothie_api_token])

#using spss (local sav file)
ds.use_spss(path_to_sav_file)

#using quantipy (local json and csv files)
ds.use_quantipy(path_to_json_metadata, path_to_csv_data)
```


## contributing and running pytest

This is best run against a development API, like one run by gitpod. This might look like: 

python -m pytest --api_url=8000-coral-mackerel-9cdy66vz.ws-eu04.gitpod.io --token=[my_token]

