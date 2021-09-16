from ._api_type import APIType
from ._content_provider import DataProvider
from ._content_type import ContentType
from .esg._esg_data_provider import esg_data_provider
from .historical_pricing._hp_data_provider import (
    hp_events_data_provider,
    hp_summaries_data_provider,
)
from .ipa._curves._curves_data_provider import curves_data_provider
from .ipa._surfaces._surfaces_data_provider import surfaces_data_provider
from .ipa.contracts._contracts_data_provider import contracts_data_provider
from ..pricing._pricing_content_provider import pricing_data_provider
from ..tools._common import urljoin

data_provider_by_content_type = {
    ContentType.FORWARD_CURVE: curves_data_provider,
    ContentType.ZC_CURVES: curves_data_provider,
    ContentType.ZC_CURVE_DEFINITIONS: curves_data_provider,
    ContentType.SURFACES: surfaces_data_provider,
    ContentType.CONTRACTS: contracts_data_provider,
    ContentType.HISTORICAL_PRICING_EVENTS: hp_events_data_provider,
    ContentType.HISTORICAL_PRICING_INTERDAY_SUMMARIES: hp_summaries_data_provider,
    ContentType.HISTORICAL_PRICING_INTRADAY_SUMMARIES: hp_summaries_data_provider,
    ContentType.ESG_STANDARD_SCORES: esg_data_provider,
    ContentType.ESG_STANDARD_MEASURES: esg_data_provider,
    ContentType.ESG_FULL_MEASURES: esg_data_provider,
    ContentType.ESG_FULL_SCORES: esg_data_provider,
    ContentType.ESG_BASIC_OVERVIEW: esg_data_provider,
    ContentType.ESG_UNIVERSE: esg_data_provider,
    ContentType.PRICING: pricing_data_provider,
}

api_config_key_by_api_type = {
    APIType.CURVES_AND_SURFACES: "apis.data.quantitative-analytics-curves-and-surfaces",
    APIType.FINANCIAL_CONTRACTS: "apis.data.quantitative-analytics-financial-contracts",
    APIType.HISTORICAL_PRICING: "apis.data.historical-pricing",
    APIType.ESG: "apis.data.environmental-social-governance",
    APIType.PRICING: "apis.data.pricing",
}

api_type_by_content_type = {
    ContentType.FORWARD_CURVE: APIType.CURVES_AND_SURFACES,
    ContentType.ZC_CURVES: APIType.CURVES_AND_SURFACES,
    ContentType.ZC_CURVE_DEFINITIONS: APIType.CURVES_AND_SURFACES,
    ContentType.SURFACES: APIType.CURVES_AND_SURFACES,
    ContentType.CONTRACTS: APIType.FINANCIAL_CONTRACTS,
    ContentType.HISTORICAL_PRICING_EVENTS: APIType.HISTORICAL_PRICING,
    ContentType.HISTORICAL_PRICING_INTERDAY_SUMMARIES: APIType.HISTORICAL_PRICING,
    ContentType.HISTORICAL_PRICING_INTRADAY_SUMMARIES: APIType.HISTORICAL_PRICING,
    ContentType.ESG_STANDARD_SCORES: APIType.ESG,
    ContentType.ESG_STANDARD_MEASURES: APIType.ESG,
    ContentType.ESG_FULL_MEASURES: APIType.ESG,
    ContentType.ESG_FULL_SCORES: APIType.ESG,
    ContentType.ESG_BASIC_OVERVIEW: APIType.ESG,
    ContentType.ESG_UNIVERSE: APIType.ESG,
    ContentType.PRICING: APIType.PRICING,
}

url_config_key_by_content_type = {
    ContentType.FORWARD_CURVE: "endpoints.forward-curves",
    ContentType.ZC_CURVES: "endpoints.zc-curves",
    ContentType.ZC_CURVE_DEFINITIONS: "endpoints.zc-curve-definitions",
    ContentType.SURFACES: "endpoints.surfaces",
    ContentType.CONTRACTS: "endpoints.financial-contracts",
    ContentType.HISTORICAL_PRICING_EVENTS: "endpoints.events",
    ContentType.HISTORICAL_PRICING_INTERDAY_SUMMARIES: "endpoints.interday-summaries",
    ContentType.HISTORICAL_PRICING_INTRADAY_SUMMARIES: "endpoints.intraday-summaries",
    ContentType.ESG_STANDARD_SCORES: "endpoints.scores-standard",
    ContentType.ESG_STANDARD_MEASURES: "endpoints.measures-standard",
    ContentType.ESG_FULL_MEASURES: "endpoints.measures-full",
    ContentType.ESG_FULL_SCORES: "endpoints.scores-full",
    ContentType.ESG_BASIC_OVERVIEW: "endpoints.basic",
    ContentType.ESG_UNIVERSE: "endpoints.universe",
    ContentType.PRICING: "endpoints.snapshots",
}


def _get_api_config_key(content_type: ContentType) -> str:
    api_type = api_type_by_content_type.get(content_type)
    api_config_key = api_config_key_by_api_type.get(api_type)
    return api_config_key


def _get_url_config_key(content_type: ContentType) -> str:
    return url_config_key_by_content_type.get(content_type)


def get_api_config(content_type: ContentType):
    from .. import configure

    api_config_key = _get_api_config_key(content_type)
    api_config = configure.get(api_config_key)

    if api_config is None:
        raise AttributeError(f"Cannot find api_key, content_type={content_type}.")

    return api_config


def get_base_url(content_type: ContentType):
    """
    Parameters
    ----------
    content_type: ContentType

    Returns
    -------
    string
    """
    api_config = get_api_config(content_type)
    base_url = api_config.get("url")
    return base_url


def get_url(content_type: ContentType, request_mode=None):
    """
    Parameters
    ----------
    content_type: ContentType
    request_mode: str in ["sync", "async"]

    Returns
    -------
    string
    """
    api_config = get_api_config(content_type)
    url_config_key = _get_url_config_key(content_type)

    if request_mode is None:
        request_mode = "sync"

    if request_mode not in ["sync", "async"]:
        raise AttributeError(f"Request mode not in ['sync', 'async'].")

    # Test if url_content is a json with sync/async endpoints
    content_url = api_config.get(".".join([url_config_key, request_mode]))
    if content_url is None:
        # then test if content_url is a single endpoint
        content_url = api_config.get(url_config_key)

    if content_url is None:
        raise AttributeError(f"Cannot find content_url, content_type={content_type}.")

    base_url = api_config.get("url")
    url = urljoin(base_url, content_url)

    return url


def make_provider(content_type, **_) -> DataProvider:
    """
    Parameters
    ----------
    content_type: ContentType

    Returns
    -------
    DataProvider
    """
    data_provider = data_provider_by_content_type.get(content_type)

    if data_provider is None:
        raise AttributeError(
            f"Cannot get data provider by content type: {content_type}."
        )

    return data_provider
