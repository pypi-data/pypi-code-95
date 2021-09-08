# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Argufy is an inspection based CLI parser.'''

import inspect
import logging
import sys
import typing
from argparse import ArgumentParser, Namespace, _SubParsersAction
# from dataclasses import is_dataclass
from inspect import Signature, _ParameterKind
from types import ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
)

from docstring_parser import DocstringParam, parse as docstring_parse

from argufy.argument import Argument
from argufy.formatter import ArgufyHelpFormatter

log = logging.getLogger(__name__)

# Define function as parameters for MyPy
F = TypeVar('F', bound=Callable[..., Any])


class Parser(ArgumentParser):
    '''Provide CLI parser for function.'''

    exclude_prefixes = ('@', '_')

    def __init__(self, *args: str, **kwargs: Any) -> None:
        '''Initialize parser.

        Parameters
        ----------
        prog: str
            The name of the program
        usage: str
            The string describing the program usage
        description: str
            Text to display before the argument help
        epilog: str
            Text to display after the argument help
        parents: list
            A list of ArgumentParser objects whose arguments should also
            be included
        formatter_class: Object
            A class for customizing the help output
        prefix_chars: char
            The set of characters that prefix optional arguments
        fromfile_prefix_chars: None
            The set of characters that prefix files from which additional
            arguments should be read
        argument_default: None
            The global default value for arguments
        conflict_handler: Object
            The strategy for resolving conflicting optionals
        add_help: str
            Add a -h/--help option to the parser
        allow_abbrev: bool
            Allows long options to be abbreviated if the abbreviation is
            unambiguous

        '''
        # TODO: handle environment variables

        module = self.__get_parent_module()
        if module:
            docstring = docstring_parse(module.__doc__)
            if not kwargs.get('description'):
                kwargs['description'] = docstring.short_description

            if 'prog' not in kwargs:
                kwargs['prog'] = module.__name__.split('.')[0]

        if 'version' in kwargs:
            self.prog_version = kwargs.pop('version')

        # if 'prefix' in kwargs:
        #     self.prefix = kwargs.pop('prefix')
        # else:
        #     self.prefix = kwargs['prog'].upper()
        # log.debug(self.prefix)

        if 'log_level' in kwargs:
            log.setLevel(getattr(logging, kwargs.pop('log_level').upper()))
        if 'log_handler' in kwargs:
            log_handler = kwargs.pop('log_handler')
            log.addHandler(logging.StreamHandler(log_handler))

        self.use_module_args = kwargs.pop('use_module_args', False)
        self.main_args_builder = kwargs.pop('main_args_builder', None)
        self.command_type = kwargs.pop('command_type', None)
        self.command_scheme = kwargs.pop('command_scheme', None)

        if 'formatter_class' not in kwargs:
            self.formatter_class = ArgufyHelpFormatter

        super().__init__(**kwargs)

        # NOTE: cannot move to formatter
        self._positionals.title = ArgufyHelpFormatter.font(
            self._positionals.title or 'arguments'
        )
        self._optionals.title = ArgufyHelpFormatter.font(
            self._optionals.title or 'flags'
        )

        # XXX version lookup infinite loop when absent
        if hasattr(self, 'prog_version'):
            self.add_argument(
                '--version',
                action='version',
                version=f"%(prog)s {self.prog_version}",
                help='display package version',
            )

    @staticmethod
    def __get_parent_module() -> Optional[ModuleType]:
        '''Get name of module importing this module.'''
        stack = inspect.stack()
        # TODO: need way to better identify parent module
        stack_frame = stack[2]
        result = inspect.getmodule(stack_frame[0]) or None
        return result

    @staticmethod
    def __clean_args(argument: Argument) -> Dict[Any, Any]:
        '''Retrieve cleaned parameters from an Argument.'''
        return {
            k[len('_Argument__'):]: v
            for k, v in vars(argument).items()
            if k.startswith('_Argument__')
        }

    @staticmethod
    def _get_excludes(exclude_prefixes: tuple = tuple()) -> tuple:
        '''Combine class excludes with instance.'''
        if exclude_prefixes != []:
            return tuple(exclude_prefixes) + Parser.exclude_prefixes
        else:
            return Parser.exclude_prefixes

    @staticmethod
    def __get_description(
        name: str, docstring: DocstringParam,
    ) -> Optional[str]:
        '''Get argument description from docstring.'''
        return next((d for d in docstring.params if d.arg_name == name), None)

    @staticmethod
    def __get_keyword_args(
        signature: Signature, docstring: DocstringParam,
    ) -> List[str]:
        '''Get keyward arguments from docstring.'''
        parameters = [x for x in signature.parameters]
        return [
            x.arg_name
            for x in docstring.params
            if x.arg_name not in parameters
        ]

    @staticmethod
    def __generate_parameter(
        name: str, module: ModuleType,
    ) -> inspect.Parameter:
        '''Generate inpect parameter.'''
        parameter = inspect.Parameter(
            name,
            _ParameterKind.POSITIONAL_OR_KEYWORD,  # type: ignore
            default=getattr(module, name),
            annotation=inspect._empty,  # type: ignore
        )
        return parameter

    def add_commands(
        self,
        module: ModuleType,
        parser: Optional[ArgumentParser] = None,
        exclude_prefixes: tuple = tuple(),
        command_type: Optional[str] = None,
    ) -> 'Parser':
        '''Add commands.

        Parameters
        ----------
        module: ModuleType,
            Module used to import functions for CLI commands.
        parser: ArgumentParser, optional
            Parser used to append subparsers to create subcommands.
        exclude_prefixes: tuple,
            Methods from a module that should be excluded.
        command_type: str, optional
            Choose format type of commands to be created.

        Returns
        -------
        self:
            Return object itself to allow chaining functions.

        '''
        # use self or an existing parser
        if not parser:
            parser = self
        parser.formatter_class = ArgufyHelpFormatter

        module_name = module.__name__.split('.')[-1]
        docstring = docstring_parse(module.__doc__)
        excludes = Parser._get_excludes(exclude_prefixes)

        # use exsiting subparser or create a new one
        if not any(isinstance(x, _SubParsersAction) for x in parser._actions):
            # TODO: use metavar for hidden commands
            parser.add_subparsers(dest=module_name, parser_class=Parser)

        # check if command exists
        command = next(
            (x for x in parser._actions if isinstance(x, _SubParsersAction)),
            None,
        )

        # set command name scheme
        if command_type is None:
            command_type = self.command_type

        # create subcommand for command
        if command_type == 'subcommand':
            if command:
                msg = docstring.short_description
                subcommand = command.add_parser(
                    module_name.replace('_', '-'),
                    description=msg,
                    formatter_class=self.formatter_class,
                    help=msg,
                )
                subcommand.set_defaults(mod=module)

            # append subcommand to exsiting command or create a new one
            return self.add_commands(
                module=module,
                parser=subcommand,
                exclude_prefixes=Parser._get_excludes(exclude_prefixes),
                command_type='command',
            )

        for name, value in inspect.getmembers(module):
            # TODO: Possible singledispatch candidate
            if not name.startswith(excludes):
                # skip classes for now
                if inspect.isclass(value):
                    # TODO: check if dataclass instance
                    # TODO: check if class instance
                    continue  # pragma: no cover

                # create commands from functions
                elif inspect.isfunction(value):
                    # TODO: Turn parameter-less function into switch

                    # merge builder function maing_args into parser
                    if (
                        self.main_args_builder
                        and name == self.main_args_builder['function']
                    ):
                        self.add_arguments(value, parser)

                    # create commands from functions
                    elif (
                        module.__name__ == value.__module__
                        and not name.startswith(', '.join(excludes))
                        or (
                            self.main_args_builder
                            and name == self.main_args_builder['function']
                        )
                    ):
                        # create command from function
                        if command:
                            # control command name format
                            if self.command_scheme == 'chain':
                                cmd_name = f"{module_name}.{name}"
                            else:
                                cmd_name = name

                            msg = docstring_parse(value.__doc__)\
                                .short_description
                            cmd = command.add_parser(
                                cmd_name.replace('_', '-'),
                                description=msg,
                                formatter_class=self.formatter_class,
                                help=msg,
                            )
                            cmd.set_defaults(mod=module, fn=value)
                        # add arguments from function
                        # log.debug(f"command {name} {value} {cmd}")
                        self.add_arguments(value, cmd)

                # create arguments from module varibles
                elif (
                    self.use_module_args
                    and not isinstance(value, ModuleType)
                    and not hasattr(typing, name)
                    and (
                        self.main_args_builder
                        and name != self.main_args_builder['instance']
                    )
                ):
                    # TODO: Reconcile inspect parameters with dict
                    # TODO: use argparse.SUPPRESS for hidden arguments
                    arguments = self.__clean_args(
                        Argument(
                            self.__get_description(name, docstring),
                            self.__generate_parameter(name, module),
                        )
                    )
                    name = arguments.pop('name')
                    parser.add_argument(*name, **arguments)
        return self

    def add_arguments(
        self, obj: Any, parser: Optional[ArgumentParser] = None
    ) -> 'Parser':
        '''Add arguments to parser/subparser.

        Parameters
        ----------
        obj: Any
            Verious module, function, or arguments that can be inspected.
        parser: ArgumentParser, optional
            Parser/Subparser that arguments will be added.

        Returns
        -------
        self:
            Return object itself to allow chaining functions.

        '''
        if not parser:
            parser = self

        # prep object for inspection
        docstring = docstring_parse(obj.__doc__)
        signature = inspect.signature(obj)

        # populate subcommand with keyword arguments
        for arg in signature.parameters:
            param = signature.parameters[arg]
            description = self.__get_description(arg, docstring)
            # log.debug(f"param: {param}, {param.kind}")

            if not param.kind == inspect.Parameter.VAR_KEYWORD:
                log.debug(f"param annotation: {param.annotation}")
                argument = self.__clean_args(Argument(description, param))
                name = argument.pop('name')
                parser.add_argument(*name, **argument)

        # populate options
        # log.debug(f"params {params}")
        for arg in self.__get_keyword_args(signature, docstring):
            description = self.__get_description(arg, docstring)
            arguments = self.__clean_args(Argument(description))
            parser.add_argument(f"--{arg.replace('_', '-')}", **arguments)

        # log.debug(f"arguments {arguments}")
        # TODO for any docstring not collected parse here (args, kwargs)
        # log.debug('docstring params', docstring.params)
        return self

    def __set_main_arguments(self, ns: Namespace) -> Namespace:
        '''Separate and set main arguments from builder function.

        Paramters
        ---------
        ns: Namespace
            Argparse namespace object for a command.

        Returns
        -------
        Namespace:
            Argparse namespace object with command arguments.

        '''
        # pass main arguments to builder function
        if self.main_args_builder:
            builder_mod = sys.modules[self.main_args_builder['module']]
            builder = getattr(builder_mod, self.main_args_builder['function'])
            builder_signature = inspect.signature(builder)
            builder_args = {}
            for param in builder_signature.parameters:
                if param in vars(ns):
                    builder_args[param] = vars(ns).pop(param)
            builder_mod.__dict__[
                self.main_args_builder['instance']
            ] = builder(**builder_args)
        return ns

    def __set_module_arguments(
        self, fn: Callable[[F], F], ns: Namespace
    ) -> Namespace:
        '''Separate and set module arguments from functions.

        Paramters
        ---------
        fn: Callable
            Function used to seperate module arguments from function.
        ns: Namespace
            Argparse namespace object for a command.

        Returns
        -------
        Namespace:
            Argparse namespace object with command arguments.

        '''
        # XXX: only works on subcommands that use 'mod'
        if 'mod' in ns:
            mod = vars(ns).pop('mod')
        else:
            mod = None

        # separate namespace from other variables
        signature = inspect.signature(fn)
        docstring = docstring_parse(fn.__doc__)

        # inspect non-signature keyword args
        keywords = self.__get_keyword_args(signature, docstring)
        args = [
            {k: vars(ns).pop(k)}
            for k in list(vars(ns).keys()).copy()
            if not signature.parameters.get(k) and k not in keywords
        ]
        log.debug(f"arguments {args}, {keywords}")

        # set module variables
        if mod and self.use_module_args:
            for arg in args:
                for k, v in arg.items():
                    mod.__dict__[k] = v
        return ns

    def retrieve(
        self,
        args: Sequence[str] = sys.argv[1:],
        ns: Optional[Namespace] = None,
    ) -> Tuple[List[str], Namespace]:
        '''Retrieve parsed values from CLI input.

        Paramters
        ---------
        args: Sequence[str]
            Command line arguments passed to the parser.
        ns: Optional[Namespace]
            Argparse namespace object for a command.

        Returns
        -------
        List[str]:
            Argparse remaining unparse arguments.
        Namespace:
            Argparse namespace object with command arguments.

        '''
        # TODO: handle invalid argument

        # show help when no arguments provided
        if args == []:
            args = ['--help']  # pragma: no cover
        main_ns, main_args = self.parse_known_args(args, ns)
        if main_args == [] and 'fn' in vars(main_ns):
            return main_args, main_ns
        else:
            # default to help message for subcommand
            if 'mod' in vars(main_ns):
                a = []
                a.append(vars(main_ns)['mod'].__name__.split('.')[-1])
                a.append('--help')
                self.parse_args(a)
            return main_args, main_ns

    def dispatch(
        self,
        args: Sequence[str] = sys.argv[1:],
        ns: Optional[Namespace] = None,
    ) -> Optional[Callable[[F], F]]:
        '''Call command with arguments.

        Paramters
        ---------
        args: Sequence[str]
            Command line arguments passed to the parser.
        ns: Optional[Namespace]
            Argparse namespace object for a command.

        Returns
        -------
        Optional[Callable[[F], F]]:
            Call function with arguments.

        '''
        # parse variables
        arguments, namespace = self.retrieve(args, ns)
        log.debug(f"dispatch: {arguments}, {namespace}")

        main_ns_result = self.__set_main_arguments(namespace)

        # call function with variables
        if 'fn' in namespace:
            ns_vars = vars(namespace)
            fn = ns_vars.pop('fn')

            self.__set_module_arguments(fn, main_ns_result)

            # XXX: only takes standard types
            # attempt to plug parameters using inspect
            splat = None
            signature = inspect.signature(fn)
            for arg in signature.parameters:
                param = signature.parameters[arg]
                if (
                    str(param).startswith('*')
                    and not str(param).startswith('**')
                ):
                    splat = ns_vars.pop(arg)

            # XXX: only works with splat and kwargs
            if splat:
                fn(*splat, **ns_vars)
            else:
                fn(**ns_vars)
        return self.dispatch(arguments) if arguments != [] else None
