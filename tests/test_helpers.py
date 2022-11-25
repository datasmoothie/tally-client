from tally.helpers import get_columns_from_crosstabs


def test_get_columns_from_crosstabs(dataset_data, dataset_meta):

    crosstabs=[{"x":["q1"], "y":"locality", "f":{"gender":[1]}, "stats":["mean"]},
               {"x":["q2b"], "y":"locality", "w": "weight_b"}]

    columns = get_columns_from_crosstabs(crosstabs=crosstabs)
    
    assert sorted(columns) == sorted(['q1', 'locality', 'gender', 'q2b', 'weight_b'])
