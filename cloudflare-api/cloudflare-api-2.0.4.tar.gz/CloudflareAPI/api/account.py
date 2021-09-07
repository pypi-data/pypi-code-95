#!/usr/bin/env python3

from json import dumps as json_dumps
from typing import Any, Dict, List, Optional, Union
from CloudflareAPI.core import CFBase
from CloudflareAPI.dataclass.account import AccountData, AccountSettings
from CloudflareAPI.exceptions import CFError


class Account(CFBase):
    def __init__(self, account_id: Optional[str] = None) -> None:
        self.request = self.get_request("accounts")
        if account_id is not None:
            self.id = account_id
        else:
            self.id = self.get_id()

    def __get_object(self, account: Dict[str, Any]) -> AccountData:
        return AccountData(
            id=account["id"],
            name=account["name"],
            settings=AccountSettings(
                enforce_twofactor=account["settings"]["enforce_twofactor"],
                access_approval_expiry=account["settings"]["access_approval_expiry"],
                use_account_custom_ns_by_default=account["settings"][
                    "use_account_custom_ns_by_default"
                ],
            ),
            created_on=account["created_on"],
        )

    def list(
        self, page: int = 1, per_page: int = 20, order: str = ""
    ) -> List[AccountData]:
        if order and (order != "asc" and order != "desc"):
            raise CFError("Invalid order parameter. Only 'asc' or 'desc' allowed.")
        params = {"page": page, "per_page": per_page, "order": order}
        params = self.parse_params(params)
        data = self.request.get(params=params)
        return [self.__get_object(account) for account in data]

    def get_id(self) -> str:
        if "id" in self.props() and self.id is not None:
            return self.id
        alist = self.list()
        if len(alist) == 1:
            self.id = alist[0].id
            return alist[0].id
        if len(alist) > 1:
            print("Please use one of the account id as parameter in Cloudflare class")
            print("Accounts: ")
            for account in self.list():
                print("   ", account.name, ":", account.id)
            exit()
        raise CFError("No account found")

    def details(
        self, minimal: bool = True, formated: bool = False
    ) -> Union[str, AccountData]:
        account = self.request.get(self.id)
        if minimal and "legacy_flags" in account.keys():
            del account["legacy_flags"]
        if formated:
            return json_dumps(account, indent=2)
        return self.__get_object(account)

    # This method is not accessable due to default token permissions
    def rename(self, account_id: str, name: str) -> AccountData:
        url = self.build_url(account_id)
        account = self.request.put(url, json=dict(name=name))
        return self.__get_object(account)
