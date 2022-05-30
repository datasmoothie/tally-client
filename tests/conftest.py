import json
import pytest
import pandas as pd

def pytest_addoption(parser):
    parser.addoption("--token", action="store", default="")
    parser.addoption("--api_url", action="store", default="tally.datasmoothie.com")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.token
    if 'token' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("token", [option_value])

    option_value = metafunc.config.option.api_url
    if 'api_url' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("api_url", [option_value])


@pytest.fixture(scope="session")
def dataset_meta():
    with open('tests/fixtures/Example Data (A).json') as json_file:
        return json.load(json_file)

@pytest.fixture(scope="session")
def dataset_data():
    return pd.read_csv('tests/fixtures/Example Data (A).csv')

@pytest.fixture(scope="session")
def dataset_spss():
    fileName = 'tests/fixtures/Example Data (A).sav'
    with open(fileName, mode='rb') as file:
        fileContent = file.read()
    return fileContent