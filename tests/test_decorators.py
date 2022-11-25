import io
import tally
import pandas as pd
from tally.decorators import add_data

#create a function and wrap it with the decorator, just immidiately return result
@add_data
def crosstab(*args, **kwargs):
    return args, kwargs
 

def test_add_data_removes_unused_columns(token, api_url, use_ssl):
    # There are 78 columns in the Example Data (A). This tests that we only 
    # send 6 columns of data
    ds = tally.DataSet()
    ds.use_quantipy('tests/fixtures/Example Data (A).json', 'tests/fixtures/Example Data (A).csv')

    crosstabs=[
        {"x":["q1", "q2"], "y":"locality", "f":{"gender":[1], "age":[2]}, "stats":["mean"]},
        {"x":["q2b"], "y":"locality", "f":{"gender":[2], "locality":[1]}, "w":"weight_b"}
    ]

    args, kwargs = crosstab(ds, crosstabs=crosstabs)
    sent_data = pd.read_csv(io.StringIO(kwargs['data_params']['data']))

    assert sent_data.shape == (8255, 8)
    assert sorted(sent_data.columns.tolist()) == sorted(['Unnamed: 0', 'weight_b', 'q2b', 'locality', 'q1', 'q2', 'gender', 'age'])


