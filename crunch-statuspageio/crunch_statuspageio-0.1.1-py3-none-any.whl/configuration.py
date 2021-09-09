from typing import Optional


class Configuration:
    '''Configuration object'''
    def __init__(
        self,
        api_key: str,
        page_id: str,
        organization_id: Optional[str] = None,
        base_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout=30,
        verify_ssl=True
    ):
        """
        :param str api_key: Personal access token.
        :param str page_id:  The page_id you wish to manage
        :param str organization_id: (optional) The organization id, used for managing user accounts
        :param bool verbose: (optional) Verbose/debug mode. Default: ``False``.
        :param int timeout: (optional) Connection and response timeout. Default: **30** seconds.
        :param bool verify_ssl: (optional) Whether to verify ssl or not. Default: ``True``.
        """

        self.api_key = api_key
        self.page_id = page_id
        self.organization_id = organization_id
        self.base_url = base_url if base_url is not None else 'https://api.statuspage.io'
        self.user_agent = user_agent if user_agent is not None else 'StatusPage/v1 Python Client'
        self.timeout = timeout
        self.verify_ssl = verify_ssl
