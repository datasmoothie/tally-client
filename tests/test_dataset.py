import pandas as pd
import os
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

def test_build_excel(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.build_excel(filename='my_tables.xlsx', x='q1', y='gender', sig_level=[0.05])
    os.remove('my_tables.xlsx')
    assert result.status_code == 200

def test_build_powerpoint(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.build_powerpoint(filename='my_powerpoint.pptx',
                                 powerpoint_template='tests/fixtures/Datasmoothie_Template.pptx', 
                                 x=['q1', 'q2', 'q3'], 
                                 y=['gender', 'locality']
                                 )
    os.remove('my_powerpoint.pptx')
    assert result.status_code == 200