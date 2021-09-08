class Config:
    host = '127.0.0.1'

    end_delimiter = b'FINISHED'

    socket_timeout = 20

    server_message_size = 8192

    client_message_size = 65536

    error_prefix = b'ERRORMSG'

    thread_id_len = 8
    message_id_len = 4

    request_signal = b'POSITIVE'
    request_cancelled = b'NEGATIVE'
