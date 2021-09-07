'''
Submission class
'''
import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import inspect
import types
from .base import Base #pylint: disable=[relative-beyond-top-level]
from .assignment import Assignment #pylint: disable=[relative-beyond-top-level]
from .cohort import Cohort #pylint: disable=[relative-beyond-top-level]
from .utils import Utils


class Submission(Base): #pylint: disable=[too-few-public-methods]
    '''
    Submission object, to track all submissions
    '''
    ATTRIBUTES = ['_id', 'cohort_member_id', 'assignment_id', 'current_score',
                 'submission_url',  'email', 'name', 'answers', 'entries','created_by',
                 'updated_by', 'created_at', 'updated_at']
    REFS = ['cohort_member', 'assignment']
    name_of_class = "submissions"

    def __repr__(self):
        return super().__repr__(['_id','cohort_member_id','assignment_id', 'current_score'])

    def register_student(self):
        def submit_email(btn):
            with output:
                clear_output()
                if (len(email_field.value) == 0):
                    print("Please enter your email")
                    return
                self.email = email_field.value.strip().lower()

                btn.description = "Submitting..."
                btn.disabled = True

                first_submit = Submission.create(self.to_json())
                if (getattr(first_submit, '_id', '')):
                    if (getattr(first_submit, 'name', '')):
                        print(f'Welcome {first_submit.name}!')
                    else:
                        print(f'Welcome {first_submit.email}')
                else:
                    self.email = ''

                btn.description = "Submit"
                btn.disabled = False

        text = widgets.HTML(value='''
            Please enter the email that you used to register for the course.<br />
            <i>Submit again will reset all of your answers and current score!<i>
        ''')

        button = widgets.Button( icon='fa-paper-plane', description="Submit", button_style='success', tooltip='Submit')
        email_field = widgets.Text(
            value='',
            placeholder='Email..',
            description='Your email',
            disabled=False
        )
        button.on_click(submit_email)
        output = widgets.Output()

        display(text)
        display(email_field)
        display(button, output)

    def generate_question(self, q_index, global_dict, height='300px', width='600px'):
        '''Generate question's content and form to submit answer
        Parameters:
            - q_index: index of the quesiton in assignment.questions
            - global_dict: globals() of the runtime environment
            - height: height of the text area to input answer (default=300px)
            - width: width of the text area to input answer (default=600px)'''
        if not getattr(self, 'assignment', None) or not isinstance(self.assignment, Assignment):
            print('ERROR: assignment not defined')
            return

        def submit_answer(btn):
            with output:
                clear_output()
                answer = answer_field.value
                if (len(answer) == 0):
                    print("Please enter your answer")
                    return

                btn.description = "Submitting..."
                btn.disabled = True
                answer = answer.strip() if isinstance(answer, str) else ','.join(answer)

                # if self.assignment.assignment_type == "EXAM":
                #     # submit answer
                #     self.answers[q_index]['answer'] = answer
                #     self.answers[q_index]['clientCheck'] = 0
                #     _ = Submission.create(self.to_json())
                #     print('You have answered:', answer, sep='\n')
                # else:
                #     self.validate_answer(q_index, answer, global_dict)
                self.validate_answer(q_index, answer, global_dict)
                    
                btn.description = "Submit"
                btn.disabled = False
        def reset_answer(btn):
            self.answers[q_index]['answer'] = ''
            answer_field.value = ''

        # GUI
        question = self.assignment.questions[q_index]
        answer = self.answers[q_index]['answer']
        display(Markdown(question['question']))
        resultType = question['resultType']
        if resultType in ['VALUE', 'SQL', 'EXPRESSION', 'FUNCTION']:
            answer_field = widgets.Textarea(
                value=answer if answer else '',
                placeholder='YOUR_ANSWER_HERE',
                description='',
                disabled=False,
                layout=widgets.Layout(height=height, width=width)
            )
        elif resultType == 'MULTICHOICE_SINGLE':
            answer_field = widgets.RadioButtons(
                options=question['choices'],
                value=answer if answer else question['choices'][0],
            #    layout={'width': 'max-content'}, # If the items' names are long
                description='Your answer:',
                disabled=False
            )
        elif resultType == 'MULTICHOICE_MANY':
            answer_field = widgets.SelectMultiple(
                options=question['choices'],
                value= answer.split(',') if answer else [],
            #    layout={'width': 'max-content'}, # If the items' names are long
                description='Your answer:',
                disabled=False
            )

        btn_submit = widgets.Button( icon='fa-paper-plane', description="Submit", button_style='success', tooltip='Submit')
        btn_reset = widgets.Button( description="Reset answer", button_style='', tooltip='Reset answer')
        btn_submit.on_click(submit_answer)
        btn_reset.on_click(reset_answer)
        output = widgets.Output()

        display(answer_field)
        display(widgets.HBox([btn_submit, btn_reset]))
        display(output)

    def validate_answer(self, q_index, answer, global_dict):
        '''Validate student's answer
        Parameters:
            - q_index: index of the question in assignment.questions
            - answer: answer of the question
            - global_dict: globals() of the runtime environment
        '''
        if not getattr(self, 'email', ''):
            print('Login required')
            print('Please submit your email')
            return
        # if not Utils.check_available([answer_str], global_dict): return

        if isinstance(answer, types.FunctionType):
            answer = inspect.getsource(answer)
        print(f'Your answer is:\n{answer}')

        result = self.assignment.check(q_index, answer, global_dict)
        # required_karguments =  self.assignment.validate_environment(q_index, global_dict)
        # if (required_karguments):
        #     if type(required_karguments) is dict:
        #         result = self.assignment.check(q_index, answer, **required_karguments)
        #     else:
        #         result = self.assignment.check(q_index, answer)

        if result != 'INVALID':
            score = self.assignment.questions[q_index]['score']
            try:
                ans = self.answers[q_index]
                ans['answer'] = answer
                if ans['clientCheck'] > 0: self.current_score -= ans['clientCheck'] 
                ans['clientCheck'] = int(result * score)
                self.current_score += ans['clientCheck']
                _ = Submission.create(self.to_json())
            except IndexError:
                print('Wrong Question Index')
            except Exception as e:
                print(f'Something else went wrong\n  {e}')
            finally:
                if self.assignment.assignment_type != 'EXAM':
                    print(f'Your current score: {self.current_score}/{self.assignment.total_score}')

    @classmethod
    def initialize_submission(cls, assignment_id):
        assignment = Assignment.find_by_id(assignment_id)
        if not getattr(assignment, '_id', None) or not assignment._id:
            print("Assignment not found")
            return
        if not getattr(assignment, 'total_score', None): assignment.total_score = sum([q['score'] for q in assignment.questions])

        submission = cls({
            "assignmentId": assignment._id,
            "answers": [{'question': q['question'], 'answer':'', 'clientCheck':-1} for q in assignment.questions],
            "currentScore": 0
        })
        if assignment.assignment_type == 'EXAM':
            Utils.DEBUG = False

        submission.assignment = assignment
        return submission



