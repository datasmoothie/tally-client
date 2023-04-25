import pandas as pd
import os
import tally
import pytest
import json
import urllib
import result_helper
from pandas.testing import assert_frame_equal


def test_derive_futures(token, api_url, use_ssl):
    # Make the dataset use futures
    ds = tally.DataSet(use_futures=True)

    ds.add_credentials(api_key=token, host=api_url, ssl=use_ssl)
    ds.use_csv('tests/fixtures/Example Data (A) no-meta.csv')

    cond_map_local = [
        (1, "Urban", {'locality':[1,2]}),
        (2, "Rural", {'locality':[3,4]})
    ]

    cond_map_religion = [
        (1, "religious", {'religion':[1,2,3,4,5,6,7,8,9,13,14,15,16]}),
        (2, "Atheist", {'religion':[10]}),
        (3, "Private", {'religion':[11, 12]})
    ]

    # These methods will be calculated in the future
    ds.derive(name='urban', label='Urban or rural', cond_map=cond_map_local, qtype="single")
    ds.derive(name='religiousity', label='Religious or not', cond_map=cond_map_religion, qtype="single")

    # These methods will be calculated in the future, get a uuid for bookkeeping
    crosstab_0_uid = ds.crosstab(x='urban', ci=['c%'])
    crosstab_1_uid = ds.crosstab(x='urban', y="religiousity", ci=['c%'])

    weight_scheme = {
        'locality':{1:10, 2:10, 3:10, 4:50, 5:20},
        'gender':{1:10, 2:90}
    }

    # These methods will be calculated in the future
    res = ds.weight(name='my weight', variable='weight_c', unique_key='resp_id', scheme=weight_scheme)

    # These methods will be calculated in the future, get a uuid for bookkeeping
    crosstab_0_uid_w = ds.crosstab(x='urban', w="weight_c", ci=['c%'])
    crosstab_1_uid_w = ds.crosstab(x='urban', y="religiousity", w="weight_c", ci=['c%'])

    # Get the results from the futures.
    result = ds.result()

    # Deserialize the results, to check them
    c_names = ['Total', 'Total']
    i_names = ['Question','Values']
    ct0 = result_helper.decode_result_to_dataframe(
            result[crosstab_0_uid],
            column_names=c_names,
            index_names=i_names)
    ct1 = result_helper.decode_result_to_dataframe(
            result[crosstab_1_uid],
            column_names=c_names,
            index_names=i_names)
    ct0w = result_helper.decode_result_to_dataframe(
            result[crosstab_0_uid_w],
            column_names=c_names,
            index_names=i_names)
    ct1w = result_helper.decode_result_to_dataframe(
            result[crosstab_1_uid_w],
            column_names=c_names,
            index_names=i_names)

    assert ct0.shape == ct0w.shape
    assert ct1.shape == ct1w.shape

    # Check that the two dataframes are not equal
    try:
        assert_frame_equal(ct0, ct0w, check_exact=False)
        assert_frame_equal(ct1, ct1w, check_exact=False)
    except AssertionError:
        pass  # Expected AssertionError because dataframes are not equal
    else:
        raise AssertionError("Dataframes are equal but should not be")

