"""Module containing the logic for the dlapp entry-points."""

import sys
import argparse
from os import path
from textwrap import dedent
from dlapp.application import Application
from dlapp import create_from_csv_file
from dlapp import create_from_json_file
from dlapp import create_from_yaml_file


def get_tutorial_examples():
    """Return the dlapp tutorial examples text."""
    text = '''
        Example 1:
        ---------
        we need to find any item in a list_of_dict where
        key of item (i.e dict) has a value starting with Ap

        In this case, we need to look into every item of a list_of_dict,
        and then grab (key, value) pair that key is equal to "a" and
        value need to have a prefix of Ap.

        first criteria is that traverses lst_of_dict and report any item
        has key is equal "a"
            >>> result = query_obj.find(lookup='a', select='')
            >>> result
            ['Apple', 'Apricot', 'Avocado']
            >>>

        second criteria is that value of key "a" must have a "Ap" prefix.
        To be able to achieve this case, we can either use regular
        expression or wildcard filtering algorithm in lookup argument.

            >>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='')
            >>> result
            ['Apple', 'Apricot']
            >>> # or use regex
            >>> result = query_obj.find(lookup='a=_regex(Ap.+)', select='')
            >>> result
            ['Apple', 'Apricot']
            >>>

        there is another way to achieve the same result by using select-statement
        WHERE clause
            >>> result = query_obj.find(lookup='a', select='WHERE a match Ap.+')
            >>> result
            ['Apple', 'Apricot']
            >>>

        Example 2:
        ---------
        Find values where items of lst_of_dict have key "a" or "c"
            >>> result = query_obj.find(lookup='_wildcard([ac])', select='')
            >>> result
            ['Apple', 'Cherry', 'Apricot', 'Cantaloupe', 'Avocado', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_regex([ac])', select='')
            >>> result
            ['Apple', 'Cherry', 'Apricot', 'Cantaloupe', 'Avocado', 'Clementine']

        Example 3:
        ---------
        Find values where items of lst_of_dict have key "a" or "c" where items
        value have letter i or y

            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_wildcard([ac])=_regex(.*[iy].*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>> result = query_obj.find(lookup='_regex([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> result = query_obj.find(lookup='_regex([ac])=_regex(.*[iy].*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']

        Note: in this case, the lookup argument contains two expressions:
        a left expression and a right expression, a separator between
        left and right expression is "=" symbol.

        lookup          : _wildcard([ac])=_regex(.*[iy].*)
        left expression : _wildcard([ac])
        right expression: _regex(.*[iy].*)

        Example 3.1:
        -----------
        Find values where items of lst_of_dict have key "a" or "c" where items
        value have letter i or y and select a, c

            >>> # this is a result without select a, c
            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='')
            >>> result
            ['Cherry', 'Apricot', 'Clementine']
            >>>
            >>> # this is a result after select a, c
            >>> result = query_obj.find(lookup='_wildcard([ac])=_wildcard(*[iy]*)', select='SELECT a, c')
            >>> result
            [{'a': 'Apple', 'c': 'Cherry'}, {'a': 'Apricot', 'c': 'Cantaloupe'}, {'a': 'Avocado', 'c': 'Clementine'}]
            >>>
        ########################################
    '''

    return dedent(text)


def show_tutorial_dlquery():
    """Print a dlapp tutorial."""
    text = '''
        ########################################
        # tutorial: dlapp                    #
        ########################################
        Assuming there is a list of dictionary

            >>> lst_of_dict = [
            ...     {"a": "Apple", "b": "Banana", "c": "Cherry"},
            ...     {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
            ...     {"a": "Avocado", "b": "Blueberry", "c": "Clementine"},
            ... ]
            >>>

        We need to instantiate dlapp.DLQuery object
        
            >>> from dlapp import DLQuery
            >>> query_obj = DLQuery(lst_of_dict)
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_csv():
    """Print a dlapp tutorial - case csv file."""
    text = '''
        ########################################
        # tutorial: CSV                        #
        ########################################
        Assuming there is a sample.csv file

        ----------------------------------------
        Console usage: try the following
            $ dlapp --filename=sample.csv --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dlapp --filename=sample.csv --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dlapp --filename=sample.csv --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.csv'
            >>> content = open(fn).read()
            >>> print(content)
            a,b,c
            Apple,Banana,Cherry
            Apricot,Boysenberry,Cantaloupe
            Avocado,Blueberry,Clementine
            >>>

        We need to instantiate dlapp.DLQuery object using create_from_csv_file function

            >>> from dlapp import create_from_csv_file
            >>> query_obj = create_from_csv_file('sample.csv')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_json():
    """Print a dlapp tutorial - case json file."""
    text = '''
        ########################################
        # tutorial: JSON                       #
        ########################################
        Assuming there is a sample.json file

        ----------------------------------------
        Console usage: try the following
            $ dlapp --filename=sample.json --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dlapp --filename=sample.json --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dlapp --filename=sample.json --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.json'
            >>> content = open(fn).read()
            >>> print(content)
            [
                {"a": "Apple", "b": "Banana", "c": "Cherry"},
                {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
                {"a": "Avocado", "b": "Blueberry", "c": "Clementine"}
            ]
            >>>

        We need to instantiate dlapp.DLQuery object using create_from_json_file function

            >>> from dlapp import create_from_json_file
            >>> query_obj = create_from_json_file('sample.json')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def show_tutorial_yaml():
    """Print a dlapp tutorial - case yaml file."""
    text = '''
        ########################################
        # tutorial: yaml                        #
        ########################################
        Assuming there is a sample.yaml file

        ----------------------------------------
        Console usage: try the following
            $ dlapp --filename=sample.yaml --lookup="a" --select="WHERE a match Ap.+"
            ['Apple', 'Apricot']
            $
            $
            $ dlapp --filename=sample.yaml --lookup="a"  --select="WHERE c not_match [Cc]a.+"
            ['Apple', 'Avocado']
            $
            $
            $ dlapp --filename=sample.yaml --lookup="a"  --select="SELECT a, c WHERE c not_match [Cc]a.+"
            [OrderedDict([('a', 'Apple'), ('c', 'Cherry')]), OrderedDict([('a', 'Avocado'), ('c', 'Clementine')])]

        ----------------------------------------

            >>> fn = 'sample.yaml'
            >>> content = open(fn).read()
            >>> print(content)
            - a: Apple
              b: Banana
              c: Cherry
            - a: Apricot
              b: Boysenberry
              c: Cantaloupe
            - a: Avocado
              b: Blueberry
              c: Clementine
            >>>

        We need to instantiate dlapp.DLQuery object using create_from_yaml_file function

            >>> from dlapp import create_from_yaml_file
            >>> query_obj = create_from_yaml_file('sample.yaml')
    '''

    data = '{}\n{}'.format(dedent(text), get_tutorial_examples())

    print(data)


def run_tutorial(options):
    """Run a selection dlapp console CLI tutorial.

    Parameters
    ----------
    options (argparse.Namespace): a argparse.Namespace instance.

    Returns
    -------
    None: will call ``sys.exit(0)`` if end user requests a tutorial
    """
    is_tutorial_needed = options.tutorial
    is_tutorial_needed |= options.tutorial_csv
    is_tutorial_needed |= options.tutorial_json
    is_tutorial_needed |= options.tutorial_yaml

    if not is_tutorial_needed:
        return None

    options.tutorial and show_tutorial_dlquery()
    options.tutorial_csv and show_tutorial_csv()
    options.tutorial_json and show_tutorial_json()
    options.tutorial_yaml and show_tutorial_yaml()
    sys.exit(0)


def run_gui_application(options):
    """Run dlapp GUI application.

    Parameters
    ----------
    options (argparse.Namespace): a argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``dlapp.Application().run()`` and ``sys.exit(0)``
    if end user requests `--application`
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(0)


class Cli:
    """dlapp console CLI application."""
    def __init__(self):
        self.filename = ''
        self.filetype = ''
        self.result = None

        parser = argparse.ArgumentParser(
            prog='dlapp',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='launch a dlapp GUI application'
        )

        parser.add_argument(
            '--filename', type=str,
            default='',
            help='a json, yaml, or csv file name'
        )

        parser.add_argument(
            '--filetype', type=str, choices=['csv', 'json', 'yaml', 'yml'],
            default='',
            help='a file type can be either json, yaml, yml, or csv'
        )

        parser.add_argument(
            '--lookup', type=str, dest='lookup',
            default='',
            help='a lookup criteria for searching a list or dictionary'
        )

        parser.add_argument(
            '--select', type=str, dest='select_statement',
            default='',
            help='a select statement to enhance multiple searching criteria'
        )

        parser.add_argument(
            '--tutorial', action='store_true', dest='tutorial',
            help='show dlapp tutorial'
        )

        parser.add_argument(
            '--tutorial-csv', action='store_true', dest='tutorial_csv',
            help='show csv tutorial'
        )

        parser.add_argument(
            '--tutorial-json', action='store_true', dest='tutorial_json',
            help='show json tutorial'
        )

        parser.add_argument(
            '--tutorial-yaml', action='store_true', dest='tutorial_yaml',
            help='show yaml tutorial'
        )

        self.parser = parser

    @property
    def is_csv_type(self):
        """Return True if filetype is csv, otherwise, False."""
        return self.filetype == 'csv'

    @property
    def is_json_type(self):
        """Return True if filetype is json, otherwise, False."""
        return self.filetype == 'json'

    @property
    def is_yaml_type(self):
        """Return True if filetype is yml or yaml, otherwise, False."""
        return self.filetype in ['yml', 'yaml']

    def validate_cli_flags(self, options):
        """Validate argparse `options`.

        Parameters
        ----------
        options (argparse.Namespace): a argparse.Namespace instance.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(1)`` if
        all flags are empty or False, otherwise, return True
        """

        chk = any(bool(i) for i in vars(options).values())

        if not chk:
            self.parser.print_help()
            sys.exit(1)

        return True

    def validate_filename(self, options):
        """Validate `options.filename` flag which is a file type of `csv`,
        `json`, `yml`, or `yaml`.

        Parameters
        ----------
        options (argparse.Namespace): a argparse.Namespace instance.

        Returns
        -------
        bool: True if `options.filename` is valid, otherwise, ``sys.exit(1)``
        """
        filename, filetype = str(options.filename), str(options.filetype)
        if not filename:
            print('*** --filename flag CAN NOT be empty.')
            sys.exit(1)

        self.filename = filename
        self.filetype = filetype

        _, ext = path.splitext(filename)
        ext = ext.lower()
        if ext in ['.csv', '.json', '.yml', '.yaml']:
            self.filetype = ext[1:]
            return True

        if not filetype:
            if ext == '':
                fmt = ('*** {} file doesnt have an extension.  '
                       'System cant determine a file type.  '
                       'Please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')

            else:
                fmt = ('*** {} file has an extension but its extension is not '
                       'csv, json, yml, or yaml.  If you think this file is '
                       'csv, json, yml, or yaml file, '
                       'please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')
            print(fmt.format(filename))
            sys.exit(1)
        else:
            self.filetype = filetype

    def run_cli(self, options):
        """Execute dlapp command line.

        Parameters
        ----------
        options (argparse.Namespace): a argparse.Namespace instance.
        """
        lookup, select = options.lookup, options.select_statement
        if not options.lookup:
            print('*** --lookup flag CANNOT be empty.')
            sys.exit(1)

        if self.is_csv_type:
            func = create_from_csv_file
        elif self.is_json_type:
            func = create_from_json_file
        elif self.is_yaml_type:
            func = create_from_yaml_file
        else:
            print('*** invalid filetype.  Check with DEV.')
            sys.exit(1)

        query_obj = func(self.filename)
        result = query_obj.find(lookup=lookup, select=select)
        if result:
            print(result)
        else:
            print('*** No record is found.')

        sys.exit(0)

    def run(self):
        """Take CLI arguments, parse it, and process."""
        options = self.parser.parse_args()
        run_tutorial(options)
        run_gui_application(options)
        self.validate_cli_flags(options)
        self.validate_filename(options)
        self.run_cli(options)


def execute():
    """Execute dlapp console CLI."""
    app = Cli()
    app.run()
