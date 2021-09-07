'''
Utils class
'''
import re
import pandas as pd
import nbformat as nbf
from functools import partial
import pandas as pd
import numpy as np

class Utils():
    '''
    Common functions holder
    '''
    is_close = partial(np.isclose,atol=1e-6,equal_nan=True)
    DEBUG = True

    @classmethod
    def to_camel_case(cls, snake_str, joining='_'):
        '''
        Translate from Python Code to JavaScript
        Parameter:
            snake_str: Python name convention
            joining: sign joinig string in python name
        Return: JavaScript name convention
        '''
        if snake_str == '_id':
            return snake_str
        components = snake_str.split(joining)
        return components[0] + ''.join(x.title() for x in components[1:])

    @classmethod
    def to_snake_case(cls, camel_str):
        '''
        Translate from JavaScript to Python
        Parameter:
            camel_str: JavaScript name convention
        Return: Python name convention
        '''
        if camel_str == '_id':
            return camel_str
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

    @classmethod
    def output_form(cls, class_, data_list, output):
        '''
        Transform a data to standardised format, default DataFrame
        Parameter:
            class_: format class to transform (list, set, tuple, numpy, etc.)
            data_list: data to transform
            output: name of the format in string so that don't need to pass a class object in class_
            (currently support only 'DataFrame')
        Return: corresponding data in chosen format
        '''
        if not data_list:
            return []
        if output == 'DataFrame':
            return pd.DataFrame(data_list) if data_list else []
        else:
            return [class_(instance) for instance in data_list]

    @classmethod
    def concatenate_output(cls, lst_1, lst_2):
        if type(lst_1) != type(lst_2):
            print('ERROR in concatenate_output(): Not the same type')
            return []
        if isinstance(lst_1, list):
            return lst_1 + lst_2
        if isinstance(lst_1, pd.DataFrame):
            return pd.concat([lst_1, lst_2], ignore_index=True)
        if not lst_1 and not lst_2:
            return []

    @classmethod
    def build_filter_params_v0(cls, filter_, pre_character='&'):
        '''
        Transform a dictionary to a string with the format: "&key_1[$regex]=x&val_1[$options]=i"
        for each member in the list and joining members by '&'
        Parameter:
            filter: dictionary to transform
            pre_character: character linking each option (default: '&')
        '''
        if not filter_:
            return ''
        result = pre_character
        if 'EXACT' in filter_:
            del filter_['EXACT']
            for key in filter_:
                result += f'{key}={filter_[key]}&'
        else:
            for key in filter_:
                result += f'{key}[$regex]={filter_[key]}&{key}[$options]=i&'
        return result[:-1]

    @classmethod
    def build_filter_params(cls, filter_, offset=0, limit=1000, order_by=''):
        '''
        Build query params object to pass to request.get(query_params=?)
        Parameter:
            filter: dictionary of query conditions
            offset, limit: for pagination
        '''
        query_params = {}
        if filter_ and type(filter_) is dict:
            for key in filter_:
                query_params[f'filter[{key}]'] = filter_[key]
        query_params['offset'] = offset
        query_params['limit'] = limit
        if order_by:
            query_params['orderBy'] = order_by
        return query_params

    @classmethod
    def remove_command_line(cls, block_code):
        return '\n'.join([c for c in block_code.split('\n') if not c.startswith('!')]).strip()

    @classmethod
    def generate_notebook(cls, filename, cells):
        '''Generate notebook from a list of cells
        '''
        nb = nbf.v4.new_notebook()
        for cell in cells:
            if cell['type'] == 'text':
                nb['cells'].append(nbf.v4.new_markdown_cell(cell['content']))
            elif cell['type'] == 'code':
                nb['cells'].append(nbf.v4.new_code_cell(cell['content']))

        with open(filename, 'w') as f:
            nbf.write(nb, f)

    @classmethod
    def printt(cls, msg):
        if cls.DEBUG: print(msg)

    @classmethod
    def is_1darray_equal(cls, a_val, b_val): # include Series
        '''
        Checking whether a and b is 1Darray and equal (or closely equal, depend on choosing value in
        global parameter is_close)
        Parameter: a, b- 1d array to check
        Return True/False
        Reminder: only take value of a and b, and fill N/A with 'NAN_VALUE'
        '''
        if hasattr(a_val, 'values'):
            a_val = a_val.values
        if hasattr(b_val, 'values'):
            b_val = b_val.values

        if (np.issubdtype(a_val.dtype.type, np.int) or np.issubdtype(a_val.dtype.type, np.float)) and \
            (np.issubdtype(b_val.dtype.type, np.int) or np.issubdtype(b_val.dtype.type, np.float)):
            return np.all(cls.is_close(a_val,b_val))

        if a_val.dtype.kind in {'U', 'S','O'} and b_val.dtype.kind in {'U', 'S','O'}:#if contain string
            # replace nan in string ndarray (all type of problems)
            a_val = pd.Series(a_val).fillna('NAN_VALUE').values
            b_val = pd.Series(b_val).fillna('NAN_VALUE').values

        return np.array_equal(a_val,b_val)

    @classmethod
    def is_df_equal(cls, a_val, b_val, **kwargs):
        '''
        Check whether two dataframe's value is exactly equal.
        Parameter: a,b - two dataframe with the type of np.array or pd.DataFrame
            **kwargs include: - same_col_name: whether the name of columns in each two dataframe must be
            the same
        Return True/False
        '''
        if a_val.shape != b_val.shape:
            return False
        same_col_name = kwargs['same_col_name'] if 'same_col_name' in kwargs else True
        if same_col_name and not a_val.columns.equals(b_val.columns):
            return False
        
        a_val_list = [a_val.iloc[:,i] for i in range(a_val.shape[1])]
        b_val_list = [b_val.iloc[:,i] for i in range(b_val.shape[1])]
        return np.all(list(map(cls.is_1darray_equal, a_val_list, b_val_list)))

    @classmethod
    def is_equal(cls, a_val, b_val, **kwargs):
        '''
        Check whether two dataf is closely equal or not. Implement is_1Darray_equal, is_df_equal.
        Parameter: a,b - two data; accepted datatype: int, float, list, tuple, ndarray, dataframe
        Return True/False
        '''
        if (a_val is None) or (b_val is None):
            return False
        if isinstance(a_val, (int, float)) and isinstance(b_val, (int,float)):
            return cls.is_close(a_val,b_val)
        if isinstance(a_val,(list,tuple)) and isinstance(b_val, (list,tuple)):
            return cls.is_1darray_equal(np.array(a_val), np.array(b_val))
        if isinstance(a_val, (np.ndarray,pd.Series)) and isinstance(b_val, (np.ndarray, pd.Series)):
            return cls.is_1darray_equal(a_val, b_val)
        if isinstance(a_val, pd.DataFrame) and isinstance(b_val, pd.DataFrame):
            return cls.is_df_equal(a_val, b_val, **kwargs)
        if not type(a_val) is type(b_val):
            return False
        return a_val==b_val

    @classmethod
    def check_value(cls, submission, solution):
        try:
            assert cls.is_equal(solution, submission)
            cls.printt('You passed! Good job!')
            return True
        except Exception as e:
            cls.printt('Your solution is not correct, try again')
            return False

    @classmethod
    def check_expression(cls, submission, solution, global_dict):
        if (not isinstance(submission, str)):
            cls.printt("Your expression answer must be a string")
            return 'INVALID'
        
        try:
            result = eval(solution, global_dict)
            result_sub = eval(submission, global_dict)
            assert cls.is_equal(result, result_sub)
            cls.printt('You passed! Good job!')
            return True
        except Exception as e:
            cls.printt(e)
            cls.printt('Your solution is not correct, try again')
            return False

    @classmethod
    def check_function(cls, submission, solution, test_cases=None):
        if not test_cases:
            cls.printt("No test cases input")
            return 'INVALID'

        try:
            score = 0
            exec(submission)
            exec(solution)
            func_name_sub = submission.split('(')[0][4:]
            func_name_sol = solution.split('(')[0][4:]
            for tc in test_cases:
                result_sub = locals()[func_name_sub](*tc)
                result_sol = locals()[func_name_sol](*tc)
                if cls.is_equal(result_sub,result_sol):
                    score += 1
            cls.printt(f'You have passed {score}/{len(test_cases)} test cases')
            return score/len(test_cases)
        except Exception as e:
            cls.printt('Your solution is not correct, try again')
            return 0

    @classmethod
    def check_sql(cls, answer, solution, connection=None):
        if not connection:
            cls.printt("No database connection input")
            return 'INVALID'

        if (not isinstance(solution, str)):
            cls.printt("Your SQL answer must be a string")
            return 'INVALID'

        try:
            df_sub = pd.read_sql_query(answer, connection)
            df_sol = pd.read_sql_query(solution, connection)
            if cls.is_equal(df_sub, df_sol, same_col_name=False):
                cls.printt('You passed! Good job!')
                return True

            cls.printt("Your solution is not correct, try again!")
            return False
        except Exception as e:
            cls.printt(f'Something went wrong. {e}')
            return 'INVALID'

    @classmethod
    def check_available(cls, variables, dict):
        for v in variables:
            if v not in dict:
                print(f'{v} is not defined. Please make sure you have run the code to define it.')
                return False
        return True