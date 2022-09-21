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
                          options={'row_format':{'rows':[4,5,6], 'format':{'bg_color':'#F15A30'}}})
    sheet.add_table(stub={'x':'q3', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, options={'base':'hide'})
    sheet.add_table(stub={'x':'q2b', 'ci':['c%'], 'f':{'locality':[1]}, 'w':'weight_a', 'xtotal':True}, dataset=ds)

    print(sheet.combine_dataframes())
    build.save_excel('test.xlsx')

def test_add_simple_table(token):
    ds = tally.DataSet(api_key=token)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)



    sheet = build.add_sheet(banner=['gender', 'locality'])

    sheet.set_question_format('percentage', {"bg_color":'#ff00ff', 'text_wrap':True})
    sheet.set_answer_format('base', {"font_color":"#F15A30", "bold":True})

    sheet.set_show_table_base_column(True)
    sheet.set_column_format('base', 1, {"bold":True})
    sheet.set_column_format('percentage', 1, {"bold":True})


    sheet.set_base_position('outside')
    sheet.options = {'pull_base_up': False}

    sheet.add_table(stub={'x' : 'q14r01c01'}) 
    sheet.add_table(stub={'x' : 'q14r02c01', 'stats':['mean']})
    sheet.add_table(stub={'x' : 'q14r03c01'},
                          options={'row_format':{'rows':[4,5], 'format':{'bg_color':'#F15A30'}}}
                   )

    build.save_excel('test.xlsx')

def test_add_many_sheets(token):
    ds = tally.DataSet(api_key=token)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    build = tally.Build(name='client A', default_dataset=ds)

    questions = list(range(1,7))
    stores = list(range(1,4))

    for store in stores:
        sheet = build.add_sheet(banner=['gender', 'locality'])
        for question in questions:
            value = f"q14r0{question}c0{store}"
            sheet.add_table(stub={'x' : value} ,
                            options={'row_format':{'rows':[4,5], 
                                     'format':{'bg_color':'#F15A30'}
                            }}
                            )
    import pdb; pdb.set_trace()
    build.save_excel('test.xlsx')