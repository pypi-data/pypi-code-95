import io
import json
import os
from time import sleep
from typing import Dict, Union, Optional, Callable

import pandas as pd
import requests
from lusid.utilities import ApiConfigurationLoader, RefreshingToken

from lumipy.common.string_utils import indent_str
from lumipy.query.query import Query


def _validate_response(response: requests.Response, endpoint_label):
    # Custom logic before .raise_for_status so we can unwrap the failure and report query errors.
    if not response.ok:
        # Inform the user
        print(
            f"Request to {endpoint_label} failed with status code "
            f"{response.status_code}, reason: '{response.reason}'."
        )
        # noinspection PyBroadException
        try:
            detail = json.loads(response.content)['detail']
            print(indent_str(f"Details:\n{indent_str(detail, n=4)}", n=4))
        except Exception:
            pass

        # Now throw
        response.raise_for_status()

    if response.content is None or len(response.content) == 0:
        raise ValueError(
            f"Request to {endpoint_label} returned status code: {response.status_code} but returned no content."
        )


def _validate_query(query):
    if not isinstance(query, Query) and not isinstance(query, str):
        raise ValueError(
            f"Query must be supplied as {type(str)} or {type(Query)} object. Was {type(query)}"
        )

    # If user supplies just a string, use the default parameters
    if isinstance(query, str):
        return Query(sql_str=query)
    else:
        return query


class Client:
    """WebApi Client for sending requests to Luminesce and getting results back as Pandas DataFrames.

    """
    luminesce_base_url_env_variable = "FBN_LUMI_API_URL"

    def __init__(self, secrets_path: Optional[str] = None, token: Optional[str] = None, retry_wait=0.5, max_retries=5):
        """__init__ method of the Luminesce Web API client class.

        Args:
            secrets_path (Optional[str]): path to secrets file containing authentication data. Optional - if not
            specified the client will get the auth data from env variables.
        """

        # Populate the configuration from the provided secrets file, this also uses environment variables if they exist
        configuration = ApiConfigurationLoader.load(api_secrets_filename=secrets_path)

        # Create a RefreshingToken from the configuration if a token is not provided
        # Note that `==` is used instead of `is` as the lusid-jam (https://github.com/finbourne/lusid-jam) refreshing
        # token can have a value of None but it still returns false here if using `is`
        if token == None:
            self.token = RefreshingToken(configuration)
        # Otherwise use the provided token
        else:
            self.token = token

        # Find the lumiApiUrl which differs from the standard ApiUrl found during the ApiConfiguration load
        if secrets_path is not None:
            with open(secrets_path, 'r') as s:
                json_str = "".join(s.read().split())
                secrets = json.loads(json_str)
        else:
            secrets = {}

        luminesce_base_url = os.getenv(self.luminesce_base_url_env_variable, secrets.get("api", {}).get("lumiApiUrl"))

        if luminesce_base_url is None:
            raise ValueError(f"Could not locate luminesce base url in secrets file at {secrets_path} or in environment variable {self.luminesce_base_url_env_variable}")

        # Override the base url with the discovered lumiApiUrl appending '/api'
        configuration.api_url = os.getenv("FBN_LUMI_API_URL", secrets.get("api", {}).get("lumiApiUrl")) + "/api"
        self.base_url = configuration.api_url

        self.retry_wait = retry_wait
        self.max_retries = max_retries

    def headers(self) -> Dict[str, str]:
        """Build a dictionary of header values for sendng with Luminesce API calls. Includes the bearer token.

        Returns:
            Dict[str,str]: dictionary of headers for requests to Luminesce.
        """
        return {
            "accept": "text/plain",
            "Content-Type": "text/plain",
            "Authorization": f"Bearer {self.token}"
        }

    def _process_request(self, request: Callable, label):
        response = request()
        retry_count = 0
        while response.status_code == 429:
            if retry_count == self.max_retries:
                raise ValueError(f"Max number of retries ({retry_count}) exceeded.")
            # Wait and try again
            sleep(self.retry_wait)
            response = request()
            retry_count += 1

        _validate_response(response, label)
        return response

    def table_field_catalog(self) -> pd.DataFrame:
        """Get the table field catalog as a DataFrame.

        The table field catalog contains a row describing each field on each provider you have access to.

        Returns:
            DataFrame: dataframe containing table field catalog information.
        """
        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/Catalog",
                headers=self.headers()
            ),
            label='table field catalog'
        )
        return pd.DataFrame(result.json())

    def query_and_fetch(self, query: Union[str, Query]):
        """Send a query to Luminesce and get it back as a pandas dataframe.

        Args:
            query (Union[str, Query]): query to be sent to Luminesce

        Returns:
            DataFrame: result of the query as a pandas dataframe.
        """
        lm_query = _validate_query(query)
        result = self._process_request(
            lambda: requests.put(
                f"{self.base_url}/Sql/csv",
                params=lm_query.params,
                data=lm_query.sql_str,
                headers=self.headers()
            ),
            label='query and fetch'
        )
        return pd.read_csv(io.StringIO(result.content.decode()))

    def start_query(self, query: Union[str, Query]):
        """Send an asynchronous query to Luminesce. Starts the query but does not wait and fetch the result.

        Args:
            query (Union[str, Query]): query to be sent to Luminesce

        Returns:
            str: string containing the execution ID

        """
        lm_query = _validate_query(query)
        result = self._process_request(
            lambda: requests.put(
                f"{self.base_url}/SqlBackground",
                params=lm_query.params,
                data=lm_query.sql_str,
                headers=self.headers()
            ),
            "start query"
        )
        return result.json()['executionId']

    def get_status(self, execution_id):
        """Get the status of a Luminesce query

        Args:
            execution_id (str): unique execution ID of the query.

        Returns:
            Dict[str, str]: dictionary containing information on the query status.
        """
        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/SqlBackground/{execution_id}",
                headers=self.headers()
            ),
            label="get query status"
        )
        return result.json()

    def delete_query(self, execution_id):
        """Deletes a Luminesce query.

        Args:
            execution_id (str): unique execution ID of the query.

        Returns:
            Dict[str, str]: dictionary containing information on the deletion.

        """
        result = self._process_request(
            lambda: requests.delete(
                f"{self.base_url}/SqlBackground/{execution_id}",
                headers=self.headers()
            ),
            label="delete query"
        )
        return result.json()

    def get_page(self, execution_id, page, page_size=100000, sort_by=None, filter_str=None):
        """Gets a single page of a completed luminesce query and returns it as a pandas dataframe.

        Args:
            execution_id (str): execution ID of the query.
            page (int): page number to fetch.
            sort_by (str): string represting a sort to apply to the result before downloading it.
            filter_str (str): string representing a filter to apply to the result before downloading it.
            page_size (int, Optional): page size when getting the result via pagination. Default = 100000.

        Returns:
            DataFrame: downloaded page from result of the query as a pandas dataframe.

        """

        fetch_parameters = {'limit': page_size}
        if sort_by is not None:
            fetch_parameters['sortBy'] = sort_by
        if filter_str is not None:
            fetch_parameters['filter'] = filter_str

        fetch_parameters['page'] = page

        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/SqlBackground/{execution_id}/{'csv'}",
                headers=self.headers(),
                params=fetch_parameters
            ),
            label="get result"
        )

        page_result = pd.read_csv(io.StringIO(result.content.decode()))
        return page_result

    def get_result(self, execution_id, page_size=100000, sort_by=None, filter_str=None):
        """Gets the result of a completed luminesce query and returns it as a pandas dataframe.

        Args:
            execution_id (str): execution ID of the query.
            sort_by (str): string represting a sort to apply to the result before downloading it.
            filter_str (str): string representing a filter to apply to the result before downloading it.
            page_size (int, Optional): page size when getting the result via pagination. Default = 100000.

        Returns:
            DataFrame: result of the query as a pandas dataframe.

        """

        fetch_parameters = {'limit': page_size}
        if sort_by is not None:
            fetch_parameters['sortBy'] = sort_by
        if filter_str is not None:
            fetch_parameters['filter'] = filter_str

        page = 0
        chunks = []

        while True:
            chunk = self.get_page(execution_id, page, page_size, sort_by, filter_str)
            if chunk.shape[0] == 0:
                break

            page += 1
            chunks.append(chunk)

        return pd.concat(chunks)

    def start_history_query(self):
        """Start a query that get data on queries that have run historically

        Returns:
            str: execution ID of the history query
        """

        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/History",
                headers=self.headers()
            ),
            label='query history'
        )
        return result.json()['executionId']

    def get_history_status(self, ex_id: str):
        """Get the status of a history query

        Args:
            ex_id (str): execution ID to check status for

        Returns:
            Dict[str,str]: dictionary containing the information from the status response json
        """
        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/History/{ex_id}",
                headers=self.headers()
            ),
            label='get history query status'
        )
        return result.json()

    def get_history_result(self, ex_id):
        """Get result of history query

        Args:
            ex_id: execution ID to get the result for

        Returns:
            DataFrame: pandas dataframe containing the history query result.
        """
        result = self._process_request(
            lambda: requests.get(
                f"{self.base_url}/History/{ex_id}/json",
                headers=self.headers()
            ),
            label='get query history result'
        )
        return pd.DataFrame(result.json())

    def delete_view(self, name: str):
        """Deletes a Luminesce view provider with the given name.

        Args:
            name (str): name of the view provider to delete.

        Returns:
            DataFrame: result of the view deletion query as a pandas dataframe.

        """
        df = self.query_and_fetch(f"""
                @x = 
                use Sys.Admin.SetupView
                --provider={name}
                --deleteProvider
                --------------
                select 1;
                enduse;
                select * from @x;
            """)
        return df


def get_client(secrets: Optional[str] = None, token: Optional[str] = None) -> Client:
    """Get luminesce web API client instance.

    Args:
        secrets (Optional[str]): path to secrets file. If not supplied authentication information will be retrieved
        from the environment.
        token (Optional[str]): authentication token.

    Returns:
        Client: the web API client instance.
    """
    return Client(secrets, token)
