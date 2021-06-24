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

    result = ds.crosstab(x='q1', y='gender', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)

    result2 = ds.crosstab(x='q2', y='locality', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)


def test_csv_crosstab(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')

    result = ds.crosstab(x='q1', y='gender', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)

def test_confirmit_crosstab(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    creds = {'source_projectid':"p913481003361",
            'source_public_url':"https://ws.euro.confirmit.com/",
            'source_idp_url':"https://idp.euro.confirmit.com/",
            'source_client_id':"71a15e5d-b52d-4534-b54b-fa6e2a9da8a7",
            'source_client_secret':"2a943d4d-58ab-42b8-a276-53d07ad34064"}
    ds.use_confirmit(**creds)
    result = ds.crosstab(x='q1')
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

    result = ds.build_excel(filename='my_tables.xlsx', x=['q1', 'q2'], y=['gender', 'locality'], sig_level=[0.05])
    os.remove('my_tables.xlsx')
    assert result.status_code == 200

def test_build_powerpoint(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.build_powerpoint(filename='my_powerpoint.pptx',
                                 powerpoint_template='tests/fixtures/Datasmoothie_Template.pptx', 
                                 x=['q1', 'q2', 'q3'], 
                                 y=['@', 'gender', 'locality']
                                 )
    os.remove('my_powerpoint.pptx')
    assert result.status_code == 200