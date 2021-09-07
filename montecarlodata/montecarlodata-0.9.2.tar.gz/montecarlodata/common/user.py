from dataclasses import dataclass
from typing import Optional, Dict, List

from montecarlodata.config import Config
from montecarlodata.errors import complain_and_abort
from montecarlodata.queries.user import GET_USER_QUERY
from montecarlodata.utils import GqlWrapper


@dataclass
class User:
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserService:
    def __init__(self, config: Config, request_wrapper: Optional[GqlWrapper] = None):
        self._config = config
        self._request_wrapper = request_wrapper or GqlWrapper(mcd_id=config.mcd_id, mcd_token=config.mcd_token)

        self._user = self._request_wrapper.make_request(GET_USER_QUERY)  # get user info

    @property
    def user(self) -> User:
        """
        Returns basic user properties
        """
        return User(first_name=self._user['getUser'].get('firstName'), last_name=self._user['getUser'].get('lastName'))

    @property
    def account(self) -> Dict:
        """
        Get account details
        """
        return self._user['getUser']['account']

    @property
    def collectors(self) -> Dict:
        """
        Get collectors in the account
        """
        return self.account.get('dataCollectors', [{}])

    @property
    def active_collector(self) -> Dict:
        """
        Get active collector from collectors.

        Errors out on accounts with > 1 collector. Legacy. Do not use.
        """
        return self.collectors[self._get_active_collector()]

    @property
    def warehouses(self) -> List[Dict]:
        """
        Get warehouses attached to the account
        """
        return self.account.get('warehouses')

    @property
    def bi_containers(self) -> List[Dict]:
        """
        Get bi attached to the account
        """
        return self.account.get('bi')

    @property
    def tableau_accounts(self) -> Dict:
        """
        Get tableau connections attached to the account
        """
        return self.account.get('tableauAccounts')

    @property
    def active_collection_regions(self) -> List[str]:
        """
        Get a list of active collection regions
        """
        return self.account.get('activeCollectionRegions')

    def _get_active_collector(self) -> Optional[int]:
        """
        Get active collector - currently only one active collector per account is supported. Abort if None are found
        """
        if len(self.collectors) > 1:
            complain_and_abort('This option is only supported in accounts with one collector.')

        for idx, collector in enumerate(self.collectors):
            if collector.get('active'):
                return idx
        complain_and_abort('No active collector found')
