from requests.structures import CaseInsensitiveDict
from requests import Session, ConnectionError
import os
import time
import logging
from datetime import datetime

BASE_URL = "https://api.planfact.io"
MAX_SENDING_TRIES = 3
MIN_TIME_BETWEEN_REQUEST = 0.1
MAX_REQUSTS_PER_FUNCTION = 100

logger = logging.getLogger(__name__)


class PfInteraction:
    def __init__(self):
        self.session = Session()
        self.headers = CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.time_at_last_request = time.time()

    def _get_header(self):
        PF_API_KEY = os.environ["PF_API_KEY"]
        self.headers["X-ApiKey"] = PF_API_KEY
        return self.headers

    def request_list(self, method, path, changes_from_date=None, data=None, params=None, headers=None):
        if params is not None:
            if method == 'get' and 'paging.limit' in params.keys():
                if changes_from_date is not None:
                    if not isinstance(changes_from_date, datetime):
                        raise TypeError('changes_from_date have to be from type datetime')
                    else:
                        params.update({
                            'sorting.field': ' ModifyDate',
                            'filter.changesFromDate': changes_from_date.strftime('%Y-%m-%dT%H:%M:%S')
                        })
            all_items = []
            for i in range(MAX_REQUSTS_PER_FUNCTION):
                res, status_code = self.request(method, path, data, params, headers)
                all_items += res.json()['data']['items']
                if len(res.json()['data']['items']) < params['paging.limit']:
                    break
                else:
                    params['paging.offset'] = params['paging.limit'] * (i + 1)
            for item in all_items:
                # convert ModifyDate into datetime
                if 'modifyDate' in item.keys():
                    try:
                        item['modifyDate'] = datetime.strptime(item['modifyDate'], '%Y-%m-%dT%H:%M:%S.%f')
                    except ValueError:
                        item['modifyDate'] = datetime.strptime(item['modifyDate'], '%Y-%m-%dT%H:%M:%S')
                else:
                    break
            return all_items
        else:
            logger.error('this is not an list operation')
            raise

    def request(self, method, path, data=None, params=None, headers=None):
        headers = self._get_header()

        max_sending_tries = MAX_SENDING_TRIES
        # make sure that the rate is not to high
        time_passed = time.time() - self.time_at_last_request
        logger.debug('time passed %s' % str(time_passed))
        # send the request,
        for send_request_tries in range(max_sending_tries):
            # wait MIN_TIME_BETWEEN_REQUEST second
            if time_passed < MIN_TIME_BETWEEN_REQUEST:
                logger.debug('have to wait %s' % str(MIN_TIME_BETWEEN_REQUEST - time_passed))
                time.sleep(MIN_TIME_BETWEEN_REQUEST - time_passed)
            # reset time
            self.time_at_last_request = time.time()

            try:
                response = self.session.request(method,
                                                url=BASE_URL + path,
                                                json=data,
                                                params=params,
                                                headers=headers)
                logger.debug('sending pf-request')
            except ConnectionError as err:
                error = ('Got an exception while %s sending: ' % method) + str(err)
                logger.warning(error)
                logger.warning(f'current try: {send_request_tries}')
                if send_request_tries < 3:
                    send_request_tries += 1
                else:
                    raise ConnectionError(err.args[0].args[0])  # Sometimes Connection aborted.
            except Exception as err:
                error = ('Got an exception while %s sending: ' % method) + str(err)
                logger.error(error)
                raise
            else:
                if response.status_code == 200:
                    if response.json()['isSuccess']:
                        return response, 200
                    else:
                        raise ConnectionError(
                            "Status is 200, but no Success, with "
                            "errorCode: {} and errorMessage: '{}'".format(response.json()['errorCode'],
                                                                          response.json()['errorMessage']))
                else:
                    raise ConnectionError("Status not 200, but: {} ({})".format(response.status_code, response.text))


pf_interaction = PfInteraction()
