import json
import pandas as pd

def decode_result_to_dataframe(json_dict, column_names=None, index_names=None):
    """
    Decodes json result string and return pd.DataFrame

    The API always returns result dataframes as json, but in order to test we might want to
    convert these to pandas dataframes to easily run calculations and checks. This function
    takes the json dict with results and returns a dataframe.

    Parameters:
    json_dict (dict) - data that represents a quantipy dataframe as json

    Returns
    pandas.DataFrame object with the results, using the same structure as quantipy.

    """
    if 'column_names' in json_dict.keys() and json_dict['column_names'] != [None] and 'index_names' in json_dict.keys() and json_dict['index_names'] != [None]:
        columns = pd.MultiIndex.from_tuples(json_dict['columns'], names=json_dict['column_names'])
        index = pd.MultiIndex.from_tuples(json_dict['index'], names=json_dict['index_names'])
    elif column_names and index_names:
        columns = pd.MultiIndex.from_tuples(json_dict['columns'], names=column_names)
        index = pd.MultiIndex.from_tuples(json_dict['index'], names=index_names)
    else:
        columns = json_dict['columns']
        index = json_dict['index']
    df = pd.DataFrame(data=json_dict['data'])
    df.columns = columns
    df.index = index
    return df

