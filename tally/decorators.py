import functools
import io

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