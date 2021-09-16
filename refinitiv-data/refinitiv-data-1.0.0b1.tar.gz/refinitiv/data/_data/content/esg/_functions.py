from .._content_type import ContentType


def _get_esg(content_type, **kwargs):
    from .._content_provider_factory import make_provider, get_url
    from .._content_provider import get_valid_session

    session = get_valid_session(kwargs.get("session"))
    provider = make_provider(content_type)
    response = provider.get_data(session, get_url(content_type), **kwargs)
    return response.data.df


def get_esg_universe():
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_universe()

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(ContentType.ESG_UNIVERSE)


def get_esg_basic_overview(universe):
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_basic_overview(universe='IBM.N')

    Parameters
    ----------
    universe: str
        Requested universe

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(
        ContentType.ESG_BASIC_OVERVIEW,
        universe=universe,
    )


def get_esg_standard_scores(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_standard_scores(universe='5000002406', start=0, end=-2)

    Parameters
    ----------
    universe: str
        Requested universe

    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(
        ContentType.ESG_STANDARD_SCORES,
        universe=universe,
        start=start,
        end=end,
    )


def get_esg_full_scores(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_full_scores(universe='4295904307', start=-5, end=0)

    Parameters
    ----------
    universe: str
        Requested universe
    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(
        ContentType.ESG_FULL_SCORES,
        universe=universe,
        start=start,
        end=end,
    )


def get_esg_standard_measures(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_standard_measures( universe='BNPP.PA', start=0, end=-2)

    Parameters
    ----------
    universe: str
        Requested universe
    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(
        ContentType.EESG_STANDARD_MEASURES,
        universe=universe,
        start=start,
        end=end,
    )


def get_esg_full_measures(universe, start=None, end=None):
    """
    Examples
    --------
    >>> import refinitiv.data as rd
    >>> df = rd.get_esg_full_measures(universe='BNPP.PA', start=0, end=-3)

    Parameters
    ----------
    universe: str
        Requested universe
    start: int, optional
    end: int, optional

    Returns
    -------
    DataFrame or None

    """
    return _get_esg(
        ContentType.ESG_FULL_MEASURES,
        universe=universe,
        start=start,
        end=end,
    )
