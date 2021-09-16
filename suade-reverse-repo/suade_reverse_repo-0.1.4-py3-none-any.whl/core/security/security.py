import pandas as pd
import datetime as dt
from pathlib import Path
from suade_reverse_repo.core.security.ifr_asset_type import IFRAssetType

volatility_adjustment_df = pd.read_csv(Path(__file__).with_name('volatility_adjustment_table.csv'),
                                       keep_default_na=False)


class Security:
    """
    A class used to represent a Security that is used as collateral within a repo/reverse-repo transaction

    Attributes
    ----------
    value : int
        CMV of the security

    replacement_cost: int
        CMV of the security adjusted upwards by the volatility adjustment factor. Used for replacement value
        in the K-TCD calculation in repo/reverse-repo transaction

    issuer_type: str
        the designated financial or legal entity category this person or legal entity falls under (e.g.: central_bank)

    asset_type : str
        the type of the security as set out in the FIRE data standard (e.g.: bond, commercial_paper)

    ifr_asset_type : str
        the type of the security as set out in the IFR collateral asset classes (Table 4, Article 30, Section 1 in IFR
        (Trading counterparty default))

    trade_date: dt.datetime object
        date at which the security traded between counterparties

    maturity: dt.datetime object
        date at which the security matures

    Properties
    ----------
    is_issuer_type_gov: str
        whether the issuer_type of the security is a central bank or a central government

    time_to_maturity: dt.datetime object
        time until the security matures

    vol_adjustment: float
        volatility adjustment for collateral value in both bilateral and cleared transactions (Table 4, Article 30,
        Section 1 in IFR (Trading counterparty default))

    collateral_value: float
        CMV of the security adjusted downwards by the volatility adjustment factor. Used for value of collateral in
        K-TCD calculation in repo/reverse-repo transaction

    """

    def __init__(self, value: int, asset_type: str, maturity: dt.datetime, trade_date: dt.datetime, issuer_type: str):
        self.value = value
        self.issuer_type = issuer_type
        self.maturity = maturity
        self.trade_date = trade_date
        self.ifr_asset_type = IFRAssetType[asset_type].value

    @property
    def is_issuer_type_gov(self) -> str:
        """
        Required for looking up volatility adjustment rate in vol_adjustment property.
        Return 'Y' if issuer_type of security is central bank or central government, 'N' otherwise.
        """
        # TO-DO: use enum
        if self.issuer_type in ['central_bank', 'central_govt', 'sovereign']:
            return 'Y'
        else:
            return 'N'

    @property
    def time_to_maturity(self) -> str:
        """
        Required for looking up volatility adjustment rate in vol_adjustment property.
        Return time to maturity as difference between trade_date date and maturity of the security.

        """
        if self.ifr_asset_type not in ['debt_sec', 'securitisation_position']:
            # time to maturity only valid for debt securities and securitisation positions as others have no maturity
            return 'n/a'
        elif (self.maturity - self.trade_date).days <= 365:
            return '< 1 year'
        elif (self.maturity - self.trade_date).days > 365 * 5:
            return '> 5 years'
        else:
            return '> 1 year < 5 years'

    @property
    def volatility_adjustment(self) -> float:
        """Required for calculation of adjusted security value when used as collateral within reverse repo K-TCD calculation.

        Volatility adjustment depends on is_issuer_type_gov, ifr_asset_type, and maturity.

        Adjustments are based on Table 4, Article 30, Section 1 in IFR (Trading counterparty default)
        """

        return volatility_adjustment_df.loc[(volatility_adjustment_df['gov'] == self.is_issuer_type_gov) &
                                            (volatility_adjustment_df['asset_type'] == self.ifr_asset_type) &
                                            (volatility_adjustment_df['maturity'] == self.time_to_maturity)] \
            ['vol_adjustment'].values[0]

    @property
    def collateral_value(self) -> float:
        """CMV of the security adjusted downwards by the volatility adjustment factor. Used for value of collateral in
        K-TCD calculation in repo/reverse-repo transaction"""

        return (1 - self.volatility_adjustment) * self.value
