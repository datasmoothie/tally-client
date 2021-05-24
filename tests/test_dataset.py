import pandas as pd

import tally

def test_spss_crosstab(token, api_url):
    ds = tally.DataSet()
    ds.from_spss('tests/fixtures/Example Data (A).sav')
    ds.crosstab(x='q1', y='gender')
