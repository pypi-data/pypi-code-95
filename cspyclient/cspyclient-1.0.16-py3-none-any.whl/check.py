'''Checking answers and related information'''
import pandas as pd
import numpy as np
import types
from functools import partial


def printt(msg,debug=True):
    '''
    Printing message for debug/ announcing
    Parameter: msg- message to print
        debug- whether should print
    '''
    if debug:
        print(msg)

is_close = partial(np.isclose,atol=1e-6,equal_nan=True)

def is_1darray_equal(a_val,b_val): # include Series
    '''
    Checking whether a and b is 1Darray and equal (or closely equal, depend on choosing value in
    global parameter is_close)
    Parameter: a, b- 1d array to check
    Return True/False
    Reminder: only take value of a and b, and fill N/A with 'NAN_VALUE'
    '''
    if hasattr(a_val,'values'):
        a_val = a_val.values
    if hasattr(b_val,'values'):
        b_val = b_val.values

    if (np.issubdtype(a_val.dtype.type, np.int) or np.issubdtype(a_val.dtype.type, np.float)) and \
        (np.issubdtype(b_val.dtype.type, np.int) or np.issubdtype(b_val.dtype.type, np.float)):
        return np.all(is_close(a_val,b_val))

    if a_val.dtype.kind in {'U', 'S','O'} and b_val.dtype.kind in {'U', 'S','O'}:#if contain string
        # replace nan in string ndarray (all type of problems)
        a_val = pd.Series(a_val).fillna('NAN_VALUE').values
        b_val = pd.Series(b_val).fillna('NAN_VALUE').values

    return np.array_equal(a_val,b_val)

def is_df_equal(a_val,b_val,**kwargs):
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
    return np.all(list(map(is_1darray_equal, a_val.to_dict('series').values(),
                    b_val.to_dict('series').values())))

def is_equal(a_val,b_val,**kwargs):
    '''
    Check whether two dataf is closely equal or not. Implement is_1Darray_equal, is_df_equal.
    Parameter: a,b - two data; accepted datatype: int, float, list, tuple, ndarray, dataframe
    Return True/False
    '''
    if (a_val is None) or (b_val is None):
        return False
    if isinstance(a_val,(int,float)) and isinstance(b_val,(int,float)):
        return is_close(a_val,b_val)
    if isinstance(a_val,(list,tuple)) and isinstance(b_val,(list,tuple)):
        return is_1darray_equal(np.array(a_val),np.array(b_val))
    if isinstance(a_val, (np.ndarray,pd.Series)) and isinstance(b_val, (np.ndarray,pd.Series)):
        return is_1darray_equal(a_val,b_val)
    if isinstance(a_val,pd.DataFrame) and isinstance(b_val,pd.DataFrame):
        return is_df_equal(a_val,b_val,**kwargs)
    if not type(a_val) is type(b_val):
        return False
    return a_val==b_val

def check_sql(submission,solution,**kwargs):
    '''
    Check sql submission with corresponding sample answers by comparing strings
    Parameter: submission & solution- in check
        **kwargs include: - connection: whether in connect
    Return True/False
    '''
    is_debug = kwargs['debug'] if 'debug' in kwargs else True

    if 'connection' not in kwargs:
        printt("No database connection input",is_debug)
        return False

    if not isinstance(solution, str):
        printt("Your SQL answer must be a string",is_debug)
        return False

    try:
        conn = kwargs['connection']
        df_sub = pd.read_sql_query(submission, conn)
        df_sol = pd.read_sql_query(solution, conn)
        if is_equal(df_sub,df_sol,same_col_name=False):
            printt('You passed! Good job!',is_debug)
            return True

        printt("Your solution is not correct, try again!\n Make sure the order of each column is" +
                "correct, as shown in the output",is_debug)
        return False
    except Exception as err:
        printt(f'Something went wrong. {err}',is_debug)
        return False

def check_function(submission,solution,**kwargs):
    '''
    Check correctness of submission function by execute both functions to see if the result
    is correct
    Parameter: submission & solution- in check
        **kwargs include - test_cases: list of test case for checking
    Return True/False
    '''
    is_debug = kwargs['debug'] if 'debug' in kwargs else True

    if 'test_cases' not in kwargs:
        printt("No test cases input",is_debug)
        return False

    try:
        test_cases = kwargs['test_cases']
        score = 0
        exec(submission)
        exec(solution)
        func_name_sub = submission.split('(')[0][4:]
        func_name_sol = solution.split('(')[0][4:]
        for t_cases in test_cases:
            result_sub = locals()[func_name_sub](*t_cases)
            result_sol = locals()[func_name_sol](*t_cases)
            if is_equal(result_sub,result_sol):
                score += 1
        printt(f'You have passed {score}/{len(test_cases)} test cases',is_debug)
        return score/len(test_cases)
    except Exception as err:
        printt('Your solution is not correct, try again',is_debug)
        return 0

def check_expression(submission,solution,**kwargs):
    '''
    Check expression type question
    Parameter: submission & solution- in check
        **kwargs include - df: dataframe using
    Return True/False
    '''
    is_debug = kwargs['debug'] if 'debug' in kwargs else True

    if not isinstance(solution, str):
        printt("Your expression answer must be a string",is_debug)
        return False

    if 'df' not in kwargs:
        printt("No variable 'df'. Make you to use 'df' as your dataframe variable",is_debug)
        return False

    try:
        df = kwargs['df']
        result = eval(solution)
        result_sub = eval(submission)
        assert is_equal(result,result_sub)
        printt('You passed! Good job!',is_debug)
        return True
    except Exception as err:
        printt('Your solution is not correct, try again',is_debug)
        return False

def check_value(submission,solution,**kwargs):
    '''
    Check value type question (like multiple choice)
    Parameter: submission & solution: in check
    Return: True/False
    '''
    is_debug = kwargs['debug'] if 'debug' in kwargs else True

    try:
        assert is_equal(solution,submission)
        printt('You passed! Good job!',is_debug)
        return True
    except Exception as err:
        printt('Your solution is not correct, try again',is_debug)
        return False

def check(submission, solution, assignment_type, **kwargs):
    '''
    Implement all four checking answer function
    Parameter: submission & solution- in check
        assignment_type- type of assignment to check; choice including: 'SQL', 'Function',
        'Expression', 'Value'
    Return True/False
    '''
    if assignment_type == 'SQL':
        return check_sql(submission,solution,**kwargs)

    if assignment_type == 'Function':
        return check_function(submission,solution,**kwargs)


    if assignment_type == "Expression":
        return check_expression(submission,solution,**kwargs)

    if assignment_type == "Value":
        return check_value(submission,solution,**kwargs)

def verify_answer(answer_idx,answer_str,**kwargs):
    '''
    Verify whether user have login, check whether user have input email, check whether user have
    input anything illegal, and check their correctness; calculate the score of user
    Parameter: answer_idx: index of the question (to retrieve corresponding sample answer for
    grading)
        answer_str: the answer the examinee have inputed
        **kwargs includes related information for each question type to run
    '''
    if not set(['submission_data','checker_str','assignment']).issubset(globals()):
        print('Login required')
        print('Please make sure you have run the first cell above')
        return

    if 'email' not in submission_data:
        print('Login required')
        print('Please submit your email')
        return

    if answer_str not in globals():
        print('The answer is not defined. Make sure you have run the cell above first.')
        return

    answer = globals()[answer_str]


    if isinstance(answer,types.FunctionType):
        answer = inspect.getsource(answer)
    print("Your answer is:")
    print(answer)

    question = assignment.questions[answer_idx]
    solution = question['solution']
    result_type = question['resultType']
    question_id = question['_id']
    result = check(answer, solution, result_type,**kwargs)
    try:
        ans = submission_data['answers'][answer_idx]
        ans['answer'] = answer
        submission_data['currentScore'] -= question['score']*ans['clientCheck']
        ans['clientCheck'] = int(result)
        submission_data['currentScore'] += question['score']*ans['clientCheck']
        _ = Submission.create(db, submission_data)
    except IndexError:
        print('Wrong Answer Index')
    except Exception as err:
        print(f'Something else went wrong\n  {err}')
    finally:
        score = submission_data['currentScore']
        print(f'Your current score: {score}/{total_score}')
