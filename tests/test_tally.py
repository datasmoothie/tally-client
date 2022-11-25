import pandas as pd

from tally import Tally

def test_new_tally(token, api_url, dataset_data, dataset_meta):
    tally = Tally(api_key=token, host=api_url, ssl=True)
    assert True

