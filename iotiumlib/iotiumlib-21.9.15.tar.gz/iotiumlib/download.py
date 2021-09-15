"""
// ========================================================================
// Copyright (c) 2020 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2020 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

activityId = str()

class download(object):

    class event(object):

        def __init__(self, action, payload=None, filters=None, event_id=None):

            if payload is None:
                payload = {}

            def request_downevent(uri):
                return download.event.DownloadEvent(self, method='post', uri=uri)

            def list_downevent(uri):
                return download.event.DownloadEvent(self, method='getv2', uri=uri, filters=filters)

            def delete_downevent(uri):
                return download.event.DownloadEvent(self, method='delete', uri=uri)

            _function_mapping = {
                'list': list_downevent,
                'request' : request_downevent,
                'delete':delete_downevent,
            }

            self.uri = {
                list_downevent: 'api/v1/download/event',
                request_downevent: 'api/v1/download/event',
                delete_downevent: 'api/v1/download/event/{eventId}',
            }

            self.payload = resourcePaylod.DownloadEvent(payload).__dict__

            self.eventId = event_id

            self.Response = Response()

            _wrapper_fun = _function_mapping[action]
            args = '{}_downevent'.format(action)
            _wrapper_fun(self.uri[eval(args)])

        def DownloadEvent(self, method, uri, filters=None):
            respOp = dict()
            paramRequired = checkforUriParam(uri)
            if paramRequired:
                for param in paramRequired:
                    uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
            if method == 'getv2':
                self.Response = getApiv2(formUri(uri), filters)
                return self.Response
            elif method == 'post':
                respOp = postApi(formUri(uri), self.payload)
            elif method == 'delete':
                respOp = deleteApi(formUri(uri))
            else:
                return self.Response
            self.Response.output = respOp.json()
            self.Response.code = respOp.status_code
            return self.Response

        @staticmethod
        def request(resource_group=None, org_id=None, own=True, start_date=None, end_date=None,
                    node_id=None, cluster_id=None):
            '''
            :param resource_group:  inode, network, service, webhook
            :param org_id:
            :param own: True/False
            :param start_date: ISO-8601 standard
            :param end_date: ISO-8601 standard
            :param node_id:
            :param cluster_id:
            :return:
            '''
            return download.event(action='request', payload=locals())

        @staticmethod
        def delete(event_id):
            return download.event(action="delete", event_id=event_id, payload=locals())

        @staticmethod
        def list(filters=None):
            return download.event(action='list', filters=filters)

        def __del__(self):
            self.payload = dict()
            self.Response = Response()

    class activity(object):

        def __init__(self, action, payload=None, filters=None, activity_id=None):

            if payload is None:
                payload = {}

            def request_downactivity(uri):
                return download.activity.DownloadActivity(self, method='post', uri=uri)

            def list_downactivity(uri):
                return download.activity.DownloadActivity(self, method='getv2', uri=uri, filters=filters)

            def delete_downactivity(uri):
                return download.activity.DownloadActivity(self, method='delete', uri=uri)

            _function_mapping = {
                'list': list_downactivity,
                'request' : request_downactivity,
                'delete':delete_downactivity,
            }

            self.uri = {
                list_downactivity: 'api/v1/download/activity',
                request_downactivity: 'api/v1/download/activity',
                delete_downactivity: 'api/v1/download/activity/{activityId}',
            }

            self.payload = resourcePaylod.DownloadActivity(payload).__dict__

            self.activityId = activity_id

            self.Response = Response()

            _wrapper_fun = _function_mapping[action]
            args = '{}_downactivity'.format(action)
            _wrapper_fun(self.uri[eval(args)])

        def DownloadActivity(self, method, uri, filters=None):
            respOp = dict()
            paramRequired = checkforUriParam(uri)
            if paramRequired:
                for param in paramRequired:
                    uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
            if method == 'getv2':
                self.Response = getApiv2(formUri(uri), filters)
                return self.Response
            elif method == 'post':
                respOp = postApi(formUri(uri), self.payload)
            elif method == 'delete':
                respOp = deleteApi(formUri(uri))
            else:
                return self.Response
            self.Response.output = respOp.json()
            self.Response.code = respOp.status_code
            return self.Response

        @staticmethod
        def request(org_id=None, start_date=None, end_date=None, own=True):
            '''
            :param org_id:
            :param start_date: ISO-8601 standard
            :param end_date: ISO-8601 standard
            :return:
            '''
            return download.activity(action='request', payload=locals())

        @staticmethod
        def delete(activity_id):
            return download.activity(action="delete", activity_id=activity_id, payload=locals())

        @staticmethod
        def list(filters=None):
            return download.activity(action='list', filters=filters)

        def __del__(self):
            self.payload = dict()
            self.Response = Response()
