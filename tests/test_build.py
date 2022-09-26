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
    sheet.set_answer_format('base', {"font_color":"#F15A30", "bold":True})
    sheet.set_question_format('percentage', {"bold":True})
    sheet.set_column_format('base', 1, {"bold":True})
    sheet.set_column_format('percentage', 1, {"bold":True})

    sheet.options = {'pull_base_up': False}
    #sheet.options = {'sig_test_level': 0.05}

    # base can be outside, above (default), hide
    sheet.add_table(stub={'x':'q2b', 'ci':['c%', 'counts'], 'xtotal':True, 'stats':['mean', 'stddev']}, dataset=ds)
    sheet.add_table(stub={'x':'q2b', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True, 'stats':['mean', 'stddev']}, dataset=ds)
    sheet.add_table(stub={'x':'q1', 'ci':['c%'], 'f':{'locality':[2]}, 'w':'weight_a', 'base':'both', 'xtotal':True}, 
                          options={'row_format':{'rows':[4,5,6], 'format':{'bg_color':'F15A30'}}})
    sheet.add_table(stub={'x':'q3', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, options={'base':'hide'})
    sheet.add_table(stub={'x':'q2b', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, dataset=ds)

    build.save_excel('test.xlsx')

def test_default_options(token):
    ds = tally.DataSet(api_key=token)
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    build = tally.Build(name='Client A', subtitle="Datasmoothie", default_dataset=ds)

    all_variables = ds.variables()
    banner_vars = ['gender', 'locality']
    stub_vars = [i for i in all_variables['single'] if i not in banner_vars]
    stub_vars = stub_vars + list(all_variables['delimited set'])

    sheet = build.add_sheet(banner=['gender', 'locality'])

    sheet.add_table(stub={'x':stub_vars[0]})

    build.sheets[0].add_table(stub={'x':'ethnicity'})

def test_add_simple_table(token):
    ds = tally.DataSet(api_key=token)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='Client A', subtitle="Datasmoothie", default_dataset=ds)
    build.add_logo('tests/fixtures/datasmoothie-logo.png')

    sheet = build.add_sheet(banner=['gender', 'locality'])
    sheet.options = {'pull_base_up': False}


    #sheet.set_question_format('percentage', {"bg_color":'fffff', 'text_wrap':True})
    #sheet.set_answer_format('base', {"font_color":"F15A30", "bold":True})

    sheet.set_show_table_base_column(True)
    sheet.set_column_format('base', 1, {"bold":True})
    sheet.set_column_format('percentage', 1, {"bold":True})


    sheet.set_base_position('outside')
    sheet.options = {'pull_base_up': False}

    sheet.add_table(stub={'x' : 'q14r01c01'}) 
    sheet.add_table(stub={'x' : 'q14r02c01', 'stats':['mean']})
    sheet.add_table(stub={'x' : 'q14r03c01'},
                          options={'row_format':{'rows':[4,5], 'format':{'bg_color':'F15A30'}}}
                   )

    build.save_excel('test_simple_table.xlsx')

def test_global_options(token):
    ds = tally.DataSet(api_key=token)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    build = tally.Build(name='client A', default_dataset=ds)

    build.add_logo('tests/fixtures/datasmoothie-logo.png')
    build.set_index_option('link_color', '57215B')

    sheet = build.add_sheet(banner=['gender', 'locality'])
    sheet2 = build.add_sheet(banner=['gender', 'locality'])

    [i.set_base_position('outside') for i in build.sheets]
    [i.freeze_panes(9,1) for i in build.sheets]
    [i.set_format('base', {'border': '1'}) for i in build.sheets]
    [i.set_default_weight('weight_a') for i in build.sheets]
    [i.set_default_show_bases('both') for i in build.sheets]

    sheet.add_table(stub={'x' : 'q14r01c01', 'stats':["mean", "stddev"]}) 
    sheet.add_table(stub={'x' : 'q14r01c02', 'stats':["mean", "stddev"]}) 

    sheet2.add_table(stub={'x' : 'q14r02c01', 'stats':["mean", "stddev"]}) 
    sheet2.add_table(stub={'x' : 'q14r02c02', 'stats':["mean", "stddev"]}) 

    build.save_excel('test_global_options.xlsx')


def test_add_many_sheets(token):
    ds = tally.DataSet(api_key=token)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)
    build.add_logo('tests/fixtures/datasmoothie-logo.png')

    questions = list(range(1,9))
    stores = list(range(1,4))

    for question in questions:
        sheet = build.add_sheet(banner=['gender', 'locality'])
        #sheet.set_sig_test_levels(0.05)
        for store in stores:
            value = f"q14r0{question}c0{store}"
            sheet.add_table(stub={'x' : value} ,
                            options={'row_format':{'rows':[4,5], 
                                     'format':{'bg_color':'F15A30'}
                            }}
                            )
    build.save_excel('test_many_sheets.xlsx')