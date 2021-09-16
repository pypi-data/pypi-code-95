import datetime as dt
from typing import Union

from pydantic import BaseModel, conlist, validator


class CustomerModel(BaseModel):
    """Type of business of the investment firm of counterparty (e.g.: regional_govt)"""
    type: str


class IssuerModel(BaseModel):
    """Type of business of the issuer of the collateral (e.g. central_bank)"""
    type: str


class RepoLegModel(BaseModel):
    """Common attributes to both RepoCashLegModel and RepoAssetLegModel"""
    id: str
    date: str
    currency_code: str
    end_date: str
    start_date: str
    trade_date: str
    customer: CustomerModel
    sft_type: str = 'rev_repo'


class RepoCashLegModel(RepoLegModel):
    """Attributes specific to the cash leg of a repo"""
    balance: int
    movement: str = 'cash'
    type: str = 'cash'


class RepoAssetLegModel(RepoLegModel):
    """Attributes specific to the asset leg of a repo"""
    mtm_dirty: int
    movement: str = 'asset'
    type: str = 'bond'
    issuer: IssuerModel


class RepoModel(BaseModel):
    """Model to load input json data for validation and to easily access data through object subscription"""
    name: str
    date: str
    data: conlist(Union[RepoCashLegModel, RepoAssetLegModel], min_items=2, max_items=2)
    
    @validator('date')
    def set_date_as_datetime_object(cls, v):
        try:
            v = dt.datetime.fromisoformat(v[:-1])
        except Exception as error:
            raise ValueError(repr(error))
        return v

    @validator('data')
    def set_leg_dates_as_datetime_objects(cls, v):
        try:
            for leg in v:
                leg.start_date = dt.datetime.fromisoformat(leg.start_date[:-1])
                leg.end_date = dt.datetime.fromisoformat(leg.end_date[:-1])
                leg.trade_date = dt.datetime.fromisoformat(leg.trade_date[:-1])
                leg.date = dt.datetime.fromisoformat(leg.date[:-1])
        except Exception as error:
            raise ValueError(repr(error))
        return v

    @validator('data')
    def check_leg_start_dates_are_identical(cls, v):
        if v[0].start_date != v[1].start_date:
            raise ValueError('Start dates between both legs must match.')
        return v

    @validator('data')
    def check_leg_end_dates_are_identical(cls, v):
        if v[0].end_date != v[1].end_date:
            raise ValueError('End dates between both legs must match.')
        return v

    @validator('data')
    def check_leg_trade_dates_are_identical(cls, v):
        if v[0].trade_date != v[1].trade_date:
            raise ValueError('Trade dates between both legs must match.')
        return v

    @validator('data')
    def check_dates_are_in_correct_chronological_order(cls, v):
        for leg in v:
            if not leg.start_date <= leg.trade_date <= leg.end_date:
                raise ValueError('Start date must be before trade date, which itself must be before end date.')
        return v
