'''
Class Assignment
'''

from string import Template
import os
import pandas as pd
from datetime import datetime
from requests.api import get
from .utils import Utils
from .cohort import Cohort
from .course import Course
from .base import Base #pylint: disable=[relative-beyond-top-level]
from .templates import templates as tl
from .templates import install_cspyclient
from .security import encrypt, decrypt


class Assignment(Base): #pylint: disable=[too-few-public-methods]
    '''
    Assignment object, to manage all test assginments
    '''
    ATTRIBUTES = ['_id', 'name', 'slug', 'cohort_id', 'assignment_type', 'preparation_code',
                  'questions', 'total_score', 'assignment_url', 'max_progress_score', 'member_only',
                  'created_by', 'updated_by', 'created_at', 'updated_at']
    REFS = ['cohort']
    name_of_class = "assignments"

    def set_attributes(self, data):
        super().set_attributes(data)
        self.__solutions = []
        if getattr(self, 'questions', '') and isinstance(self.questions, list):
            for question in self.questions:
                if question and ('resultType' in question) and ('solution' in question):
                    self.__solutions.append(encrypt(question['solution']))
                    del question['solution']

    def save(self):
        '''
        Update data of the object in server, if the object has not in server yet,
        create a new instance and put the object on
        '''
        if not self.db_service.is_user():
            print('ERROR: Login required')
            return

        for index, solution in enumerate(self.__solutions):
            encrypt_solution = decrypt(solution)
            self.questions[index]['solution'] = encrypt_solution

        if not getattr(self, '_id', ''):
            new_data = self.db_service.post(f'/{self.name_of_class}', self.to_json())
            if new_data and '_id' in new_data:
                self.set_attributes(new_data)
        else:
            updated_data = self.db_service.put(f'/{self.name_of_class}/{self._id}', self.to_json())
            if updated_data and '_id' in updated_data:
                self.set_attributes(updated_data)

    def __repr__(self):
        return super().__repr__(['_id', 'name'])

    def __get_assignment_cells(self, show_solution=True ):
        ''' Return the list of cells in auto-generated assignment notebook'''
        if (not getattr(self, 'name', '') or not getattr(self, '_id', '')):
            print('Assignment name and id are required')
            return []

        assignment_cells = [
            { 'content': tl['coderschool_logo'], 'type': 'text'},
            { 'content': Template(tl['notebook_title']).substitute({'name': self.name}), 'type': 'text'},
            { 'content': Template(tl['assignment_init']).substitute({'assignment_id': self._id, 'install_cspyclient': install_cspyclient}), 'type': 'code'},
            { 'content': tl['preparation_md'], 'type': 'text'},
            { 'content': self.preparation_code, 'type': 'code'},
        ]

        for i, question in enumerate(self.questions):
            assignment_cells.append({'content': Template(tl['question_title']).substitute({'index': i+1, 'score': question['score'], 'type': question['resultType']} ), 'type': 'text'})
            assignment_cells.append({'content': Template(tl['question_generate']).substitute({'index': i, 'index_inc': i+1 }), 'type': 'code'})
            # version 1
            '''
            assignment_cells.append({'type': 'text', 'content': question['question']})
            if (question['resultType'] == 'SQL'):
                assignment_cells.append({'content': Template(tl['answer_types']['SQL']).substitute({'index': i+1}), 'type': 'code'})
                assignment_cells.append({'content': Template(tl['solution_types']['SQL']).substitute({'index': i+1, 'solution': question['solution']}), 'type': 'code'})
                assignment_cells.append({'content': Template(tl['verify_types']['SQL']).substitute({'index': i+1}), 'type': 'code'})
            elif (question['resultType'] == 'FUNCTION'):
                assignment_cells.append({'content': Template(tl['answer_types']['FUNCTION']).substitute({'index': i+1}), 'type': 'code'})
                assignment_cells.append({'content': Template(tl['verify_types']['FUNCTION']).substitute({'index': i+1}), 'type': 'code'})
                if show_solution:
                    assignment_cells.append({'content': question['solution'], 'type': 'code'})
            elif (question['resultType'] == 'EXPRESSION'):
                assignment_cells.append({'content': Template(tl['answer_types']['EXPRESSION']).substitute({'index': i+1}), 'type': 'code'})
                if show_solution:
                    assignment_cells.append({'content': question['solution'], 'type': 'code'})
            elif (question['resultType'] == 'VALUE'):
                # TODO: answer type value with select box -> need to add list of choices
                assignment_cells.append({'content': Template(tl['answer_types']['VALUE']).substitute({'index': i+1, 'options': ["A", "B", "C", "D", "E"]}), 'type': 'code'})
                if show_solution:
                    solution = question['solution']
                    assignment_cells.append({'content': f'solution_{i+1} = {solution}', 'type': 'code'})
            '''
        return assignment_cells

    def export_notebook(self, path='.', run_all_test=True):
        '''Export assignment to notebook
        
        Parameters:
            - path: path to the folder that contains the output notebook
            - run_all_test: include solution in the answer to test the notebook by run all cells
        '''
        if not self.db_service.is_user():
            print('ERROR: Login required')
            return

        if (not getattr(self, 'name', '') or not getattr(self, '_id', '')):
            print('Assignment name and id are required')
            return None
        filename = os.path.join(path, f'{self.name}.ipynb')
        return Utils.generate_notebook(filename, self.__get_assignment_cells())

    def check_prep_code(self):
        if not self.preparation_code:
            print('ERROR: Missing preparation code')
            return False

        try:
            lines_of_prep_code = self.preparation_code.split('\n')
            for i, line in enumerate(lines_of_prep_code):
                if line.startswith('!'):
                    os.system(line[1:])
                    lines_of_prep_code.pop(i)
            prep_code = '\n'.join(lines_of_prep_code)
            exec(prep_code)

            # code = Utils.remove_command_line(self.preparation_code)
            # exec(code)
            print('Preparation Code is fine!')
            return True
        except Exception as e:
            print('Some thing wrong with your prep code')
            print(e)
            return False

    def check_question(self, index):
        '''Validate a question by it's index

        Parameters:
            - index: index of the question in assignment.questions
        '''
        try:
            if (not getattr(self, 'questions', '') or not isinstance(self.questions, (list))):
                print('Assignment questions are not available')
                return False
            if len(self.questions) <= index:
                print(f'Error - questions[{index}]: Wrong index')
                return False
            question = self.questions[index]
            if ('question' not in question or not question['question'].strip()):
                print(f'Error - questions[{index}]: Question is empty')
                return False
            if ('resultType' not in question):
                print(f'Error - questions[{index}]: Missing resultType')
                return False
            if ('score' not in question):
                print(f'Error - questions[{index}]: Missing score')
                return False
            if ('solution' not in question):
                print(f'Error - questions[{index}]: Missing solution')
                return False

            if (question['resultType'] == 'EXPRESSION'):
                code = Utils.remove_command_line(self.preparation_code)
                exec(code)
                output = eval(question['solution'], locals())

            if (question['resultType'] == 'FUNCTION'):
                code = Utils.remove_command_line(self.preparation_code)
                exec(code)
                exec(question['solution'], locals())

                if ('testCases' not in question):
                    print(f'Error - questions[{index}]: Missing test cases')
                    return False
                
                func_name_sol = question['solution'].split('(')[0][4:]
                for tc in question['testCases']:
                    output = locals()[func_name_sol](*tc)

            if (question['resultType'] == 'SQL'):
                if (not isinstance(question['solution'], str)):
                    print(f'Error - questions[{index}]: Your SQL query must be a string')
                    return False

            if (question['resultType'] == 'MULTICHOICE_SINGLE'):
                if ('choices' not in question):
                    print(f"Error - questions[{index}]: Missing the array choices. Example ['A', 'B', 'C', 'D']")
                    return False
                if (question['solution'] not in question['choices']):
                    print(f"Error - questions[{index}]: The solution must be an element of choices")
                    return False

            if (question['resultType'] == 'MULTICHOICE_MANY'):
                if ('choices' not in question):
                    print(f"Error - questions[{index}]: Missing the array choices. Example ['A', 'B', 'C', 'D']")
                    return False
                if (not isinstance(question['solution'], str)):
                    print(f'''Error - questions[{index}]: The solutions should be a string. Example "A,B"''')
                    return False
                if not set(question['solution'].split(',')).issubset(set(question['choices'])) :
                    print(f"Error - questions[{index}]: The solution after splitting by ',' must be a subset of choices")
                    return False

            print(f'Question {index} is fine!')
            return True
        except Exception as e:
            print(f'Some thing wrong with question[{index}]')
            print(e)
            return False

    def validate_questions(self):
        '''Validate list of questions'''
        if (not getattr(self, 'questions', '') or not isinstance(self.questions, (list))):
            print('Assignment questions are not available')
            return False
        for i in range(len(self.questions)):
            if not self.check_question(i):
                return False
        return True

    def check(self, index, answer, global_dict):
        resultType = self.questions[index]['resultType']
        solution = decrypt(self.__solutions[index])
        if (resultType == 'SQL'):
            if Utils.check_available(['conn'], global_dict): # and str(type(global_dict['conn'])) == "<class 'sqlite3.Connection'>":
                conn = global_dict['conn']
                return Utils.check_sql(answer, solution, connection=conn)
            else:
                return 'INVALID'

        if (resultType == 'FUNCTION'):
            return Utils.check_function(answer, solution, self.questions[index]['testCases'])

        if (resultType == "EXPRESSION"):
            return Utils.check_expression(answer, solution, global_dict)
            
        if (resultType == "VALUE"):
            return Utils.check_value(answer, solution)

        if (resultType == "MULTICHOICE_SINGLE"):
            return Utils.check_value(answer.upper(), solution.upper())

        if (resultType == "MULTICHOICE_MANY"):
            return Utils.check_value([a.upper().strip() for a in answer.split(',')], 
                                     [s.upper().strip() for s in solution.split(',')])

    def evaluate_single_submission(self, submission, exec_prep_code=True):
        '''Evaluate answers of a submission. The answers is a list of answer for all of the questions in assignment
        Before the evaluation, the preparation code of the assignment will be executed.
        Parameters:
            - answers: list of answer for quesions in assignment.questions
        Return: Total score of the assignment
        '''
        if not getattr(submission, 'answers', None) or not isinstance(submission.answers, list):
            return 0
        
        # execute preparation code, run the commandline (the line which starts with !) separately
        if exec_prep_code:
            lines_of_prep_code = self.preparation_code.split('\n')
            for i, line in enumerate(lines_of_prep_code):
                if line.startswith('!'):
                    os.system(line[1:])
                    lines_of_prep_code.pop(i)
            prep_code = '\n'.join(lines_of_prep_code)
            exec(prep_code)

        answers = submission.answers
        score = 0
        for idx, (question, answer) in enumerate(zip(self.questions, answers)):
            try:
                result = self.check(idx, answer['answer'], locals())
                if result != 'INVALID':
                    score += int(question['score'] * result)
            except Exception as e:
                print(f'{e}')
        return score

    def evaluate_submissions(self, submissions, output='DataFrame', exec_prep_code=True):
        '''Evaluate all submissions to this assignment.
        Return: A DataFrame of Submission Grades'''
        if not isinstance(submissions, list) or not submissions:
            print('ERROR: Submissions must be a non-empty list')
            return
        if getattr(submissions[0], 'assignment_id', '') != self._id:
            print('ERROR: Invalid submissions')
            return
        
        # execute preparation code, run the commandline (the line which starts with !) separately
        if exec_prep_code:
            lines_of_prep_code = self.preparation_code.split('\n')
            for i, line in enumerate(lines_of_prep_code):
                if line.startswith('!'):
                    os.system(line[1:])
                    lines_of_prep_code.pop(i)
            prep_code = '\n'.join(lines_of_prep_code)
            exec(prep_code)

        report = {
            'email': [], 
            'totalScore': [], 
            'assignmentId': [],
            'cohortMemberId': [],
            'graderId': [],
            'notes': [],
            'status': []
        }
        for submission in submissions:
            score = 0
            answers = submission.answers
            for idx, (question, answer) in enumerate(zip(self.questions, answers)):
                try:
                    result = self.check(idx, answer['answer'], locals())
                    if result != 'INVALID':
                        score += int(question['score'] * result)
                except Exception as e:
                    print(f'{e}')
            report['email'].append(submission.email)
            report['totalScore'].append(score)
            report['assignmentId'] = self.id
            report['cohortMemberId'] = submission.cohort_member_id
            report['graderId'] = self.db_service.get_current_user_id()
            report['notes'] = "Evaluated by instructors"
            report['status'] = "COMPLETED"
            
        if output=='DataFrame':
            return pd.DataFrame(report)
        else:
            return report

    def validate_environment(self, q_index, global_dict):
        if (self.questions[q_index]['resultType'] == 'SQL'):
            if Utils.check_available(['conn'], global_dict) and str(type(global_dict['conn'])) == "<class 'sqlite3.Connection'>":
                return {'connection': global_dict['conn']}
            return False
        return True

    @classmethod
    def find_one_by_name(cls, the_name):
        '''
        Get the first value of the class that match a key, with default key is its 'name'
        Parameter:
            the_name: the current key in query
        Return: result in current object type
        '''
        return cls.find_one(filter_={'name':the_name})

    def edit_assignment_template(self, path='.'):
        '''Generate a notebook template to create new assignments
        
        Parameters:
            - path: path to the folder that contains the output notebook
        '''
        if not self.db_service.is_user():
            print('ERROR: Login required')
            return

        if not getattr(self, '_id', ''):
            print('ERROR: Invalid assignment')
            return

        num_question = len(self.questions)
        cohort = Cohort.find_by_id(self.cohort_id)
        cells = [
            { 'content': tl['coderschool_logo'], 'type': 'text'},
            { 'content': Template(tl['notebook_title']).substitute({'name': self.name}), 'type': 'text'},
            { 'content': install_cspyclient, 'type': 'code'},
            { 'content': tl['google_login'], 'type': 'code'},
            { 'content': Template(tl['init_edit_assignment']).substitute({
                'assignment_id': self._id, 
                'name': self.name,
                'cohort_name': cohort.name, 
                'assignment_type':self.assignment_type, 
                'max_progress_score': self.max_progress_score }), 'type': 'code'},
            { 'content': Template(tl['preparation_code']).substitute({'preparation_code': self.preparation_code}), 'type': 'code'},
            { 'content': Template(tl['assign_preparation_code']).substitute({'preparation_code': self.preparation_code}), 'type': 'code'},
        ]

        for i in range(num_question):
            cells.append({ 'content': Template(tl['question_title']).substitute({'index': i+1, 'type': self.questions[i]['resultType'], 'score': self.questions[i]['score']} ), 'type': 'text'})
            cells.append({ 'content': Template(tl['init_question']).substitute({'index': i, 'result_type': self.questions[i]['resultType'], 'score': self.questions[i]['score']}), 'type': 'code'})
            cells.append({ 'content': Template(tl['question_md']).substitute({'question': self.questions[i]['question']}), 'type': 'text'})
            cells.append({ 'content': Template(tl['solution_code']).substitute({'solution': decrypt(self.__solutions[i])}), 'type': 'code'})
            cells.append({ 'content': Template(tl['check_question']).substitute({'index': i, 'question': self.questions[i]['question'], 'solution': decrypt(self.__solutions[i])}), 'type': 'code'})

        cells.append({'content': '## Save assignment', 'type': 'text'})
        cells.append({'content': tl['validate_all_questions'], 'type': 'code'})
        filename = os.path.join(path, f'edit_{self.name}.ipynb')
        return Utils.generate_notebook(filename, cells)

    @classmethod
    def create_assignment_template(cls, num_question, path='.'):
        '''Generate a notebook template to create new assignments
        
        Parameters:
            - path: path to the folder that contains the output notebook
        '''
        if not cls.db_service.is_user():
            print('ERROR: Login required')
            return

        if (not isinstance(num_question, (int)) or num_question <= 0):
            print('num_question must be a positive number')
            return None

        cells = [
            { 'content': tl['coderschool_logo'], 'type': 'text'},
            { 'content': Template(tl['notebook_title']).substitute({'name': 'Create new Assignment'}), 'type': 'text'},
            { 'content': install_cspyclient, 'type': 'code'},
            { 'content': tl['google_login'], 'type': 'code'},
            { 'content': Template(tl['init_create_assignment']).substitute({'num_question': num_question}), 'type': 'code'},
            { 'content': Template(tl['preparation_code']).substitute({'preparation_code': ''}), 'type': 'code'},
            { 'content': Template(tl['assign_preparation_code']).substitute({'preparation_code': 'COPY_PASTE_YOUR_PREP_CODE_HERE'}), 'type': 'code'},
        ]

        for i in range(num_question):
            cells.append({ 'content': Template(tl['question_title']).substitute({'index': i+1, 'type': '', 'score': ''} ), 'type': 'text'})
            cells.append({ 'content': Template(tl['init_question']).substitute({'index': i, 'result_type': 'VALUE', 'score': 10}), 'type': 'code'})
            cells.append({ 'content': Template(tl['question_md']).substitute({'question': '**Edit this for the question markdown content**'}), 'type': 'text'})
            cells.append({ 'content': Template(tl['solution_code']).substitute({'solution': "# YOUR_SOLUTION_HERE"}), 'type': 'code'})
            cells.append({ 'content': Template(tl['check_question']).substitute({'index': i, 'question': 'COPY_PASTE_YOUR_QUESTION_MARKDOWN', 'solution': 'COPY_PASTE_YOUR_SOLUTION'}), 'type': 'code'})

        cells.append({'content': '## Save assignment', 'type': 'text'})
        cells.append({'content': tl['validate_all_questions'], 'type': 'code'})

        now = str(int(datetime.timestamp(datetime.now())))
        filename = os.path.join(path, f'create_assignment_{now}.ipynb')
        return Utils.generate_notebook(filename, cells)

    # @classmethod
    # def evaluate_assignments_template(cls, cohort_id, student_only=True, path='.'):
    #     '''Generate a notebook for evaluating submissions of assignments
    #     Parameters:
    #         - student_only: Get student submissions only
    #     '''
    #     cohort = Cohort.find_by_id(cohort_id)
    #     if (not cohort):
    #         print('Course or Cohort not exists')
    #         return
    #     course = Course.find_by_id(cohort.course_id)
    #     assignments, _ = cls.find({'cohortId': cohort._id}, output='object')
    #     assignment_names = [a.name for a in assignments]
    #     assignment_dict = {a.name: a._id for a in assignments}
    #     cells = [
    #         { 'content': tl['coderschool_logo'], 'type': 'text'},
    #         { 'content': tl['notebook_title'], 'type': 'text'},
    #         { 'content': tl['evaluation_init'], 'type': 'code'},
    #         { 'content': tl['list_assignments'], 'type': 'code'},
    #         { 'content': tl['prepare_prep_code'], 'type': 'code'},
    #         { 'content': tl['evaluate_submissions'], 'type': 'code'},
    #         { 'content': tl['submission_overview'], 'type': 'code'},
    #         { 'content': tl['score_by_time'], 'type': 'code'},
    #         { 'content': tl['student_performance'], 'type': 'code'},
    #         { 'content': tl['tricky_question'], 'type': 'code'},
    #     ]

    #     filename = os.path.join(path, f'evaluate_{cohort.name}.ipynb')
    #     return Utils.generate_notebook(filename, cells)

    @classmethod
    def __evaluate_assignments_template(cls, cohort_id, student_only=True, path='.'):
        '''Generate a notebook for evaluating submissions of assignments
        Parameters:
            - student_only: Get student submissions only
        '''
        cohort = Cohort.find_by_id(cohort_id)
        if (not cohort):
            print('Course or Cohort not exists')
            return
        course = Course.find_by_id(cohort.course_id)
        assignments, _ = cls.find({'cohortId': cohort._id}, output='object')
        assignment_names = [a.name for a in assignments]
        assignment_dict = {a.name: a._id for a in assignments}
        cells = [
            { 'content': tl['coderschool_logo'], 'type': 'text'},
            { 'content': Template(tl['notebook_title']).substitute({'name': 'Assignment Grade Viewer'}), 'type': 'text'},
            { 'content': Template(tl['evaluation_init']).substitute({'install_cspyclient': install_cspyclient}), 'type': 'code'},
            { 'content': Template(tl['list_assignments']).substitute({
                'first': assignment_names[0], 
                'list': assignment_names,
                'dict': assignment_dict,
                'cohort_id': cohort._id,
                'course_id': course._id
                }), 'type': 'code'},
            { 'content': tl['prepare_prep_code'], 'type': 'code'},
            { 'content': tl['evaluate_submissions'], 'type': 'code'},
            { 'content': tl['submission_overview'], 'type': 'code'},
            { 'content': tl['score_by_time'], 'type': 'code'},
            { 'content': tl['student_performance'], 'type': 'code'},
            { 'content': tl['tricky_question'], 'type': 'code'},
        ]

        filename = os.path.join(path, f'evaluate_{cohort.name}.ipynb')
        return Utils.generate_notebook(filename, cells)

    