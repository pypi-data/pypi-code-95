'''This contains templates which are used to generate notebooks'''

''' Dictionary of templates in general
'''
# install_cspyclient = '!pip install -q --index-url https://test.pypi.org/simple/ cspyclient'
install_cspyclient = '!pip install -q cspyclient'
templates = {
    'coderschool_logo': '![](https://i.imgur.com/0AUxkXt.png)',

    'notebook_title': '# $name',

    'assignment_init': '''\
#@title Before you start, please login with the same email you have registered for the course {display-mode: "form"}

$install_cspyclient
import cspyclient as cs

submission = cs.Submission.initialize_submission('$assignment_id')

submission.register_student()''',

    'google_login': '''\
#@title Please log in with your CoderSchool email
import cspyclient as cs

cs.Base.db_service.colab_google_login()
# Or login with your account
# cs.Base.db_service.auth(user=cs.User({'email': 'coderschool_email', 'password': 'your_password'}))''',

    'preparation_md': '**Import data and libraries**', 

    'question_title': '### Question $index ($type - $score pts)',
    'question_generate': '''\
#@title Run this to start question $index_inc

submission.generate_question($index, globals(), height='100px')''',

    'answer_types': {
        'SQL': '''\
answer_$index="""
    YOUR QUERY HERE
"""
pd.read_sql_query(answer_$index, conn)''',

        'FUNCTION': '''\
def answer_$index(df):
    # YOUR CODE HERE''',

        'EXPRESSION': '''\
#@title ####Put your answer here
answer_$index = "" #@param {type:"string"}

idx = $index
assignment.verify_answer(idx-1, f'answer_{idx}')''',

        'VALUE': '''\
#@title Choose your answer from the dropdown list
answer_$index = '' #@param $options {allow-input: true}

idx = $index
assignment.verify_answer(idx-1,f'answer_{idx}')''',
    },

    'verify_types': {
        'SQL': '''\
#@title Run this to check your answer
idx=$index
assignment.verify_answer(idx-1, f'answer_{idx}', connection=conn)''',
        'FUNCTION': '''\
#@title Run this to check your answer
idx=$index
assignment.verify_answer(idx-1, f'answer_{idx}')'''
    },

    'solution_types': {
        'SQL': '''\
# Expected result
solution_$index="""
    $solution
"""
pd.read_sql_query(solution_$index, conn)'''
    },

    # create/edit new assignment
    'init_create_assignment': '''\
#@title Initialize assignment
#@markdown Fill the form and then run the cell

name = ''  #@param {type: "string"}
cohort_name = ''  #@param {type: "string"}
assignment_type = "LAB" #@param ["LAB", "EXAM", "QUIZ", "PREWORK"]
max_progress_score = 10  #@param {type: "slider", min: 1, max: 20}
#@markdown ---

assignment = None
num_question = $num_question
cohort = cs.Cohort.find_one_by_name(cohort_name)
if (not cohort):
    print('ERROR: Cohort not found.')
else:
    assignment = cs.Assignment({'name': name, 'cohortId': cohort._id, 'assignmentType': assignment_type, 'maxProgressScore': max_progress_score, 'questions': [{} for _ in range(num_question)]})
if (assignment and assignment.name == name):
    print('Done')''',

    'init_edit_assignment': '''\
#@title Initialize assignment
#@markdown Fill the form and then run the cell

name = '$name'  #@param {type: "string"}
cohort_name = '$cohort_name'  #@param {type: "string"}
assignment_type = '$assignment_type' #@param ["LAB", "EXAM", "QUIZ", "PREWORK"]
max_progress_score = $max_progress_score  #@param {type: "slider", min: 1, max: 20}
#@markdown ---

assignment = cs.Assignment.find_by_id("$assignment_id")
cohort = cs.Cohort.find_by_id(assignment.cohort_id)
assignment.name = name
assignment.assignment_type = assignment_type
assignment.max_progress_score = max_progress_score
assignment.save()''',

    'preparation_code': '''\
# Preparation code
# The code needed to run this assignment
$preparation_code''',

    'assign_preparation_code': '''\
assignment.preparation_code = """
$preparation_code
"""

assignment.check_prep_code()''',

    'init_question': '''\
#@title Init question
#@markdown Fill the form and then run the cell

result_type = "$result_type" #@param ["VALUE", "EXPRESSION", "SQL", "FUNCTION", "MULTICHOICE_SINGLE", "MULTICHOICE_MANY"]
score = $score  #@param {type: "number"}
#@markdown ---

index = $index
assignment.questions[index]['resultType'] = result_type
assignment.questions[index]['score'] = score''',

    'question_md': '$question',

    'solution_code': '''\
# For testing
$solution''',

    'check_question': '''\
index = $index
assignment.questions[index]['question'] = """
$question
""".strip()

assignment.questions[index]['solution'] = """
$solution
""".strip()

assignment.check_question(index)''',

    'validate_all_questions': '''\
# Validate all questions before save
if assignment.validate_questions():
    assignment.save()''',

    # Evaluation
    'evaluation_init': '''\
#@title #*step1* ▸ Log in with your CoderSchool email

# --------- Identification ------------ 
$install_cspyclient
import cspyclient as cs

cs.Base.db_service.colab_google_login()

# --------- Libraries ------------ 

# Handle data
import sqlite3
import pandas as pd
%load_ext google.colab.data_table

# Visualization
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns
sns.set_style("whitegrid")

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Misc
import json
import re
import warnings
warnings.filterwarnings('ignore')
import IPython
from IPython.display import clear_output
from google.colab import output

# --------- Hyper-parameters ------------ 
STAFF_EMAILS = ['nhamhung.gttn@gmail.com',
                'hieutrinh.au@gmail.com',
                'minhhuu291@gmail.com',
                'thongn29798@gmail.com',
                'janetvn@gmail.com',
                'binh.tpa1@gmail.com',
                'kimhiennguyen2811@gmail.com',
                'hangnguyennn13@gmail.com',
                'anhquan0412@gmail.com',
                'quan.tran@coderschool.vn',
                'nhan.phan@coderschool.vn',
                'ai.nguyen@coderschool.vn',
                'minhdh@coderschool.vn',
                'dhminh1024@gmail.com',
                'huynhdao0808@gmail.com',
                'sang@coderschool.vn',
                'giang@coderschool.vn',
                'tom@coderschool.vn'
                ]''',

    'list_assignments': '''\
#@title #*step2* ▸ Choose assignment to and click run to view

assignment_name = '$first' #@param $list

course = cs.Course.find_by_id('$course_id')
cohort = cs.Cohort.find_by_id('$cohort_id')
assignment = cs.Assignment.find_one_by_name(assignment_name)

print(f"You are viewing the report of: \n{course} \n{cohort} \n {assignment}")
''',

    'prepare_prep_code': '''\
#@title #*step3* ▸ Run to prepare grading material
DEBUG = False
try:
    exec(assignment.preparation_code)
    print(f"Grading material is ready for {assignment}")
except Exception as e:
    print(e)
''',

    'evaluate_submissions': """\
#@title #*step4* ▸ Run to evaluate students' submissions

def get_graded_submissions(assignment):
    # Get submission dataset
    print("Getting submissions...")
    submissions, _ = cs.Submission.find(filter_={'assignmentId': assignment._id})

    # Cleaning
    submissions = submissions[~submissions['email'].isin(STAFF_EMAILS)]                
    submissions = submissions[['_id', 'cohortMember', 'assignment', 'name', 'email', 'answers', 'createdAt']]
    submissions['createdAt'] = pd.to_datetime(submissions['createdAt'])

    # --------- EVALUATION -----------------------------------------------------
    print("Start evaluating...")
    submissions['score'] = submissions['answers'].apply(lambda x: assignment.evaluate(answers=x))

    # --------- COMPUTE DURATION -----------------------------------------------
    first_created = submissions.groupby('email')['createdAt'].min().reset_index().rename(columns={'createdAt': 'firstCreated'})
    result = pd.merge(submissions, first_created, on='email')
    result['time'] = (result['createdAt'] - result['firstCreated']) / pd.to_timedelta(1, 'm')
    
    #---------- COMPUTE WHICH QUESTION THE STUDENT IS AT -----------------------
    # Sort by email and time. Placeholding questionAt column
    result = result.sort_values(['name', 'time'], ascending=[True, False])
    result['questionAt'] = 0

    # Get questions that user committed
    def get_clientCheck(x):
        result = np.array([dic['clientCheck'] for dic in x])
        return result

    result['questionCommit'] = result['answers'].apply(get_clientCheck)

    # Get index of the question that user at 
    def get_question_idx(x):
        if 1 in x:
            return np.argmax(x) + 1
        else: 
            return None

    # Apply on each user
    def compute_question_at(df, email):
        # Filter email and index 
        df_ = df[df['email'] == email]
        idx = df_.index

        # Get the updated answer
        current_question_at = df_['questionCommit']
        previous_question_at = current_question_at.shift(periods=-1)

        diff = current_question_at - previous_question_at
        # Fillna: ffill to fill the work in progess, bfill to fill the complete case, fill-1 for people who never get pass Q1
        output = diff.apply(get_question_idx).fillna(method='ffill').fillna(method='bfill').fillna(1)
        df.loc[idx, 'questionAt'] = output.values

    # Apply on the whole dataset
    for email in result['email'].unique():
        compute_question_at(result, email)

    # --------- DISPLAY INFO ---------------------------------------------------
    clear_output()

    # Get number of submission
    number_submissions = submissions.shape[0]
    number_students = submissions['email'].nunique()

    # Get max score reached
    total = pd.DataFrame(assignment.questions)['score'].sum()
    max_score = result['score'].max()
    num_max_students = result[result['score'] == max_score]['email'].nunique()

    # Display

    message = f"###Received {number_submissions} submissions from {number_students} students ❊ Max score reached is {max_score}/{total} by {num_max_students} students."
    display(IPython.display.Markdown(message))
    display(IPython.display.Markdown(f"*Use the Filter button on the right to explore*"))
    
    return result, submissions


result, submissions = get_graded_submissions(assignment=assignment)
result = result.sort_values(['name', 'score'], ascending=[True, False])
result[['cohortMember', 'name', 'email', 'createdAt', 'score', 'time']]""",

    'submission_overview': """\
#@title ## 🧮 Submission Overview
by_email = result.groupby('email')['score'].agg(['idxmax', 'count']).reset_index()
plot_data = result.loc[by_email['idxmax'].values].sort_values('email')
plot_data = plot_data.merge(by_email[['email', 'count']]).rename(columns={'count':'attempt'})

# Plot Histogram
display(IPython.display.HTML('''
    <h3> Distribution of score and time spent </h3>
    '''))

fig = make_subplots(rows=1, cols=2, subplot_titles=('Score', 'Time'))
fig.add_trace(go.Histogram(x=plot_data['score'], 
                           nbinsx=5, 
                           marker_color='slateblue', 
                           name='Time',
                           hovertemplate=
                           '<i>Range</i>: %{x}'+
                           '<br><i>Count</i>: %{y}'),
              row=1, col=1)

fig.add_trace(go.Histogram(x=plot_data['time'], 
                           nbinsx=10, 
                           marker_color='salmon', 
                           name='Time',
                           hovertemplate=
                           '<i>Range</i>: %{x}'+
                           '<br><i>Count</i>: %{y}'),
              row=1, col=2)

fig.update_layout(template="plotly_white", showlegend=False)
fig.show()


# Display score table
display(IPython.display.HTML('''
    <h3> Students and their best scores </h3>
    <i> Use Filter button to view students in certain score range.</i>
    '''))
plot_data[['_id', 'name', 'email', 'createdAt', 'score', 'time', 'attempt']].sort_values('score', ascending=False)""",

    'score_by_time': """\
#@title ##💯 Score by Time 

display(IPython.display.HTML('''
    <h3><i>Choose area to zoom in / Double click to zoom out</i></h3>
    <p>Darker markers means more attempts were made to get there.</p>
    '''))

fig = px.scatter(plot_data, 
                 x='time', 
                 y='score',
                 color='attempt',
                 hover_name='email',
                 template="plotly_white",
                 color_continuous_scale='Reds',
                 labels={'time':'Time (minute) ', 'score':'Score', 'attempt':'Attempts', 'email':'Email'})

fig.update_traces(marker=dict(size=8))
fig.show()""",

    'student_performance': """\
#@title ## 📈 Student Performance

Option = 'Exclude no progress students' #@param ["Include no progress students", "Exclude no progress students"]

display(IPython.display.HTML('''
    <h3><i>Double-click on the legend to select certain student(s) data.</i></h3>
    '''))

no_progress = plot_data[plot_data['score'] == 0]['email']

if Option == 'Include no progress students':
    plot_data_2 = result.sort_values(['email', 'time'])
else:
    plot_data_2 = result[~result['email'].isin(no_progress)].sort_values(['email', 'time'])                                    

fig = px.line(plot_data_2, 
              x="time", 
              y="score", 
              color="email", 
              hover_name="email",
              template="plotly_white")
fig.update_traces(mode="markers+lines")
fig.show()""",

    'tricky_question': """\
#@title ##😤 Which Question Is Tricky? 

Option = 'Include no progress students' #@param ["Include no progress students", "Exclude no progress students"]

display(IPython.display.HTML('''
    <h3><i>Double-click on the legend to select certain student(s) data.</i></h3>
    '''))

no_progress = plot_data[plot_data['score'] == 0]['email']

if Option == 'Include no progress students':
    plot_data_2 = result.sort_values(['email', 'time'])
else:
    plot_data_2 = result[~result['email'].isin(no_progress)].sort_values(['email', 'time']) 

fig = px.line(plot_data_2, 
              x="time", 
              y="questionAt", 
              color="email", 
              hover_name="email",
              template="plotly_white")
fig.update_traces(mode="markers+lines")
fig.update_layout(yaxis_range=[1,len(assignment.questions)])
fig.show()""",

    'who_not_submitted': """\
#@title ##😴 Who Have Not Submitted? 

def get_student_list_dataframe(cohort):
    cohort_students, _ = cohort.get_student_list()
    return cohort_students[['_id', 'name','email', 'progressScore', 'cohortMemberId']]

cohort_students = get_student_list_dataframe(cohort)
cohort_students = cohort_students[~cohort_students['email'].isin(STAFF_EMAILS)]['email'].unique() 
submitted_students = result['email'].unique()
no_submit_students = set(cohort_students).symmetric_difference(set(submitted_students))

print(f"{len(no_submit_students)}/{len(cohort_students)} students haven't submitted their assignments.")
no_submit_students"""
}


