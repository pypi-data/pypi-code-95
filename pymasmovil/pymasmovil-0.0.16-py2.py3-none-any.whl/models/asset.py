from pymasmovil.client import Client
from pymasmovil.models.contract import Contract
from pymasmovil.errors.exceptions import TariffChangeRequiredParamsError, UnknownMMError


class Asset(Contract):
    _route = "/v2/assets"

    maxNumTariff = ""
    numTariff = ""
    assetType = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def get(cls, session, asset_id):
        contract = super().get(session, asset_id)

        return cls(**contract["asset"])

    @classmethod
    def get_by_phone(cls, session, phone):
        """
        Retrieve the asset associated to a given phone number from the MM sytem.

        :param:
            phone (str): Phone number of the contract we expect
        :return: dict containing the asset from the MM response
        """
        params = {"rowsPerPage": 1, "actualPage": 1, "phone": phone}

        response = Client(session).get(cls._route, **params)

        return cls(**response["rows"][0])

    @classmethod
    def update_product(
        cls,
        session,
        asset_id,
        transaction_id="",
        product_id="",
        execute_date="",
        additional_bonds=[],
        bonds_to_remove=[],
        promotions=[],
    ):
        """
        Modify asset request:
            - change tariff
            - add one-shot bonds

        :param:
            asset_id (str): MM Asset ID
            transaction_id (str): Unique and correlative 18-length numeric code
            productId (str): ID from the new tariff we want to apply
                            [only for change tariff]
            execute_date (str): request date [only for change tariff]
            additional_bonds (list): additional bonds to add
            bonds_to_remove (list): additional bonds to delete
            promotions (list): promotions to add
        :return: modified asset
        """

        route = "{}/{}/change-asset".format(cls._route.replace("v2", "v1"), asset_id)

        cls._check_required_params(
            asset_id, transaction_id, product_id, execute_date, additional_bonds
        )

        active_change = cls._build_active_change(
            transaction_id, product_id, execute_date, additional_bonds,
            bonds_to_remove, promotions
        )
        response = Client(session).patch(route, (), active_change)

        if response == "Petición aceptada":
            return response
        else:
            raise UnknownMMError(response)

    def _check_required_params(
        asset_id, transaction_id, product_id, execute_date, additional_bonds
    ):

        required_params_dct = {"asset_id": asset_id, "transaction_id": transaction_id}
        if product_id:
            update_type = "tariff change"
            required_params_dct.update(
                {
                    "product_id": product_id,
                    "execute_date": execute_date,
                }
            )
        else:
            update_type = "one shot additional bond"
            required_params_dct.update(
                {
                    "additional_bonds": additional_bonds,
                }
            )

        required_params = set(required_params_dct.keys())
        present_params = set(filter(required_params_dct.get, required_params))
        missing_params = required_params - present_params

        if len(list(missing_params)) != 0:
            raise TariffChangeRequiredParamsError(update_type, sorted(missing_params))

    def _build_active_change(transaction_id, product_id, execute_date,
                             additional_bonds, bonds_to_remove, promotions):
        return {
            "transactionId": transaction_id,
            "assetInfo": {
                "executeDate": execute_date,
                "productId": product_id,
                "additionalBonds": additional_bonds,
                "removeBonds": [{"assetId": bond_id} for bond_id in bonds_to_remove],
                "promotions": promotions,
            }
        }
