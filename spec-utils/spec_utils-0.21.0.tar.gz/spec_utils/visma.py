from __future__ import annotations
from urllib.parse import urljoin, urlparse
from aiohttp import ClientSession
from asyncio import gather as aio_gather
from base64 import b64decode
from math import ceil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import requests
import datetime
import warnings

try:
    from ._base import OAuthClient, AsyncOAuthClient
except ImportError:
    from _base import OAuthClient, AsyncOAuthClient


class JsonObject:
    """ Convert a dict['element'] for access like object.property. """

    def __init__(self, json: dict):
        for k, v in json.items():
            setattr(self, k, v)

class Client(OAuthClient):

    __name__ = "Visma"

    class Account:
        def __init__(self, **kwargs):
            self.tenants = [JsonObject(tnt) for tnt in kwargs.get('tenants')]
            self.user_info = JsonObject(kwargs.get('user_info'))
            self.roles = [JsonObject(roles) for roles in kwargs.get('roles')]

        @property
        def first_tenant_id(self):
            """ Return the id of the first available tenant. """
            return getattr(self.tenants[0], 'Id', None)

        def get_tenant_id(self, filters_: dict):
            """
            Get tenant ID from tenant name. Use to use specific tenant.
            
            :param filters_: Dict with parameters to eval. Eg.
                {"DBName": "Name_Of_Database", "TenantName": "Tenant_Test"}.
            :param tenant_name: (optional) Str with name of tenant.
            :param **kwargs: Optional arguments to filter.
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

    def __init__(
        self,
        *,
        url: Union[str, Path],
        username: str,
        pwd: str,
        admin_url: Optional[Union[str, Path]] = None,
        session: Optional[requests.Session] = None,
        tenant_filter: Optional[Dict[str, Any]] = None,
    ) -> None:
        """ Create a conection with visma app using recived parameters.

        Args:
            url (Union[str, Path]): Visma URL.
            username (str): Visma User
            pwd (str): Visma Password
            session (Optional[requests.Session], optional):
                Optional session handler. Defaults to None.
            tenant_filter (Optional[Dict[str, Any]], optional):
                Optional filters to get tenant. Defaults to None.
        """

        super().__init__(
            url=url,
            username=username,
            pwd=pwd,
            session=session
        )

        # dict to filter tenant
        self.tenant_filter = tenant_filter
        
        # base headers
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
        }

        self.authentication = None
        self.account = None
        self.tenant = None

        # auth url
        self.admin_url = admin_url
        if admin_url:
            self.client_admin_url = urlparse(admin_url) 
        else:
            # deprecation warning
            warnings.warn(
                message='You are using old Visma API. Update to new servers.',
                category=DeprecationWarning
            )

            self.client_admin_url = urlparse(urljoin(
                self.client_url.geturl(),
                '/Admin/'
            ))
            self.client_url = urlparse(urljoin(
                self.client_url.geturl(),
                '/WebApi/')
            )

    def refresh_headers(
        self,
        auth_data: Optional[Dict[str, Any]] = None,
        tenant: Optional[Union[int, str]] = None,
        remove_auth: Optional[bool] = False,
        remove_content_type: Optional[bool] = False
    ) -> None:
        if remove_auth:
            self.authentication = None
            self.session.headers.pop("Authorization", None)

        if remove_content_type:
            self.headers.pop("Content-Type", None)
            self.session.headers.pop("Content-Type", None)
        
        if auth_data:
            self.authentication = self.Authentication(**auth_data)

        if tenant:
            self.headers.update({'X-RAET-Tenant-Id': tenant})
            self.session.headers.update({'X-RAET-Tenant-Id': tenant})

        if self.authentication:
            self.headers.update({
                "Authorization": str(self.authentication)
            })
            self.session.headers.update({
                "Authorization": str(self.authentication)
            })

        if "Content-Type" not in self.headers and not remove_content_type:
            self.headers.update({
                "Content-Type": "application/json;charset=UTF-8"
            })
            self.session.headers.update({
                "Content-Type": "application/json;charset=UTF-8"
            })

    @property
    def access_token(self) -> Union[str, None]:
        return getattr(self.authentication, 'access_token', None)
    
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

    def get_account(self, path: str) -> Dict[str, Any]:
        # data prepare
        account_url = urljoin(self.client_admin_url.geturl(), 'account/')
        path_url = urljoin(account_url, path)
        
        return self.get(url=path_url)

    def set_account(self) -> None:
        self.account = self.Account(
            tenants=self.get_account(path='tenants'),
            user_info=self.get_account(path='user-info'),
            roles=self.get_account(path='roles')
        )

    def login(self) -> None:
        
        if self.is_connected:
            return

        # remove content type from headers. Must be not json
        self.refresh_headers(remove_auth=True, remove_content_type=True)

        # data prepare
        # data prepare
        login_url = urljoin(
            self.client_admin_url.geturl(),
            'authentication/login'
        )
        data = {
            "username": self.username,
            "password": b64decode(self.pwd).decode('utf-8'),
            "grant_type": "password"
        }

        # consulting nettime
        json_data = self.post(url=login_url, data=data)

        # self.authentication = self.Authentication(**json_data)
        self.refresh_headers(auth_data=json_data)
        self.refresh_session()

        # update tenant
        self.set_account()
        if self.tenant_filter:
            self.tenant = self.account.get_tenant_id(
                filters_=self.tenant_filter
            )
        else:
            self.tenant = getattr(
                self.account,
                'first_tenant_id',
                None
            )

        self.refresh_headers(tenant=self.tenant)
        self.refresh_session()

    def logout(self) -> None:
        """ Disconnect a client to clean the access_token. """

        if not self.is_connected:
            return

        # data prepare
        logout_url = urljoin(
            self.client_admin_url.geturl(),
            'authentication/logout'
        )

        # disconnect ...
        response = self.post(url=logout_url)

        self.refresh_headers(remove_auth=True, remove_content_type=True)
        self.refresh_session()

    def relogin(self):
        """ Reconnect client cleaning headers and access_token. """

        # logout and login. Will fail if has no token
        logout_result = self.logout()
        login_result = self.login()

    def get_employee_detail(
        self,
        employee: Union[str, int],
        extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        employee_detail = self.get_employees(employee=employee)

        # empty list to iter
        extensions = extensions if extensions else []
        for extension in extensions:
            employee_detail[f'_{extension}'] = self.get_employees(
                employee=employee,
                extension=extension,
                all_pages=True
            ).get('values')

        return employee_detail


    def get_employees(
        self,
        employee: Optional[Union[str, int]] = None,
        extension: Optional[str] = None,
        all_pages: bool = False,
        get_detail: bool = False,
        get_extensions: Optional[List[str]] = None,
        bulk_get: bool = False,
        **kwargs
    ):
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
        path = 'employees{}{}'.format(
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
            num_pages = ceil(
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

        if get_detail and not employee:
            response['values'] = [self.get_employee_detail(
                employee=_employee.get('externalId'),
                extensions=get_extensions
            ) for _employee in response.get('values')]

        if extension:
            response['extension'] = extension

        # return elements
        return response

    def get_addresses(self, address: str = None, extension: str = None, \
            **kwargs):

        # check validity
        if address and extension:
            raise KeyError("No se pueden especificar un address y extension.")
        
        # path prepare
        path = 'addresses{}{}'.format(
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
        path = 'birth-places'

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
        path = 'countries'

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
        path = 'family-members/types'

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
        path = 'journals{}{}'.format(
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
        path = 'leaves{}'.format(
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
        path = 'loans'

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
        path = 'loans'

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
        path = 'pay-elements/individual'

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
        path = 'pay-elements/individual'

        # request.get -> json
        return self.post(path=path, json={"values": values}, **kwargs)

    def get_payments(self, extension: str, **kwargs):

        # path prepare
        path = f'payments/{extension}'

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
        path = f'payrolls/{extension}'

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
        path = 'phases{}'.format(
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
        path = 'phones{}{}'.format(
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
        path = 'scales'

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
        path = 'seizures'

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
        path = 'structures{}'.format(
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
        path = 'sync{}'.format(
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
        path = 'sync{}'.format(
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
        return self.get(path='version')


class AsyncClient(AsyncOAuthClient):

    __name__ = "Visma"

    class Account:
        def __init__(self, **kwargs):
            self.tenants = [JsonObject(tnt) for tnt in kwargs.get('tenants')]
            self.user_info = JsonObject(kwargs.get('user_info'))
            self.roles = [JsonObject(roles) for roles in kwargs.get('roles')]

        @property
        def first_tenant_id(self):
            """ Return the id of the first available tenant. """
            return getattr(self.tenants[0], 'Id', None)

        def get_tenant_id(self, filters_: dict):
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

    def __init__(
        self,
        *,
        url: Union[str, Path],
        username: str,
        pwd: str,
        admin_url: Optional[Union[str, Path]] = None,
        session: Optional[ClientSession] = None,
        tenant_filter: Optional[Dict[str, Any]] = None,
    ) -> None:
        """ Create a conection with visma app using recived parameters.

        Args:
            url (Union[str, Path]): Visma URL.
            username (str): Visma User
            pwd (str): Visma Password
            session (Optional[requests.Session], optional):
                Optional session handler. Defaults to None.
            tenant_filter (Optional[Dict[str, Any]], optional):
                Optional filters to get tenant. Defaults to None.
        """

        super().__init__(
            url=url,
            username=username,
            pwd=pwd,
            session=session
        )

        # dict to filter tenant
        self.tenant_filter = tenant_filter
        
        # base headers
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
        }

        self.authentication = None
        self.account = None
        self.tenant = None

        # auth url
        self.admin_url = admin_url
        if admin_url:
            self.client_admin_url = urlparse(admin_url) 
        else:
            # deprecation warning
            warnings.warn(
                message='You are using old Visma API. Update to new servers.',
                category=DeprecationWarning
            )

            self.client_admin_url = urlparse(urljoin(
                self.client_url.geturl(),
                '/Admin/'
            ))
            self.client_url = urlparse(urljoin(
                self.client_url.geturl(),
                '/WebApi/')
            )

    def refresh_headers(
        self,
        auth_data: Optional[Dict[str, Any]] = None,
        tenant: Optional[Union[int, str]] = None,
        remove_auth: Optional[bool] = False,
        remove_content_type: Optional[bool] = False
    ) -> None:
        if remove_auth:
            self.authentication = None
            self.session.headers.pop("Authorization", None)

        if remove_content_type:
            self.headers.pop("Content-Type", None)
            self.session.headers.pop("Content-Type", None)
        
        if auth_data:
            self.authentication = self.Authentication(**auth_data)

        if tenant:
            self.headers.update({'X-RAET-Tenant-Id': tenant})
            self.session.headers.update({'X-RAET-Tenant-Id': tenant})

        if self.authentication:
            self.headers.update({
                "Authorization": str(self.authentication)
            })
            self.session.headers.update({
                "Authorization": str(self.authentication)
            })

        if "Content-Type" not in self.headers and not remove_content_type:
            self.headers.update({
                "Content-Type": "application/json;charset=UTF-8"
            })
            self.session.headers.update({
                "Content-Type": "application/json;charset=UTF-8"
            })

    @property
    def access_token(self) -> Union[str, None]:
        return getattr(self.authentication, 'access_token', None)
    
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

    @property
    def access_token(self) -> Union[str, None]:
        return getattr(self.authentication, 'access_token', None)
    
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

    async def get_account(self, path: str) -> Dict[str, Any]:
        # data prepare
        account_url = urljoin(self.client_admin_url.geturl(), 'account/')
        path_url = urljoin(account_url, path)
        
        return await self.get(url=path_url)

    async def set_account(self) -> None:
        
        self.account = self.Account(
            tenants=await self.get_account(path='tenants'),
            user_info=await self.get_account(path='user-info'),
            roles=await self.get_account(path='roles')
        )

    async def login(self) -> None:
        
        if self.is_connected:
            return

        # remove content type from headers. Must be not json
        self.refresh_headers(remove_auth=True, remove_content_type=True)

        # data prepare
        login_url = urljoin(
            self.client_admin_url.geturl(),
            'authentication/login'
        )
        data = {
            "username": self.username,
            "password": b64decode(self.pwd).decode('utf-8'),
            "grant_type": "password"
        }
        # consulting visma
        json_data = await self.post(url=login_url, data=data)

        # self.authentication = self.Authentication(**json_data)
        self.refresh_headers(auth_data=json_data)
        self.refresh_session()

        # update tenant
        await self.set_account()
        if self.tenant_filter:
            self.tenant = self.account.get_tenant_id(
                filters_=self.tenant_filter
            )
        else:
            self.tenant = getattr(
                self.account,
                'first_tenant_id',
                None
            )

        self.refresh_headers(tenant=self.tenant)
        self.refresh_session()

    async def logout(self) -> None:
        """ Disconnect a client to clean the access_token. """

        if not self.is_connected:
            return

        # data prepare
        logout_url = urljoin(
            self.client_admin_url.geturl(),
            'authentication/logout'
        )

        # disconnect ...
        response = await self.post(url=logout_url)

        self.refresh_headers(remove_auth=True, remove_content_type=True)
        self.refresh_session()

    async def relogin(self):
        """ Reconnect client cleaning headers and access_token. """

        # logout and login. Will fail if has no token
        logout_result = await self.logout()
        login_result = await self.login()

    async def get_employee_detail(
        self,
        *,
        employee: Union[str, int],
        extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        employee_detail = await self.get_employees(employee=employee)
        if extensions:
            coroutines = [self.get_employees(
                employee=employee,
                extension=extension,
                all_pages=True
            ) for extension in extensions]
            tasks = self.get_async_tasks(*coroutines)
            extensions_detail = await aio_gather(*tasks)

            for ext_detail in extensions_detail:
                ext_name = f'_{ext_detail.get("extension")}'
                employee_detail[ext_name] = ext_detail.get('values', [])

        return employee_detail

    async def get_employees(
        self,
        *,
        employee: Optional[Union[str, int]] = None,
        extension: Optional[str] = None,
        all_pages: bool = False,
        get_detail: bool = False,
        get_extensions: Optional[List[str]] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'employees{}{}'.format(
            f'/{employee}' if employee else '',
            f'/{extension}' if employee and extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "active": kwargs.get("active", None),
            "updatedFrom": kwargs.get("updatedFrom", None),
            "timeout": kwargs.get("timeout", self.defaults.TIME_OUT)
        }

        # request.get -> json
        response = await self.get(path=path, params=params)

        totalCount = response.get('totalCount', 0)
        pageSize = params.get('pageSize')

        # recursive call to get all pages values
        if all_pages and totalCount > pageSize:
            # remove page of params
            params.pop('page', None)
            
            # calculate num of pages
            num_pages = ceil(
                response.get('totalCount') / params.get('pageSize')
            )
            coroutines = [self.get(
                path=path,
                params={**params, 'page': i}
            ) for i in range(2, num_pages + 1)]
            tasks = self.get_async_tasks(*coroutines)
            responses = await aio_gather(*tasks)

            for child_response in responses:
                response['values'].extend(child_response.get('values'))

        if get_detail and not employee:
            coroutines = [self.get_employee_detail(
                employee=_employee.get('externalId'),
                extensions=get_extensions
            ) for _employee in response.get('values')]
            tasks = self.get_async_tasks(*coroutines)
            response['values'] = await aio_gather(*tasks)
            # response['values'] = responses

        if extension:
            response['extension'] = extension

        # return elements
        return response

    async def get_addresses(
        self,
        *,
        address: Optional[str] = None,
        extension: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # check validity
        if address and extension:
            raise KeyError("No se pueden especificar un address y extension.")

        # path prepare
        path = 'addresses{}{}'.format(
            f'/{address}' if address else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
        }

        return await self.get(path=path, params=params)

    async def get_birth_places(self, **kwargs) -> Union[Dict, List]:
        
        # path prepare
        path = 'birth-places'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "countryId": kwargs.get("countryId", None),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_countries(self, **kwargs) -> Union[Dict, List]:
        
        # path prepare
        path = 'countries'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", self.defaults.PAGE_SIZE),
            "pageSize": kwargs.get("pageSize", 5),
            "search": kwargs.get("search", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_family_members(self, **kwargs) -> Union[Dict, List]:
        
        # path prepare
        path = 'family-members/types'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_journals(
        self,
        *,
        journal: Optional[str] = None,
        extension: str = "lines",
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'journals{}{}'.format(
            f'/{journal}' if journal and extension else '',
            f'/{extension}' if journal and extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "dateFrom": kwargs.get(
                "dateFrom",
                self.defaults.DATE_FROM.isoformat()
            ),
            "dateTo": kwargs.get("dateTo", None),
            "processDate": kwargs.get("processDate", None),
            "companyId": kwargs.get("companyId", None),
            "companyName": kwargs.get("companyName", None),
            "account": kwargs.get("account", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)
    
    async def get_leaves(
        self,
        *,
        extension: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'leaves{}'.format(
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get(
                "dateFrom",
                self.defaults.DATE_FROM.isoformat()
            ),
            "typeLeaveId": kwargs.get("typeLeaveId", None),
            "leaveState": kwargs.get("leaveState", None),
            "employeeId": kwargs.get("employeeId", None),
            "dateTo": kwargs.get("dateTo", None),
            "dayType": kwargs.get("dayType", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "search": kwargs.get("search", None),
            "year": kwargs.get("year", None),
            "typeId": kwargs.get("typeId", None),
            "holidayModelId": kwargs.get("holidayModelId", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_loans(self, **kwargs) -> Union[Dict, List]:
        # path prepare
        path = 'loans'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "dateFrom": kwargs.get(
                "dateFrom",
                self.defaults.DATE_FROM.isoformat()
            ),
            "employeeId": kwargs.get("employeeId", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_nationalities(self, **kwargs) -> Union[Dict, List]:
        
        # path prepare
        path = 'loans'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_pay_elements(
        self,
        *,
        employeeExternalId: str,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'pay-elements/individual'

        # parameters prepare
        params = {
            "employeeExternalId": employeeExternalId,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "search": kwargs.get("search", None),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "conceptExternalId": kwargs.get("conceptExternalId", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def post_pay_elements(
        self,
        *,
        values: list,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'pay-elements/individual'

        # request.get -> json
        return await self.post(path=path, json={"values": values}, **kwargs)

    async def get_payments(
        self,
        *,
        extension: str,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = f'payments/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_payrolls(
        self,
        *,
        extension: str,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = f'payrolls/{extension}'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
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
        return await self.get(path=path, params=params)

    async def get_phases(
        self,
        *,
        phase: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'phases{}'.format(
            f'/{phase}' if phase else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "dateFrom": kwargs.get("dateFrom", None),
            "dateTo": kwargs.get("dateTo", None),
            "type": kwargs.get("type", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_phones(
        self,
        *,
        phone: Optional[str] = None,
        extension: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # check validity
        if phone and extension:
            raise KeyError("Cant use `phone` and `extension`.")

        # path prepare
        path = 'phones{}{}'.format(
            f'/{phone}' if phone else '',
            f'/{extension}' if extension else '',
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_scales(
        self,
        *,
        scale: int,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'scales'

        # parameters prepare
        params = {
            "id": scale,
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "coordinates": kwargs.get("coordinates", None),
            "order": kwargs.get("order", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_seizures(
        self,
        *,
        startDate: str,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'seizures'

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "startDate": startDate,
            "employeeId": kwargs.get("employeeId", None),
            "stateId": kwargs.get("stateId", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_structures(
        self,
        *,
        extension: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'structures{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "typeId": kwargs.get("typeId", None),
            "active": kwargs.get("active", None),
            "search": kwargs.get("search", None)
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def get_sync(
        self,
        *,
        extension: Optional[str] = None,
        applicationName: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        
        if not extension and not applicationName:
            raise KeyError("Must specify an `applicationName`")

        # path prepare
        path = 'sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "applicationName": applicationName,
            "parentEntity": kwargs.get("parentEntity", None),
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
            "lastUpdate": kwargs.get("lastUpdate", None),
        }

        # request.get -> json
        return await self.get(path=path, params=params)

    async def post_sync(self, **kwargs) -> Union[Dict, List]:
        raise NotImplementedError("Method not allowed")

    async def get_time_management(
        self,
        *,
        extension: Optional[str] = None,
        **kwargs
    ) -> Union[Dict, List]:
        
        # path prepare
        path = 'sync{}'.format(
            f'/{extension}' if extension else ''
        )

        # parameters prepare
        params = {
            "orderBy": kwargs.get("orderBy", None),
            "page": kwargs.get("page", None),
            "pageSize": kwargs.get("pageSize", self.defaults.PAGE_SIZE),
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
        return await self.get(path=path, params=params)

    async def post_time_management(self, **kwargs) -> Union[Dict, List]:
        raise NotImplementedError("Method not allowed")

    async def get_version(self) -> Union[Dict, List]:
        
        # request.get -> json
        return await self.get(path='version')