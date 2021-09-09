# <copyright file="helpers.py" company="Mobilize.Net">
#     Copyright (C) Mobilize.Net info@mobilize.net - All Rights Reserved
#
#     This file is part of the Mobilize Frameworks, which is
#     proprietary and confidential.
#
#     NOTICE:  All information contained herein is, and remains
#     the property of Mobilize.Net Corporation.
#     The intellectual and technical concepts contained herein are
#     proprietary to Mobilize.Net Corporation and may be covered
#     by U.S. Patents, and are protected by trade secret or copyright law.
#     Dissemination of this information or reproduction of this material
#     is strictly forbidden unless prior written permission is obtained
#     from Mobilize.Net Corporation.
# </copyright>

import atexit
import csv
import datetime
import inspect
import logging
import re
import sys
import subprocess
import snowflake.connector
import traceback
from functools import singledispatch
from os import access, getenv, R_OK, makedirs, path, stat, system
from deprecated import deprecated

snow_debug_colors = getenv("SNOW_DEBUG_COLOR", "").strip().upper()

if snow_debug_colors:
    import termcolor

def colored(text, color="blue"):
    """Prints colored text from the specified color.

        text
            The text to be printed
        color="blue"
            The color to print

    """
    if (snow_debug_colors == "YES" or snow_debug_colors == "ON" or snow_debug_colors == "TRUE"):
        return termcolor.colored(text, color)
    return text

# constants
COMPANY_NAME = "Mobilize.Net"

# global status values
max_errors = 1
current_error_count = 0
activity_count = 0
error_code = 0
error_level = 0
warning_code = 0
system_return_code = 0
quit_application_already_called = False

# severities dictionary
_severities_dictionary = dict()
_default_error_level = 8

# last executed sql statement
_previous_executed_sql = ""

has_passed_variables = False
passed_variables = {}

def configure_log():
    """Configures the logging that will be performed for any data related execution on the snowflake connection.
    The log file is named 'snowflake_python_connector.log'
    """
    logging.basicConfig(
        filename='snowflake_python_connector.log',
        level=logging.DEBUG,
        filemode='w')

def get_from_vars_or_args_or_environment(arg_pos, variable_name, vars, args):
    """Gets the argument from the position specified or gets the value from the table vars or gets the environment variable name passed.

        arg_pos
            The argument position to be used from the arguments parameter.
        variable_name
            The name of the variable to be obtained.
        vars
            The hash with the variables names and values.
        args
            The arguments array parameter.
    """
    if (arg_pos < len(args)):
        return args[arg_pos]
    var_value = vars.get(variable_name, None)
    if (var_value is not None):
        return var_value
    env_value = getenv(variable_name)
    return env_value

def get_argkey(astr):
    """Gets the argument key value from the passed string.

    It must start with the string '--param-'
        astr
            The argument string to be used
            The string should have a value similar to --param-column=32 and
            the returned string will be 'column'
    """
    if astr.startswith('--param-'):
        astr = astr[8:astr.index('=')]
    return astr

def get_argvalue(astr):
    """Gets the argument value from the passed string.
    It must start with the string '--param-'

        astr
            The argument string to be used
            The string should have a value similar to --param-column=32 and
            the returned string will be '32'
    
    """
    if astr.startswith('--param-'):
        astr = astr[astr.index('=')+1:]
    return astr

def read_param_args(args):
    """Reads the parameter arguments from the passed array.

        args
            The arguments to be used
    """
    script_args = [item for item  in args if item.startswith("--param-")]
    dictionary = {}
    if len(script_args) > 0:
        dictionary = { get_argkey(x) : get_argvalue(x) for x in args}
        if len(dictionary) != 0:
            has_passed_variables = True
            print("Using variables")
            print_table(dictionary)
    return dictionary

def print_table(dictionary):
    """
    Prints the dictionary without exposing user and password values
    """
    length = len(dictionary)
    i = 0
    terminator = ', '
    print("{", end='')
    for key,value in dictionary.items():
        if ("PASSWORD" in key or "USER" in key):
            value = "*" * 12
        i += 1
        if (i == length) :
            terminator = ''
        print(f"'{key}':'{value}'", end=terminator)
    print("}")

def expandvars(path, params, skip_escaped=False):
    """Expand environment variables of form $var and ${var}.
       If parameter 'skip_escaped' is True, all escaped variable references
       (i.e. preceded by backslashes) are skipped.
       Unknown variables are set to 'default'. If 'default' is None,
       they are left unchanged.
    """
    def replace_var(m):
        varname = m.group(3) or m.group(2)
        passvalue = params.get(varname, None)
        return getenv(varname, m.group(0) if passvalue is None else passvalue)
    reVar = (r'(?<!\)' if skip_escaped else '') + r'(\$|\&)(\w+|\{([^}]*)\})'
    return re.sub(reVar, replace_var, path)

def expands_using_params(statement, params):
    """Expands the statement passed with the parameters.

        statement
            The sql statement to be used
        params
            The parameters of the sql statement
    """
    def replace_var(m):
        varname = m.group(1)
        passvalue = params.get(varname, None)
        if (passvalue is None):
            return m.group(0)
        else:
            return str(passvalue)
    reVar = r'\{([^}]*)\}'
    return re.sub(reVar, replace_var, statement) 

def expandvar(str):
    """Expands the variable from the string passed.

        str
            The string to be expanded with the variables.
    """
    return expandvars(str, passed_variables)

opened_connections = []

def log_on(user=None, password=None, account=None, database=None, warehouse=None, role=None, login_timeout=10):
    """Logs on the snowflake database with the credentials, database, role and 
    warehouse passed parameters.

        user
            The user of the database
        password
            The password of the user of the database
        database
            The database to be connected
        warehouse
            The warehouse of the database to be connected
        role
            The role to be connected
        login_timeout
            The maximum timeout before giving error if the connection is taking too
            long to connect
    """
    global error_code
    global opened_connections
    print("arguments: ", sys.argv)
    # exclude arguments passed inline to the script
    args = [item for item in sys.argv if not item.startswith("--param-")]
    if (user is None):
        user = get_from_vars_or_args_or_environment(1, "SNOW_USER", passed_variables, args)
    if (password is None):
        password = get_from_vars_or_args_or_environment(2, "SNOW_PASSWORD", passed_variables, args)
    if (account is None):
        account = get_from_vars_or_args_or_environment(3, "SNOW_ACCOUNT", passed_variables, args)
    if (database is None):
        database = get_from_vars_or_args_or_environment(4, "SNOW_DATABASE", passed_variables, args)
    if (warehouse is None):
        warehouse = get_from_vars_or_args_or_environment(5, "SNOW_WAREHOUSE", passed_variables, args)
    if (role is None):
        role = get_from_vars_or_args_or_environment(6, "SNOW_ROLE", passed_variables, args)
    query_tag = passed_variables.get("SNOW_QUERYTAG", None)
    if (query_tag is None):
        query_tag = getenv("SNOW_QUERYTAG", None)
    if query_tag is None:
        frm = inspect.stack()[1]
        query_tag = path.basename(frm.filename)
    c = None
    try:
        c = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            database=database,
            warehouse=warehouse,
            application=COMPANY_NAME,
            role=role,
            login_timeout=login_timeout,
            session_parameters={
                'QUERY_TAG': query_tag
            }
        )
    except Exception as e:
        print(colored('*** Failure: logon failed :', 'red') + str(e))
        error_code = 333
        quit_application(error_code)
    if c:
        opened_connections.append(c)
        error_code = 0
    return c

def at_exit_helpers():
    """Executes at the exit of the execution of the script
    """
    print("Script done >>>>>>>>>>>>>>>>>>>>")
    for c in opened_connections:
        if not c.is_closed():
            c.close()
    quit_application()

def exception_hook(exctype, value, traceback):
    """Executes when there is an exception.

        exctype
            The type of the exception
        value
            The value of the exception
        traceback
            The call stack when the exception was produced
    """
    traceback_formatted = traceback.format_exception(exctype, value, traceback)
    traceback_string = colored("*** Failure: " + "".join(traceback_formatted), 'red')
    print(traceback_string, file=sys.stderr)
    quit_application(1)

def using(*argv):
    using_dict = {}
    Import.using(using_dict, *argv)
    return using_dict

def import_file(filename, separator=' '):
    """Imports the passed filename with the optional separator.

        filename
            The file name path to be imported
        separator=' '
            The optional separator.
    """
    return Import.file(filename, separator)

def import_reset():
    return Import.reset()

def exec(sql_string, using=None, con=None):
    """Executes a sql string using the last connection, optionally it uses arguments or an specific connection.

        sql_string
            The definition of the sql
        using=None
            The optional parameter that can be used in the sql passed
        con=None
            The connection to be used, if None is passed it will use the last
            connection performed

        Examples:
            exec("SELECT * FROM USER")

            exec("SELECT * FROM SALE", con)

            exec("SELECT * FROM CUSTOMER WHERE CUSTOMERID= %S", customer)
    """
    global opened_connections
    global activity_count
    global current_error_count
    global max_errors
    global error_code
    global _previous_executed_sql
    if (con is None):
        # get last connection
        con = opened_connections[-1]

    cur = con.cursor()
    try:
        error_code = 0
        print(colored("Executing: ", 'blue') + colored(sql_string, 'cyan'))
        if ("$" in sql_string or "&" in sql_string):
            print ("Expanding variables in SQL statement")
            sql_string = expandvars(sql_string, passed_variables)
            print (colored("Expanded string: ") + colored(sql_string, 'green'))
        if (using is not None):
                #we need to change variables from {var} to %(format)
                sql_string = re.sub(r'\{([^}]*)\}', r'%(\1)', sql_string)
                print(f"using parameters {using}")
        cur.execute(sql_string, params=using)
        activity_count = cur.rowcount
        if activity_count and activity_count >= 1:
            _print_result_set(cur)
        else:
            if (Export.expandedfilename is not None):
                _print_result_set(cur)
    except snowflake.connector.errors.ProgrammingError as e:
        current_error_count = current_error_count + 1
        _handle_syntax_error(e, sql_string)
    except: # catch *all* exceptions
        current_error_count = current_error_count + 1
        e = sys.exc_info()
        msg = colored("*** Failure running statement", 'red')
        print(msg)
        print(e)
    finally:
        _previous_executed_sql = sql_string
        cur.close()
        if current_error_count >= max_errors:
            print(colored(f'*** Failure: reached max error count {max_errors}', 'red'))
            quit_application(1)

def repeat_previous_sql_statement(con=None, n=1):
    """Repeats the previous executed sql statement(s).

        con=None
            Connection if specified. If it is not passed it will use the last
            connection performed
        n=1
            The number of previous statements to be executed again
    """
    if _previous_executed_sql == "":
        if n == 0:
            n = 1
        for rep in xrange(n):
            exec(_previous_executed_sql, con)
    else:
        print("Warning: No previous SQL request.")

def _print_result_set(cur):
    if (Export.expandedfilename is None):
        # if there is not export file set then print to console
        print("Printing Result Set:")
        print(','.join([col[0] for col in cur.description]))
        for row in cur:
            print(','.join([str(val) for val in row]))
        print()
    else:
        print(">>>>>> Exporting to " + Export.expandedfilename)
        reportdir = path.dirname(Export.expandedfilename)
        makedirs(reportdir, exist_ok=True)
        with open(Export.expandedfilename, 'a') as f:
            for row in cur:
                allarenone = all(v is None for v in row)
                if (allarenone):
                    print("Row is 'None' it will not be exported")
                else:
                    rowval = Export.separator.join([str(val) for val in row])
                    print(rowval, file=f)

def _handle_syntax_error(e, sql_string):
    if "syntax error" in e.msg:
        regex = r"syntax error line (\d+) at position (\d+)"
        matches = re.finditer(regex, e.msg, re.MULTILINE)
        error_fragment = "SYNTAX ERROR:\n"
        sql_lines = sql_string.splitlines()
        last_line = -1       
        for matchNum, match in enumerate(matches, start=1):
                line = int(match.groups()[0])-1
                column = int(match.groups()[1])
                if line != last_line:
                    error_line = sql_lines[line]
                    error_line = error_line[:column] + colored(error_line[column:], 'red')
                    error_fragment = error_fragment + f"{line:0>2d},{column:0>2d}:{error_line}\n"
                last_line = line
        print(error_fragment)
    _handle_sql_error(e)

def _handle_sql_error(e):
    global error_code, error_level
    error_code = e.errno
    if error_code not in _severities_dictionary or _severities_dictionary[error_code] != 0:
        msg = colored("*** Failure " + str(e), 'red')
        print(msg, file=sys.stderr)
        if error_code in _severities_dictionary:
            error_level = max(error_level, _severities_dictionary[error_code])
        else:
            error_level = max(error_level, _default_error_level)

@singledispatch
def set_error_level(arg, severity_value):
    f"Invoked set_error_level with arg={arg}, severity_value={severity_value}"

@set_error_level.register(int)
def _(arg, severity_value):
    _severities_dictionary[arg] = severity_value

@set_error_level.register(list)
def _(arg, severity_value):
    for code in arg:
        _severities_dictionary[code] = severity_value

def set_default_error_level(severity_value):
    global _default_error_level
    _default_error_level = severity_value

def os(args):
    global system_return_code
    system_return_code = system(args)

def readrun(line, skip=0):
    """Reads the given filename lines and optionally skips some lines at
    the beginning of the file.

        line
            The filename to be read
        skip=0
            The lines to be skipped
    """
    expandedpath = path.expandvars(line)
    if path.isfile(expandedpath):
        return open(expandedpath).readlines()[skip:]
    else:
        return []

def exec_file(filename, con=None):
    """Reads the content of a file and executes the sql statements contained 
    with the specified connection

        filename
            The filename to be read and executed
        con=None
            The connection to be used, if None is passed it will use the last
            connection performed
    """
    expandedpath = path.expandvars(filename)
    if path.isfile(expandedpath):
        with open(expandedpath, 'r') as f:
            contents = f.read()
            statements = contents.split(";")
            for statement in statements:
                exec(statement, con=con)
    else:
        print(colored("*** Error: File does not exist", 'red'))

def remark(arg):
    """Prints the argument.

        arg
            The argument to be printed
    """
    print(arg)

def get_error_position():
    """Gets the error position from the file using the
    information of the stack of the produced error.
    """
    stack = inspect.stack()
    important_frames = []
    for i in range(len(stack)):
        current_stack = stack[i]
        if current_stack.filename.endswith(__name__ + ".py"):
            # we skip the first one because is the frame for this function
            # now we take this element and the next max 5 ones
            next_frames = i + 5 if i + 5 < len(stack) else len(stack)
            important_frames.extend(stack[i+1:next_frames])
    stack_trace = "Error at:\n"
    for frame in important_frames:
        stack_trace = stack_trace + f"{frame.filename}:{frame.lineno} function: {frame.function} \n"
    return stack_trace

def quit_application(code=None):
    """Quits the application and optionally returns the passed code.

        code=None
            The code to be returned after it quits
    """
    global quit_application_already_called
    if quit_application_already_called:
        return
    quit_application_already_called = True
    code = code or error_level
    print(colored(f"Error Code {code}", 'red'))
    if code != 0:
        stack_trace = get_error_position();
        print(colored(stack_trace, 'red'))
    sys.exit(code)

def import_file_to_temptable(filename, tempTableName, columnDefinition):
    """Imports the file passed to a temporary table.
    It will use a public stage named as the temporary table with the prefix
    Stage_.
    At the end of the loading to the temporary table it will delete the stage
    that was used in the process.
        filename
            The name of the file to be read
        tempTableName
            The name of the temporary table
        columnDefinition
            The definition of all the fields that will have the temporary table
    """
    tempTableName = expandvar(tempTableName)
    filename = expandvar(filename)
    stageName = f"Stage_{tempTableName}"
    exec(f"CREATE TRANSIENT TABLE PUBLIC.{tempTableName} ({columnDefinition})")
    exec(f"CREATE OR REPLACE TEMPORARY STAGE PUBLIC.{stageName} FILE_FORMAT=(TYPE=CSV)")
    exec(f"PUT file://{filename} @PUBLIC.{stageName} OVERWRITE=TRUE")
    exec(f"COPY INTO PUBLIC.{tempTableName} FROM @PUBLIC.{stageName}  FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1) ON_ERROR=CONTINUE")
    exec(f"DROP STAGE PUBLIC.{stageName}")

def drop_transient_table(tempTableName, con=None):
    """Drops the transient table with the specified name.
        tempTablename
            The name of the temporary table
        con=None
            The connection to be used, if None is passed it will use the last
            connection performed    
    """
    global opened_connections
    if (con is None):
        # get last connection
        con = opened_connections[-1]

    sql = f"""DROP TABLE {tempTableName}"""
    exec(sql, con)

def file_exists_and_readable(filename):
    return access(path.expandvars(filename), R_OK)

def exec_os(command):
    """Executes a command in the operative system.
    """
    print(f"executing os command: {command}")
    return subprocess.getoutput(command)

def fast_load(target_schema, filepath, stagename, target_table_name, con=None):
    """Executes the fast load with the passed parameters target_schema, filepath, stagename and target_table_name.
        target_schema
            The name of the schema to be used in the fast load
        filepath
            The file name path to be loaded in the table
        target_table_name
            The name of the table that will have the data loaded
        con=None
            The connection to be used, if None is passed it will use the last
            connection performed
    """
    global opened_connections
    if (con is None):
        # get last connection
        con = opened_connections[-1]   ## expand any environment var
    target_schema = expandvar(target_schema)
    filepath = expandvar(filepath)
    filename = path.basename(filepath)
    stagename = expandvar(stagename)
    target_table_name = expandvar(target_table_name)
    exec(f""" USE SCHEMA {target_schema} """, con)
    print(f"Putting file {filepath} into {stagename}...")
    exec(f"PUT file://{filepath} @{stagename} OVERWRITE = TRUE", con)
    print(f"Done put file...ErrorCode {error_code}")
    print(">>>Copying into...")
    exec(f"""
    COPY INTO {target_schema}.{target_table_name}
    FROM @{stagename}/{filename}
    FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1)
    ON_ERROR=CONTINUE""", con)
    print(f"<<<Done copying. ErrorCode {error_code}")
    print(f">>>Creating temp table CTE_{target_table_name}")
    sql = f"CREATE TABLE {target_schema}.CTE_{target_table_name}  AS SELECT DISTINCT * FROM {target_schema}.{target_table_name}"
    exec(sql, con)
    print(f"<<<Done creating temp table. ErrorCode {error_code}")
    print(f">>>Droping old {target_table_name}")
    sql = f"DROP TABLE {target_schema}.{target_table_name}"
    exec(sql, con)
    print(f"<<<Done droping old table. ErrorCode {error_code}")
    print(f">>>Renaming old CTE_{target_table_name}")
    sql = f"ALTER TABLE {target_schema}.CTE_{target_table_name} RENAME TO {target_schema}.{target_table_name}"
    exec(sql, con)
    print(f"<<<Done droping old table. ErrorCode {error_code}")

@deprecated(version='2.0', reason="This function will be removed soon, please use exec function instead")
def execute_sql_statement(sql_string, con, using=None):
    """Executes a sql statement in the connection passed, with the optional arguments.

        sql_string
            The sql containing the string to be executed
        con
            The connection to be used
        using
            The optional parameters to be used in the sql execution
    """
    exec(sql_string, con, using)

@deprecated(version='2.0', reason="This function will be removed soon, please use import_file_to_temptable function instead")
def import_data_to_temptable(tempTableName, inputDataPlaceholder, con):
    """Imports data to a temporary table using an input data place holder.

        tempTableName
            The temporary table name.
        inputDataPlaceholder
            The input place holder used that is a stage in the snowflake database
        con
            The connection to be used
    """
    sql = f"""COPY INTO {tempTableName} FROM {inputDataPlaceholder}  FILE_FORMAT=(TYPE=CSV SKIP_HEADER=1) ON_ERROR=CONTINUE"""
    exec(sql, con)

@deprecated(version='2.0', reason="This function will be removed soon, please use fast_load function instead")
def simple_fast_load(con, target_schema, filepath, stagename, target_table_name):
    """Executes a simple fast load in the connection and the passed parameter
    target_schema, filepath, stagename and target table name.
        con
            The connection to be used
        target_schema
            The name of the schema to be used in the fast load
        filepath
            The file name path to be loaded in the table
        target_table_name
            The name of the table that will have the data loaded
    """
    fast_load(target_schema, filepath, stagename, target_table_name, con)

atexit.register(at_exit_helpers)

def exception_hook(exctype, value, tback):
    print(colored(f"*** Failure: {value}", 'red'), file=sys.stderr)
    traceback_formatted = traceback.format_exception(exctype, value, tback)
    traceback_string = "".join(traceback_formatted)
    print(traceback_string, file=sys.stderr)
    quit_application(1)

sys.excepthook = exception_hook
   
class Import:
    expandedfilename = None
    separator=' '
    reader = None
    no_more_rows = False
    read_obj = None

    @staticmethod
    def file(file, separator=' '):
        Import.separator = separator
        Import.expandedfilename = path.expandvars(file)
        Import.reader = None
        if (not Import.read_obj is None):
            Import.read_obj.close()
        Import.read_obj = None
        Import.no_more_rows = False

    @staticmethod
    def using(globals, *argv):
        print (argv)
        try:
            variables_li = [] 
            types_li = []
            i = 0
            while i < len(argv):
                elem = argv[i]
                if (i % 2 == 0): 
                    variables_li.append(elem) 
                else: 
                    types_li.append(elem)
                i += 1
            i = 0
            # init the global variables for the using clause
            while i < len(variables_li):
                initvalue = None
                if (types_li[i].startswith("DECIMAL")):
                    initvalue = 0
                else:
                    if (types_li[i].startswith("DATE")):
                        initvalue = datetime.date.min
                    else:
                         if (types_li[i].startswith("TIMESTAMP")):
                            initvalue = datetime.datetime.min
                globals[variables_li[i]] = initvalue
                i += 1
            # open file in read mode
            if (Import.expandedfilename is not None):
                if (Import.reader is None):
                    read_obj = open(Import.expandedfilename, 'r')
                    print(f">>>>>>>>> Importing from {Import.expandedfilename}")
                    if (stat(Import.expandedfilename).st_size == 0):
                        print("Import file is empty")
                        return
                    else:
                        # pass the file object to reader() to get the reader object
                        Import.reader = csv.reader(read_obj)
                # read next row
                print("Reading row")
                row = next(Import.reader)
                # row variable is a list that represents a row in csv
                i = 0
                while i < len(variables_li):
                    globals[variables_li[i]] = row[i]
                    i += 1
        except StopIteration:
            Import.no_more_rows = True
            print ("No more rows")
        except Exception as e:
            print (f"*** Failure importing {e}")
        print("Done importing")
    def reset():
            Import.expandedfilename = None
            Import.separator = ' '

class Export:
    expandedfilename = None
    separator = ' '
    _record_mode = False
    _separator_width = 2
    _side_titles = False
    _title_dashes = False
    _title_dashes_with = 0
    _width = 80
    _null = '?'

    @staticmethod
    def defaults():
        Export.reset()

    @staticmethod
    def null(value = None):
        if value is not None:
            Export._null = value
        return Export._null

    @staticmethod
    def record_mode(value = None):
        if value is not None:
            Export._record_mode = value
        return Export._record_mode

    @staticmethod
    def report(file, separator=' '):
        Export.separator = separator
        Export.expandedfilename = path.expandvars(file)

    @staticmethod
    def reset():
        Export.expandedfilename = None
        Export.record_mode(False)
        Export.title_dashes(False, 0)
        Export.side_titles(False)
        Export.separator_string(' ')
        Export.separator_width(2)
        Export.width(80)
        Export.null('?')

    @staticmethod
    def separator_string(value = None):
        if (value is not None):
            Export.separator = value
        return Export.separator

    @staticmethod
    def separator_width(value = None):
        if (value is not None):
            Export._separator_width = value
        return Export._separator_width

    @staticmethod
    def side_titles(value = None):
        if value is not None:
            Export._side_titles = value
        return Export._side_titles

    @staticmethod
    def title_dashes(value = None, withValue = None):
        if value is not None:
            Export._title_dashes = value
        if withValue is not None:
            Export.title_dashes_with(withValue)
        return Export._title_dashes
    
    @staticmethod
    def title_dashes_with(value = None):
        if value is not None:
            Export._title_dashes_with = value
        return Export._title_dashes_with

    @staticmethod
    def width(value = None):
        if value is not None:
            Export._width = value
        return Export._width

class Parameters:
    passed_variables = {}

## Loading extra parameters from command line
passed_variables = read_param_args(sys.argv[1:])
