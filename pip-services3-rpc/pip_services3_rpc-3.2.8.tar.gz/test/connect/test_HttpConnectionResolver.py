# -*- coding: utf-8 -*-
"""
    tests.connect.test_HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors.ConfigException import ConfigException

from pip_services3_rpc.connect import HttpConnectionResolver


class TestHttpConnectionResolver:

    def test_resolve_uri(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples("connection.uri", "http://somewhere.com:777"))
        connection = connection_resolver.resolve(None)

        assert connection.get_as_string('protocol') == "http"
        assert connection.get_as_string('host') == "somewhere.com"
        assert connection.get_as_integer('port') == 777
        assert connection.get_as_string('uri') == "http://somewhere.com:777"

    def test_resolve_parameters(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.protocol", "http",
            "connection.host", "somewhere.com",
            "connection.port", 777
        ))
        connection = connection_resolver.resolve(None)
        assert connection.get_as_string('uri') == "http://somewhere.com:777"

    def test_https_with_credentials_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file",
            "credential.ssl_crt_file", "ssl_crt_file"
        ))

        connection = connection_resolver.resolve(None)

        assert 'https' == connection.get_as_string('protocol')
        assert 'somewhere.com' == connection.get_as_string('host')
        assert 123 == connection.get_as_integer('port')
        assert 'https://somewhere.com:123' == connection.get_as_string('uri')
        assert 'ssl_key_file' == connection.get_as_string('ssl_key_file')
        assert 'ssl_crt_file' == connection.get_as_string('ssl_crt_file')

    def test_https_with_no_credentials_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.internal_network", "internal_network"
        ))
        connection = connection_resolver.resolve(None)

        assert 'https' == connection.get_as_string('protocol')
        assert 'somewhere.com' == connection.get_as_string('host')
        assert 123 == connection.get_as_integer('port')
        assert 'https://somewhere.com:123' == connection.get_as_string('uri')
        assert connection.get_as_string('internal_network') is None

    def test_https_with_missing_credentials_connection_params(self):
        # Section missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https"
        ))
        print('Test - section missing')
        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_CREDENTIAL'
            assert err.name == 'NO_CREDENTIAL'
            assert err.message == 'SSL certificates are not configured for HTTPS protocol'
            assert err.category == 'Misconfiguration'

        # ssl_crt_file missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file"
        ))

        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_SSL_CRT_FILE'
            assert err.name == 'NO_SSL_CRT_FILE'
            assert err.message == 'SSL crt file is not configured in credentials'
            assert err.category == 'Misconfiguration'

        # ssl_key_file missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_crt_file", "ssl_crt_file"
        ))

        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_SSL_KEY_FILE'
            assert err.name == 'NO_SSL_KEY_FILE'
            assert err.message == 'SSL key file is not configured in credentials'
            assert err.category == 'Misconfiguration'

        # ssl_key_file, ssl_crt_file present
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file",
            "credential.ssl_crt_file", "ssl_crt_file"
        ))

        connection = connection_resolver.resolve(None)
        assert 'https' == connection.get_as_string('protocol')
        assert 'somewhere.com' == connection.get_as_string('host')
        assert 123 == connection.get_as_integer('port')
        assert 'https://somewhere.com:123' == connection.get_as_string('uri')
        assert 'ssl_key_file' == connection.get_as_string('ssl_key_file')
        assert 'ssl_crt_file' == connection.get_as_string('ssl_crt_file')
