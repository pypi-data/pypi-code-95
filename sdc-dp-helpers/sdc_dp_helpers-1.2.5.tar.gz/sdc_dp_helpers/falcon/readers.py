"""
    CUSTOM FALCON READER CLASSES
"""
import os
import time

import requests
import simplejson
import yaml

from sdc_dp_helpers.api_utilities.retry_managers import request_handler, retry_handler
from sdc_dp_helpers.api_utilities.date_managers import date_handler


class CustomFalconReader:
    """
        Custom Falcon Reader
    """

    def __init__(self, api_key_path, config_path=None):
        self.api_key_path = api_key_path
        self.config_path = config_path

        self.api_key = self.get_api_key()
        self.config = self.get_configuration()

        self.request_session = requests.Session()

    def get_api_key(self):
        """
            Gathers key and value pairs of client and their token.
        """
        with open(self.api_key_path, 'r') as file:
            data = yaml.safe_load(file)
            return data.get('api_key')

    def get_configuration(self):
        """
            Gathers optional and required configuration that
            defines the params for the api. This is optional.
            The configuration resembles the parameters of the
            given api method. eg:

            since: '2020-10-01T22:00:00.000Z'
            until: '2021-02-09T22:00:00.000Z'
            channels:
                - 'twitter_110592_91962761'
                - 'linkedin_110592_4840205'
            statuses:
                - 'all'
            limit: '30'
        """
        if self.config_path is not None:
            with open(self.config_path, 'r') as file:
                data = yaml.safe_load(file)
                return data
        return None

    def get_channel_ids(self):
        """
            Gather all available channel ids.
        """
        url = 'https://api.falcon.io/channels?apikey={apikey}' \
            .format(apikey=self.api_key)

        # no configs required, everything should be fetched, set limit to as high as possible
        try:
            response = requests.get(url=url, params={'limit': '999'}).json()
        except simplejson.errors.JSONDecodeError as err:
            raise EnvironmentError from err

        data_set = []
        for items in response['items']:
            data_set.append(items['id'])

        return data_set

    @request_handler(
        wait=int(os.environ.get('REQUEST_WAIT_TIME', 0)),
        backoff_factor=float(os.environ.get('REQUEST_BACKOFF_FACTOR', 0.01)),
        backoff_method=os.environ.get('REQUEST_BACKOFF_METHOD', 0.01)
    )
    def _query_metrics_by_channel(self, url, params):
        """
        Separate initial request for the request handler.
        """
        return self.request_session.post(url=url, json=params)

    @retry_handler(exceptions=ConnectionRefusedError, total_tries=10)
    def metrics_by_channel(self, channel_ids, filter_type='all'):
        """
        Get metrics by channel Id context returns a request session with the ability
        to page with offsets.
        Content (or Post level) contains all metrics about your specific piece of
        content (posts). Here you will find impressions, reach, likes,
        shares and other metrics that show how well your specific post has performed.
        https://falconio.docs.apiary.io/reference/content-api/get-copied-content
        :channel_ids: list. List of channels for the API to return metrics on.
        :offset: int. Offset number from 0 until None is returned.
        :filter_type: str. filter type of 'all', 'default' or 'post'
        """
        url = 'https://api.falcon.io/measure/api/v1/content/metrics?apikey={apikey}' \
            .format(apikey=self.api_key)

        params = self.config
        params['channels'] = channel_ids

        # there are three options for dynamic time filtering
        if filter_type == 'default':
            params['since'] = date_handler(params['since'])
            params['until'] = date_handler(params['until'])
        elif filter_type == 'post':
            params['postsSince'] = date_handler(params['postsSince'])
            params['postsUntil'] = date_handler(params['postsUntil'])
        elif filter_type == 'all':
            params['since'] = date_handler(params['since'])
            params['until'] = date_handler(params['until'])
            params['postsSince'] = date_handler(params['postsSince'])
            params['postsUntil'] = date_handler(params['postsUntil'])
        else:
            raise ValueError('{val} is not a valid filter_today_type option'.format(
                val=filter_type
            ))

        offset, status_count, data_set = 0, 0, []
        while True:
            params['offset'] = offset
            print(f'Config: {self.config}')
            response = self._query_metrics_by_channel(url=url, params=params)

            # handle rate limit & rolling window limit with
            # a sleep method and counter before failure for non 429 responses
            if response.status_code == 500:
                # the api only returns 500 if a configuration is bad or invalid
                raise EnvironmentError('Status Code [500] returned.'
                                       'The reader configuration may be invalid.')

            if response.status_code == 429:
                print('Rolling Window Quota [429] reached, waiting for 15 minutes.')
                time.sleep(900)
            elif response.status_code != 200:
                raise ConnectionRefusedError

            data = response.json()
            print(f'Data: {data}')

            # break when there is no more data returned
            try:
                data_set.append(data[0])
                offset += 1
            except (IndexError, KeyError):
                print('No more data in response, stopping.')
                break

        return data_set
