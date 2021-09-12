import argparse
import pytest
import logging
from tests.helpers_mailman import mailman_create_config, mailman_write_config


for lib in ('urllib3',):
    logger = logging.getLogger(lib)
    logger.setLevel(logging.WARNING)
    logger.propagate = False


@pytest.fixture
def test_options(version, tmpdir):
    api_key = open(f'{version}/apikey').read().strip()
    ip = open(f'{version}/ip').read().strip()
    url = f'http://{ip}'
    n = 'listname'
    mailman_write_config(f'{tmpdir}/config.pck', mailman_create_config())
    return argparse.Namespace(debug=True,
                              list=n,
                              domain='example.com',
                              mailman_config=f'{tmpdir}/config.pck',
                              dry_run=False,
                              api_key=api_key,
                              api_user='api',
                              url=url,
                              mailman_encoding='UTF-8',
                              preserve_existing_user_preferences=False,
                              force_private=False,
                              skip_ban_list=False)
