from pymasmovil.client import Client
from pymasmovil.models.order_item import OrderItem
from pymasmovil.models.asset import Asset
from pymasmovil.errors.exceptions import (AccountRequiredParamsError,
                                          OrderItemNotFoundByICC)


class Account:
    _v1_route = "/v1/accounts"
    _v2_route = "/v2/accounts"

    town = ""
    surname = ""
    stair = ""
    roadType = ""
    roadNumber = ""
    roadName = ""
    region = ""
    province = ""
    postalCode = ""
    phone = ""
    name = ""
    id = ""
    flat = ""
    email = ""
    door = ""
    documentType = ""
    documentNumber = ""
    corporateName = ""
    buildingPortal = ""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(Account, key):
                setattr(self, key, value)

    @classmethod
    def get(cls, session, account_id):
        """
        Returns an account instance obtained by id.

        :param id:
        :return: Account:
        """

        account_response = Client(session).get(
            route="{}/{}".format(cls._v1_route, account_id)
        )

        return cls(**account_response)

    @classmethod
    def get_by_NIF(cls, session, NIF):
        """
        Returns an account instance searched by its NIF number.

        :param NIF: Document ID
        :return: Account
        """

        params = {"rowsPerPage": 1, "actualPage": 1, "documentNumber": NIF}

        response = Client(session).get(route=cls._v2_route, **params)

        return cls(**response["rows"][0])

    @classmethod
    def create(cls, session, **new_account):
        """
        Creates an account instance.

        :param **new_account:
        :return:
        """

        cls._check_required_attributes(new_account)

        new_account_id = Client(session).post(cls._v2_route, (), new_account)

        return cls(id=new_account_id, **new_account)

    def get_asset_by_phone(self, session, phone):
        return Asset(**self._get_contract_by_phone("assets", session, phone))

    def get_order_item_by_phone(self, session, phone):
        return OrderItem(**self._get_contract_by_phone("order-items", session, phone))

    def get_order_item_by_ICC(self, session, ICC):
        """
        Retrieve the order_item associated to a given account with a given ICC,
        from the MM sytem.

        :param: session: MM login session instance,
                ICC: ICC number of the order-item we need
        :return: OrderItem object with corresponding ICC
        """
        params = {"rowsPerPage": 30, "actualPage": 1}

        response = Client(session).get(
            "{}/{}/order-items".format(self._v1_route, self.id), **params
        )
        order_item_list = response["rows"]

        order_item = [order_item for order_item in order_item_list
                      if order_item.get("simAttributes").get("ICCID") == str(ICC)]

        if order_item:
            # There can be just one order-item with a given ICC.
            # The MM system does not accept a repeated ICC, so it is a unique identifier.
            return OrderItem(**order_item[0])
        else:
            raise OrderItemNotFoundByICC(ICC, self.id)

    def _get_contract_by_phone(self, entity, session, phone):
        """
        Retrieve the order_item/asset associated to a given account and filter one
        corresponding to a given phone number, from the MM sytem.

        :param: entity: string representing which object we want (order-items or asset)
                session: MM login session instance,
                phone: Phone number of the contract we expect
        :return: dict containing the object from the MM response
        """
        params = {"rowsPerPage": 1, "actualPage": 1, "phone": phone}

        response = Client(session).get(
            "{}/{}/{}".format(self._v1_route, self.id, entity), **params
        )

        return response["rows"][0]

    def _check_required_attributes(new_account):
        required_attributes = [
            "name",
            "surname",
            "documentNumber",
            "documentType",
            "email",
            "phone",
            "postalCode",
            "province",
            "region",
            "roadName",
            "roadNumber",
            "roadType",
            "town",
        ]

        if new_account.get("documentType") == "1":
            # CIF. Organization client
            required_attributes.append("corporateName")

        account_filled_attributes = set(filter(new_account.get, new_account.keys()))

        missing_attributes = set(required_attributes) - account_filled_attributes

        if len(missing_attributes) != 0:
            raise AccountRequiredParamsError(sorted(missing_attributes))
