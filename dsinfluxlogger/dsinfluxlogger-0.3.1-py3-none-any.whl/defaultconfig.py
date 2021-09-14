"""Default configuration file contents"""

# Remember to add tests for keys into test_influxlogger.py
DEFAULT_CONFIG_STR = """
[zmq]
pub_sockets = ["ipc:///tmp/influxlogger_pub.sock", "tcp://*:58770"]

[db]
host = "127.0.0.1"
# enable for real use
#port = 8486
#ssl = true
#verify_ssl = true
username = "user"
password = "password"
db = "mydb"

[[subscriptions]]  # make this kind of section for each subscription
zmq = ["ipc:///tmp/something.sock", "topic"]
measurement = "mymeas"
tag_fields = ["field1"]  # which fields to use as tags
exclude_fields = ["field2"]  # optional, not used if include_fields is used
include_fields = ["field3", "field4"]  # optional if not set all fields are included

""".lstrip()
