import json
import requests
import pandas as pd

from .decorators import add_data

class DataSet:
    """
    A class that wraps a dataset and has all the information needed to send to the API in order to perform the various tasks.

    Parameters
    ----------
      name: string
        Name for the dataset
    """
    dataset_type = None
    sav_data = None

    def __init__(self, name=None):
        self._name = name

    def from_spss(self, file_path):
        """
        Load SPSS file into memory as the file to send with all requests.

        Parameters
        ----------
            file_path: string
                Path to the sav file we want to use as our data.
        """
        filename = file_path
        with open(filename, mode='rb') as file:
            fileContent = file.read()
        
        dataset_type = 'sav'
        sav_data = fileContent

    @add_data(data_type=dataset_type)
    def crosstab(self, x=None, y=None, data_params=None):
        # payload = {
        #     'data': csv_data.to_csv(),
        #     'meta': json.dumps(json_meta),
        #     'params': json.dumps({
        #         'x': ['q1'],
        #         'y': ['gender']
        #     })
        # }
        import pdb; pdb.set_trace()
        return True
        #response = self.post_request('tally', 'crosstab', payload)
        #json_dict = json.loads(response.content)

        # if 'result' in json_dict:
        #     if returnDataframe:
        #         return self.result_to_dataframe(json_dict['result'])
        #     else:
        #         return response.content
        # else:
        #     raise ValueError