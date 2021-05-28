import json
import requests
import pandas as pd
import os
import io

from .decorators import add_data
from .tally import Tally

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
    qp_meta = None
    qp_data = None
    tally = None

    def __init__(self, name=None, api_key=None, host='tally.datasmoothie.com/', ssl=True):
        self._name = name
        self.add_credentials(api_key=api_key, host=host, ssl=ssl)

    def add_credentials(self, api_key=None, host='tally.datasmoothie.com/', ssl=True):
        tally = Tally(api_key=api_key, host=host, ssl=ssl)
        self.tally = tally

    def use_spss(self, file_path):
        """
        Load SPSS file into memory as the file to send with all requests.

        Parameters
        ----------
            file_path: string
                Path to the sav file we want to use as our data.
        """
        # this is okay because the path format will be the same as the OS running this
        self.filename = os.path.basename(file_path)

        with open(file_path, mode='rb') as file:
            fileContent = file.read()
        
        self.dataset_type = 'sav'
        self.sav_data = fileContent

    def use_quantipy(self, meta_json, data_csv):
        with open(meta_json) as json_file:
            self.qp_meta = json.dumps(json.load(json_file))
        self.qp_data = pd.read_csv(data_csv).to_csv()
        self.dataset_type = 'quantipy'

    def prepare_post_params(self, data_params, params={}):
        # initialise the payload with our chosen data
        if 'binary_data' in data_params:
            files = data_params['binary_data']
            payload = {}
        else:
            files = None
            payload = data_params
        payload['params'] = params
        return (files, payload)

    @add_data
    def crosstab(self, data_params=None, **kwargs):
        # initialise the payload with our chosen data
        files, payload = self.prepare_post_params(data_params, kwargs)
        response = self.tally.post_request('tally', 'crosstab', payload, files)
        json_dict = json.loads(response.content)
        if 'result' in json_dict.keys():
            df = Tally.result_to_dataframe(json_dict['result'])
            return df
        else:
            raise ValueError

    @add_data
    def convert_spss_to_csv_json(self, data_params=None):
        files, payload = self.prepare_post_params(data_params)
        response = self.tally.post_request('tally', 'convert_spss_to_csv_json', payload, files)
        json_dict = json.loads(response.content)
        result = {}
        result['csv'] = json_dict['csv']
        result['json'] = json_dict['json']
        return result

    @add_data
    def build_excel(self, data_params=None, filename=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        response = self.tally.post_request('tally', 'build_excel', payload, files)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
        return response

    @add_data
    def build_powerpoint(self, data_params=None, filename=None, powerpoint_template=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        files['pptx_template'] = (
            'template.pptx', 
            open(powerpoint_template, 'rb').read(), 
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response = self.tally.post_request('tally', 'build_powerpoint', payload, files)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
        return response
