import json
import pandas as pd
import io
from functools import partial
import urllib.request

from difflib import SequenceMatcher
from .decorators import add_data, format_response, valid_params
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

    def __init__(self, api_key=None, host='tally.datasmoothie.com', ssl=True):
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
        if response.status_code == 404:
            return self._method_not_found_response(api_endpoint)
        json_dict = json.loads(response.content)
        json_dict = self._clean_error_response(json_dict)
        if self._has_keys(json_dict, VARIABLE_KEYS):
            self.add_column_to_data(json_dict['meta']['name'], json_dict['data'], json_dict['meta'])
            return
        if self._has_keys(json_dict, META_VARIABLE_KEYS):
            self.add_column_to_data(json_dict['meta']['name'], None, json_dict['meta'])
            return
        if self._has_keys(json_dict, NEW_DATASET_KEYS):
            self.qp_data = json_dict['dataset_data']
            self.qp_meta = json.dumps(json_dict['dataset_meta'])
            return
        return json_dict

    def _method_not_found_response(self, method):
        try:
            didyoumean = ""
            with urllib.request.urlopen("https://tally.datasmoothie.com/openapi/?format=openapi-json") as url:
                data = json.load(url)
                endpoints = [i.replace('/tally/', '')[:-1] for i in data['paths'].keys()]
                matches = []
                for endpoint in endpoints:
                    matches.append((endpoint, SequenceMatcher(None, method, endpoint).ratio()))
                matches.sort(key=lambda tup: tup[1],reverse=True)
                if matches[0][1] > 0.8:
                    didyoumean = matches[0][0]
        except:
            pass
        if len(didyoumean)>0:
            infotext = "Unknown method '{}'. Did you mean '{}'? See https://tally.datasmoothie.com for available methods.".format(method, didyoumean)
        else:
            infotext = "Unknown method '{}'. See https://tally.datasmoothie.com for available methods.".format(method)
        raise ValueError(infotext)


    def _clean_error_response(self, error_response):
        if 'error' in error_response:
            if 'payload' in error_response['error'] and error_response['error']['payload'] == {}:
                del error_response['error']['payload'] 
            if 'detailed_message' in error_response['error'] and error_response['error']['detailed_message'] == error_response['error']['message']:
                del error_response['error']['detailed_message']
        return error_response

    def _has_keys(self, response, required_keys):
        return all(elem in response.keys() for elem in required_keys)

    def _generate_functions_from_api(self):
        with urllib.request.urlopen("https://tally.datasmoothie.com/openapi/?format=openapi-json") as url:
            data = json.load(url)
        endpoints = [i.replace('/tally/', '')[:-1] for i in data['paths'].keys()]
        result = ""
        for endpoint in endpoints:
            available = dir(self)
            if endpoint not in available:
                result = result + self._endpoint_api_to_docstring(data, endpoint)

        return result

    def _endpoint_api_to_docstring(self, data, endpoint):
        docstring = "    \"\"\""
        path_info = data['paths']['/tally/{}/'.format(endpoint)]
        parameter_docstring = ""
        docstring = docstring + path_info['post']['description']
        # check if there are parameters
        if endpoint in data['components']['schemas'] and type(data['components']['schemas'][endpoint]['properties']['params']) == dict:
            param_properties = data['components']['schemas'][endpoint]['properties']['params']['properties']
            docstring = docstring + "\tParameters\n\t=====\n"
            for key in param_properties:
                docstring = docstring + """\t{} : {}\n \t\t{}\n""".format(key, param_properties[key]["type"], param_properties[key]["description"])
        docstring = docstring + '\t\"\"\"'

        function_string = """
            def {}(self, **kwargs):
            {}
            return self._call_tally('{}', **kwargs)
        """.format(endpoint, docstring, endpoint)
        print(function_string)
        return function_string


    def add_credentials(self, api_key=None, host='tally.datasmoothie.com', ssl=True):
        """
        Add your API key and what server it is authorized to connect to. Useful for on-prem installations and development.          
        """
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
        """
        Writes the dataset to an SPSS (sav) file.

        Parameters
        ----------
            file_path: string
                Path to the sav file to write.
        """
        payload = {}
        files, payload = self.prepare_post_params(data_params, {})
        response = self.tally.post_request('tally', 'convert_data_to_sav', payload, files)
        file = open(file_path, "wb")
        file.write(response.content)
        file.close()
        return response

    def write_quantipy(self, file_path_json, file_path_csv):
        """
        Write the case and meta data as Quantipy compatible json and csv files. 

        Parameters
        ----------
            file_path_json: string
                Path to the json meta data file to create.
            file_path_csv: string
                Path to the csv data file to create.
        """
        json_file = open(file_path_json, "w")
        n = json_file.write(self.qp_meta)
        json_file.close()
        csv_file = open(file_path_csv, "w")
        n = csv_file.write(self.qp_data)
        csv_file.close()

    def use_quantipy(self, meta_json, data_csv):
        """
        Load Quantipy meta and data files to this dataset.

        Parameters
        ----------
            meta_json: string
                Path to the json file we want to use as our meta data.
            data_csv: string
                Path to the csv file we want to use as our data file.
        """
        with open(meta_json) as json_file:
            self.qp_meta = json.dumps(json.load(json_file))
        self.qp_data = pd.read_csv(data_csv).to_csv()
        self.dataset_type = 'quantipy'

    def use_csv(self, csv_file):
        """
        Load CSV file into the dataset as the file to send with all requests.

        Parameters
        ----------
            csv_file: string
                Path to the CSV file we want to use as our data.
        """        
        csv = pd.read_csv(csv_file).to_csv()
        payload = {'csv': csv}
        response = self.tally.post_request('tally', 'convert_data_to_csv_json', payload)
        result = json.loads(response.content)
        self.qp_meta = json.dumps(result['json'])
        self.qp_data = result['csv']
        self.dataset_type = 'quantipy'

    def use_nebu(self, nebu_url):
        """
        Load remote Nebu/Enghouse file into the dataset as the file to send with all requests.

        Parameters
        ----------
            nebu_url: string
                Path to the Nebu data file we want to use as our data.
        """       
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
        """
        Load remote Forsta/Confirmit data into the dataset as the data to send with all requests.

        Parameters
        ----------
        source_projectid: string
            Project id of the survey
        source_idp_url: string
            IPD Url of the survey
        source_client_id: string
            Your client id
        source_client_secret: string
            Client secret (don't commit this to a repository)
        source_public_url: string
                Public url to source
        """               
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
            if type(data_params) == str:
                raise ValueError("The Tally client does not support non keyword arguments. For example, use dataset.crosstab(x='age'), not dataset.crosstab('age').")
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

    @valid_params(['filename', 'dataframes', 'client_formats'])
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

    def band(self, **kwargs):
        """Group numeric data with band definitions treated as group text labels.

        Parameters
        =====
        name : string
            The column variable name keyed in _meta['columns'] that will be banded into summarized categories.
        bands : array
            The categorical bands to be used. Bands can be single numeric values or ranges.
        new_name : (string, default None)
            The created variable will be named '<name>_banded', unless a desired name is provided explicitly here.
        label : (string, default None)
            The created variable's text label will be identical to the originating one's passed in name, unless a desired label is provided explicitly here.
        text_key : (string, default None)
            Text key for text-based label information. Uses the DataSet.text_key information if not provided.
        """
        return self._call_tally('band', **kwargs)
        
    def compare(self, **kwargs):
        """Compares types, codes, values, question labels of two datasets.

        Parameters
        =====
        dataset : object
            (quantipy.DataSet instance). Test if all variables in the provided dataset are also in self and compare their metadata definitions.
        variables : str, array of str
            Check only these variables
        strict : (bool, default False)
            If True lower/ upper cases and spaces are taken into account.
        text_key : str, array of str
            Text key for text-based label information. Uses the DataSet.text_key information if not provided.
	    """
        return self._call_tally('compare', **kwargs)
        
    def convert_data_to_csv_json(self, **kwargs):
        """Converts data, either sent or from an external source to Quantipy CSV and JSON.

        The data to convert can be from parquet, SPSS, or UNICOM Intelligence (fka Dimensions) or a pure CSV exported from Excel.

        """
        return self._call_tally('convert_data_to_csv_json', **kwargs)
        
    def convert_data_to_sav(self, **kwargs):
        """Converts data, either sent or from an external source to an SPSS sav file.

        The data to convert can be from Quantipy, or UNICOM Intelligence (fka Dimensions) or a pure CSV exported from Excel.

        The sav files created do not support Quantipy's delimited set.

            """
        return self._call_tally('convert_data_to_sav', **kwargs)
        
    def copy(self, **kwargs):
        """Copy meta and case data of the variable defintion given per name.

        Parameters
        =====
        name : string
            The column variable name.
        suffix : string (default "rec")
            The new variable name will be constructed by suffixing the original `name` with `_suffix`, e.g. `age_rec`
        copy_data : boolean (default true)
            The new variable assumes the data of the original variable.
        slicer : dict
            If the data is copied it is possible to filter the data with a complex logic.
        copy_only : int or list of int, default None
            If provided, the copied version of the variable will only contain (data and) meta for the specified codes.
        copy_not : int or list of int, default None
            If provided, the copied version of the variable will contain (data and) meta for the all codes, except of the indicated.
        new_name : string
            If provided, the returned object will contain this new name instead of `name_suffix`
        """
        return self._call_tally('copy', **kwargs)
        
    def derive(self, **kwargs):
        """Create meta and recode case data by specifying derived category logics.

    Derived variables have their answer codes derived from other variables. Derived variables can either be
    multi-choice (called delimited set) or single-choice.

    A derived variable can be created from one variable, for example when a likert scale question
    has NETs added to it, or it can be created from multiple variables. When a derived variable is
    created from multiple variables, the user has to define how these variables should be used to create the 
    new one with by defining whether the new variable is an intersection or a union (logical expressions `and` or `or`).

    The conditional map has a list/array of of either three or four elements of following structures:

    #### 3 elements, type of logic not specified:
    [code, label, logic dictionary], e.g.:

    ``[1, "People who live in urban and sub-urban settings", {'locality': [1,2]}``

    #### 4 elements, type of logic speficied:
    [1, label, type of logic, logic_dictionary), e.g.:

    ``[1, "Men in urban and suburban locations", 
    'intersection', 
    {'gender': [1] 'locality': [1,2]))]``

    ``[2, "Women in urban and suburban locations", 'intersection', {'gender': [2] 'locality': [1,2]))``

    The logic types are 'union' and 'intersection'. If no logic type is specified, 'union' is used.
    `union` is equivalent to the logical expression `or` and `intersection` is equivalent to `and`.
    


        Parameters
        =====
        name : string
            The column variable name.
        label : string
            Name of the variable to show meta data for
        qtype : string
            The structural type of the data the meta describes (``int``, ``float``, ``single`` or ``delimited set``)
        cond_maps : array
            List of logic dictionaries that define how each answer and code is derived.
        cond_map : array (deprecated)
            List of "tuples", see documentatio above.
        """
        return self._call_tally('derive', **kwargs)
        
    def extend_values(self, **kwargs):
        """Add an answer/value and code to the list of answer/values/codes already in the meta data for the variable.

        Attempting to add already existing value codes or providing already
        present value texts will both raise invalid_arguments error!

        """
        return self._call_tally('extend_values', **kwargs)
        
    def feature_select(self, **kwargs):
        """Shows the variables that score the highest with a given ML features select algorithm

            	"""
        return self._call_tally('feature_select', **kwargs)
        
    def filter(self, **kwargs):
        """Filter the DataSet using a logical expression.

        Parameters
        =====
        alias : string
            Name of the filter
        condition : object
            An object that defines the filter logic
        """
        return self._call_tally('filter', **kwargs)
        
    def find(self, **kwargs):
        """Find variables by searching their names for substrings.

        Parameters
        =====
        str_tags : string or list of strings
            The strings tags to look for in the variable names. If not provided, the modules’ default global list of substrings from VAR_SUFFIXES will be used.
        suffixed : boolean (default false)
            If true, only variable names that end with a given string dequence will qualitfy.
        """
        return self._call_tally('find', **kwargs)
        
    def get_variable_text(self, **kwargs):
        """Return the variables text label information.

	"""
        return self._call_tally('get_variable_text', **kwargs)
        
    def hmerge(self, **kwargs):
        """Merge Quantipy datasets together by appending rows.
        This function merges two Quantipy datasets together,
        updating variables that exist in the left dataset and
        appending others.
        New variables will be appended in the order indicated by the
        'data file' set if found, otherwise they will be appended in
        alphanumeric order. This merge happens vertically (row-wise).

        Parameters
        =====
        dataset : object
            (quantipy.DataSet instance). Test if all variables in the provided dataset are also in self and compare their metadata definitions.
        on : str, default=None
            The column to use to identify unique rows in both datasets.
        left_on : str, default=None
            The column to use to identify unique in the left dataset.
        right_on : str, default=None
            The column to use to identify unique in the right dataset.
        row_id_name : str, default=None
            The named column will be filled with the ids indicated for each dataset, as per left_id/right_id/row_ids. If meta for the named column doesn't already exist a new column definition will be added and assigned a reductive-appropriate type.
        left_id : str, int, float, default=None
            Where the row_id_name column is not already populated for the dataset_left, this value will be populated.
        right_id : str, int, float, default=None
            Where the row_id_name column is not already populated for the dataset_right, this value will be populated.
        row_ids : array of (str, int, float), default=None
            When datasets has been used, this list provides the row ids that will be populated in the row_id_name column for each of those datasets, respectively.
        overwrite_text : bool, default=False
            If True, text_keys in the left meta that also exist in right meta will be overwritten instead of ignored.
        from_set : str, default=None
            Use a set defined in the right meta to control which columns are merged from the right dataset.
        uniquify_key : str, default=None
            An int-like column name found in all the passed DataSet objects that will be protected from having duplicates. The original version of the column will be kept under its name prefixed with 'original'.
        reset_index : bool, default=True
            If True pandas.DataFrame.reindex() will be applied to the merged dataframe.
        """
        return self._call_tally('hmerge', **kwargs)
        
    def joined_crosstab(self, **kwargs):
        """Does crosstab tabulation using the provided parameters, allowing for multiple
        datasources to be sent along with the request to run multiple crosstabs in one result. 
        Returns a json ecoded dataframe as a result. 
	    """
        return self._call_tally('joined_crosstab', **kwargs)
        
    def meta(self, **kwargs):
        """Shows the meta-data for a variable

        Parameters
        =====
        variable : string
            Name of the variable to show meta data for
        variables : array
            Name of multiple variables to show meta data for
        """
        return self._call_tally('meta', **kwargs)
        
    def recode(self, **kwargs):
        """Create a new or copied series from data, recoded using a mapper.

        This function takes a mapper of {key: logic} entries and injects the
        key into the target column where its paired logic is True. The logic
        may be arbitrarily complex and may refer to any other variable or
        variables in data. Where a pre-existing column has been used to
        start the recode, the injected values can replace or be appended to
        any data found there to begin with. The recoded data will always comply 
        with the column type indicated for the target column according to the meta. 

        #### Mapping example:
            recode_mapper = {
                1: {"$union":[{"$intersection": [{'locality': [3]}, {"gender":[1]}]},{"$intersection": [{'locality': [4]}, {"gender":[1]}]}]               },
                2: {"$intersection":[{'locality': [2]}, {'gender':[2]}]},
                3: {"$union":[{'locality': [1]}, {'gender':[1]}]},
                4: {'locality': [4]},
                5: {'locality': [5]},
                6: {'locality': [6]}
            }
        Logical functions are strings preceded with the symbol $ and logic can be nested at an arbitrary depth.


        Parameters
        =====
        target : string
            The variable name of the target of the recode.
        mapper : dict
            A mapper of {key: logic} entries.
        default : string
            The column name to default to in cases where unattended lists are given in your logic, where an auto-transformation of {key: list} to {key: {default: list}} is provided. Note that lists in logical statements are themselves a form of shorthand and this will ultimately be interpreted as: {key: {default: has_any(list)}}. 
        append : boolean
            Should the new recoded data be appended to values already found in the series? If False, data from series (where found) will overwrite whatever was found for that item instead.
        intersect : dict
            If a logical statement is given here then it will be used as an implied intersection of all logical conditions given in the mapper. For example, we could limit our mapper to males.
        initialize : str (default: None)
            Name of variable to use to populate the variable before the recode
        fillna : int
            If provided, can be used to fill empty/nan values.
        """
        return self._call_tally('recode', **kwargs)
        
    def remove_values(self, **kwargs):
        """Erase value codes safely from both meta and case data components.


    	"""
        return self._call_tally('remove_values', **kwargs)
        
    def set_value_texts(self, **kwargs):
        """Rename or add value texts in the ‘values’ object.

        This method works for array masks and column meta data.

        """
        return self._call_tally('set_value_texts', **kwargs)
        
    def set_variable_text(self, **kwargs):
        """Change the variable text for a named variable.

	"""
        return self._call_tally('set_variable_text', **kwargs)
        
    def sum(self, **kwargs):
        """Adds all values in each column and returns the sum for each column.
        Parameters
        =====
        new_variable_name : string
            Name for new variable that will contain the summarized amounts.
        variables : array
            The variables to sum. Only float or int types.
        """
        return self._call_tally('sum', **kwargs)
        
    def to_array(self, **kwargs):
        """Create a new variable grid (array) variable from two or more `single` variables with the same labels.

    	"""
        return self._call_tally('to_array', **kwargs)
        
    def to_delimited_set(self, **kwargs):
        """Create a new variable delimited set (multi choice) variable from two or more `single` variables.

    	"""
        return self._call_tally('to_delimited_set', **kwargs)
        
    def values(self, **kwargs):
        """Get a list of value texts and codes for a categorical variable, as a dictionary. 
        The method will return the codes in the data and the labels that apply to those codes
        in the chosen language (or the default language if no language is chosen).


        Parameters
        =====
        name : string
            Name of variable to fetch values/codes for.
        text_key : string (default None)
            The language key that should be used when taking labels from the meta data.
        include_variable_texts : boolean (default false)
            Include labels for the variable name in the results.
        """
        return self._call_tally('values', **kwargs)
        
    def variables(self, **kwargs):
        """
        Shows list of variables.

	    """
        return self._call_tally('variables', **kwargs)
        
    def vmerge(self, **kwargs):
        """
        Merge Quantipy datasets together by appending rows.
        This function merges two Quantipy datasets together, updating variables
        that exist in the left dataset and appending others. New variables
        will be appended in the order indicated by the 'data file' set if
        found, otherwise they will be appended in alphanumeric order. This
        merge happens vertically (row-wise).

        Parameters
        =====
        dataset : object
            (quantipy.DataSet instance). Test if all variables in the provided dataset are also in self and compare their metadata definitions.
        on : str, default=None
            The column to use to identify unique rows in both datasets.
        left_on : str, default=None
            The column to use to identify unique in the left dataset.
        right_on : str, default=None
            The column to use to identify unique in the right dataset.
        row_id_name : str, default=None
            The named column will be filled with the ids indicated for each dataset, as per left_id/right_id/row_ids. If meta for the named column doesn't already exist a new column definition will be added and assigned a reductive-appropriate type.
        left_id : str, int, float, default=None
            Where the row_id_name column is not already populated for the dataset_left, this value will be populated.
        right_id : str, int, float, default=None
            Where the row_id_name column is not already populated for the dataset_right, this value will be populated.
        row_ids : array of (str, int, float), default=None
            When datasets has been used, this list provides the row ids that will be populated in the row_id_name column for each of those datasets, respectively.
        overwrite_text : bool, default=False
            If True, text_keys in the left meta that also exist in right meta will be overwritten instead of ignored.
        from_set : str, default=None
            Use a set defined in the right meta to control which columns are merged from the right dataset.
        uniquify_key : str, default=None
            An int-like column name found in all the passed DataSet objects that will be protected from having duplicates. The original version of the column will be kept under its name prefixed with 'original'.
        reset_index : bool, default=True
            If True pandas.DataFrame.reindex() will be applied to the merged dataframe.
        """
        return self._call_tally('vmerge', **kwargs)
        