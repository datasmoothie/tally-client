import functools
import io
import json
import pandas as pd

import tally

def add_data(func):
    @functools.wraps(func)
    def wrapper(*aargs, **kkwargs):
        if aargs[0].dataset_type == 'quantipy':
            kkwargs['data_params'] = {
                'meta': aargs[0].qp_meta, 
                'data': aargs[0].qp_data
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
        format = kkwargs.pop('format', 'dataframe')
        result = func(*aargs, **kkwargs)
        if format == 'dict':
            result = result
        elif format == 'json':
            result = json.dumps(result)
        elif format == 'dataframe':
            if 'result' in result.keys():
                result = tally.result_to_dataframe(result['result'])
            elif all(elem in result.keys() for elem in ['index', 'columns', 'data']):
                result = tally.result_to_dataframe(result)
            else:
                if 'params' in result:
                    del result['params']
                result = pd.DataFrame({k:pd.Series(v) for k,v in result.items()})
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


