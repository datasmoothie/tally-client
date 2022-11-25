import functools
import io
import json
import pandas as pd

from .helpers import result_to_dataframe, get_columns_from_crosstabs


def add_data(func):
    @functools.wraps(func)
    def wrapper(*aargs, **kkwargs):
        if aargs[0].dataset_type is None:
            raise ValueError("You haven't selected any data. Use one of the dataset.use_* methods to load data.")
        if aargs[0].dataset_type == 'quantipy':
            data_as_csv = aargs[0].qp_data

            # The __qualname__ is the name of the method that the decorator applied to
            # If it's in the list, then we reduce the dataset column size
            if func.__qualname__ in ["crosstab"]:  # Only apply to function names in this list
                columns = get_columns_from_crosstabs(crosstabs = kkwargs['crosstabs'])
                data = pd.read_csv(io.StringIO(data_as_csv))
                # Filter out columns that are needed and reserialize so we only send the columns we need
                data_as_csv = data[columns].to_csv()

            kkwargs['data_params'] = {
                'meta': aargs[0].qp_meta, 
                'data': data_as_csv
            }
        elif aargs[0].dataset_type == 'sav':
            kkwargs['data_params'] = {
                'binary_data': {'spss': (aargs[0].filename, 
                                  io.BytesIO(aargs[0].sav_data), 
                                  'application/x-spss-sav')
                        }
            }
        return func(*aargs, **kkwargs)
    return wrapper

def format_response(func):
    @functools.wraps(func)
    def wrapper(*aargs, **kkwargs):
        format = kkwargs.pop('format', None)
        result = func(*aargs, **kkwargs)
        if result is None:
            return
        if 'text' in result:
            return result['text']

        if format is None:
            if all(k in result for k in ("index","columns","data")):
                format = 'dataframe'
            elif 'result' in result and all(k in result['result'] for k in ("index","columns","data")):
                format = 'dataframe'
            else:
                format = 'dict'

        if format == 'dict':
            result = result
        elif format == 'json':
            result = json.dumps(result)
        elif format == 'dataframe':
            if 'result' in result.keys():
                result = result_to_dataframe(result['result'])
            elif all(elem in result.keys() for elem in ['index', 'columns', 'data']):
                result = result_to_dataframe(result)
            else:
                if 'params' in result:
                    del result['params']
                result = pd.DataFrame({k:pd.Series(v, dtype='object') for k,v in result.items()})
        else:
            pass # Do nothint, internally use json
        return result
    return wrapper

def valid_params(valid_params_list):
    """
    A decorator that gets list of valid parameters and returns an error if user supplies a parameter
    that isn't in the list. Useful for making sure invalid params aren't sent up to Tally.
    """
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*aargs, **kkwargs):
            sent_args = list(kkwargs.keys())
            invalid = list(set(sent_args) - set(valid_params_list))
            if len(invalid) > 0:
                raise ValueError("invalid parameter: {}. Valid parameters are: {}\n See https://tally.datasmoothie.com for documentation.".format(invalid, valid_params_list))
            result = func(*aargs, **kkwargs)
            return result
        return wrapper
    return actual_decorator

    
def verify_no_tables(func):
    @functools.wraps(func)
    def wrapper(*aargs, **kkwargs):
        error = f"You are using {func.__name__} after you have used sheet.add_table. Options have to be set before add_table is called"
        if aargs[0].parent.table_count() > 0:
            raise Exception(error)

        result = func(*aargs, **kkwargs)
        return result
    return wrapper

def verify_token(func):
    @functools.wraps(func)
    def wrapper(*aargs, **kkwargs):
        result = func(*aargs, **kkwargs)
        if result.status_code == 401:
            result_dict = json.loads(result.content)
            if 'detail' in result_dict and result_dict['detail'] == "Invalid token.":
                raise ValueError("Invalid or expired API token: {}".format(aargs[0]._Tally__api_key))
        return result
    return wrapper

