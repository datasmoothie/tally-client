# The API

The Python SDK API (which is a Python wrapper to the Tally API) allows users to both perform data processing tasks such as cleaning, weighting and creating new variables, and to build deliverables to clients.

:::{warning}
Note that all methods sent to the DataSet object have to use keyword arguments. This is because the parameters get sent straight to the API. So, use `dataset.crosstab(x='q1', y='gender')` instead of `dataset.crosstab('q1', 'gender')`.
:::


The Two main aspects of the API is the DataSet and the Build. The DataSet object represents the data and meta-data in a survey is used for loading and converting data, saving to files, and all the data processing tasks.

- [Build](api_build)
- [DataSet](api_dataset)