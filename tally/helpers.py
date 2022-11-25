import io
import json
import pandas as pd


def result_to_dataframe(json_dict):
    """ Deserializes a dataframe that was serialized with orient='split'
    """
    if 'column_names' and 'index_names' in json_dict.keys():
        columns = pd.MultiIndex.from_tuples(json_dict['columns'], names=json_dict['column_names'])
        index = pd.MultiIndex.from_tuples(json_dict['index'], names=json_dict['index_names'])
    else:
        columns = json_dict['columns']
        index = json_dict['index']
    df = pd.DataFrame(data=json_dict['data'])
    df.columns = columns
    df.index = index
    return df

def find_columns_in_crosstab(key, crosstab):
    columns = []
    if key in crosstab:
        if key == 'f':
            columns += list(crosstab[key].keys())
        elif isinstance(crosstab[key], str):
            columns.append(crosstab[key])
        elif isinstance(crosstab[key], list):
            columns = crosstab[key]
    return columns

def get_columns_from_crosstabs(crosstabs):
    columns = []
    for crosstab in crosstabs:
        for key in ['x', 'y', 'f', 'w']:
            columns += find_columns_in_crosstab(key, crosstab)
    return list(set(columns))
