import argparse
import html
import pytest
from mailman2discourse import mailman
from tests.helpers_mailman import mailman_write_config, mailman_create_config, mailman_add


def test_load_synthetic(tmpdir):
    n = 'listname'
    mailman_write_config(f'{tmpdir}/config.pck', mailman_create_config())
    m = mailman.Mailman(argparse.Namespace(mailman_config=f'{tmpdir}/config.pck',
                                           mailman_encoding='UTF-8',
                                           list=n))
    assert m.load() is True
    assert 'subscribe_policy' in m.info
    assert 'private_roster' in m.info


def test_ban_list(tmpdir):
    n = 'listname'
    c = mailman_create_config()
    email = 'some@example.com'
    mailman_add(c, email)
    banned1 = 'banned1@example.com'
    mailman_add(c, banned1)
    banned2 = 'banned2@example.com'
    c['ban_list'] = [banned1, banned2]
    mailman_write_config(f'{tmpdir}/config.pck', c)
    m = mailman.Mailman(argparse.Namespace(mailman_config=f'{tmpdir}/config.pck',
                                           mailman_encoding='UTF-8',
                                           list=n))
    assert m.load() is True
    assert banned1 not in m.user
    assert banned1 in m.info['ban_list']
    assert banned2 in m.info['ban_list']


def test_load_skip(tmpdir, caplog):
    n = 'listname'
    c = mailman_create_config()
    email = 'some@example.com'
    c['digest_members'][email] = 0
    c['language'][email] = 'fr'
    mailman_write_config(f'{tmpdir}/config.pck', c)
    m = mailman.Mailman(argparse.Namespace(mailman_config=f'{tmpdir}/config.pck',
                                           mailman_encoding='UTF-8',
                                           list=n))
    assert m.load() is True
    assert f'SKIP digest_members for unknown user {email}' in caplog.text
    assert f'SKIP language for unknown user {email}' in caplog.text


def test_load_username_none(tmpdir):
    n = 'listname'
    c = mailman_create_config()
    email = 'some@example.com'
    c['members'][email] = 0
    c['usernames'][email] = None
    mailman_write_config(f'{tmpdir}/config.pck', c)
    m = mailman.Mailman(argparse.Namespace(mailman_config=f'{tmpdir}/config.pck',
                                           mailman_encoding='UTF-8',
                                           list=n))
    assert m.load() is True
    assert m.user[email]['usernames'] == ''


@pytest.mark.parametrize("workload,encoding", [('greek', 'iso-8859-1'),
                                               ('regular', 'UTF-8'),
                                               ('instances', 'UTF-8')])
def test_load_realistic(workload, encoding):
    m = mailman.Mailman(argparse.Namespace(mailman_config=f'tests/data/{workload}/config.pck',
                                           mailman_encoding=encoding,
                                           list=workload))
    assert m.load() is True


@pytest.mark.parametrize("raw,cooked", [
    ('my name', 'my name'),
    ('ampersand & not interpreted', 'ampersand & not interpreted'),
    ('&#201; Capital E, acute accent', 'É Capital E, acute accent'),
])
def test_html_unescape(raw, cooked):
    assert html.unescape(raw) == cooked
