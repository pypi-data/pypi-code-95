#!/usr/bin/python
from __future__ import print_function

from sys import stdout
from os import path, getcwd, listdir, chdir, makedirs, remove
from subprocess import call
from io import FileIO
from glob import glob
from functools import wraps
from contextlib import contextmanager
from runana import input_file_handling
from operator import add, mul
from runana.read_numbers import ignored

try:
    from operator import div
except ImportError:
    from operator import truediv as div

try:
    basestring          # Python 2.x
except NameError:
    basestring = str    # Python 3.x


OPERATIONS = {'add': add, 'mul': mul, 'div': div}


@contextmanager
def cwd(path):
    """ Contextmanager that changes working directory temporarily """
    oldpwd = getcwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(oldpwd)


def generate_seq(start, incr, nvalues=0, incr_func=add):
    """Iterator that returns a sequence of numbers

    :param incr_func: function used to increment the return value. Can be one
        of the strings 'add', 'mul' or 'div'
    :type incr_func: func or str
    """
    if isinstance(incr_func, basestring):
        incr_func = OPERATIONS[incr_func]
    value = start
    yield value
    for i in range(1, nvalues):
        value = incr_func(value, incr)
        yield value


def generate_list(*args, **kwargs):
    """Wrap of generate_seq that returns a list instead of an iterator"""
    return list(generate_seq(*args, **kwargs))


class Dirs(object):
    """Container class for names of directories

    :param str scratch_base: Directory prefix
    :param str local_scratch_base: Prefix for directory in which programs
        are run. If `None` then `scratch_base` is used
    :param list copy_2_scratch: List of strings that are globbed and copied
        from the local scratch directory to scratch directory
    """
    def __init__(self, scratch_base, local_scratch_base=None,
                 copy_2_scratch=['*.txt', '*.nml', '*.stdout', '*.dat']):
        if local_scratch_base is None:
            local_scratch_base = scratch_base
        self.scratch_base = scratch_base
        self.local_scratch_base = local_scratch_base
        self.copy_2_scratch = copy_2_scratch
        makedir(self.scratch_base)


def makedir(dir_):
    if not path.exists(dir_):
        makedirs(dir_)


class OpenWithNone(FileIO):
    def __init__(self, file_string, *args, **kwargs):
        self.file_string = file_string
        if file_string:
            super(OpenWithNone, self).__init__(file_string, *args, **kwargs)

    def __enter__(self):
        handle = None
        if self.file_string:
            handle = super(OpenWithNone, self).__enter__()
        self.fd = handle
        return self.fd

    def __exit__(self, type, value, traceback):
        if self.fd:
            super(OpenWithNone, self).__exit__()


def replace_string_in_file(fileName, text_to_search, text_to_replace):
    with open(fileName, 'r') as file_handle:
        filedata = file_handle.read()
    filedata = filedata.replace(text_to_search, text_to_replace)
    with open(fileName, 'w') as file_handle:
        file_handle.write(filedata)


def run_program(program, cmdargs, stdin_f, stdout_f, stderr_f,
                run=True, cmd_prepend="", run_from_cmd=True,
                **kwargs):
    """Runs `program` with `cmdargs` using `subprocess.call`.
    :param str stdin_f: File from which to take standard input
    :param str stdout_f: File in which to put standard output
    :param str stderr_f: File in which to put standard error
    :param bool run: Whether to actually run `program`
    If `True` the program return code is returned.
    If false a string pointing to the script which will run
 the program is returned
    :param str cmd_prepend: Put in the beginning of the bash script
    :param bool run_from_cmd: Run `program` using the generated bash
    script instead of running it directly

    """
    time_file_name = '.'.join(stdout_f.split('.')[:-1])+'.time'
    cmd_file_name = '.'.join(stdout_f.split('.')[:-1])+'.sh'
    with open(cmd_file_name, 'w') as cmd_file:
        cmd = ' '.join([program]+cmdargs)
        time_cmd = "/usr/bin/time -o {time_file}".format(time_file=time_file_name)
        cmd = "{time_cmd} {cmd} 1> {stdout} 2> {stderr} \n".format(time_cmd=time_cmd,
                                                                   cmd=cmd,
                                                                   stdout=stdout_f,
                                                                   stderr=stderr_f)
        cmd = cmd_prepend + cmd
        cmd_file.write(cmd)
    if run:
        with OpenWithNone(stdin_f, 'r') as input_file,  open(stdout_f, 'w') as stdout_file, open(stderr_f, 'w') as stderr_file:
            if run_from_cmd:
                retcode = call(["bash", cmd_file_name], **kwargs)
            else:
                try:
                    with open(time_file_name, 'w') as time_file:
                        with print_time(time_file):
                            retcode = call([program]+cmdargs, stdin=input_file,
                                           stdout=stdout_file, stderr=stderr_file, **kwargs)
                except Exception as e:
                    print(e)
                    print('program ', program)
                    print('cmdargs', cmdargs)
                    print('stdin   ', stdin_f)
                    print('stdout  ', stdout_f)
                    print('stderr  ', stderr_f)
                    # print 'kwargs  ', kwargs
                    print(getcwd())
                    raise
                
        replace_string_in_file(stdout_f, '\r', '\n')
        return retcode
    else:
        return cmd_file_name


from subprocess import Popen, PIPE
from time import sleep
# from time import time
# from os import fsync
def run_program_print_output(program, cmdargs,
                             stdin_f, stdout_f, stderr_f, print_output=False,
                             **kwargs):
    with OpenWithNone(stdin_f, 'r') as input_file:
        with open(stdout_f, 'w', buffering=0) as stdout_file:
            with open(stderr_f, 'w', buffering=0) as stderr_file:
                try:
                    with open(stdout_f+'.sh', 'w') as cmd_file:
                        cmd_file.write(' '.join([program]+cmdargs))
                    if print_output:
                        # start_time = time()
                        process = Popen([program]+cmdargs, stdin=input_file,
                                        stdout=PIPE, stderr=PIPE, bufsize=0, **kwargs)
                        # print(time()-start_time)
                        # print('Right after process call')
                        while True:
                            stdout = process.stdout.readline()
                            stderr = process.stderr.readline()
                            if stdout == '' and stderr == '' and process.poll() is not None:
                                break
                            if stdout:
                                # print(time()-start_time)
                                print(stdout, end='')
                                stdout_file.write(stdout)
                                # stdout_file.flush()
                                # fsync(stdout_file.fileno())
                            if stderr:
                                print(stderr, end='')
                                stderr_file.write(stderr)
                            sleep(0.1)
                    else:
                        call([program]+cmdargs, stdin=input_file,
                             stdout=stdout_file, stderr=stderr_file, bufsize=0, **kwargs)
                except Exception as e:
                    print(e)
                    print('program ', program)
                    print('cmdargs', cmdargs)
                    print('stdin   ', stdin_f)
                    print('stdout  ', stdout_f)
                    print('stderr  ', stderr_f)
                    # print 'kwargs  ', kwargs
                    print(getcwd())
                    raise
    replace_string_in_file(stdout_f, '\r', '\n')


def name_stdout(program, add=''):
    if isinstance(program, basestring):
        prog = program
    else:
        prog = program[0]
    stdouts = prog.split('/')[-1]
    # stdouts = stdouts.split('.')[0].split('_')[0]+add+'.std'
    stdouts = stdouts+add+'.std'
    return stdouts+'out', stdouts+'err'


def run_prog(program, cmdargs=[], stdin_f=None, add='', **kwargs):
    # run_program_print_output(program, cmdargs, stdin_f,
    return run_program(program, cmdargs, stdin_f,
                       *name_stdout(program, add), **kwargs)


def copy_ignore_same(from_file, to_file):
    from shutil import copy, Error
    try:
        copy(from_file, to_file)
    except Error as err:
        with open('shutil.err', 'a') as f1:
            f1.write(str(err)+'\n')
    except IOError:
        pass


def copy_to_scratch(WorkDir, file_strings):
    files = []
    for file_string in file_strings:
        files = files+glob(file_string)
    for fil in files:
        copy_ignore_same(fil, WorkDir)


@ignored(OSError)
def get_subdirs(a_dir='./'):
    return [name for name in listdir(a_dir)
            if path.isdir(path.join(a_dir, name))]


def generate_run_ID(work_dir, invalid_IDs=[], prepend=""):
    subdirs = get_subdirs(work_dir)
    ID = 1
    while True:
        strID = str(ID)
        if prepend:
            strID = prepend + strID
        if strID in subdirs or strID in invalid_IDs:
            ID = ID+1
        else:
            return strID


def make_run_dirs(ScratchBase, LScratchBase, **gen_ID_kwargs):
    ID = generate_run_ID(ScratchBase, **gen_ID_kwargs)
    work_dir = path.join(ScratchBase, ID)
    lwork_dir = path.join(LScratchBase, ID)
    makedir(work_dir)
    makedir(lwork_dir)
    return ID, work_dir, lwork_dir


def lock_wrap_retry(Dir, nretries=10, wait=0.1):
    def decorate(f):
        @wraps(f)
        def call(*args, **kwargs):
            import fcntl, time
            pid_file = path.join(Dir, 'lock_ID_gen.pid')
            with open(pid_file, 'w') as lock_fp:
                for attempt in range(nretries):
                    try:
                        fcntl.lockf(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except IOError:
                        import random
                        print('Waiting for lock on', Dir, attempt)
                        time.sleep(wait+0.05*random.random())
                        continue
                    break
                else:
                    print('Failed to get ID generation lock')
                try:
                    ret = f(*args, **kwargs)
                    fcntl.lockf(lock_fp, fcntl.LOCK_UN)
                finally:
                    fcntl.lockf(lock_fp, fcntl.LOCK_UN)
            return ret
        return call
    return decorate


def save_info_in_file(filename, command, copy_back=None):
    with open(filename, 'w') as output_file:
        call(command, stdout=output_file)
    if copy_back:
        copy_ignore_same(filename, copy_back)


def calc_all(replacements, dirs, inp_file, programs,
             print_finish=True, filter_func='f90nml', use_stdin=False,
             use_inp_file=True,
             **gen_ID_kwargs):

    base_dir = dirs.scratch_base
    dirID, work_dir, lwork_dir = lock_wrap_retry(base_dir, nretries=10, wait=0.1)(
        make_run_dirs)(base_dir, dirs.local_scratch_base, **gen_ID_kwargs)

    inp_file_local = path.join(work_dir, path.basename(inp_file))
    input_file_handling.INP_FILE_FILTERS[filter_func](inp_file, inp_file_local, replacements)

    with cwd(lwork_dir):
        save_info_in_file('hostname.txt', 'hostname', work_dir)
        save_info_in_file('started.txt', 'date', work_dir)
        inp_file_relative = path.relpath(inp_file_local, lwork_dir)
        run_core(programs, inp_file_relative, use_stdin=use_stdin,
                 use_inp_file=use_inp_file)
        copy_to_scratch(work_dir, dirs.copy_2_scratch)
        save_info_in_file('ended.txt', 'date', work_dir)
    if print_finish:
        print('Finished', dict((is_it_tuple(key),elem) for key,elem in replacements.items()))
    return dirID


def is_it_tuple(it):
    if isinstance(it, tuple):
        return it[1]
    else:
        return it


@contextmanager
def NamedTempFile(name, mode="w", **kwargs):
    """Contextmanager for creating a named temporary file """
    try:
        with open(name, mode=mode, **kwargs) as f:
            yield f
    finally:
        with ignored(FileNotFoundError):
            remove(name)


def run_core(programs, inp_file_relative, use_stdin=False,
             use_inp_file=True, add_temp_ignore_file=True):
    if add_temp_ignore_file:
        with NamedTempFile("ignore"):
            run_core_inner(programs, inp_file_relative, use_stdin,
                           use_inp_file)
    else:
        run_core_inner(programs, inp_file_relative, use_stdin,
                       use_inp_file)


def run_core_inner(programs, inp_file_relative, use_stdin=False,
                   use_inp_file=True):
    for program in programs:
        if hasattr(program, '__call__'):
            if use_inp_file:
                program(inp_file_relative)
            else:
                program()
        else:
            if use_inp_file:
                if use_stdin:
                    run_prog(program, [], stdin_f=inp_file_relative)
                else:
                    run_prog(program, [inp_file_relative])
            else:
                run_prog(program)


def add_to_fname(fname, add=''):
    fname_list = fname.split('.')
    fname_list[-2] = fname_list[-2]+add
    return '.'.join(fname_list)


def rerun(replacements, lworkdir, inp_file, programs, filter_func='f90nml'):
    inp_file_replace = add_to_fname(inp_file, '_rerun')
    with cwd(lworkdir):
        input_file_handling.INP_FILE_FILTERS[filter_func](inp_file,
                                                          inp_file_replace,
                                                          replacements)
        save_info_in_file('re_hostname.txt', 'hostname')
        save_info_in_file('restarted.txt', 'date')
        run_core(programs, inp_file_replace, lworkdir)
        save_info_in_file('re_ended.txt', 'date')


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def product_replacements(product_iters):
    from itertools import product
    for value_set in product(*product_iters.values()):
        yield dict(zip(product_iters.keys(), value_set))


def co_replacements(co_iters):
    if len(co_iters) >= 1:
        for vector in zip(*co_iters.values()):
            yield dict(zip(co_iters.keys(), vector))
    else:
        yield {}


def chain_replacements(chain_iters):
    if len(chain_iters) >= 1:
        for key, chain_iter in chain_iters.items():
            for value in chain_iter:
                yield {key: value}
    else:
        yield {}


def replace_iter_gen(product_iters={}, chain_iters={}, co_iters={},
                     just_replace={}):
    for prod_iter in product_replacements(product_iters):
        for chain_iter in chain_replacements(chain_iters):
            for co_iter in co_replacements(co_iters):
                yield merge_dicts(merge_dicts(merge_dicts(just_replace,
                                                          prod_iter),
                                              chain_iter),
                                  co_iter)


def check_dirs(dirs):
    if not isinstance(dirs, Dirs):
        dirs = Dirs(dirs)
    return dirs

from functools import partial
def pick_filter_func(filter_func, calc_all):
    return partial(calc_all,filter_func=filter_func)


def execute(programs, input_file, dirs,
            chain_iters={}, product_iters={}, co_iters={}, just_replace={},
            filter_func='f90nml', use_stdin=False,
            calc_all=calc_all, **kwargs):
    """Run sequence of programs with different parameters defined by iters.

    :param list programs: List of strings with names of programs. Should
        contain absolute paths. Could alternately contain functions

    :param str input_file: Input file

    :param runana.run.Dirs dirs: Base directory in which programs will be run
    :type dirs: str or runana.run.Dirs

    :param dict chain_iters: Entries of the form
        {'Name of parameter':[*values to replace with*]}

    :param dict product_iters: Like `chain_iters`, but runs all combinations

    :param dict co_iters: Runs with several parameters changing simultanously

    :param dict just_replace: Entries of the form
        {'Name of parameter':*value to replace with*}

    :param str filter_func: Which filter function to use. Options are listed
        as keys in the INPUT_FILE_FILTERS dictionary

    :param bool use_stdin: send in the content of the filtered input file
        through stdin rather passing the name of the input file as the
        first command line argument

    :param func calc_all: Hook for the parallel decorator, please ignore
         this argument
    """
    dirs = check_dirs(dirs)
    input_file = path.abspath(input_file)
    calc_all = pick_filter_func(filter_func, calc_all)
    dir_IDs = []
    for replacers in replace_iter_gen(product_iters=product_iters,
                                      chain_iters=chain_iters,
                                      co_iters=co_iters,
                                      just_replace=just_replace):
        dir_ID = calc_all(replacers, dirs, input_file, programs,
                          use_stdin=use_stdin, **kwargs)
        dir_IDs.append(dir_ID)
    return dir_IDs


def execute_lock_par(lock, parallel, *args, **kwargs):
    """ Convenience function for running execute with a lock and/or in parallel """
    execute_here = execute
    if parallel:
        execute_here = parallel_wrap(parallel)(execute_here)
    if lock:
        execute_here = lock_wrap(lock)(execute_here)
    return execute_here(*args, **kwargs)


def common_start(chain_iters, just_replace):
    """ Returns modified `chain_iters` and `just_replace` such that the
 calculations will start at the first value of each variable in chain_iter
    """
    chain_iters_out = chain_iters.copy()
    replacers = {}
    if len(chain_iters_out) > 0:
        for (key, elem) in chain_iters_out.items():
            replacers[key] = elem.pop(0)
        else:
            elem.insert(0, replacers[key])
    just_replace = just_replace.copy()
    just_replace.update(replacers)
    return chain_iters_out, just_replace


class PoolApplyAsyncWrap(object):
    def __init__(self, pool):
        self.pool = pool

    def __call__(self, fun):
        def wrapped_f(*args, **kwargs):
            import copy
            for arg in args:
                print(arg)
                copy.deepcopy(arg)
            args = copy.deepcopy(args)
            kwargs = copy.deepcopy(kwargs)
            ret = self.pool.apply_async(fun, args, kwargs)
            return ret
        return wrapped_f


@contextmanager
def multi_stuff(parallel, kwargs):
    import multiprocessing
    import signal

    def initializer():
        """Ignore CTRL+C in the worker process."""
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    number_of_cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(number_of_cpus, initializer=initializer)

    if parallel == 'Calc all':
        kwargs['calc_all'] = PoolApplyAsyncWrap(pool)(calc_all)
    elif parallel == 'auto_converge_var':
        if 'auto_converge_var' in kwargs:
            kwargs['auto_converge_var'] = PoolApplyAsyncWrap(pool)(kwargs['auto_converge_var'])
        else:
            kwargs['auto_converge_var'] = PoolApplyAsyncWrap(pool)(auto_converge_var)
    try:
        yield kwargs
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
        pool.join()
        raise


import collections
def map_nested_dicts(dict_, func):
    if isinstance(dict_, collections.Mapping):
        ret = dict((k, map_nested_dicts(v, func)) for k, v in dict_.items()) 
    else:
        ret = func(dict_)
    return ret


def parallel_wrap(parallel=None):
    def decorate(fun):
        @wraps(fun)
        def call(*args, **kwargs):
            if parallel is None:
                converged_parameters = fun(*args, **kwargs)
            else:
                with multi_stuff(parallel, kwargs) as kwargs:
                    converged_parameters = fun(*args, **kwargs)
                    if converged_parameters:
                        converged_parameters = list(map(lambda x: x.get(), converged_parameters))
                        # converged_parameters = map_nested_dicts(converged_parameters, lambda x: x.get())
                # converged_parameters = multi_stuff(parallel, fun, args, kwargs)
            return converged_parameters
        return call
    return decorate


def lock_wrap(dir_):
    def decorate(fun):
        @wraps(fun)
        def call(*args, **kwargs):
            import fcntl
            makedir(dir_)
            pid_file = path.join(dir_, 'lock.pid')
            with open(pid_file, 'w') as lock_fp:
                try:
                    fcntl.lockf(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    print('Another instance is running')
                    print('Lock file ', pid_file)
                    raise SystemExit
                try:
                    ret = fun(*args, **kwargs)
                    fcntl.lockf(lock_fp, fcntl.LOCK_UN)
                finally:
                    fcntl.lockf(lock_fp, fcntl.LOCK_UN)
            return ret
        return call
    return decorate


INTERVALS = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )


def display_time(seconds, granularity=2, intervals=INTERVALS):
    list_ = display_time_list(seconds, granularity=granularity,
                              intervals=intervals)
    return ', '.join(list_)
    # result = []
    # for name, count in intervals:
    #     value = seconds // count
    #     if value:
    #         seconds -= value * count
    #         if value == 1:
    #             name = name.rstrip('s')
    #         result.append("{0:.0f} {1}".format(value, name))
    # return ', '.join(result[:granularity])


def display_time_list(seconds, granularity=2, intervals=INTERVALS):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{0:.0f} {1}".format(value, name))
    return result[:granularity]


@contextmanager
def print_time(file_=stdout):
    """ Contextmanager that prints how much time was spent in it"""
    import time
    start = time.time()
    yield
    end = time.time()
    print(display_time(end-start), file=file_)


def rel_err_rel_var(O1, O2, x1, x2):
    """ Estimate of relative error `abs(x2/(x2-x1)*(O1-O2)/O2)` """
    return abs(x2/(x2-x1)*(O1-O2)/O2)

class ConvCrit(object):
    """ Contains information on how to check for convergence.

    :parameter func data_read: Function which will be executed in the directory in which the programs was run. It should return the observable in terms of which convergence is sought

    :parameter float eps: Desired precision

    :parameter func conv_funv: Function that calculates convergence criterion. It should take 4 arguments, `f(O1,O2,x1,x2)`, where `x1` and `x2` are the values of the numerical parameter at the current and previous calculation and `O1` and `O2` are the corresponding observable values

    """
    def __init__(self, data_read, eps = 1.0e-3, conv_func = rel_err_rel_var, itermax=10, common_start=False):
        self.eps = eps
        self.conv_func = conv_func
        self.data_read = data_read
        self.itermax = itermax
        self.common_start = common_start


def make_run_string(replacers):
    replacers = dict((is_it_tuple(key), elem) for key, elem in replacers.items())
    return str(replacers)


def float_also_array(varvalue):
    try:
        varvalue_f = float(varvalue)
    except TypeError:
        varvalue_f = varvalue[0]
    return varvalue_f


def auto_converge_var(var_name, var, replacements, dirs, inp_file, programs, conv_crit):
    data_read = conv_crit.data_read
    prevdirID = getattr(var, 'dirID', None)
    yield_diff = 1.0
    iteration = 1
    if prevdirID is None:
        iteration = 0
    for iteration, varvalue in enumerate(var, start=iteration):
        replacers = merge_dicts(replacements,{var_name:varvalue})
        dirID = calc_all(replacers, dirs, inp_file, programs, print_finish=False)
        if not prevdirID is None:
            # print(prevdirID,varvalue_prev,varvalue,data_read(path.join(dirs.local_scratch_base, dirID))
            with cwd(path.join(dirs.local_scratch_base, prevdirID)):
                O1 = data_read()
            with cwd(path.join(dirs.local_scratch_base, dirID)):
                O2 = data_read()
            yield_diff = conv_crit.conv_func(O1,O2,
                                             float_also_array(varvalue_prev),
                                             float_also_array(varvalue))
        try:
            print('{: <10.10}\t {:.2f}\t {:.2e}\t {}\t {}'.format(var_name[1], varvalue,
                                                                  yield_diff, iteration, dirID))
        except ValueError:
            print('{: <10.10}\t {}\t {:.2e}\t {}\t {}'.format(var_name[1], varvalue,
                                                                  yield_diff, iteration, dirID))
        if (abs(yield_diff) < conv_crit.eps):
            break
        prevdirID = dirID
        varvalue_prev = varvalue
    return {'VarValue': varvalue, 'PrevVarValue': varvalue_prev, 'iteration': iteration+1}


def auto_conv_sub(chain_iters,replacers, dirs, inp_file, programs, conv_crit, auto_converge_var):
    results={}
    for chain_iter in chain_iters:
        results[chain_iter] = auto_converge_var(chain_iter, chain_iters[chain_iter],
                                                replacers, dirs, inp_file, programs, conv_crit)
    return results


def auto_conv(programs, inp_file, dirs, conv_crit, chain_iters,
              product_iters={}, co_iters={}, just_replace={},
              auto_converge_var=auto_converge_var, auto_conv_sub=auto_conv_sub):
    """ Run programs until converged or chain_iters is exhausted.

    :param list programs: List of strings with names of programs. Should contain absolute paths. Could alternately contain functions

    :param str input_file: Input file

    :param runana.run.Dirs dirs: Base directory in which programs will be run
    :type dirs: str or runana.run.Dirs

    :param runana.run.ConvCrit conv_crit: Object specifying type of convergence

    :param dict chain_iters: Entries of the form {'Name of parameter':[*values to replace with*]}

    :param dict product_iters: Like `chain_iters`, but runs all combinations

    :param dict co_iters: Runs with several parameters changing simultanously

    :param bool use_stdin: send in the content of the filtered input file through stdin rather passing the name of the input file as the first command line argument
    """
    # :param dict just_replace: Entries of the form {'Name of parameter':*value to replace with*}
    # :param str filter_func: Which filter function to use. Options are listed as keys in the INPUT_FILE_FILTERS dictionary
    dirs = check_dirs(dirs)
    inp_file = path.abspath(inp_file)
    results = {}
    for replacers in replace_iter_gen(product_iters=product_iters,
                                      co_iters=co_iters,
                                      just_replace=just_replace):
        run_string = make_run_string(replacers)
        results[run_string] = auto_conv_sub(chain_iters,replacers, dirs, inp_file, programs,
                                        conv_crit, auto_converge_var)
    return results


def intercept_argument(args, kwargs, iarg, name):
    if len(args)>iarg:
        ret = args[iarg]
    else:
        ret = kwargs.get(name)
    return ret

def reinsert_argument(args, kwargs, iarg, name, argument):
    if len(args)>iarg:
        args= args[:iarg] + (argument, ) + args[iarg+1:]
    else:
        kwargs[name] = argument
    return args, kwargs


def inject_status(recursion_dict):
    def decorate(fun):
        @wraps(fun)
        def call(*args, **kwargs):
            chain_iters = intercept_argument(args, kwargs, 0, 'chain_iters')
            replacements = intercept_argument(args, kwargs, 1, 'replacements')
            
            run_string = make_run_string(replacements)
            this_converged = recursion_dict[run_string].get('This Converged', False)
            if not this_converged:
                replacers = recursion_dict[run_string].get('Replacers', {})
                if replacers:
                    chain_iters_new = {}
                    for (key,var) in chain_iters.items():
                        var = var[var.index(replacers[key]):]
                        chain_iters_new[key] = var
                    replacements = merge_dicts(replacements, replacers)
                args, kwargs = reinsert_argument(args, kwargs, 0, 'chain_iters', chain_iters_new)
                args, kwargs = reinsert_argument(args, kwargs, 1, 'replacements', replacements)
                return fun(*args, **kwargs)
            else:
                return {}
        return call
    return decorate

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

def auto_conv_rerun(fun):
    """ Decorator for rerunning :func:`auto_conv`, until convergence is achieved in 
the first two calculations for each parameter. This is useful for cases where 
parameters are strongly correlated"""
    @wraps(fun)
    @static_vars(status={})
    def call(*args, **kwargs):
        converged_parameters = fun(*args, **kwargs)
        everything_converged=True
        for run_string in converged_parameters:
            replacements={}
            prevvarvalues={}
            call.status[run_string]=call.status.get(run_string, {})
            this_converged = call.status[run_string].get('This Converged', False)
            if not this_converged:
                this_converged = True
                for var_name in converged_parameters[run_string]:
                    replacements[var_name]=converged_parameters[run_string][var_name]['VarValue']
                    if converged_parameters[run_string][var_name]['iteration']>2:
                        this_converged = False
                        everything_converged = False
                    prevvarvalues[var_name]=converged_parameters[run_string][var_name]['PrevVarValue']
                if this_converged:
                    call.status[run_string]['Final replacements'] = replacements
                call.status[run_string]['This Converged'] = this_converged
                call.status[run_string]['Replacers'] = prevvarvalues
                call.status[run_string]['Run no'] = call.status[run_string].get('Run no', 0)+1
        import pprint
        pprint.pprint(call.status)
        if not everything_converged:
            auto_conv_handle = inject_status(call.status)(auto_conv_sub)
            kwargs.update({'auto_conv_sub': auto_conv_handle})
            converged_parameters=call(*args, **kwargs)
        else:
            converged_parameters=call.status
        return converged_parameters
    return call
