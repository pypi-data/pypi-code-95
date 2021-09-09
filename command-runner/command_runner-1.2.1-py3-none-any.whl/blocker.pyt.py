import sys
from subprocess import PIPE, Popen
from threading import Thread

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty  # python 2.x

ON_POSIX = 'posix' in sys.builtin_module_names

def run(cmd):
    def enqueue_output(out, queue):

        # EOF char might be binary or string depending on encoding given to Popen
        eof_char = '' if hasattr(out, 'encoding') else b''

        for line in iter(out.readline, eof_char):
            queue.put(line)
        # Let's notify the queue that no more output will be given back
        queue.put(None)
        out.close()

    p = Popen(cmd, shell=True, stdout=PIPE, bufsize=16384, close_fds=ON_POSIX, encoding='utf-8')
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True # thread dies with the program
    t.start()

    output = ''

    # ... do other things here
    while True:
        # read line without blocking
        # try:  line = q.get_nowait() # or q.get(timeout=.1)
        try:  line = q.get(timeout=.05)
        except Empty:
            pass
        else:
            if line is None:
                break
            else: # got line
                output += str(line)
    return output

cmd = r'type C:\GIT\IMFAGENT\PythonSRC\imfExporter.log'

# Now lets run the above code a couple of times and compare output of each run with previous run
previous_output = None
for i in range(0, 20000):
    print('\nRun {}'.format(i))
    output = run(cmd)
    if previous_output:
        if output != previous_output:
            print('Failed on run {}'.format(i))
            break
    previous_output = output
print('done')

