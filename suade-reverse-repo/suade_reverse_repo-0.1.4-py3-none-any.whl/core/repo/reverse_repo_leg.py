from typing import Union
from suade_reverse_repo.core.repo.risk_factors import RiskFactors
from suade_reverse_repo.core.security.security import Security


from suade_reverse_repo.models.repo_transaction import RepoCashLegModel, RepoAssetLegModel


class ReverseRepoLeg:
    """
    A class used to represent a leg of a reverse repo transaction

    Attributes
    ----------
    leg : str
        Whether it is the cash leg or asset leg

    investment_firm_data: RepoCashLegModel or RepoAssetLegModel
        Pydantic model containing data on id, date, currency_code, start_date, trade_date, end_date, customer, sft_type,
        balance, movement, type, mtm_dirty, and security issuer.

    counterparty_data: RepoCashLegModel or RepoAssetLegModel
        Pydantic model containing data on id, date, currency_code, start_date, trade_date, end_date, customer, sft_type,
        balance, movement, type, mtm_dirty, and security issuer.

    alpha: float
        factor in the calculation of K-TCD, fixed to 1.2 by the IFR

    credit_valuation_adjustment: float
        factor in the calculation of K-TCD, set to 1 in cases of Securities Financing Transactions by IFR (attribute is
        float as it could be 1.5 in other circumstances)

    Properties
    ----------
    risk_factor: float
        factor in the calculation of K-TCD which depends on the business type of the counterparty

    replacement_cost: float
        factor in the calculation of K-TCD equal to +/- balance attribute in either investment_firm_data or
        counterparty_data depending on whether money is lent or borrowed

    collateral_value: float
        factor in the calculation of K-TCD which depends on the volatility of the underlying security. Calculated within
        the Security class.

    exposure_value: float
        factor in the calculation of K-TCD equal to max(0, replacement_cost - collateral)

    k_tcd: float
        calculation of counterparty risk. Defined in IFR as alpha * exposure_value * risk_factor *
        credit_valuation_adjustment

    """
    def __init__(self, leg: str, investment_firm_data: Union[RepoCashLegModel, RepoAssetLegModel], counterparty_data):
        self.leg = leg
        self.investment_firm_data = investment_firm_data
        self.counterparty_data = counterparty_data
        self.alpha = 1.2  # Used for calculation of K-TCD, the number is fixed by the IFR
        self.credit_valuation_adjustment = 1  # Used for calculation of K-TCD, = 1 for all SFT (Article 32, Chapter 4
        # in IFR)

    @property
    def risk_factor(self) -> float:
        """
        Used in the calculation of K-TCD

        Risk factor for counterparties that are central governments, central banks, public sector entities, credit
        institutions and investment firms set to 1.6% and 8% for all others

        Code looks up risk factor for associated counterparty customer type using an Enum class
        """
        return RiskFactors[self.counterparty_data.customer.type].value

    @property
    def replacement_cost(self):
        """
        Used in the calculation of K-TCD

        For repurchase transactions and securities or commodities lending or borrowing transactions, RC is determined
        as the amount of cash lent or borrowed; cash lent by the investment firm is to be treated as a positive
        amount and cash borrowed by the investment firm is to be treated as a negative amount.
        """
        if self.leg == 'cash':
            return -1 * self.investment_firm_data.balance
        else:
            return self.counterparty_data.balance

    @property
    def collateral(self) -> float:
        """
        Used in the calculation of K-TCD

        Calculated as the sum of the CMV of the security leg and the net amount of collateral posted or received by
        the investment firm.
        """
        if self.leg == 'cash':
            return Security(
                value=self.counterparty_data.mtm_dirty,
                asset_type=self.counterparty_data.type,
                maturity=self.counterparty_data.end_date,
                trade_date=self.counterparty_data.trade_date,
                issuer_type=self.counterparty_data.issuer.type
            ).collateral_value
        else:
            return Security(
                value=self.investment_firm_data.mtm_dirty,
                asset_type=self.investment_firm_data.type,
                maturity=self.investment_firm_data.end_date,
                trade_date=self.investment_firm_data.trade_date,
                issuer_type=self.investment_firm_data.issuer.type
            ).collateral_value

    @property
    def exposure_value(self) -> float:
        """
        Used in the calculation of K-TCD
        """
        return max(0, self.replacement_cost - self.collateral)

    @property
    def k_tcd(self) -> float:
        return self.alpha * self.exposure_value * self.risk_factor * self.credit_valuation_adjustment
