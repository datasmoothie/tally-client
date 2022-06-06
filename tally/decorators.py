import functools
import io
import json

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
            result = tally.result_to_dataframe(result['result'])
        else:
            pass # Do nothint, internally use json
        return result
    return wrapper