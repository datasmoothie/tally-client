import pandas as pd
import os
import tally
import pytest
import json
import urllib


def test_qp_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    df = ds.crosstab(x='q1', y='gender')
    assert isinstance(df,pd.core.frame.DataFrame)

    json_result = ds.crosstab(x='q1', y='gender', format='dict')
    assert isinstance(json_result, dict)

    json_result = ds.crosstab(x='q1', y='gender', format='json')
    assert isinstance(json_result, str)

def test_rebase(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    df = ds.crosstab(x='q1', ci=['c%'])
    df2 = ds.crosstab(x='q2b', ci=['c%'])
    df3 = ds.crosstab(x='q2b', ci=['c%'], rebase='q1')

    # base in q2b should be the q1 base
    assert df3.iloc[0,0] == df.iloc[0,0]
    assert df2.iloc[0,0] != df3.iloc[0,0]

def test_crosstab_formats(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    df = ds.crosstab(x='q1', y='gender')
    assert isinstance(df,pd.core.frame.DataFrame)

    dict_result = ds.crosstab(x='q1', y='gender', format='dict')
    assert isinstance(dict_result, dict)

    df = tally.result_to_dataframe(dict_result['result'])
    df2 = ds.crosstab(x='q1', y='gender')
    assert df.equals(df2)

    json_result = ds.crosstab(x='q1', y='gender', format='json')
    assert isinstance(json_result, str)

def test_joined_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    result = ds.crosstab(
        crosstabs=[
            {"x":["q1"]},
            {"x":["q1"], "ci":["c%",  "counts"], "f":{"gender":[1]}},
            {"x":["q1"], "ci":["mean"]}
        ]
    )
    assert isinstance(result, pd.DataFrame)


def test_spss_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.crosstab(x='q1', y='gender', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)

    result2 = ds.crosstab(x='q2b', y='locality', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)
    
def test_filter(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    result = ds.filter(alias='women', condition={'gender':[2]})
    assert ds.crosstab(x='q1').iloc[0,0] == 4303.0

def test_set_value_texts(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    result = ds.set_value_texts(name="gender", renamed_vals={1:"Men", 2:"Women"})
    assert list(ds.crosstab(x='gender').index.get_level_values(1)) == ['Base', 'Men', 'Women']

def test_copy_variable(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    result = ds.copy(name="q1", suffix="test")
    assert ds.crosstab(x='q1_test').iloc[0,0] == 8255.0

def test_find(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    result = ds.find(str_tags=['q14'], format=dict)
    assert result['variables'] == ['q14_1', 'q14_2', 'q14_3']

def test_values(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')
    result = ds.values(name="q1", format="dict")
    assert list(result['values'].keys()) == ['1', '2', '3', '4', '5', '6', '7', '8', '9', '96', '98', '99']


def test_variables(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')
    result = ds.variables()
    assert 'single' in result.keys()

def test_meta(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')
    result = ds.meta(variable='q1')
    assert result.shape == (12, 3)

def test_get_variable_text(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    result = ds.get_variable_text(name='gender')
    assert result == 'What is your gender?'

def test_expand_with_data(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    ds.extend_values(
        name='locality', 
        ext_values=[[6, "Urban/CBD"], [7, "Rural/Remote"]],
        add_data={6: {"locality": [1,2]}, 7: {"locality": [4,5]}}
    )


@pytest.mark.skip(reason="Change this to reflect error message from API")
def test_invalid_params(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')
    with pytest.raises(ValueError):
        result = ds.meta(var='q1')

def test_to_delimited_set(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (B).sav')
    result = ds.to_delimited_set(name='satisfaction', label="Sports", variables=['overall', 'price', 'service'], from_dichotomous=False)
    ct = ds.crosstab(x='satisfaction')

@pytest.mark.skip(reason="Tally was updated to always return 'features':[], so this this test should be fixed or Tally updated.")
def test_feature_select(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (B).sav')
    categoricals = ds.variables(format='dict')['single']
    categoricals.remove('overall')
    result = ds.feature_select(x=categoricals, y="overall")
    assert result['features'][0] == 'service'

def test_derive(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')
    cond_map = [
        (1, "Urban", {'locality':[1,2]}),
        (2, "Rural", {'locality':[3,4]})
    ]
    result = ds.derive(name='urban', label='Urban or rural', cond_map=cond_map, qtype="single")

    crosstab = ds.crosstab(x='urban')
    assert crosstab.shape == (3,1) 

def test_error_messages(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    scheme = {
        'locality':{1:36.0, 2:27.4, 3:16.0, 4:10.0, 5:10.6},
        'gender':{1:49.0, 2:51.0}
    }

    with pytest.raises(ValueError) as e_info:
        ds.meta(variable='unknown', format='dict')
    assert '"detailed_message":"unknown - is not in the dataset"' in str(e_info.value)

    result = ds.weight(name='my weight', variable='weight_c', unique_key='unknown_column', scheme=scheme)
    assert "'message': 'unknown_column - the unique key specified for the weighting does not " + \
        "exist in the dataset'" in str(result)

    scheme = {
        'error':{1:36.0, 2:27.4, 3:16.0, 4:10.0, 5:10.6},
        'gender':{1:49.0, 2:51.0}
    }
    result = ds.weight(name='my weight', variable='weight_c', unique_key='unique_id', scheme=scheme)
    assert 'error' in result

def test_weight_spss(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    scheme={
            'locality':{1:36.0, 2:27.4, 3:16.0, 4:10.0, 5:10.6},
            'gender':{1:49.0, 2:51.0}
        }
    result = ds.weight(name='my weight', variable='weight_c', unique_key='unique_id', scheme=scheme)
    ct1 = ds.crosstab(x='gender', ci=['c%'], w='weight_c')
    assert ct1.loc[('What is your gender?','Female')][0] == 51.1
    ct2 = ds.crosstab(x='locality', ci=['c%'], w='weight_c')
    assert ct2.loc[('How would you describe the areas in which you live?','Urban')][0] == 27.4

def test_weight_unicom(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_unicom('tests/fixtures/Example_Museum.mdd', 'tests/fixtures/Example_Museum.ddf')
    scheme={
            'gender':{1:49.0, 2:51.0}
        }
    result = ds.weight(name='my weight', variable='weight_c', unique_key='serial', scheme=scheme)
    ct1 = ds.crosstab(x='gender', ci=['c%'], w='weight_c')
    assert 'interest' in list(ds.variables()['single'])
    assert ct1.loc[('Gender of respondent','Female')][0] == 51.0

def test_weight_csv(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')

    scheme={
            'locality':{1:36.0, 2:27.4, 3:16.0, 4:10.0, 5:10.6},
            'gender':{1:49.0, 2:51.0}
        }
    result = ds.weight(name='my weight', variable='weight_c', unique_key='resp_id', scheme=scheme)
    ct1 = ds.crosstab(x='gender', ci=['c%'], w='weight_c')
    assert ct1.loc[('','Female')][0] == 49.1

@pytest.mark.skip(reason="Need to finalise unicom conversion")
def test_unicom_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    ds.use_unicom('tests/fixtures/Example_Museum.mdd', 'tests/fixtures/Example_Museum.ddf')

    result = ds.crosstab(x='gender')
    assert isinstance(result, pd.DataFrame)

@pytest.mark.skip(reason="We don't store the pq and csv files in the repo, upload them first")
def test_parquet_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    ds.use_parquet('tests/fixtures/Tabulation_Test_Project.pq', 
                   'tests/fixtures/Tabulation_Test_Project.csv')

    result = ds.crosstab(x='q2')
    assert isinstance(result, pd.DataFrame)

    ds.derive(
            name="banner_var_4", 
            label="Location",
            cond_maps=[(1, 'Central Scotland', {'q4': [1]})],
            qtype="single"
    )

    ds.extend_values(name="banner_var_4",ext_values=[[2, 'East England']], add_data={2: {'q4':[2]}})

 

def test_csv_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')

    result = ds.crosstab(x='q1', y='gender', sig_level=[0.05])
    assert isinstance(result, pd.DataFrame)

@pytest.mark.skip(reason="Don't test on live confirmit api")
def test_confirmit_crosstab(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    creds = {'source_projectid':"p913481003361",
            'source_public_url':"https://ws.euro.confirmit.com/",
            'source_idp_url':"https://idp.euro.confirmit.com/",
            'source_client_id':"71a15e5d-b52d-4534-b54b-fa6e2a9da8a7",
            'source_client_secret':"2a943d4d-58ab-42b8-a276-53d07ad34064"}
    ds.use_confirmit(**creds)
    result = ds.crosstab(x='q1')
    assert isinstance(result, pd.DataFrame)

# uncomment to test nebu api
#def test_nebu_crosstab(token, api_url, use_ssl):
#    ds = tally.DataSet()
#    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
#    ds.use_nebu('https://app.nebu.com/app/rest/spss/[insert_key]?language=en')
#    result = ds.crosstab(x='Gender')
#    assert isinstance(result, pd.DataFrame)

def test_spss_to_csv_json(token, api_url, use_ssl):
    ds = tally.DataSet()
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    result = ds.convert_spss_to_csv_json()
    assert 'csv' in result.keys()

def test_crosstabs_with_format_column(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    ct1 = ds.crosstab(crosstabs=[{"x":"q1", "y":"gender"}], add_format_column=True)

    ct2 = ds.crosstab(
        crosstabs= [{'x': 'q1', 'y': 'gender'},
                    {'x': 'q2', 'y': 'gender'}],
        add_format_column=True
    )



def test_build_excel_from_dataframes(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)

    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    ct1 = ds.crosstab(
        crosstabs=[{
            "x":["q1", "q2b"], "y":"gender"
        }],
        add_format_column=True,
        format='dict'
    )
    ct2 = ds.crosstab(
        crosstabs=[
            {
                "x":["q1"], "y":"locality", "f":{"gender":[1]}, "stats":["mean"]
            },
            {
                "x":["q2b"], "y":"locality"
            }

        ],
        add_format_column=True,
        format='dict'
    )

    dataframes = [ct1['result'], ct2['result']]
    res = ds.build_excel_from_dataframes(filename='myfile.xlsx', dataframes=dataframes)
    #os.remove('myfile.xlsx')

def test_build_excel(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.build_excel(filename='my_tables.xlsx', x=['q1', 'q2b'], y=['gender', 'locality'], sig_level=[0.05])
    os.remove('my_tables.xlsx')
    assert result.status_code == 200

def test_build_powerpoint(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    
    ds.use_spss('tests/fixtures/Example Data (A).sav')

    result = ds.build_powerpoint(filename='my_powerpoint.pptx',
                                 powerpoint_template='tests/fixtures/Datasmoothie_Template.pptx', 
                                 x=['q1', 'q2b'], 
                                 y=['@', 'gender', 'locality']
                                 )
    os.remove('my_powerpoint.pptx')
    assert result.status_code == 200

def test_save_spss(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    result = ds.write_spss('my_sav.sav')
    os.remove('my_sav.sav')
    assert result.status_code == 200

def test_api_to_python_doc(token, api_url, use_ssl):
    with urllib.request.urlopen("https://tally.datasmoothie.com/openapi/?format=openapi-json") as url:
        data = json.load(url)
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    meta_string = ds._endpoint_api_to_docstring(data, 'meta')
    variable_string = ds._endpoint_api_to_docstring(data, 'variables')

@pytest.mark.skip(reason="This test is only run to generate new methods")
def test_meta_created_variables_function(token, api_url, use_ssl):
    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    result = ds._generate_functions_from_api()
    with open('functions.py', 'w') as f:
        f.write(result)

def test_error_response(token, api_url, use_ssl):
    params = {
        "name":"singleVar",
        "label":"variable of type single",
        "qtype":"single"
    }

    ds = tally.DataSet(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_spss('tests/fixtures/Example Data (A).sav')
    with pytest.raises(ValueError) as e_info:
        ds.create_empty_variable(**params)
    assert str(e_info.value) == \
        '{"error":{"type":"invalid_arguments","message":"Must provide \'categories\' ' + \
        'when requesting data of type single.","detailed_message":"Must provide' + \
        ' \'categories\' when requesting data of type single.","payload":{}}}'