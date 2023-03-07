# Load/extract data
The first step is always loading your data into Tally. This converts the data from whatever format your data provider uses to a uniform, open source data format (built on the open source Quantipy).

In the following examples, we assume an instance of Tally has been created by using your API key.

```
import tally
dataset = tally.DataSet(api_key=MY_KEY)
```

## Supported platforms and file types

Files supported by Tally include 

- SPSS
- CSV
- Excel
- Parquet
- Unicom (FKA Dimensions) files.

Support for online data sources includes:

- Unicom
- Forsta (FKA Confirmit)
- Enghouse
- Alchemer

In the following examples, we assume the `tally` instance has been created by [loading your API key](../get_started).

:::{note}
If your platform is not listed here, we can add it! We are constantly adding new platforms and the next ones on our list are Qualtrics and Decipher.
:::


## File based data

Loading file based data with Tally is easy.

```
#unicom
unicom_dataset.use_unicom('data/Example_Museum.mdd', 'data/Example_Museum.ddf')
# CSV
csv_dataset.use_csv('data/Example.CSV')
# SPSS
spss_dataset.use_spss('data/Example Data.sav')
```

## Remote/online data

Tally also works with online/remote data.

```
# Forsta
dataset.use_forsta(credentials)
# NEBU/Enghouse
dataset.use_nebu('https://app.nebu.com/app/rest/spss/{}?language=en'.format(keys['nebu']))
```

