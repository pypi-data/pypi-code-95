from typing import Any, Optional, List, Iterator, Dict
from kenna import DEFAULT_API_KEY, DEFAULT_REGION
from hodgepodge.requests import DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_READ_ERRORS, DEFAULT_BACKOFF_FACTOR

import datetime
import logging
import urllib.parse
import requests
import hodgepodge.archives
import hodgepodge.compression
import hodgepodge.files
import hodgepodge.hashing
import hodgepodge.requests
import hodgepodge.requests
import hodgepodge.time
import hodgepodge.web
import kenna.authentication
import kenna.data.parser
import kenna.region

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

_MAX_PAGES_ALLOWED_BY_API = 20


class _Kenna:
    def __init__(self, api_key: str = DEFAULT_API_KEY, region: str = DEFAULT_REGION,
                 max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
                 max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
                 max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
                 backoff_factor: float = DEFAULT_BACKOFF_FACTOR):

        self.region = region = kenna.region.validate_name(region)
        self.url = kenna.region.get_endpoint(region)

        self.session = requests.Session()
        self.session.headers['X-Risk-Token'] = kenna.authentication.validate_api_key(api_key)

        policy = hodgepodge.requests.get_automatic_retry_policy(
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )
        hodgepodge.requests.attach_http_request_policies_to_session(session=self.session, policies=[policy])

    def get_object(self, collection_name: str, object_id: int):
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(collection_name, object_id))
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def iter_pages_by_collection_name(self, collection_name: str) -> List[Dict[str, Any]]:
        url = urllib.parse.urljoin(self.url, collection_name)
        return self.iter_pages_by_url(url=url)

    def iter_pages_by_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Notes:
        - The default page size is 500 for larger record sets (e.g. assets and vulnerabilities);
        - Pagination is limited to 20 pages (i.e. at most 10,000 rows can be read via the REST API);
        - To retrieve more than 10,000 rows, you will need to use the export data APIs.
        """
        response = self.session.get(url)
        response.raise_for_status()
        page = response.json()
        yield page

        #: Read any remaining pages (if applicable).
        if isinstance(page, list):
            yield page

        elif isinstance(page, dict):
            meta = page.get('meta')
            if meta:
                total_pages = meta['pages']
                if total_pages > _MAX_PAGES_ALLOWED_BY_API:
                    logger.warning(
                        "Only %d/%d pages are retrievable via this API endpoint - consider using the data export API instead (%s)",
                        _MAX_PAGES_ALLOWED_BY_API, total_pages, url)

                #: Read pages concurrently across a thread pool.
                for page_number in range(meta['page'] + 1, min(total_pages, _MAX_PAGES_ALLOWED_BY_API) + 1):
                    params = {
                        'page': page_number,
                    }
                    response = self.session.get(url, params=params)
                    response.raise_for_status()
                    page = response.json()
                    yield page

    def iter_objects(self, collection_name: str, object_ids: List[int] = None,
                     min_create_time: Optional[datetime.datetime] = None,
                     max_create_time: Optional[datetime.datetime] = None,
                     min_update_time: Optional[datetime.datetime] = None,
                     max_update_time: Optional[datetime.datetime] = None,
                     limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        object_ids = object_ids or []
        min_create_time = None if not min_create_time else hodgepodge.time.as_datetime(min_create_time)
        max_create_time = None if not max_create_time else hodgepodge.time.as_datetime(max_create_time)
        min_update_time = None if not min_update_time else hodgepodge.time.as_datetime(min_update_time)
        max_update_time = None if not max_update_time else hodgepodge.time.as_datetime(max_update_time)
        limit = None if limit is None else max(0, limit)

        i = 1
        for page in self.iter_pages_by_collection_name(collection_name=collection_name):
            for obj in page[collection_name]:

                #: Filter objects by ID.
                if object_ids and obj['id'] not in object_ids:
                    continue

                #: Filter objects by min/max object creation timestamp.
                if min_create_time or max_create_time:
                    create_time = hodgepodge.time.as_datetime(obj['created_at'])
                    if not hodgepodge.time.is_within_range(
                            timestamp=create_time,
                            minimum=min_create_time,
                            maximum=max_create_time,
                    ):
                        continue

                #: Filter objects by min/max object update timestamp.
                if min_update_time or max_update_time:
                    update_time = hodgepodge.time.as_datetime(obj['updated_at'])
                    if not hodgepodge.time.is_within_range(
                            timestamp=update_time,
                            minimum=min_update_time,
                            maximum=max_update_time,
                    ):
                        continue

                yield obj

                #: Optionally limit the number of search results.
                if limit:
                    if i >= limit:
                        return
                    i += 1

    def get_application(self, application_id: int) -> Optional[Any]:
        logger.info("Looking up application (application ID: %s)", application_id)
        return self.get_object(collection_name='applications', object_id=application_id)

    def get_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_applications(application_ids=application_ids, limit=limit))

    def iter_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up applications (application IDs: %s)", application_ids)
        for app in self.iter_objects(
                collection_name='applications',
                object_ids=application_ids,
                limit=limit,
        ):
            yield app

    def get_asset(self, asset_id: int) -> Optional[Any]:
        logger.info("Looking up asset (asset ID: %s)", asset_id)
        return self.get_object(collection_name='assets', object_id=asset_id)

    def get_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_assets(asset_ids=asset_ids, limit=limit))

    def iter_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up assets (asset IDs: %s)", asset_ids)
        for asset in self.iter_objects(
                collection_name='assets',
                object_ids=asset_ids,
                limit=limit,
        ):
            yield asset

    def get_connector(self, connector_id: int) -> Optional[Any]:
        logger.info("Looking up connector (connector ID: %s)", connector_id)
        return self.get_object(collection_name='connectors', object_id=connector_id)

    def get_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_connectors(connector_ids=connector_ids, limit=limit))

    def iter_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up connectors (connector IDs: %s)", connector_ids)
        for connector in self.iter_objects(
                collection_name='connectors',
                object_ids=connector_ids,
                limit=limit,
        ):
            yield connector

    def get_connector_runs(self, connector_run_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_connector_runs(connector_run_ids=connector_run_ids, limit=limit))

    def iter_connector_runs(self, connector_ids: List[int] = None,
                            connector_run_ids: List[int] = None,
                            limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        logger.info("Looking up connector runs (connector IDs: %s, connector run IDs: %s)", connector_ids,
                    connector_run_ids)
        i = 0
        for connector in self.iter_connectors(connector_ids=connector_ids):
            url = urllib.parse.urljoin(self.url, '{}/{}/{}'.format('connectors', connector['id'], 'connector_runs'))
            for page in self.iter_pages_by_url(url):
                for run in page:
                    if connector_run_ids and run['id'] not in connector_run_ids:
                        continue

                    yield run

                    i += 1
                    if limit and i >= limit:
                        break

    def get_connector_run(self, connector_id: int, connector_run_id: int):
        return next(self.iter_connector_runs(connector_ids=[connector_id], connector_run_ids=[connector_run_id]), None)

    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[Any]:
        logger.info("Looking up dashboard group (dashboard group ID: %s)", dashboard_group_id)
        return self.get_object(collection_name='dashboard_groups', object_id=dashboard_group_id)

    def get_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit))

    def iter_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up dashboard groups (dashboard group IDs: %s)", dashboard_group_ids)
        for dashboard_group in self.iter_objects(
                collection_name='dashboard_groups',
                object_ids=dashboard_group_ids,
                limit=limit,
        ):
            yield dashboard_group

    def get_fix(self, fix_id: int) -> Optional[Any]:
        logger.info("Looking up fix (fix ID: %s)", fix_id)
        return self.get_object(collection_name='fixes', object_id=fix_id)

    def get_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_fixes(fix_ids=fix_ids, limit=limit))

    def iter_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up fixes (fix IDs: %s)", fix_ids)
        for fix in self.iter_objects(
                collection_name='fixes',
                object_ids=fix_ids,
                limit=limit,
        ):
            yield fix

    def get_vulnerability(self, vulnerability_id: int) -> Optional[Any]:
        logger.info("Looking up vulnerability (vulnerability ID: %s)", vulnerability_id)
        return self.get_object(collection_name='vulnerabilities', object_id=vulnerability_id)

    def get_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit))

    def iter_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up vulnerability IDs (vulnerability IDs: %s)", vulnerability_ids)
        for vulnerability in self.iter_objects(
                collection_name='vulnerabilities',
                object_ids=vulnerability_ids,
                limit=limit,
        ):
            yield vulnerability

    def get_user(self, user_id: int) -> Optional[Any]:
        logger.info("Looking up user (user ID: %s)", user_id)
        return self.get_object(collection_name='users', object_id=user_id)

    def get_users(self, user_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_users(user_ids=user_ids, limit=limit))

    def iter_users(self, user_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up users (user IDs: %s)", user_ids)
        for user in self.iter_objects(collection_name='users', object_ids=user_ids, limit=limit):
            yield user

    def get_role(self, role_id: int) -> Optional[Any]:
        logger.info("Looking up role (role ID: %s)", role_id)
        return self.get_object(collection_name='roles', object_id=role_id)

    def get_roles(self, role_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_roles(role_ids=role_ids, limit=limit))

    def iter_roles(self, role_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up roles (role IDs: %s)", role_ids)
        for role in self.iter_objects(collection_name='roles', object_ids=role_ids, limit=limit):
            yield role


class Kenna:
    def __init__(self, api_key: str = DEFAULT_API_KEY, region: str = DEFAULT_REGION,
                 max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
                 max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
                 max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
                 backoff_factor: float = DEFAULT_BACKOFF_FACTOR):

        self.raw = _Kenna(
            api_key=api_key,
            region=region,
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )

    def get_application(self, application_id: int) -> Optional[Any]:
        return self.raw.get_application(application_id=application_id)

    def get_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_applications(application_ids=application_ids, limit=limit))

    def iter_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for app in self.raw.iter_applications(application_ids=application_ids, limit=limit):
            yield app

    def get_asset(self, asset_id: int) -> Optional[Any]:
        return self.raw.get_asset(asset_id=asset_id)

    def get_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_assets(asset_ids=asset_ids, limit=limit))

    def iter_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for asset in self.raw.iter_assets(asset_ids=asset_ids, limit=limit):
            yield asset

    def get_connector(self, connector_id: int) -> Optional[Any]:
        return self.raw.get_connector(connector_id=connector_id)

    def get_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_connectors(connector_ids=connector_ids, limit=limit))

    def iter_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for connector in self.raw.iter_connectors(connector_ids=connector_ids, limit=limit):
            yield connector

    def get_connector_runs(self, connector_ids: List[int] = None, connector_run_ids: List[int] = None,
                           limit: Optional[int] = None) -> List[Any]:

        return list(self.iter_connector_runs(
            connector_ids=connector_ids,
            connector_run_ids=connector_run_ids,
            limit=limit,
        ))

    def iter_connector_runs(self, connector_ids: List[int] = None, connector_run_ids: List[int] = None,
                            limit: Optional[int] = None) -> Iterator[Any]:

        for run in self.raw.iter_connector_runs(
                connector_ids=connector_ids,
                connector_run_ids=connector_run_ids,
                limit=limit,
        ):
            yield run

    def get_connector_run(self, connector_id: int, connector_run_id: int) -> Optional[Any]:
        return self.raw.get_connector_run(connector_id=connector_id, connector_run_id=connector_run_id)
    
    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[Any]:
        return self.raw.get_dashboard_group(dashboard_group_id=dashboard_group_id)

    def get_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit))

    def iter_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for dashboard_group in self.raw.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit):
            yield dashboard_group
    
    def get_fix(self, fix_id: int) -> Optional[Any]:
        return self.raw.get_fix(fix_id=fix_id)

    def get_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_fixes(fix_ids=fix_ids, limit=limit))

    def iter_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for fix in self.raw.iter_fixes(fix_ids=fix_ids, limit=limit):
            yield fix
    
    def get_vulnerability(self, vulnerability_id: int) -> Optional[Any]:
        return self.raw.get_vulnerability(vulnerability_id=vulnerability_id)

    def get_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit))

    def iter_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for vulnerability in self.raw.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit):
            yield vulnerability

    def get_user(self, user_id: int) -> Optional[Any]:
        return self.raw.get_user(user_id=user_id)

    def get_users(self, user_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_users(user_ids=user_ids, limit=limit))

    def iter_users(self, user_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for user in self.raw.iter_users(user_ids=user_ids, limit=limit):
            yield user

    def get_role(self, role_id: int) -> Optional[Any]:
        return self.raw.get_role(role_id=role_id)

    def get_roles(self, role_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_roles(role_ids=role_ids, limit=limit))

    def iter_roles(self, role_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for role in self.raw.iter_roles(role_ids=role_ids, limit=limit):
            yield role
