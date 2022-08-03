import json
import requests
import pandas as pd
import os
import io
from functools import partial

from .decorators import add_data, format_response, valid_params
import tally
from .tally import Tally

# these are the keys returned in results that indicate what should happen with the local dataset
VARIABLE_KEYS = ['meta', 'data']
META_VARIABLE_KEYS = ['meta']
NEW_DATASET_KEYS = ['dataset_meta', 'dataset_data']

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

    def __init__(self, api_key=None, host='tally.datasmoothie.com/', ssl=True):
        self.add_credentials(api_key=api_key, host=host, ssl=ssl)

    #@add_data
    def __getattr__(self, name):
        method = partial(self._call_tally, name)
        return method

    @add_data
    @format_response
    def _call_tally(self, api_endpoint, *args, **kwargs):
        data_params = kwargs.pop('data_params')
        files, payload = self.prepare_post_params(data_params, kwargs)
        response = self.tally.post_request('tally', api_endpoint, payload, files)
        json_dict = json.loads(response.content)
        json_dict = self._clean_error_response(json_dict)
        if self._has_keys(json_dict, VARIABLE_KEYS):
            self.add_column_to_data(json_dict['meta']['name'], json_dict['data'], json_dict['meta'])
        if self._has_keys(json_dict, META_VARIABLE_KEYS):
            self.add_column_to_data(json_dict['meta']['name'], None, json_dict['meta'])
        if self._has_keys(json_dict, NEW_DATASET_KEYS):
            self.qp_data = json_dict['dataset_data']
            self.qp_meta = json.dumps(json_dict['dataset_meta'])
        return json_dict

    def _clean_error_response(self, error_response):
        if 'error' in error_response:
            if 'payload' in error_response['error'] and error_response['error']['payload'] == {}:
                del error_response['error']['payload'] 
            if 'detailed_message' in error_response['error'] and error_response['error']['detailed_message'] == error_response['error']['message']:
                del error_response['error']['detailed_message']
        return error_response

    def _has_keys(self, response, required_keys):
        return all(elem in response.keys() for elem in required_keys)

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

        with open(file_path, mode='rb') as file:
            fileContent = file.read()
        
        payload={}
        files=[ ('spss',('Example Data (A).sav',io.BytesIO(fileContent),'application/x-spss-sav')) ]
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload, files)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    @add_data
    def write_spss(self, file_path, data_params, **kwargs):
        payload = {}
        files, payload = self.prepare_post_params(data_params, {})
        response = self.tally.post_request('tally', 'convert_data_to_sav', payload, files)
        file = open(file_path, "wb")
        file.write(response.content)
        file.close()
        return response

    def use_quantipy(self, meta_json, data_csv):
        with open(meta_json) as json_file:
            self.qp_meta = json.dumps(json.load(json_file))
        self.qp_data = pd.read_csv(data_csv).to_csv()
        self.dataset_type = 'quantipy'

    def use_csv(self, csv_file):
        csv = pd.read_csv(csv_file).to_csv()
        payload = {'csv': csv}
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    def use_nebu(self, nebu_url):
        payload = {
            'datasource': {
                'type' : 'Nebu',
                'nebu_url' : nebu_url
            }
        }
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    def use_confirmit(self, source_projectid, source_idp_url, source_client_id, source_client_secret, source_public_url):
        payload = {
            'datasource': {
                'type': 'Confirmit',
                'source_idp_url' : source_idp_url,
                'source_projectid': source_projectid,
                'source_client_id' : source_client_id,
                'source_client_secret' : source_client_secret,
                'source_public_site_url' : source_public_url
            },
        }
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    def use_parquet(self, pq_data_filename, pq_meta_filename=None):

        with open(pq_data_filename, mode='rb') as file:
            fileContent_data = file.read()
        
        payload={}

        files=[ 
            ('pq', (pq_data_filename,io.BytesIO(fileContent_data), 'application/x-parquet')) 
        ]

        if pq_meta_filename is not None:
            with open(pq_meta_filename, mode='rb') as file:
                fileContent_meta = file.read()
            files.append(
                ('pq_meta',(pq_meta_filename,io.BytesIO(fileContent_meta),'text/plain')),
            )
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload, files)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'


    def use_unicom(self, mdd_filename, ddf_filename):
        with open(mdd_filename, mode='rb') as file:
            fileContent_mdd = file.read()

        with open(ddf_filename, mode='rb') as file:
            fileContent_ddf = file.read()
        
        payload={}

        files=[ 
            ('mdd',(mdd_filename,io.BytesIO(fileContent_mdd),'text/xml')),
            ('ddf', (ddf_filename,io.BytesIO(fileContent_ddf), 'application/x-sqlite3')) 
        ]
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload, files)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    def get_dataframe(self):
        return pd.read_csv(io.StringIO(self.qp_data))

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

    @valid_params(['crosstabs', 'x', 'y', 'w', 'f', 'ci', 'stats', 'sig_level', 'decimals', 'base', 'painted', 'rebase', 'factors', 'format', 'add_format_column'])
    @add_data
    @format_response
    def crosstab(self, data_params=None, **kwargs):
        # initialise the payload with our chosen data
        # construct a crosstab option which references the dataset we are uploading with the request
        if 'crosstabs' not in kwargs.keys():
            kwargs['dataset'] = 'one'
            params = {"crosstabs":[kwargs]}
        else:
            crosstabs = kwargs['crosstabs']
            for ct in crosstabs:
                ct['dataset'] = 'one'
            params = {"crosstabs":crosstabs}
        files, payload = self.prepare_post_params(data_params, params)
        # the datasource will be a quantipy one, so we provide meta and data
        datasources={"one":{"meta":payload.pop('meta'), "data":payload.pop('data')}}
        payload['params']['datasources'] = datasources
        response = self.tally.post_request('tally', 'joined_crosstab', payload, files)
        json_dict = json.loads(response.content)
        if 'result' in json_dict.keys():
            return json_dict
        else:
            if 'message' in json_dict.keys():
                raise ValueError(json_dict['message'])
            else:
                raise ValueError("Crosstab returned no result.")

    @valid_params(['scheme', 'unique_key', 'variable', 'name'])
    @add_data
    def weight(self, data_params=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        response = self.tally.post_request('tally', 'weight', payload, files)
        json_dict = json.loads(response.content)
        if 'error' in json_dict:
            json_dict = self._clean_error_response(json_dict)
            return json_dict
        self.merge_column_to_data(kwargs['variable'], json_dict['weight_data'], json_dict['weight_var_meta'], kwargs['unique_key'])
        return json_dict

    def merge_column_to_data(self, name, data, new_meta, merge_on):
        df = pd.read_csv(io.StringIO(self.qp_data))
        new_series = pd.Series(data)
        new_series.index = new_series.index.astype(df[merge_on].dtype)
        new_series.name = name
        df = pd.merge(df, new_series, left_on=merge_on, right_on=new_series.index)
        self.qp_data = df.to_csv()
        meta = json.loads(self.qp_meta)
        meta['columns'][name] = new_meta
        self.qp_meta = json.dumps(meta)


    def add_column_to_data(self, name, data, new_meta):
        if data is not None:
            df = pd.read_csv(io.StringIO(self.qp_data))
            new_series = pd.Series(data)
            new_series.index = new_series.index.astype(int)
            df[name] = new_series
            self.qp_data = df.to_csv()
        meta = json.loads(self.qp_meta)
        meta['columns'][name] = new_meta
        self.qp_meta = json.dumps(meta)

    @add_data
    def convert_spss_to_csv_json(self, data_params=None):
        files, payload = self.prepare_post_params(data_params)
        response = self.tally.post_request('tally', 'convert_spss_to_csv_json', payload, files)
        json_dict = json.loads(response.content)
        result = {}
        result['csv'] = json_dict['csv']
        result['json'] = json_dict['json']
        return result

    @valid_params(['filename', 'sig_level', 'x', 'y', 'w', 'f', 'decimals'])
    @add_data
    def build_excel(self, data_params=None, filename=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        response = self.tally.post_request('tally', 'build_excel', payload, files)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
        return response

    @valid_params(['filename', 'dataframes'])
    @add_data
    def build_excel_from_dataframes(self, data_params=None, filename=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        payload = kwargs
        response = self.tally.post_request('tally', 'build_excel_from_dataframes', payload, files)
        file = open(filename, "wb")
        file.write(response.content)
        file.close()
        return response

    @valid_params(['x', 'y', 'w', 'f', 'decimals', 'filename', 'powerpoint_template'])
    @add_data
    def build_powerpoint(self, data_params=None, filename=None, powerpoint_template=None, **kwargs):
        files, payload = self.prepare_post_params(data_params, kwargs)
        if files is None:
            files = {}
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
