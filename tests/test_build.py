import pandas as pd
import os
import tally
import pytest

def test_add_table(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)

    sheet = build.add_sheet(banner=['gender', 'locality'])
    sheet.table_options = {
        'base': 'outside',
        'format': {
            'base':{"font_color":"#ff00ff", "bold":True}
        }
    }
    sheet.options = {'pull_base_up': False}

    # base can be outside, above (default), hide
    sheet.add_table(stub={'x':'q1', 'f':{'locality':[2]}, 'w':'weight_a', 'base':'both'})
    sheet.add_table(stub={'x':'q3', 'f':{'locality':[1]}, 'w':'weight_a'}, options={'base':'hide'})
    sheet.add_table(stub={'x':'q2b', 'f':{'locality':[1]}, 'w':'weight_a'}, dataset=ds)

    print(sheet.combine_dataframes())
    build.save_excel('test.xlsx')