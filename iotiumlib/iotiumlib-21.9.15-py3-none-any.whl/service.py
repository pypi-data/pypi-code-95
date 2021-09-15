"""
// ========================================================================
// Copyright (c) 2018-2019 Iotium, Inc.
// ------------------------------------------------------------------------
// All rights reserved.
//
// ========================================================================
"""

__author__ = "Rashtrapathy"
__copyright__ = "Copyright (c) 2018-2019 by Iotium, Inc."
__license__ = "All rights reserved."
__email__ = "rashtrapathy.c@iotium.io"


from iotiumlib.requires.commonWrapper import *
from iotiumlib.requires.resourcePayload import *

serviceId = str()
orgId = str()

class service(object):

    """
    Service Resource
    """

    def __init__(self, action, payload=None, service_id=None, template_id=None, filters=None):

        if payload is None:
            payload = {}

        def add_service(uri):
            return service.Service(self, method='post', uri=uri)

        def edit_service(uri):
            return service.Service(self, method='put', uri=uri)

        def delete_service(uri):
            return service.Service(self, method='delete', uri=uri)

        def get_service(uri):
            return service.Service(self, method='get', uri=uri)

        def getv2_service(uri):
            return service.Service(self, method='getv2', uri=uri, filters=filters)

        def getv2_template_service(uri):
            return service.Template(self, method='getv2', uri=uri)

        def get_template_service(uri):
            return service.Template(self, method='get', uri=uri)

        def get_service_id_service(uri):
            return service.Service(self, method='get', uri=uri)

        def restart_service(uri):
            return service.Service(self, method='post', uri=uri)

        _function_mapping = {
            'add': add_service,
            'edit':edit_service,
            'delete':delete_service,
            'get':get_service,
            'get_service_id': get_service_id_service,
            'getv2_template':getv2_template_service,
            'get_template': get_template_service,
            'getv2': getv2_service,
            'restart':restart_service

        }

        self.uri = {
            add_service: 'api/v1/service',
            get_service: 'api/v1/service',
            edit_service: 'api/v1/service/{serviceId}',
            delete_service: 'api/v1/service/{serviceId}',
            get_service_id_service: 'api/v1/service/{serviceId}',
            getv2_service: 'api/v2/service',
            getv2_template_service:'api/v2/servicetemplate',
            get_template_service: 'api/v1/servicetemplate/{templateId}',
            restart_service: 'api/v1/service/{serviceId}/restart'
        }

        #self.payload = resourcePaylod.Service(payload).__dict__
        self.payload = payload

        self.serviceId = service_id
        self.templateId = template_id

        self.orgId = orch.id

        self.Response = Response()

        _wrapper_fun = _function_mapping[action]
        args = '{}_service'.format(action)
        _wrapper_fun(self.uri[eval(args)])

    def __del__(self):
        self.payload = dict()
        self.Response = Response()


    def Service(self, method, uri, filters=None):

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

    def Template(self, method, uri, filters=None):

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

def delete(service_id):
    return service(action='delete', service_id=service_id)

def get(service_id=None, template_id=None):
    if service_id is not None:
        return service(action='get_service_id', service_id=service_id)
    elif template_id is not None:
        return service(action='get_template', template_id=template_id)
    else:
        return service(action='get')

def getv2(filters=None):
    return service(action='getv2', filters=filters)

def getv2_template(filters=None):
    return service(action='getv2_template', filters=filters)

def add(payload):
    return service(action="add", payload=payload)

def edit(service_id, payload):
    return service(action="edit", payload=payload, service_id=service_id)

def restart(service_id):
    return service(action="restart", service_id=service_id)
