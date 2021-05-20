import pandas as pd

from tally import Tally

def test_new_tally(token, api_url, dataset_data, dataset_meta):
    tally = Tally(api_key=token, host=api_url, ssl=True)
    assert True
    df = tally.crosstab(csv_data=dataset_data, json_meta=dataset_meta, params={
        "x":['q1', 'q2'],
        "2":['Gender']
    })
    assert type(df) == pd.DataFrame
