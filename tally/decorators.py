import functools

def add_data(data_type=None):
    import pdb; pdb.set_trace()
    def the_decorator(func):
        @functools.wraps(func)
        def wrapper(*aargs, **kkwargs):
            import pdb; pdb.set_trace()
            kkwargs['data_params'] = {'spss':'geir was here'}
            return func(*aargs, **kkwargs)
        return wrapper
    return the_decorator
