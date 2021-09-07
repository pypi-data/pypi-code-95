# -*- coding: utf-8 -*-
#
#    TypeAtlas External Commands
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

from collections import namedtuple, OrderedDict
import subprocess as sp
import shutil
import shlex
import os
import os.path
import sys
import traceback

import typeatlas
from collections.abc import Callable
from typeatlas.util import generic_type

Union = generic_type('Union')
Optional = generic_type('Optional')
Literal = generic_type('Literal')
AnyStr = generic_type('AnyStr')
SequenceOf = generic_type('Sequence')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
MappingOf = generic_type('Mapping')
TupleOf = generic_type('Tuple')


STOP = object()

DEFAULT_NEWLINE = b'\n'
N_ = lambda s: s
_UNSPECIFIED = object()

ON_DEMAND = object()

commands_by_provisions = {}
commands_by_executable = {}


def commands_providing(executor: 'Executor',
                       provision: str) -> 'IteratorOf[ExternalCommand]':
    """Yield all external commands providing the requested provision
    (i.e. program) using the provided executor.

    For example, commands_providing(Executor(), 'fc-list') yield
    commands that call fc-list locally using subprocess.Popen().
    And 'ssh-execute' would provide SSH execution, whereas 'font-view'
    would provide commands providing external viewers.
    """

    commands = []
    for cls in commands_by_provisions.get(provision, ()):
        command = cls(executor)
        if command.available():
            yield command


def command_providing(executor: 'Executor',
                      provision: str,
                      default=_UNSPECIFIED) -> 'Optional[ExternalCommand]':
    """Return an external command providing the requested provision
    (i.e. program) using the provided executor.

    For example, command_providing(Executor(), 'fc-list') returns
    a command that call fc-list locally using subprocess.Popen().
    """
    for command in commands_providing(executor, provision):
        return command

    if default is _UNSPECIFIED:
        raise KeyError(provision)
    return default


def register(cls: type) -> type:
    """Register a given class to provide external commands.

    The commands which it provides are taken from its provides attribute,
    which needs to be an iterable.

    This can be used as a decorator."""

    for provision in cls.provides:
        commands_by_provisions.setdefault(provision, []).append(cls)
    commands_by_executable.setdefault(cls.executable, []).append(cls)
    return cls


def get_line_maker_callbacks(line_callback: Callable,
                             exit_callback: Callable,
                             delimiter: bytes=DEFAULT_NEWLINE,
                             ) -> TupleOf[Callable, Callable]:
    """Convert a line and exit callback to data and exit callback.

    You provide a callback that accepts processed lines of bytes as arguments,
    and  a callback that is called on exit or completion of an external command.
    Returned are a callback that accepts chunks of byte data, and anopther callback
    that is called on exit or completion.

    The chunks are merged progressively as the returned data callback is called,
    and any lines found along the way are split and passed to your line callback.

    Your callbacks will be called respectively. Your exit callback will be
    called with the same arguments as the returned one will be, but after
    any remaining lines are passed back to the line callback.

    You can change the delimited from b'\n'.

    This method only supports bytes, supporting strings is left as an exercise
    for the reader.
    """

    buf = [b'']

    def line_wrapper(data: bytes):
        data = buf[0] + data
        lines = data.split(delimiter)
        if data != b'':
            buf[0] = lines.pop()

        for line in lines:
            if line_callback(line) is STOP:
                return STOP

    def exit_wrapper(*args, **kwargs):
        if buf[0]:
            # XXX Should always be one line
            for line in buf[0].split(delimiter):
                line_callback(line)
        return exit_callback(*args, **kwargs)

    return line_wrapper, exit_wrapper


def get_merger_callbacks(data_callback: Callable,
                         exit_callback: Callable,
                         ) -> TupleOf[Callable, Callable]:

    """Convert a callback that receives the entire data, and an exit callback,
    to a pair of callbacks that receives data chunks and handle exit.

    You provide a callback that receives the entire data as bytes or str,
    and a callback called at exit. Returned is a callback that accepts data
    chunks, and one to be called at completion or exit.

    The chunks received are accumulated as the returned data callback is
    called, until completion, when a single merged string is passed to
    your data_callback, and then your exit callback is called with the same
    arguments as the original one was.

    If NO CHUNKS are received, your data callback is not called at all.

    This method supports both str and bytes.
    """

    buf = []

    def data_wrapper(data: AnyStr):
        buf.append(data)

    def exit_wrapper(*args, **kwargs):
        if buf and isinstance(buf, str):
            data_callback(''.join(buf))
        else:
            data_callback(b''.join(buf))
        return exit_callback(*args, **kwargs)

    return data_wrapper, exit_wrapper


class Call(object):

    """A call to an external commands, containing arguments, environment,
    and CallCallbacks instance to process the result."""

    def __init__(self, args: SequenceOf[AnyStr],
                       env: MappingOf[AnyStr, AnyStr]=None,
                       postprocess_callbacks: 'CallCallbacks'=None):
        self.args = args
        self.env = env
        self.postprocess_callbacks = postprocess_callbacks


class CallDefinition(object):

    """A special descriptor to decorate a method of ExternalCommand for
    calling external commands. Use the cls.make() decorator.

    The decorated method will return the arguments or Call() instance, and
    if an executor is present, it will be executed. Otherwise, the arguments
    will be returned.

    A translatable description can be added for each definition, which
    will be used in the GUI for locating external commands. As well as the
    name of an argument (presently unused).

    If wait=True is passed, the process is waited for, and postprocessing
    is performed. If wait=ON_DEMAND is passed to the class, the actual
    waiting is up to the caller.

    For commands expecting result, wait=True is to be used. For commands
    that are started (e.g. an external font viewer), wait=False (default)
    is to be used. For commands executing other commnads (e.g. ssh),
    wait=ON_DEMAND is to be used.

    The line_output argument is presently unused.
    """

    def __init__(self, function: Callable,
                       description: str=None,
                       wait: 'Union[bool, Literal[ON_DEMAND]]'=False,
                       line_output: bool=True, argument: str=None,
                       postprocess_callbacks: 'CallCallbacks'=None):
        self.function = function
        self.description = description
        self.wait = wait
        self.postprocess_callbacks = postprocess_callbacks

    @classmethod
    def make(cls, *args, **kwargs) -> Callable:
        """Return a decorator that turns a method a call definition, making
        it callable with your loaded executor."""
        def decorator(func):
            return cls(func, *args, **kwargs)
        return decorator

    def __call__(self, instance, *args, **kwargs):
        """Calls the method, processing any output and waiting if requested."""
        exec_kwargs = {}

        callbacks = kwargs.pop('callbacks', instance.executor.callbacks)

        if self.wait is ON_DEMAND:
            exec_kwargs['wait'] = kwargs.pop('wait', False)

        call = self.function(instance, *args, **kwargs)

        if not isinstance(call, Call):
            cmdline_args = call
        else:
            cmdline_args = call.args
            postprocess = call.postprocess_callbacks
            if postprocess is None:
                postprocess = self.postprocess_callbacks
            if postprocess is not None:
                callbacks = postprocess.result_wrapper(callbacks)
            exec_kwargs['env'] = call.env 

        exec_kwargs['callbacks'] = callbacks

        if instance.executor:
            return instance.executor.execute(self, instance,
                                             cmdline_args,
                                             **exec_kwargs)

        return cmdline_args

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return CallDefinitionMethod(self, instance)


class CallDefinitionMethod(object):

    """A bound variant of CallDefinition that calls the call definition
    with self as required."""

    def __init__(self, definition, instance):
        self.definition = definition
        self.instance = instance

    def __getattr__(self, attr):
        return getattr(self.definition, attr)

    def __call__(self, *args, **kwargs):
        return self.definition(self.instance, *args, **kwargs)


RETURN_DEFAULT = object()


class ResultCallbacks(object):

    """Result callbacks for the post-processed output of the commands.

    These are used by command *callers* to get the result and/or error
    asynchronously, providing a result and error callback.

    They are different from the postprocess callbacks used internally to
    postproces the result (see below for CallCallbacks).

    If error_callback is RETURN_DEFAULT (the default), the provided
    default is given to the result_callback(). The exception printed
    on stderr, unless callable error_callback is provided.
    """

    def __init__(self, result_callback: Callable=None,
                       error_callback: Callable=RETURN_DEFAULT,
                       default=None):
        if result_callback is not None:
            self.handle_result = result_callback

        self.default_on_error = False
        if error_callback is RETURN_DEFAULT:
            self.default_on_error = True
        elif error_callback is not None:
            self.handle_error = error_callback

        self.default = default

    def handle_result(self, result):
        """Handle the result. This is replaced by the result_callback if
        provided, and you can override in subclass."""
        return result

    def handle_error(self, exc_type, exc_value, exc_traceback):
        """Handle error. The default prints the exception to stderr,
        and if requested, gives the default to the result handler."""
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        if self.default_on_error:
            return self.handle_result(self.default)


class CallCallbacks(object):

    """Callbacks for post-processing the output to get a single result.


    These are used internally by the commands, and different from the
    result callbacks provided by the command callers to get the result
    asynchronously (see above for ResultCallbacks).

    They can contain a stdout and exit callback, receiving the stdout and
    exit code, respectively, line_mode=True (default) makes sure that
    is provided as lines, and chunked=False and line_mode=False makes
    sure it is merged into a single bytestring instead.

    If merge_outputs=True is passed, stderr is passed to stdout.

    A command can require blocking or non-blocking mode, which is an odd
    thing to do.

    You can provide a bufsize other than the default of 256 KB.
    """

    def __init__(self, stdout_callback: Callable=None,
                       exit_callback: Callable=None,
                       line_mode: bool=True,
                       chunked: bool=True,
                       bufsize: int=256 * 1024,
                       merge_outputs: bool=False,
                       require_blocking: bool=False,
                       require_nonblocking: bool=False):

        if stdout_callback is not None:
            self.process_stdout = stdout_callback
        if exit_callback is not None:
            self.handle_exit = exit_callback

        self.line_mode = line_mode
        self.chunked = chunked
        self.bufsize = bufsize

        self.require_blocking = require_blocking
        self.require_nonblocking = require_nonblocking

        self.merge_outputs = merge_outputs

    def result_wrapper(self, callbacks: ResultCallbacks=None) -> 'CallCallbacks':
        """Wrap ResultCallbacks and return a new CallCallbacks which
        will call the caller's ResultCallbacks callback."""
        if callbacks is None:
            return self

        exit_handler = self.handle_exit

        def exit_wrapper(exitcode):
            try:
                result = exit_handler(exitcode)
            except:
                exc_tuple = sys.exc_info()
                return callbacks.handle_error(*exc_tuple)
            else:
                return callbacks.handle_result(result)

        cls = type(self)

        return cls(self.process_stdout, exit_wrapper,
                   line_mode=self.line_mode, chunked=self.chunked,
                   merge_outputs=self.merge_outputs,
                   require_blocking=self.require_blocking,
                   require_nonblocking=self.require_nonblocking)

    def chunked_wrapper(self) -> 'CallCallbacks':
        """Return a CallCallbacks instance that accepts chunked output, and
        cannot provide line_mode themselves.

        This should be called by executors that provide such output, like Qt."""
        if self.chunked and not self.line_mode:
            return self
        cls = type(self)

        if self.line_mode:
            return cls(*get_line_maker_callbacks(
                              self.process_stdout,
                              self.handle_exit),
                       line_mode=False, chunked=True,
                       merge_outputs=self.merge_outputs,
                       require_blocking=self.require_blocking,
                       require_nonblocking=self.require_nonblocking)
        else:
            return cls(*get_merger_callbacks(
                              self.process_stdout,
                              self.handle_exit),
                       line_mode=False, chunked=True,
                       require_blocking=self.require_blocking,
                       require_nonblocking=self.require_nonblocking)

    @classmethod
    def single(cls, callback: Callable,
                    line_mode: bool=True,
                    chunked: bool=False,
                    *args, **kwargs) -> 'CallCallbacks':
        """Create CallCallbacks instance that accepts both exit code and stdout
        in a single callback."""
        stdout = []

        def stdout_callback(data):
            stdout.append(data)

        def exit_callback(exitcode):
            if chunked or line_mode:
                return callback(exitcode, stdout)
            else:
                return callback(exitcode, stdout[0])

        return cls(stdout_callback, exit_callback,
                   line_mode=line_mode, chunked=chunked, *args, **kwargs)

    def process_stdout(self, data: bytes):
        """Process part of the output or the whole output. This is replaced
        with the stdout  callback provided to the constructor."""
        pass

    def handle_exit(self, exitcode: int):
        """Handle the exit code. This is replaced with the exit callback
        provided to the constructor."""
        return exitcode


class ExecutorCallbacksWrapper(object):

    """An executor wrapper that provides given set of processing CallCallbacks
    callbacks to it automatically for every command.

    This is used by the with_callbacks() executor method, which is not seeing
    much use.
    """

    def __init__(self, executor: 'Executor',
                       callbacks: CallCallbacks=None):
        self.executor = executor
        self.callbacks = callbacks

    def __getattr__(self, attr):
        return getattr(self.executor, attr)

    def execute(self, call: CallDefinition,
                      command: 'ExternalCommand',
                      args: SequenceOf[AnyStr],
                      callbacks: CallCallbacks=_UNSPECIFIED,
                      *a, **kw):
        if callbacks is _UNSPECIFIED:
            callbacks = self.callbacks

        return self.executor.execute(call, command, args,
                                     callbacks=callbacks,
                                     *a, **kw)


class ExecutionModeUnsupportedError(RuntimeError):
    pass


class BlockingModeUnsupported(ExecutionModeUnsupportedError):
    pass


class NonblockingModeUnsupported(ExecutionModeUnsupportedError):
    pass


class Executor(object):

    """An executor for commands that uses Python's subprocess by default.

    It accepts custom_paths to specify the full path to a command executable,
    or to forward it to a wrapper found in your operating system.

    It can also include default CallCallbacks which is seldom used as default ones.
    """

    def __init__(self, custom_paths: MappingOf[str, str]={},
                       callbacks: CallCallbacks=None, *args, **kwargs):
        super(Executor, self).__init__(*args, **kwargs)
        self.custom_paths = custom_paths
        self.callbacks = callbacks

    def with_callbacks(self, callbacks) -> ExecutorCallbacksWrapper:
        """Get a wrapped executor with changed default callbacks."""
        return ExecutorCallbacksWrapper(self, callbacks)

    def get_executable_path(self, executable: str) -> Optional[str]:
        """Get the path of a given executable."""
        path = self.custom_paths.get(executable)
        if path is not None and os.access(path, os.X_OK):
            return path
        return shutil.which(executable)

    def executable_available(self, executable_path: Optional[str]) -> bool:
        """Return True if the executable is available (its path is not
        None)."""
        return executable_path is not None

    def execute(self, call: CallDefinition,
                      command: 'ExternalCommand',
                      args: SequenceOf[AnyStr],
                      env: MappingOf[AnyStr, AnyStr]=None,
                      callbacks: CallCallbacks=_UNSPECIFIED,
                      wait: 'Union[bool, Literal[ON_DEMAND]]'=_UNSPECIFIED):
        """Execute the given command, using the provided definition,
        external command instance, arguments, environment, processing
        callbacks (that *can* wrap result callbacks that will call the
        original caller's callbacks asynchronously)."""

        if callbacks is _UNSPECIFIED:
            callbacks = self.callbacks

        if callbacks.require_nonblocking:
            raise NonblockingModeUnsupported('subprocess is always blocking')

        if wait is _UNSPECIFIED:
            wait = call.wait

        if env is not None:
            procenv = dict(os.environ)
            procenv.update(env)
        else:
            procenv = None

        popen_kwargs = {}

        if wait and callbacks is not None:
            popen_kwargs['stdout'] = sp.PIPE
            if callbacks.merge_outputs:
                popen_kwargs['stderr'] = sp.STDOUT

        p = sp.Popen(args, env=procenv, **popen_kwargs)

        if wait:
            if callbacks is not None:
                if callbacks.line_mode:
                    for line in p.stdout:
                        callbacks.process_stdout(line.rstrip(DEFAULT_NEWLINE))
                elif callbacks.chunked:
                    while True:
                        buf = p.stdout.read(callbacks.bufsize)
                        if not buf:
                            break
                        callbacks.process_stdout(buf)
                else:
                    callbacks.process_stdout(p.stdout.read())

            exitcode = p.wait()

            if callbacks is not None:
                return callbacks.handle_exit(exitcode)
            return exitcode


class ExternalCommand(object):

    """An external command, like ssh, fc-list

    The command calls are provided by the class, and it is instantiated
    with an executor and custom executable path. The latter is filled
    automatically from the executor if not provided.
    """

    kind = 'command'
    provides = []

    executable = None
    icon = None

    def __init__(self, executor: Executor, executable_path: str=None):
        if not executable_path:
            executable_path = executor.get_executable_path(self.executable)
        self.executable_path = executable_path
        self.executor = executor

    def available(self) -> bool:
        """Return True if the command is available with the given executor."""
        return self.executor.executable_available(self.executable_path)


class SshExecutor(Executor):

    """An executor that uses SSH to execute commands remotely on a host."""

    def __init__(self, ssh: 'SshCommand', host: str,
                       callbacks: CallCallbacks=None):
        self.ssh = ssh
        self.host = host
        self.callbacks = callbacks

    def get_executable_path(self, executable: str) -> Optional[str]:
        # Opportunistic approach - hope it's in PATH on remote side
        return executable

    def executable_available(self, executable_path: str) -> bool:
        # Opportunistic approach - assume its available if ssh is available
        return self.ssh.available()

    def execute(self, call: CallDefinition,
                      command: ExternalCommand,
                      args: SequenceOf[AnyStr],
                      callbacks: CallCallbacks=_UNSPECIFIED,
                      wait: 'Union[bool, Literal[ON_DEMAND]]'=_UNSPECIFIED):

        if callbacks is _UNSPECIFIED:
            callbacks = self.callbacks

        if wait is not _UNSPECIFIED:
            wait = call.wait

        return self.ssh.remote_execute(self.host, args,
                                       wait=wait,
                                       callbacks=callbacks)


@register
class SshCommand(ExternalCommand):

    """SSH command for executing other commands remotely. That's used
    by the SshExecutor."""

    provides = ['ssh-executor', 'ssh-execute',
                'remote-executor', 'remote-execute']
    executable = 'ssh'

    def get_remote_executor(self, host):
        return SshExecutor(self, host)

    get_ssh_executor = get_remote_executor

    @CallDefinition.make(description=N_("Execute command with OpenSSH"),
                         wait=ON_DEMAND)
    def remote_execute(self, host: str, args: SequenceOf[str]):
        """Execute a remote command"""
        args = [arg if isinstance(arg, str) else arg.decode('ascii')
                for arg in args]

        return [self.executable_path, '-o', 'BatchMode=yes', '--', host,
                ' '.join(shlex.quote(arg) for arg in args)]

    ssh_execute = remote_execute

PackageFormat = namedtuple('PackageFormat', 'ext description icon')
PackageResult = namedtuple('PackageResult', 'format name')


package_formats = {
    'deb': PackageFormat('deb', N_('Debian package'), 'application-x-deb'),
    'rpm': PackageFormat('deb', N_('RPM package'), 'application-x-rpm'),
}


def _dpkg_callbacks(filename: str=None) -> CallCallbacks:

    """Return callbacks for parsing dpkg output."""

    result = OrderedDict()

    def line_callback(line):
        package, sep, filename = line.decode('utf8').partition(':')
        if not sep: 
            return
        filename = filename.lstrip().rstrip('\n')
        result[filename] = PackageResult('deb', package.strip())

    def exit_callback(exitcode):
        if filename is not None:
            result.get(filename)
        return result

    return CallCallbacks(line_callback, exit_callback, 
                         line_mode=True)


@register
class DpkgCommand(ExternalCommand):

    """A dpkg command for discovering package information."""

    provides = ['find-file-package', 'find-files-packages', 'dpkg']
    executable = 'dpkg'

    @CallDefinition.make(description=N_("Find the package containing file"),
                         wait=True)
    def find_file_package(self, filename: str):
        """Find the package containing given file."""
        return Call([self.executable_path, '-S', '--', filename],
                    postprocess_callbacks=_dpkg_callbacks(filename),
                    env=dict(LC_ALL='C.UTF-8'))

    @CallDefinition.make(description=N_("Find the package containing file"),
                         wait=True)
    def find_files_packages(self, filenames: IterableOf[str]):
        """Find the packages containing a given iterable of files."""
        return Call([self.executable_path, '-S', '--'] + list(filenames),
                    postprocess_callbacks=_dpkg_callbacks(),
                    env=dict(LC_ALL='C.UTF-8'))


def _rpm_callbacks(filenames: IterableOf[str],
                   filename: str=None) -> CallCallbacks:

    """Return callbacks for parsing rpm output."""

    # FIXME: WRONG?

    result = OrderedDict()
    filenames = iter(filenames)

    def line_callback(line):
        try:
            filename = next(filenames)
        except StopIteration:
            return
        if line.startswith(b'error: ') or b'not owned' in line:
            return
        package = line.decode('utf8').strip()
        result[filename] = PackageResult('rpm', package)

    def exit_callback(exitcode):
        if filename is not None:
            result.get(filename)
        return result

    return CallCallbacks(line_callback, exit_callback, 
                         line_mode=True, merge_outputs=True)


@register
class RpmCommand(ExternalCommand):

    """A rpm command for discovering package information."""

    provides = ['find-file-package', 'find-files-packages', 'rpm']
    executable = 'rpm'

    @CallDefinition.make(description=N_("Find the package containing file"),
                         wait=True)
    def find_file_package(self, filename: str):
        """Find the package containing given file."""
        return Call([self.executable_path, '-q', '-f', '--', filename],
                    postprocess_callbacks=_rpm_callbacks([filename], filename),
                    env=dict(LC_ALL='C.UTF-8'))

    @CallDefinition.make(description=N_("Find the package containing file"),
                         wait=True)
    def find_files_packages(self, filenames: SequenceOf[str]):
        """Find the packages containing a given iterable of files."""
        return Call([self.executable_path, '-q', '-f', '--'] + list(filenames),
                    postprocess_callbacks=_rpm_callbacks(filenames),
                    env=dict(LC_ALL='C.UTF-8'))


@register
class FcListCommand(ExternalCommand):

    """A fc-list command for querying the complete fontconfig font list."""

    provides = ['fc-list']
    executable = 'fc-list'

    @CallDefinition.make(wait=True)
    def custom(self, args: IterableOf[AnyStr]):
        """Run fc-list with custom arguments."""
        return [self.executable_path] + list(args)


@register
class FcMatchCommand(ExternalCommand):

    """A fc-list command for performing custom matches against the fontconfig
    font list."""

    provides = ['fc-match']
    executable = 'fc-match'
    
    @CallDefinition.make(wait=True)
    def custom(self, args: IterableOf[AnyStr]):
        """Run fc-list with custom arguments."""
        return [self.executable_path] + list(args)


@register
class FontForgeCommand(ExternalCommand):

    """Access to any installed fontforge for font opening and editing."""

    provides = ['font-edit', 'font-open']
    executable = 'fontforge'
    icon = 'fontforge'

    @CallDefinition.make(description=N_("Edit with FontForge"), 
                         argument='font')
    def edit(self, font: 'typeatlas.fontlist.FontLike'):
        """Edit font with font forge."""
        return [self.executable_path, os.path.abspath(font.file)]

    open = edit


@register
class KFontViewCommand(ExternalCommand):

    """Access to any installed kfontview for font opening and viewing."""

    provides = ['font-view', 'font-open']
    executable = 'kfontview'
    icon = 'kfontview'

    @CallDefinition.make(description=N_("View with KFontView"),
                         argument='font')
    def view(self, font: 'typeatlas.fontlist.FontLike'):
        """View font with kfontview."""
        return [self.executable_path, os.path.abspath(font.file)]

    open = view


@register
class GnomeFontViewerCommand(ExternalCommand):

    """Access to any installed gnome-font-viewer for font opening
    and viewing."""

    provides = ['font-view', 'font-open']
    executable = 'gnome-font-viewer'
    icon = 'fonts'

    @CallDefinition.make(description=N_("View with GNOME Font Viewer"),
                         argument='font')
    def view(self, font: 'typeatlas.fontlist.FontLike'):
        """View font with gnome-font-view."""
        return [self.executable_path, os.path.abspath(font.file)]

    open = view


@register
class GnomeCharMapCommand(ExternalCommand):

    """Access to any installed gucharmap for font opening and viewing."""

    provides = ['font-view', 'font-open']
    executable = 'gucharmap'
    icon = 'gucharmap'

    @CallDefinition.make(description=N_("Open GNOME Character Map with "
                                        "this font"),
                         argument='font')
    def view(self, font: 'typeatlas.fontlist.FontLike'):
        """View font with gucharmap."""
        return [self.executable_path, '--font', font.fullname + ' 24']

    open = view


@register
class FontyPythonCommand(ExternalCommand):

    """Access to any installed fontypython for font directory viewing."""

    provides = ['directory-open']
    executable = 'fontypython'
    icon = 'fontypython'

    @CallDefinition.make(description=N_("View fonts with Fonty Python"),
                         argument='directory')
    def open(self, path: str):
        """View the directory with fontypython."""
        return [self.executable_path, os.path.abspath(path)]

