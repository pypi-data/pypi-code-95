from __future__ import annotations
from pydantic import validate_arguments
from typing import Optional, Union, Dict, List

import datetime as dt
import json

try:
    from ._base import APIKeyClient
    from ._schemas import specmanager as sm_schema
except ImportError:
    from _base import APIKeyClient
    from _schemas import specmanager as sm_schema


__specmanager__ = "5.0.0r17013"


class EmployeeType:
    OWN: str = "own"
    ENCAE: str = "encae"
    CONTRACTOR: str = "contractor"


class Client(APIKeyClient):

    __name__ = "SPECManager"

    def get_clockings(
        self,
        type_: str,
        from_: Union[dt.datetime, str],
        to_: Union[dt.datetime, str],
        fromHistory: Optional[bool] = False,
        employeeDetail: Optional[bool] = False,
        employeeData: Optional[List[Union[int, str]]] = [],
        pageSize: Optional[int] = 20,
        page: Optional[int] = 1,
        **kwargs
    ) -> Union[Dict, List]:
        """ Get clockings from SM API with self.get() passing type_ and 
            parameters recived.

        Args:
            type_ (str): Employee type. Check EmployeeType class for options.
            from_ (Union[dt.datetime, str]):
                Datetime to apply as start filter of clockings.
            to_ (Union[dt.datetime, str]):
                Datetime to apply as end filter of clockings.
            fromHistory (Optional[bool], optional):
                True or False to get clockings from HISTORICO.
                Defaults to False.
            employeeDetail (Optional[bool], optional):
                True to get serialized employee.
                Defaults to False.
            employeeData (Optional[List[Union[int, str]]], optional):
                List of Optional Data of employee to get from SM.
                Defaults to [].
            pageSize (Optional[int], optional):
                Max results per page.
                Defaults to 20.
            page (Optional[int], optional):
                Page number.
                Defaults to 1.

        Returns:
            Union[Dict, List]: List of match clockings
        """
        
        # path prepare
        path = f'clockings/{type_}'

        # datetime to str
        if isinstance(from_, dt.datetime):
            from_ = from_.strftime("%Y%m%d%H%M%S")

        if isinstance(to_, dt.datetime):
            to_ = to_.strftime("%Y%m%d%H%M%S")

        # parameters prepare
        params = {
            "from": from_,
            "to": to_,
            "fromHistory": fromHistory,
            "employeeDetail": employeeDetail,
            "pageSize": pageSize,
            "page": page
        }

        # append data
        if employeeData:
            params["employeeData"] = ','.join([str(e) for e in employeeData])

        # request.get -> json
        return self.get(path=path, params=params, **kwargs)
        

    def get_clockings_contractor(
        self,
        from_: Union[dt.datetime, str],
        to_: Union[dt.datetime, str],
        fromHistory: Optional[bool] = False,
        employeeDetail: Optional[bool] = False,
        employeeData: Optional[List[Union[int, str]]] = [],
        pageSize: Optional[int] = 20,
        page: Optional[int] = 1,
        **kwargs
    ) -> Union[Dict, List]:
        """ Get contractor clockings from SM API with self.get_clockings() and 
            recived parameters.

        Args:
            from_ (Union[dt.datetime, str]):
                Datetime to apply as start filter of clockings.
            to_ (Union[dt.datetime, str]):
                Datetime to apply as end filter of clockings.
            fromHistory (Optional[bool], optional):
                True or False to get clockings from HISTORICO.
                Defaults to False.
            employeeDetail (Optional[bool], optional):
                True to get serialized employee.
                Defaults to False.
            employeeData (Optional[List[Union[int, str]]], optional):
                List of Optional Data of employee to get from SM.
                Defaults to [].
            pageSize (Optional[int], optional):
                Max results per page.
                Defaults to 20.
            page (Optional[int], optional):
                Page number.
                Defaults to 1.

        Returns:
            Union[Dict, List]: List of match clockings
        """

        # parameters prepare
        params = {
            "type_": EmployeeType.CONTRACTOR,
            "from_": from_,
            "to_": to_,
            "fromHistory": fromHistory,
            "employeeDetail": employeeDetail,
            "pageSize": pageSize,
            "page": page,
            "employeeData": employeeData
        }

        # request.get -> json
        return self.get_clockings(**params, **kwargs)

    @validate_arguments
    def post_employee(
        self,
        type_: str,
        employee: sm_schema.Employee,
        **kwargs
    ) -> dict:
        """ Send employee to SM API with self.post()

        Args:
            type_ (str):
                Employee type enpoint to add in POST /employees/{type_} SM API.
                Check EmployeeType class for options.
            employee (sm_schema.Employee):
                Employee schema (spec_utils._schemas.specmanager.Employee).
                Can be Employee instance or dict with values. 

        Returns:
            dict: Import result
        """

        # path prepare
        path = f'employees/{type_}'

        # to dict without unset
        json_employee = employee.json(
            exclude=employee.Meta.nondefault,
            exclude_unset=True
        )
        dict_employee = json.loads(json_employee)

        # update nondefault fields
        for nondef in employee.Meta.nondefault:
            _method = getattr(employee, f'get_{nondef}')
            if callable(_method):
                dict_employee.update(_method())

        # request.get -> json
        return self.post(path=path, params=dict_employee, **kwargs)

    @validate_arguments
    def post_employees(
        self,
        type_: str,
        employees: List[sm_schema.Employee],
        **kwargs
    ) -> List[dict]:
        """ Send employees to SM API with self.post_employee()

        Args:
            type_ (str):
                Employee type enpoint to add in POST /employees/{type_} SM API.
                Check EmployeeType class for options.
            employees (List[sm_schema.Employee]): List of Employee schema.

        Returns:
            List[dict]: List of import result
        """

        # empty response
        resp = []
        
        for employee in employees:
            # rewrite if OK, raise if error
            resp.append(self.post_employee(
                type_=type_,
                employee=employee,
                **kwargs
            ))

        # return last response (or raise before)
        return resp

