import json
import requests
import pandas as pd
import copy

def result_to_dataframe(json_dict):
    """ Deserializes a dataframe that was serialized with orient='split'
    """
    if 'column_names' and 'index_names' in json_dict.keys():
        columns = pd.MultiIndex.from_tuples(json_dict['columns'], names=json_dict['column_names'])
        index = pd.MultiIndex.from_tuples(json_dict['index'], names=json_dict['index_names'])
    else:
        columns = json_dict['columns']
        index = json_dict['index']
    df = pd.DataFrame(data=json_dict['data'])
    df.columns = columns
    df.index = index
    return df

class Tally:
    """Tally is a wrapper for the cloud-based Tally API.

    Parameters
    ----------
    api_key : string
        API key used to authenticate calls. This is provided by Datasmoothie, email info@datasmoothie.com to get one.

    Attributes
    ----------
    __api_key : string
        The API key used for authentication.
    __headers : type
        The headers used for http requests.

    """

    def __init__(self, api_key, host="tally.datasmoothie.com/tally/", ssl=True):
        """Initialise the client with an API key.

        Parameters
        ----------
        api_key : string
            The API key used for authentication, provided by Datasmoothie.
        host : string
            The path to the server api
        ssl : boolean
            Datasmoothie does not support non ssl communication, but this is
            useful for development and local unit testing.

        """
        self.host = host
        if ssl:
            self.base_url = "https://{}".format(host)
        else:
            self.base_url = "http://{}".format(host)
        self.__api_key = api_key
        self.__headers = {
            "Authorization": "Token {}".format(self.__api_key),
            "Content-Type": "application/json",
            "Accept": "application/json"
            }

    def _get_headers(self):
        return self.__headers

    def get_request(self, resource, action=None):
        """Send a get request to the API with a convenient wrapper.

        Parameters
        ----------
        resource : string
            Name of the resource we are calling.
            These are the root paths of the API.
        action : type
            Name of the action to take on the resouce,
            e.g. datasource/1/meta_data
        binary : boolean
            Are we sending data in a binary format or not? Spss files are binary, CSVs are not.

        Returns
        -------
        type
            JSON object representing the result of the API request.

        """
        if action is None:
            action = ""
        request_path = "{}/{}/{}".format(self.base_url, resource, action)
        result = requests.get(request_path, headers=self._get_headers())
        result = json.loads(result.content)
        return result

    def post_request(self, resource, action="", data={}, files=None):
        """Send a POST request to the API with a wrapper.

        This is used by other objects
        to call the API and not used by the users themselves.

        Parameters
        ----------
        resource : string
            Name of the resource we are calling.
            These are the root paths of the API.
        action : string
            Name of the action to take on the resouce,
            e.g. datasource/1/meta_data
        data : type
            JSON object with the payload to send with a POST request.

        Returns
        -------
        type
            Description of returned object.

        """
        # http doesn't support nested data structures, so we flatten the params
        if 'params' in data.keys():
            data['params'] = json.dumps(data['params'])
        if len(action) == 0:
            request_path = "{}/{}/".format(self.base_url, resource)
        else:
            request_path = "{}/{}/{}/".format(self.base_url, resource, action)
        if files is not None:
            headers = copy.deepcopy(self._get_headers())
            if "Content-Type" in headers.keys():
                del headers["Content-Type"]
            result = requests.post(request_path, headers=headers, data=data, files=files)
        else:
            result = requests.post(request_path, headers=self._get_headers(), data=json.dumps(data))
        return result

    def put_request(self, resource, data):
        request_path = "{}/{}/".format(self.base_url, resource)
        result = requests.put(request_path,
                              headers=self._get_headers(),
                              json=data
                              )
        return result

    def delete_request(self, resource, primary_key):
        """Send a delete request to the API.

        Parameters
        ----------
        resource : string
            Path location of the resource.
        primary_key : string
            The reports primary key, as reported by get reports.

        Returns
        -------
        type
            The response from the server.

        """
        request_path = "{}/{}/{}".format(self.base_url, resource, primary_key)
        result = requests.delete(request_path,
                                 headers=self._get_headers())
        return result

    def get_base_url(self, api=True):
        if api:
            return self.host
        else:
            return self.host.replace("api2", "")

    def build_excel(self, filename=None, params={}):
        """
        Build Excel tables with aggregated results.

        Parameters
        ----------
        filename : string
            Name of file that has the survey data. to be used 

        """


    def weight(self):
        """Get a list of all the datasources this account has.

        Returns
        -------
        type
            A JSON object with meta information about the datasources.
            This can be used to get the primary keys of the datasource
            the user wants to manipulate.

        """
        result = self.get_request('datasource')
        return result

