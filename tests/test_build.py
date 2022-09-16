import pandas as pd
import os
import tally
import pytest

def test_add_table(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    ds.add_credentials(api_key=token, host=api_url, ssl=True)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)

    table = build.add_table(banner=['gender', 'locality'])

    # base can be outside, above (default), hide
    table.add_data(
        stub={'x':'q1', 'f':{'locality':[1]}, 'w':'weight_a', 'base':'both'}, 
        options={'base':'outside'}, 
        dataset=ds
        )

    table.add_data(
        stub={'x':'q3', 'f':{'locality':[1]}, 'w':'weight_a'}, 
        options={'base':'hide'}
        )

    table.add_data(
        stub={'x':'q2b', 'f':{'locality':[1]}, 'w':'weight_a'}, 
        options={'base':'outside'}, 
        dataset=ds
        )

    print(table.combine_dataframes())