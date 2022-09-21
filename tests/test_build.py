import pandas as pd
import os
import tally
import pytest

def test_add_table(token, api_url):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=True)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)

    sheet = build.add_sheet(banner=['gender', 'locality'])

    sheet.set_base_position('outside')
    sheet.set_answer_format('base', {"font_color":"#ff00ff", "bold":True})
    sheet.set_question_format('percentage', {"bold":True})
    sheet.set_column_format('base', 1, {"bold":True})
    sheet.set_column_format('percentage', 1, {"bold":True})

    sheet.options = {'pull_base_up': False}
    #sheet.options = {'sig_test_level': 0.05}

    # base can be outside, above (default), hide
    sheet.add_table(stub={'x':'q2b', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True, 'stats':['mean', 'stddev']}, dataset=ds)
    sheet.add_table(stub={'x':'q1', 'ci':['c%'], 'f':{'locality':[2]}, 'w':'weight_a', 'base':'both', 'xtotal':True})
    sheet.add_table(stub={'x':'q3', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, options={'base':'hide'})
    sheet.add_table(stub={'x':'q2b', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, dataset=ds)

    print(sheet.combine_dataframes())
    build.save_excel('test.xlsx')