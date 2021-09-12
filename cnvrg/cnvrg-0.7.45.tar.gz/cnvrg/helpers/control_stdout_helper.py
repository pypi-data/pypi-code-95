import sys
import io
import time
import threading
import builtins as __builtin__
import re
ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def before_run():
    olderrio = sys.stderr
    oldstdio = sys.stdout
    sys.stdout = std_buffer = io.StringIO()
    sys.stderr = err_buffer = io.StringIO()
    return std_buffer, err_buffer, olderrio, oldstdio


def after_run(buffer, err_buffer, errio, stdio):
    buffer.close()
    err_buffer.close()
    sys.stdout = stdio
    sys.stderr = errio



def remove_colors(block):
    first_filter = [ANSI_ESCAPE.sub('', line) for line in block.strip().split("\n")]
    return [line for line in filter(lambda x: x, first_filter)]

def check_buffer_thread(buffer, callback):
    def p(seek):
        v = buffer.getvalue()
        v = v[seek:]
        if v:
            lines = remove_colors(v)
            callback(lines)
        return seek + len(v)

    seek = 0
    while not buffer.closed:
        seek = p(seek)
        time.sleep(0.5)

def get_buffer_callbacks(callback, f_io):
    callbacks = []
    callbacks.append(lambda x: print("\n".join(map(str, x)), file=f_io))
    if callback: callbacks.append(callback)
    return lambda x: [cb(x) for cb in callbacks]


def run_callable(callable, arguments: list=None, callback=None, err_callback=None):
    ### the idea here is to "redirect" to stdout/stderr to buffers.


    ### on error: it will log to err_buffer instead of sys.stderr
            ##      from err_buffer it will go to stderr and to
    buffer, err_buffer, errio, stdio = before_run()

    ## those threads will monitor the buffer and will call the relevant "prints"
    t = threading.Thread(target=check_buffer_thread, args=(buffer, get_buffer_callbacks(callback, stdio)))
    terr = threading.Thread(target=check_buffer_thread, args=(err_buffer, get_buffer_callbacks(err_callback, errio)))
    t.start()
    terr.start()
    try:
        exit_status = callable(*arguments)
    except Exception as e:
        exit_status = 1
        err_callback(str(e))
    except KeyboardInterrupt as e:
        exit_status = -100
        err_callback("Keyboard Interrupt")
    time.sleep(0.5)
    after_run(buffer, err_buffer, errio, stdio)
    t.join()
    terr.join()
    return exit_status

