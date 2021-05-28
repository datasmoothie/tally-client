import pandas as pd

import tally

def test_qp_crosstab(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    ds.crosstab(x='q1', y='gender')

def test_spss_crosstab(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.crosstab(x='q1', y='gender', sig_level=0.05)
    assert isinstance(result, pd.DataFrame)

def test_spss_to_csv_json(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    result = ds.convert_spss_to_csv_json()
    assert 'csv' in result.keys()