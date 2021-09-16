import json

from suade_reverse_repo.core.repo.reverse_repo_leg import ReverseRepoLeg
from suade_reverse_repo.models.repo_transaction import RepoModel


class ReverseRepoTransaction:
    """
    A class used to represent a reverse repo transaction

    Attributes
    ----------
    cash_leg : RepoCashLegModel
        Pydantic model containing data on id, date, currency_code, start_date, trade_date, end_date, customer, sft_type,
        balance, movement, type, and issuer.

    asset_leg : RepoCashLegModel
        Pydantic model containing data on id, date, currency_code, start_date, trade_date, end_date, customer, sft_type,
        balance, movement, type, and issuer.

    Methods
    ----------
    return_ktcd_calculation_json : str
        Collates and returns the KTCD result and its components in JSON format


    """
    def __init__(self, transaction_json):
        # load json data into pydantic model for data validation and to easily access data through object subscription
        self._transaction_data = RepoModel.parse_obj(transaction_json)

        # separate cash leg and asset leg data into their own objects to calculate their counterparty risk from their
        # own perspective
        self.cash_leg = ReverseRepoLeg(investment_firm_data=self._transaction_data.data[0],
                                       counterparty_data=self._transaction_data.data[1],
                                       leg='cash')
        self.asset_leg = ReverseRepoLeg(investment_firm_data=self._transaction_data.data[1],
                                        counterparty_data=self._transaction_data.data[0],
                                        leg='asset')

    def return_ktcd_calculation_json(self) -> str:
        """Collates and returns the KTCD result and its components in JSON format"""
        cash_leg_dict = {'alpha': self.cash_leg.alpha,
                         'replacement_cost': self.cash_leg.replacement_cost,
                         'collateral': self.cash_leg.collateral,
                         'exposure_value': self.cash_leg.exposure_value,
                         'risk_factor': self.cash_leg.risk_factor,
                         'credit_valuation_adjustment': self.cash_leg.credit_valuation_adjustment,
                         'k_tcd': self.cash_leg.k_tcd}

        asset_leg_dict = {'alpha': self.asset_leg.alpha,
                          'replacement_cost': self.asset_leg.replacement_cost,
                          'collateral': self.asset_leg.collateral,
                          'exposure_value': self.asset_leg.exposure_value,
                          'risk_factor': self.asset_leg.risk_factor,
                          'credit_valuation_adjustment': self.asset_leg.credit_valuation_adjustment,
                          'k_tcd': self.asset_leg.k_tcd}

        return json.dumps({'cash_leg': cash_leg_dict, 'asset_leg': asset_leg_dict})
