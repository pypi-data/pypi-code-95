from .pyruvate import serve, FileWrapper  # noqa: F401


def serve_paste(app, global_conf, **kw):
    write_blocking = bool(kw.get('write_blocking', 'False') == 'True')
    num_headers = int(kw.get('max_number_headers', 32))
    async_logging = bool(kw.get('async_logging', 'True') != 'False')
    chunked_transfer = bool(kw.get('chunked_transfer', 'False') == 'True')
    reuse_count = int(kw.get('max_reuse_count', 0))
    keepalive_timeout = int(kw.get('keepalive_timeout', 60))
    serve(
        app,
        kw.get('socket'),
        int(kw['workers']),
        write_blocking=write_blocking,
        max_number_headers=num_headers,
        async_logging=async_logging,
        chunked_transfer=chunked_transfer,
        max_reuse_count=reuse_count,
        keepalive_timeout=keepalive_timeout)
    return 0
