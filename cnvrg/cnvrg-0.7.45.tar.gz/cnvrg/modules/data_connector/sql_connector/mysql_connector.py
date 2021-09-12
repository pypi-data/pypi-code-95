from .base_sql_connector import BaseSqlConnector
is_loaded = False
try:
    import pymysql
    is_loaded = True

except ImportError:
    is_loaded = False



class MysqlConnector(BaseSqlConnector):

    @staticmethod
    def requirements():
        return """pymysql"""

    @staticmethod
    def key_type():
        return "mysql"
    # host – Host where the database server is located
    # user – Username to log in as
    # password – Password to use.
    # database – Database to use, None to not use a particular one.
    # port – MySQL port to use, default is usually OK. (default: 3306)
    # bind_address – When the client has multiple network interfaces, specify the interface from which to connect to the host. Argument can be a hostname or an IP address.
    # unix_socket – Optionally, you can use a unix socket rather than TCP/IP.
    # read_timeout – The timeout for reading from the connection in seconds (default: None - no timeout)
    # write_timeout – The timeout for writing to the connection in seconds (default: None - no timeout)
    # charset – Charset you want to use.
    # sql_mode – Default SQL_MODE to use.
    # read_default_file – Specifies my.cnf file to read these parameters from under the [client] section.
    # conv – Conversion dictionary to use instead of the default one. This is used to provide custom marshalling and unmarshalling of types. See converters.
    # use_unicode – Whether or not to default to unicode strings. This option defaults to true for Py3k.
    # client_flag – Custom flags to send to MySQL. Find potential values in constants.CLIENT.
    # cursorclass – Custom cursor class to use.
    # init_command – Initial SQL statement to run when connection is established.
    # connect_timeout – Timeout before throwing an exception when connecting. (default: 10, min: 1, max: 31536000)
    # ssl – A dict of arguments similar to mysql_ssl_set()’s parameters.
    # read_default_group – Group to read from in the configuration file.
    # compress – Not supported
    # named_pipe – Not supported
    # autocommit – Autocommit mode. None means use server default. (default: False)
    # local_infile – Boolean to enable the use of LOAD DATA LOCAL command. (default: False)
    # max_allowed_packet – Max size of packet sent to server in bytes. (default: 16MB) Only used to limit size of “LOAD LOCAL INFILE” data packet smaller than default (16KB).
    # defer_connect – Don’t explicitly connect on construction - wait for connect call. (default: False)
    # auth_plugin_map – A dict of plugin names to a class that processes that plugin. The class will take the Connection object as the argument to the constructor. The class needs an authenticate method taking an authentication packet as an argument. For the dialog plugin, a prompt(echo, prompt) method can be used (if no authenticate method) for returning a string from the user. (experimental)
    # server_public_key – SHA256 authentication plugin public key value. (default: None)
    # db – Alias for database. (for compatibility to MySQLdb)
    # passwd – Alias for password. (for compatibility to MySQLdb)
    # binary_prefix – Add _binary prefix on bytes and bytearray. (default: False)
    def __init__(self, data_connector):
        super(MysqlConnector, self).__init__(data_connector)

    def _connection(self, username=None, password=None, host=None, **kwargs):
        return pymysql.connect(
            **{"host": host, "password": password, "user": username, **kwargs},cursorclass=pymysql.cursors.DictCursor
        )
