"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2020 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"

from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

userId = str()
subId = str()
webhookId = str()

class user(object):
    def __init__(self, action, payload=None, filters=None, user_id=None):

        if payload is None:
            payload = {}

        def getv2_user(uri):
            return user.User(self, method='getv2', uri=uri, filters=filters)

        def add_user(uri):
            return user.User(self, method='post', uri=uri)

        def edit_user(uri):
            return user.User(self, method='put', uri=uri)

        def delete_user(uri):
            return user.User(self, method='delete', uri=uri)

        def notifications_user(uri):
            return user.Notifications(self, method='notifications', uri=uri, filters=filters)

        _function_mapping = {
            'getv2': getv2_user,
            'add' : add_user,
            'edit' : edit_user,
            'delete':delete_user,
            'notifications': notifications_user
        }

        self.uri = {
            getv2_user: 'api/v2/user',
            add_user: 'api/v1/user',
            edit_user: 'api/v1/user/{userId}',
            delete_user: 'api/v1/user/{userId}',
            notifications_user: 'api/v2/notification'
        }

        self.payload = resourcePaylod.User(payload).__dict__

        self.userId = user_id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_user'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def User(self, method, uri, filters=None):

        respOp = dict()
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)

        if method == 'get':
            respOp = getApi(formUri(uri))
        elif method == 'getv2':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response
        elif method == 'post':
            respOp = postApi(formUri(uri), self.payload)
        elif method == 'put':
            respOp = putApi(formUri(uri), self.payload)
        elif method == 'delete':
            respOp = deleteApi(formUri(uri))
        else:
            return self.Response
        self.Response.output = respOp.json()
        self.Response.code = respOp.status_code
        return self.Response

    def Notifications(self, method, uri, filters=None):
        paramRequired = checkforUriParam(uri)
        if paramRequired:
            for param in paramRequired:
                uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
        if method == 'notifications':
            self.Response = getApiv2(formUri(uri), filters)
            return self.Response
        else:
            return self.Response

    @staticmethod
    def add(name, email, password, role_id, org_id=None, timezone=None):
        return user(action='add', payload=locals())

    @staticmethod
    def edit(user_id, name=None, role_id=None):
        return user(action='edit', payload=locals(), user_id=user_id)

    @staticmethod
    def delete(user_id):
        return user(action='delete', user_id=user_id)

    @staticmethod
    def getv2(filters=None):
        return user(action='getv2', filters=filters)

    @staticmethod
    def notifications(org_id=None, node_id=None, type=None, filters=None):

        if filters is None:
            filters = dict()

        if org_id:
            filters.update({"org_id": org_id})

        if node_id:
            filters.update({"node_id": node_id})

        if type:
            filters.update({'type': type})

        return user(action="notifications", filters=filters)

    def __del__(self):
        self.payload = dict()
        self.Response = Response()

    class mysubscriptions(object):
        def __init__(self, action, payload=None, filters=None, sub_id=None):

            if payload is None:
                payload = {}

            def add_sub(uri):
                return user.mysubscriptions.MySub(self, method='post', uri=uri)

            def getv2_sub(uri):
                return user.mysubscriptions.MySub(self, method='getv2', uri=uri, filters=filters)

            def delete_sub(uri):
                return user.mysubscriptions.MySub(self, method='delete', uri=uri)

            _function_mapping = {
                'getv2': getv2_sub,
                'add' : add_sub,
                'delete':delete_sub,
            }

            self.uri = {
                getv2_sub: 'api/v2/mysubscriptions',
                add_sub: 'api/v1/mysubscriptions',
                delete_sub: 'api/v1/mysubscriptions/{subId}',
            }

            self.payload = resourcePaylod.Subscriptions(payload).__dict__

            self.subId = sub_id

            self.Response = Response()

            _wrapper_fun = _function_mapping[action]
            args = '{}_sub'.format(action)
            _wrapper_fun(self.uri[eval(args)])

        def MySub(self, method, uri, filters=None):
            respOp = dict()
            paramRequired = checkforUriParam(uri)
            if paramRequired:
                for param in paramRequired:
                    uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
            if method == 'notifications':
                self.Response = getApiv2(formUri(uri), filters)
                return self.Response

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
        def add(alert_name, type, org_id, node_id=None, include_child=False, duration=5,
                pod_id=None, network_id=None, tunnel_id=None, channel_type=None, channel_id=None):
            """
            :param pod_id:
            :param network_id:
            :param tunnel_id:
            :param alert_name:
            :param type:
                CERT_EXPIRY,
                HEADLESS_EXPIRY,
                NODE_STATE_CHANGE,
                SERVICE_STATE_CHANGE,
                TUNNEL_STATE_CHANGE,
                NODE_IP_CHANGE,
                NODE_REBOOT,
                NODE_INTERNAL,
                SERVICE_INTERNAL,
                NETWORK_INTERNAL,
                USER_WELCOME_EMAIL,
                USER_VERIFY_EMAIL,
                USER_FORGOT_PASSWORD,
                USER_PASSWORD_CHANGED,
                NODE_UPGRADE;
            :param duration: in minutes.
            :param org_id:
            :param node_id:
            :param channel_type: EMAIL or WEBHOOK
            :param channel_id: Webhook ID
            :param include_child: bool
            :return:
            """
            def get_alert_me_from_type(_type):
                _map_ = {
                    'NODE_STATE_CHANGE': "ALIVE,UNREACHABLE",
                    'TUNNEL_STATE_CHANGE': "CONNECTED,TERMINATED",
                    'SERVICE_STATE_CHANGE': "HEALTHY,TERMINATED,UNHEALTHY",
                    'CERT_EXPIRY': "80,100",
                    'HEADLESS_EXPIRY': "80,100",
                    'NODE_UPGRADE': "ENABLED,DISABLED,SUCCESSFUL,FAILED",
                    'NODE_IP_CHANGE': "PRIVATE_IP,PUBLIC_IP"
                }
                return _map_.get(_type, None)
            alert_me = get_alert_me_from_type(type)
            return user.mysubscriptions(action='add', payload=locals())

        @staticmethod
        def delete(sub_id):
            return user.mysubscriptions(action="delete", sub_id=sub_id, payload=locals())

        @staticmethod
        def getv2(filters=None):
            return user.mysubscriptions(action='getv2', filters=filters)

        def __del__(self):
            self.payload = dict()
            self.Response = Response()

    class webhook(object):
        __class__ = "webhook"

        """
        webhook Resource
        """

        def __init__(self, action, filters=None, payload=None, webhook_id=None):

            if payload is None:
                payload = {}

            def add_webhook(uri):
                return user.webhook.Webhook(self, method='post', uri=uri)

            def edit_webhook(uri):
                return user.webhook.Webhook(self, method='put', uri=uri)

            def delete_webhook(uri):
                return user.webhook.Webhook(self, method='delete', uri=uri)

            def get_webhook(uri):
                return user.webhook.Webhook(self, method='get', uri=uri)

            def getv2_webhook(uri):
                return user.webhook.Webhook(self, method='getv2', uri=uri, filters=filters)

            def get_webhook_id_webhook(uri):
                return user.webhook.Webhook(self, method='get', uri=uri)

            def verify_webhook(uri):
                return user.webhook.Webhook(self, method='post', uri=uri)

            def test_webhook(uri):
                return user.webhook.Webhook(self, method='post', uri=uri)

            _function_mapping = {
                'add': add_webhook,
                'edit': edit_webhook,
                'delete': delete_webhook,
                'get': get_webhook,
                'verify': verify_webhook,
                'get_webhook_id': get_webhook_id_webhook,
                'getv2': getv2_webhook,
                'test': test_webhook
            }

            self.uri = {
                add_webhook: 'api/v1/webhook',
                get_webhook: 'api/v1/webhook',
                getv2_webhook: 'api/v2/webhook',
                edit_webhook: 'api/v1/webhook/{webhookId}',
                delete_webhook: 'api/v1/webhook/{webhookId}',
                get_webhook_id_webhook: 'api/v1/webhook/{webhookId}',
                verify_webhook: 'api/v1/webhook/{webhookId}/verify',
                test_webhook: 'api/v1/webhook/{webhookId}/test'
            }

            if action == "test":
                self.payload = resourcePaylod.WebhookTest(payload).__dict__
            else:
                self.payload = resourcePaylod.Webhook(payload).__dict__

            self.webhookId = webhook_id
            self.orgId = orch.id

            self.Response = Response()

            _wrapper_fun = _function_mapping[action]
            args = '{}_webhook'.format(action)
            _wrapper_fun(self.uri[eval(args)])

        def __del__(self):
            self.payload = dict()
            self.Response = Response()

        def Webhook(self, method, uri, filters=None):

            paramRequired = checkforUriParam(uri)
            if paramRequired:
                for param in paramRequired:
                    uri = re.sub(r'{{{}}}'.format(param), eval('self.{}'.format(param)), uri)
            if method == 'get':
                respOp = getApi(formUri(uri))
            elif method == 'getv2':
                self.Response = getApiv2(formUri(uri), filters)
                return self.Response
            elif method == 'post':
                respOp = postApi(formUri(uri), self.payload)
            elif method == 'put':
                respOp = putApi(formUri(uri), self.payload)
            elif method == 'delete':
                respOp = deleteApi(formUri(uri))
            else:
                return self.Response
            self.Response.output = respOp.json()
            self.Response.code = respOp.status_code
            return self.Response

        @staticmethod
        def add(name, url, secret, headers=None, label=None):
            """
            Add webhook
            :param name: webhook Name
            :param url: URL of webhook server
            :param secret: secret configured for the URL at webhook server
            :param headers: Headers expected by webhook server
            :param label: Labels pairs associated to the webhook
            :return: resp object
            """
            return user.webhook(action="add", payload=locals())

        @staticmethod
        def edit(webhook_id, name=None, url=None, secret=None, headers=None, label=None):
            resp = user.webhook.get(webhook_id=webhook_id)
            name = resp.Response.output['name'] if name is None else name
            url = resp.Response.output['url'] if url is None else url
            secret = resp.Response.output['secret'] if secret is None else secret
            headers = resp.Response.output['headers'] if headers is None else headers

            if label is None:
                labels = []
                for k, v in resp.Response.output['metadata']['labels'].items():
                    if not k.startswith('_'):
                        labels.append(":".join([k.strip(), v.strip()]))
                label = str(','.join(labels))
            elif label.title() == "None":
                label = "None"

            return user.webhook(action="edit",
                           payload=locals(),
                           webhook_id=webhook_id
                           )

        @staticmethod
        def delete(webhook_id):
            return user.webhook(action="delete",
                           webhook_id=webhook_id
                           )

        @staticmethod
        def verify(webhook_id):
            return user.webhook(action="verify",
                           webhook_id=webhook_id
                           )

        @staticmethod
        def test(webhook_id, alert_type):
            return user.webhook(action="test",
                           webhook_id=webhook_id,
                           payload=locals()
                           )

        @staticmethod
        def get(webhook_id=None):
            if webhook_id is not None:
                return user.webhook(action='get_webhook_id', webhook_id=webhook_id)
            else:
                return user.webhook(action="get")

        @staticmethod
        def getv2(filters=None):
            return user.webhook(filters=filters, action='getv2')

