import pandas as pd
import tally
import pytest

def test_method_not_found(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    with pytest.raises(ValueError) as e:
        result = ds.unknown_method()
    assert str(e.value) == "Unknown method 'unknown_method'. See https://tally.datasmoothie.com for available methods."


def test_method_not_found_but_close(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    with pytest.raises(ValueError) as e:
        result = ds.variabbles()

    assert str(e.value) == "Unknown method 'variabbles'. Did you mean 'variables'? See https://tally.datasmoothie.com for available methods."

@pytest.mark.skip("not supported for now")
def test_no_kwargs(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    with pytest.raises(ValueError) as e:
        ds.crosstab('gender')

    assert str(e.value) == "The Tally client does not support non keyword arguments. For example, use dataset.crosstab(x='age'), not dataset.crosstab('age')."

def test_no_data_loaded(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    with pytest.raises(ValueError) as e:
        ds.crosstab(x='gender', ci=['c%'])
    
    assert str(e.value) == "You haven't selected any data. Use one of the dataset.use_* methods to load data."
    
def test_invalid_token(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key='invalid', host=api_url, ssl=use_ssl)

    with pytest.raises(ValueError) as e:
        ds.use_spss('tests/fixtures/Example Data (A).sav')
    
    assert str(e.value) == "Invalid or expired API token: invalid"
