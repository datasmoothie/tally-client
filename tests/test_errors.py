import pandas as pd
import tally

def test_method_not_found(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    result = ds.unknown_method()
    assert result == "Unknown method 'unknown_method'. See https://tally.datasmoothie.com for available methods."


def test_method_not_found_but_close(token, api_url):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    result = ds.variabbles()
    assert result == "Unknown method 'variabbles'. Did you mean 'variables'? See https://tally.datasmoothie.com for available methods."

