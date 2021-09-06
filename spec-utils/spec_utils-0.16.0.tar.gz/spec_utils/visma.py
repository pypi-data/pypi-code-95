from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from base64 import b64encode, b64decode
import requests
import datetime
import math


# TODO: Change to use requests sessions


class JsonObject:
    """ Convert a dict['element'] for access like object.property. """

    def __init__(self, json: dict):
        for k, v in json.items():
            setattr(self, k, v)

class Client:

    class Account:
        def __init__(self, **kwargs):
            self.tenants = [JsonObject(tnt) for tnt in kwargs.get('tenants')]
            self.user_info = JsonObject(kwargs.get('user_info'))
            self.roles = [JsonObject(roles) for roles in kwargs.get('roles')]

        @property
        def ft_id(self):
            """ Return the id of the first available tenant. """
            return getattr(self.tenants[0], 'Id', None)

        def get_tenant_id(self, filters_: dict):
            """
            Get tenant ID from tenant name. Use to use specific tenant.
            
            :param filters_: Dict with parameters to eval. Eg.
                {"DBName": "Name_Of_Database", "TenantName": "Tenant_Test"}.
            :param tenant_name: (optional) Str with name of tenant.
            :param \*\*kwargs: Optional arguments to filter.
            :return: :class:`int` object
            :rtype: int
            """
            
            # view all tenants
            for _t in self.tenants:
                
                # matches to eval
                _m = []

                # eval all key: value parameters
                for k, v in filters_.items():    
                    _m.append(True if getattr(_t, k, None) == v else False)

                # return tenant if all evals match
                if all(_m):
                    return getattr(_t, 'Id', None)
            
            # if None matche -or not all-
            return None
    
    class Authentication:
        def __init__(self, **kwargs):
            self.access_token = kwargs.get('access_token')
            self.token_type = kwargs.get('token_type', 'Bearer').capitalize()
            self.expires = self.get_expires(kwargs.get('expires_in'))

            self.rol = kwargs.get('rol')
            self.user_info = kwargs.get('user_info')

        def __str__(self):
            return f'{self.token_type} {self.access_token}'

        def __bool__(self):
            return self.is_alive

        def get_expires(self, expires_in: int) -> datetime.datetime:
            now = datetime.datetime.now()
            return now + datetime.timedelta(seconds=expires_in - 10)

        @property
        def is_alive(self):
            return self.expires > datetime.datetime.now()

        @property
        def is_expired(self):
            return not self.is_alive

    def __init__(self, url: str, username: str, pwd: str, *args, **kwargs):
        """ Create a conection with visma app using recived parameters. """

        self.client_url = urlparse(url)
        self.username = username
        self.pwd = b64encode(pwd.encode('utf-8'))

        self.authentication = None
        self.account = None

        # connect client and set authentication object automatically
        self.connect()

        # set account data automatically
        self.account = self.Account(
            tenants=self.get(path='/Admin/account/tenants'),
            user_info=self.get(path='/Admin/account/user-info'),
            roles=self.get(path='/Admin/account/roles')
        )

        # dict to filter tenant
        self.tenant_filter = kwargs.get('tenant_filter', None)

    def __str__(self):
        return '{}{} en {}'.format(
            f'{self.access_token} para ' if self.access_token else '',
            self.username,
            self.client_url.geturl()
        )

    def __repr__(self):
        return "{}(url='{}', username='{}', pwd='{}')".format(
            self.__class__.__name__,
            self.client_url.geturl(),
            self.username,
            b64decode(self.pwd).decode('utf-8'),
        )

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return self.disconnect()

    @property
    def headers(self):
        """ Get headers of the client with current data """

        # empty headers initial
        data = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
        }

        # logged user
        if self.authentication:
            data["Authorization"] = str(self.authentication)

        # tenant obtained
        if self.account:
            if self.tenant_filter:
                # get id with filter dict
                data["X-RAET-Tenant-Id"] = self.account.get_tenant_id(
                    filters_=self.tenant_filter
                )
            else:
                # get first available tenant
                data["X-RAET-Tenant-Id"] = getattr(
                    self.account,
                    'ft_id',
                    None
                )

        return data
    
    @property
    def is_connected(self):
        """ Informs if client has headers and access_token. """

        return bool(self.authentication)

    @property
    def session_expired(self):
        """
        Informs if the session has expired and it is necessary to reconnect.
        """

        return getattr(self.authentication, 'is_expired', None)

    def get(self, path: str, params: dict = None, **kwargs):
        """
        Sends a GET request to visma url.

        :param path: path to add to URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # check if session has expired
        if self.session_expired:
            self.reconnect()

        # safety only
        if not self.is_connected and not kwargs.get('force', None):
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # query prepare
        query = {
            "url": urljoin(self.client_url.geturl(), path),
            "params": params,
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 60),
            "stream": kwargs.get("stream", False)
        }

        # consulting nettime
        response = requests.get(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        try:
            # if request is stream type, return all response
            if kwargs.get("stream"):
                return response

            # return json response
            return response.json()
        except:
            return {}

    def bulk_get(self, path: str, params: dict = {}, \
            together: tuple = tuple(), max_workers: int = 50, \
            response_to_dict: bool = False, **kwargs):
        """
        Get from client object simultaneously.
        
        :param path: path to add to URL for the new :class:`Request` object.
        :param params: (optional) Dictionary, list of tuples or bytes to send
            in the query string for the :class:`Request`.
        :param together: Iterator of dicts to get together. E.g. 
            [{
                'page': 1
            },{
                'page': 2
            }]
        :max_workers: int to specify max workers number to run simultaneously.
        :response_to_dict: bool to group responses if there are dict objects.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # structures prepare
        responses = {} if response_to_dict else []
        processes = []
        params_ = params

        # create executor context
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # processes prepare
            for e_ in together:
                params_.update(e_)
                processes.append(
                    executor.submit(
                        self.get,
                        path=path,
                        params=params_,
                        **kwargs
                    )
                )

            # execute and put result in out structure
            if response_to_dict:
                [responses.update(r.result()) for r in as_completed(processes)]
            else:
                [responses.append(r.result()) for r in as_completed(processes)]

            # close executor
            executor.shutdown(wait=True)

        # return responses
        # list of pages result
        return responses

    def post(self, path, data=None, json=None, **kwargs):
        """
        Sends a POST request to visma url.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the 
            :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`dict` object
        :rtype: dict
        """

        # check if session has expired
        if self.session_expired:
            self.reconnect()

        # wait active conection
        if not self.is_connected and not kwargs.get('force', None):
            raise ConnectionError("Cliente desconectado. Utilice connect().")

        # query prepare
        query = {
            "url": urljoin(self.client_url.geturl(), path),
            "data": data,
            "json": json,
            "headers": self.headers,
            "timeout": kwargs.get("timeout", 20),
        }

        # consulting nettime
        response = requests.post(**query)

        # raise if was an error
        if response.status_code not in range(200, 300):
            raise ConnectionError(response.text)

        # to json -> json
        try:
            return response.json()
        except:
            return {}

    def connect(self):
        """ Connect the client to get access_token and headers values. """

        # None or not is_alive
        if self.is_connected:
            return

        # url and data prepare
        data = {
            "username": self.username,
            "password": b64decode(self.pwd).decode('utf-8'),
            "grant_type": "password"
        }
        response = self.post(
            path='/Admin/authentication/login',
            data=data,
            force=True
        )

        # if everything ok
        self.authentication = self.Authentication(**response)

    def disconnect(self):
        """ Disconnect the client if is connected. """

        # None or not is_alive
        if not self.is_connected:
            return

        response = self.post(path='/Admin/authentication/logout')
        self.authentication = None

    def reconnect(self):
        """ Reconnect client cleaning headers and access_token. """

        # clean token for safety
        self.authentication = None
        self.connect()

    def get_employees(self, employee: str = None, extension: str = None, \
            all_pages: bool = False, bulk_get: bool = False, **kwargs):
        """
        Use the endpoint to obtain the employees with the received data.
        
        :param employee: Optional internal id (rh-#) or external id (#).
        :param extension: Oprtional str for add to endpoint.
            :Possible cases:
            'addresses', 'phones', 'phases', 'documents', 'studies',
            'structures', 'family-members', 'bank-accounts',
            'accounting-distribution', 'previous-jobs', *'image'*.
        :param **kwargs: Optional arguments that ``request`` takes.
            :Possible cases:
            'orderBy': Results order. Format: Field1-desc|asc, Field2-desc|asc.
            'page': Number of the page to return.
            'pageSize': The maximum number of results to return per page.
            'active': Indicates whether to include only active Employees, 
                inactive Employees, or all Employees.
            'updatedFrom': Expected format "yyyy-MM-dd". If a date is provided, 
                only those records which have been modified since that date are 
                considered. If no Date is provided (or None), all records will 
                be returned.
        
        :return: :class:`dict` object
        :rtype: json
        """
        
        # path prepare
        path = '/WebApi/employees{}{}'.format(
            f'/{employee}' if employee else '',
            f'/{extension}' if employee and extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 50),
            "active": kwargs.get("active", None),
            "updatedFrom": kwargs.get("updatedFrom", None),
            "timeout": kwargs.get("timeout", 60)
        }

        # request.get -> json
        response = self.get(path=path, params=params)
        
        # recursive call to get all pages values
        if all_pages and response.get('totalCount', 0) > params.get('pageSize'):
            # calculate num of pages
            num_pages = math.ceil(
                response.get('totalCount') / params.get('pageSize')
            )
            
            # TODO: fix it
            # only with bulk_get param
            if bulk_get:
                together = [{'page': i} for i in range(2, num_pages + 1)]

                # get list of pages
                pages_result = self.bulk_get(
                    path=path,
                    params=params,
                    together=together,
                    max_workers=kwargs.get('max_workers', 50)
                )

                # get values and add to structure
                for pr in pages_result:
                    response['values'].extend(pr.get('values'))

            else:
                # recursive get and extend response values
                for i in range(2, num_pages + 1):
                    # update page
                    params['page'] = i
                    response['values'].extend(
                        self.get(path=path, params=params).get('values')
                    )

        
        # put elements in dict if is ask extensions
        if bulk_get and extension and kwargs.get('group_results', None):
            return {employee: {extension: response}}

        # return elements
        return response

    def get_addresses(self, address: str = None, extension: str = None, \
            **kwargs):

        # check validity
        if address and extension:
            raise KeyError("No se pueden especificar un address y extension.")
        
        # path prepare
        path = '/WebApi/addresses{}{}'.format(
            f'/{address}' if address else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_birth_places(self, **kwargs):
        
        # path prepare
        path = '/WebApi/birth-places'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "countryId": kwargs.get("countryId", None),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_countries(self, **kwargs):

        # path prepare
        path = '/WebApi/countries'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_family_members(self, **kwargs):

        # path prepare
        path = '/WebApi/family-members/types'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_journals(self, journal: str = None, extension: str = "lines", \
            **kwargs):

        # path prepare
        path = '/WebApi/journals{}{}'.format(
            f'/{journal}' if journal and extension else '',
            f'/{extension}' if journal and extension else '',
        )

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "dateTo": kwargs.get("dateTo", None),
            "processDate": kwargs.get("processDate", None),
            "companyId": kwargs.get("companyId", None),
            "companyName": kwargs.get("companyName", None),
            "account": kwargs.get("account", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_leaves(self, extension: str = None, **kwargs):

        # path prepare
        path = '/WebApi/leaves{}'.format(
            f'/{extension}' if extension else '',
        )

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "typeLeaveId": kwargs.get("typeLeaveId", None),
            "leaveState": kwargs.get("leaveState", None),
            "employeeId": kwargs.get("employeeId", None),
            "dateTo": kwargs.get("dateTo", None),
            "dayType": kwargs.get("dayType", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "year": kwargs.get("year", None),
            "typeId": kwargs.get("typeId", None),
            "holidayModelId": kwargs.get("holidayModelId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_loans(self, **kwargs):

        # path prepare
        path = '/WebApi/loans'

        # getting default date
        today = datetime.date.today()

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get("dateFrom", today.isoformat()),
            "employeeId": kwargs.get("employeeId", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_nationalities(self, **kwargs):

        # path prepare
        path = '/WebApi/loans'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_pay_elements(self, employeeExternalId: str, **kwargs):

        # path prepare
        path = '/WebApi/pay-elements/individual'

        # parameters prepare
        params = {
            "employeeExternalId": employeeExternalId,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "conceptExternalId": kwargs.get("conceptExternalId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def post_pay_elements(self, values: list, **kwargs):
        """
        Use the endpoint to post recived payment/s data.

        :param values: list of dict for send to api. Each dict must be like:
            {
                "employeeExternalId": "string",         
                # Legajo del empleado (Obligatorio) 
                "periodFrom": "string",                 
                # Descripcion Periodo (opcional) para retroactividad
                "periodTo": "string",                   
                #  Descripcion Periodo  (opcional) para retroactividad
                "reason": "string",                     
                # razón (descriptivo)   (opcional)
                "reasonTypeExternalId": "string",       
                # id tipo razon (opcional)
                "action": 0,                            
                # 0 inserta, 1 Actualiza 
                "retroactive": Boolean,                 
                # true o false (retroactividad)
                "journalModelId": 0,                    
                # id modelo de asiento  (opcional)
                "journalModelStructureId1": 0,          
                # id estructura 1 del modelo de asiento  (opcional)
                "journalModelStructureId2": 0,          
                # id estructura 2 del modelo de asiento  (opcional)
                "journalModelStructureId3": 0,          
                # id estructura 3 del modelo de asiento  (opcional)
                "conceptExternalId": "string",          
                # Codigo externo del concepto (Obligatorio)
                "parameterId": 0,                       
                # código interno del del parámetro (Obligatorio)
                "dateFrom": "2020-10-01T18:23:50.691Z", 
                # fecha de vigencia desde (opcional) 
                "dateTo": "2020-10-01T18:23:50.691Z",   
                # fecha de vigencia hasta  (opcional)
                "value": 0                              
                # valor de la novedad (Obligatorio)
            }
        
        :return: json object
        :rtype: json
        """

        # path prepare
        path = '/WebApi/pay-elements/individual'

        # request.get -> json
        return self.post(path=path, json={"values": values}, **kwargs)

    def get_payments(self, extension: str, **kwargs):

        # path prepare
        path = f'/WebApi/payments/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_payrolls(self, extension: str, **kwargs):

        # path prepare
        path = f'/WebApi/payrolls/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
            "year": kwargs.get("year", None),
            "month": kwargs.get("month", None),
            "periodId": kwargs.get("periodId", None),
            "companyId": kwargs.get("companyId", None),
            "modelId": kwargs.get("modelId", None),
            "stateId": kwargs.get("stateId", None),
            "conceptTypeId": kwargs.get("conceptTypeId", None),
            "printable": kwargs.get("printable", None),
            "search": kwargs.get("search", None),
            "employeeId": kwargs.get("employeeId", None),
            "accumulatorId": kwargs.get("accumulatorId", None),
            "processId": kwargs.get("processId", None),
            "conceptId": kwargs.get("conceptId", None),
            "conceptCode": kwargs.get("conceptCode", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_phases(self, phase: str = None, **kwargs):

        # path prepare
        path = '/WebApi/phases{}'.format(
            f'/{phase}' if phase else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "type": kwargs.get("type", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_phones(self, phone: str = None, extension: str = None, **kwargs):

        # check validity
        if phone and extension:
            raise KeyError("No se pueden especificar un phone y extension.")

        # path prepare
        path = '/WebApi/phones{}{}'.format(
            f'/{phone}' if phone else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_scales(self, scale: int, **kwargs):

        # path prepare
        path = '/WebApi/scales'

        # parameters prepare
        params = {
            "id": scale,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "coordinates": kwargs.get("coordinates", None),
            "order": kwargs.get("order", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_seizures(self, startDate: str, **kwargs):

        # path prepare
        path = '/WebApi/seizures'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "startDate": startDate,
            "employeeId": kwargs.get("employeeId", None),
            "stateId": kwargs.get("stateId", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_structures(self, extension: str = None, **kwargs):

        # path prepare
        path = '/WebApi/structures{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "typeId": kwargs.get("typeId", None),
            "active": kwargs.get("active", None),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def get_sync(self, extension: str = None, applicationName: str = None, \
            **kwargs):

        if not extension and not applicationName:
            raise KeyError("Debe especificar un applicationName.")

        # path prepare
        path = '/WebApi/sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "applicationName": applicationName,
            "parentEntity": kwargs.get("parentEntity", None),
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "lastUpdate": kwargs.get("lastUpdate", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)
    
    def post_sync(self, **kwargs):
        pass

    def get_time_management(self, extension: str = None, **kwargs):
        
        # path prepare
        path = '/WebApi/sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", 5),
            "employeeId": kwargs.get("employeeId", None),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "typeOfHours": kwargs.get("typeOfHours", None),
            "search": kwargs.get("search", None),
            "shiftId": kwargs.get("shiftId", None),
            "statusId": kwargs.get("statusId", None),
            "clockId": kwargs.get("clockId", None),
            "subShiftId": kwargs.get("subShiftId", None),
            "active": kwargs.get("active", None),
            "detail": kwargs.get("detail", None),
            "structureTypeId1": kwargs.get("structureTypeId1", None),
            "structureId1": kwargs.get("structureId1", None),
            "structureTypeId2": kwargs.get("structureTypeId2", None),
            "structureId2": kwargs.get("structureId2", None),
            "structureTypeId3": kwargs.get("structureTypeId3", None),
            "structureId3": kwargs.get("structureId3", None),
        }

        # request.get -> json
        return self.get(path=path, params=params)

    def post_time_management(self, **kwargs):
        pass

    def get_version(self):
        """
        Get current version information related with the assemblies name and 
        version.
        """

        # request.get -> json
        return self.get(path='/WebApi/version')

