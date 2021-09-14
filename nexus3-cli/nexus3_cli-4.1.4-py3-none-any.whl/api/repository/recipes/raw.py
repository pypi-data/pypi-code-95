from nexuscli import exception, nexus_util
from nexuscli.api.repository.base_models import Repository
from nexuscli.api.repository.base_models import GroupRepository
from nexuscli.api.repository.base_models import HostedRepository
from nexuscli.api.repository.base_models import ProxyRepository

__all__ = ['RawHostedRepository', 'RawProxyRepository', 'RawGroupRepository']


class _RawRepository(Repository):
    RECIPE_NAME = 'raw'


class RawGroupRepository(_RawRepository, GroupRepository):
    pass


class RawHostedRepository(_RawRepository, HostedRepository):
    def upload_file(self, source, destination):
        """
        Upload a single file to a raw repository.

        :param source: path to the local file to be uploaded.
        :param destination: directory under dst_repo to place file in. When None,
            the file is placed under the root of the raw repository
        :raises exception.NexusClientInvalidRepositoryPath: invalid repository path.
        :raises exception.NexusClientAPIError: unknown response from Nexus API.
        """
        destination, dst_file = nexus_util.get_dst_path_and_file(source, destination)

        params = {'repository': self.name}
        files = {'raw.asset1': open(source, 'rb').read()}
        data = {
            'raw.directory': destination,
            'raw.asset1.filename': dst_file,
        }

        response = self._client.post(
            'components', files=files, data=data, params=params, stream=True)

        if response.status_code != 204:
            raise exception.NexusClientAPIError(
                f'Uploading to {self.name}. Reason: {response.reason} '
                f'Status code: {response.status_code} Text: {response.text}')


class RawProxyRepository(_RawRepository, ProxyRepository):
    pass
