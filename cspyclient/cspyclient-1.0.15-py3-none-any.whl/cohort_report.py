import json
from .cohort_group import CohortGroup
from .cohort import Cohort
from .session import Session
from .submission_grade import SubmissionGrade
from .assignment import Assignment
from .attendance import Attendance
from .submission import Submission
import pandas as pd
import numpy as np
import math

def cohort_report(cohort_name, time_range={}, port=8051):
    '''Generate a real-time Dash app that shows the cohort report

    Parameters:
        - cohort_name: name of the cohort
    '''
    try:
        import dash
        from jupyter_dash import JupyterDash
        import dash_core_components as dcc
        import dash_html_components as html
        import dash_bootstrap_components as dbc
        import dash_daq as daq
        from dash.dependencies import Input, Output, State
        import dash_table
        import plotly.express as px
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go        
    except:
        print('Installation required: pip install -q jupyter-dash dash-bootstrap-components dash-daq')
        return

    app = JupyterDash(
        __name__, 
        external_stylesheets=[dbc.themes.SUPERHERO, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
        meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}]
    )

    cohort = Cohort.find_one_by_name(cohort_name)
    if not getattr(cohort, '_id', None) or not cohort._id:
        print("ERROR: Cohort not found")
        return

    cohort_groups, n_group = CohortGroup.find({'cohortId': cohort._id})
    if n_group == 0:
        sessions = pd.DataFrame(columns=['_id', 'cohort', 'name'])

    sessions, n_session = Session.find({'cohortId': cohort._id, **time_range})
    if (n_session > 0):
        sessions['createdAt'] = pd.to_datetime(sessions['createdAt'])
        sessions['Date'] = sessions['createdAt'].dt.date
    else:
        sessions = pd.DataFrame(columns=['_id', 'cohort', 'sessionType', 'location', 'createdAt', 'Date'])
        
    assignments, n_assignment = Assignment.find({'cohortId': cohort._id, 'memberOnly': 'true'})
    if n_assignment > 0:
        survey = assignments[assignments['assignmentType']=='FEEDBACK'].iloc[0].to_dict()
        survey = Assignment(survey)
        assignments = assignments[assignments['assignmentType']!='FEEDBACK']
        assignments = assignments.sort_values('name').reset_index()
    else:
        assignments = pd.DataFrame(columns=['_id', 'assignmentType', 'name', 'cohort', 'questions', 'totalScore'])
        survey = Assignment({'_id': '', 'questions': []})
        
    survey_questions = {}
    for q_index, q in enumerate(survey.questions):
        if len(q['choices'])>=10:
            survey_questions[q_index] = q['question'].split('\n')[0]
    survey_questions 

    filters = {'include_staffs': False}

    # cohort = Cohort.find_one_by_name(cohort_name)
    # cohort_groups, n_group = CohortGroup.find({'cohortId': cohort._id})
    initial_state = {
        'engagement_score': 0,
        'performance_score': 0,
        'happiness_score': 0,
        'n_student': 0,
        'n_staff': 0,
        'n_session': sessions.shape[0],
        'n_submission': 0,
        'n_assignment': assignments.shape[0],
        'attendance_report': pd.DataFrame(columns=['session', 'participant', 'attendance_rate']),
        'assignment_report': pd.DataFrame(columns=['n_submitted', 'avg_score', 'name', 'submission_rate']),
        'survey_subs': pd.DataFrame(columns=['_id', 'cohortMember', 'assignment', 'name', 'email', 'currentScore', 'answers', 'createdAt']),
    }
    store = initial_state

    def load_data(store):
        std_columns = ['_id', 'name', 'email', 'status', 'progressScore',  'memberType', 'cohortMemberId', 'cohortGroupName']
        # Get and filter data
        df_student, n_student = cohort.get_student_list()
        if (n_student > 0):
            if 'cohortGroupName' not in df_student.columns:
                df_student['cohortGroupName'] = 'None'
            df_student = df_student[std_columns]
        else:
            df_student = pd.DataFrame(columns=std_columns)

        df_staff, num_staff = cohort.get_staff_list()
        if (num_staff > 0):
            if ('cohortGroupName' not in df_staff.columns):
                df_staff['cohortGroupName'] = 'None'
            df_staff = df_staff[std_columns]
        else:
            df_staff = pd.DataFrame(columns=std_columns)

        grade_columns = ['_id', 'assignment', 'cohortMember', 'grader', 'status', 'totalScore']
        grades_raw = pd.DataFrame(columns=grade_columns)
        for assignment_id in assignments['_id'].values:
            assignment_grades, n_grade = SubmissionGrade.find_all({'assignmentId': assignment_id, 'status': 'COMPLETED', **time_range})
            if n_grade > 0:
                assignment_grades = assignment_grades[grade_columns]
            else:
                assignment_grades = pd.DataFrame(columns=grade_columns)
            grades_raw = pd.concat([grades_raw, assignment_grades])
            
        attendance_columns = ['_id', 'cohortMember', 'session', 'status', 'notes']
        attendances_raw = pd.DataFrame(columns=attendance_columns)
        for session_id in sessions['_id'].values:
            session_attendances, n_attendance = Attendance.find_all({'sessionId': session_id, 'status': 'PRESENT', **time_range})
            if n_attendance > 0:
                session_attendances = session_attendances[attendance_columns]
            else:
                session_attendances = pd.DataFrame(columns=attendance_columns)
            attendances_raw = pd.concat([attendances_raw, session_attendances])
            
        if survey._id:
            subs_columns = ['_id', 'cohortMember', 'assignment', 'name', 'email', 'currentScore', 'answers', 'createdAt']
            survey_subs_raw, n_submission = Submission.find_all({'assignmentId': survey._id, **time_range})
            if n_submission > 0:
                survey_subs_raw = survey_subs_raw[subs_columns]
            else:
                survey_subs_raw = pd.DataFrame(subs_columns)

        # Save data in store
        store['df_student'] = df_student
        store['df_staff'] = df_staff
        store['grades_raw'] = grades_raw
        store['attendances_raw'] = attendances_raw
        store['survey_subs_raw'] = survey_subs_raw
        
    def filter_data(store):
        df_staff = store['df_staff']
        n_staff = df_staff.shape[0]

        students = store['df_student'].copy()
        if ('include_staffs' in filters) and (filters['include_staffs']) and (df_staff.shape[0] > 0):
            # include staff in student list
            students = pd.concat([students, df_staff], axis=0)

        if ('group_name' in filters) and (filters['group_name']):
            students = students[students['cohortGroupName'] == filters['group_name']]
            n_staff = df_staff[df_staff['cohortGroupName'] == filters['group_name']].shape[0]

        member_ids = students['cohortMemberId'].unique()
        store['grades'] = store['grades_raw'][store['grades_raw']['cohortMember'].isin(member_ids)].copy()
        store['attendances'] = store['attendances_raw'][store['attendances_raw']['cohortMember'].isin(member_ids)].copy()
        store['survey_subs'] = store['survey_subs_raw'][store['survey_subs_raw']['cohortMember'].isin(member_ids)].copy()

        store['students'] = students
        store['n_student'] = store['students'].shape[0]
        store['n_staff'] = n_staff
        store['n_survey_subs'] = store['survey_subs'].shape[0]
        
    def get_assignment_report(row, store):
        grades = store['grades']
        result = {
            'n_submitted': [0],
            'avg_score': [0],
        }
        result['name'] = [row['name']]
        assignment_grades = grades[grades['assignment']==row['_id']]
        assignment_grades = assignment_grades[assignment_grades['totalScore']>0]
        n_grade = assignment_grades.shape[0]
        if (n_grade > 0):
            result['n_submitted'] = [n_grade]
            result['avg_score'] = [math.ceil(100*assignment_grades['totalScore'].median())/100]
        return result

    def get_survey_report(row):
        result = {
            'name': [row['name']],
            'email': [row['email']],
            'createdAt': [row['createdAt']],
        }
        average = 0
        for q_index, question in survey_questions.items():
            try:
                result[question] = [int(row['answers'][q_index]['answer'])]
            except:
                result[question] = [0]
            average += result[question][0]
        result['avg_score'] = [ math.ceil((100*average)/len(survey_questions)) / 100 ]
        return result
        
    def preprocess_data(store):
        attendances = store['attendances']
        n_student = store['n_student']
        grades = store['grades']
        survey_subs = store['survey_subs']
        
        attendance_report = pd.DataFrame({
            'session': sessions['Date'].values,
            'participant': [attendances[attendances['session'] == s_id].shape[0] for s_id in sessions['_id'].values]
        })
        attendance_report['attendance_rate'] = (attendance_report['participant']*100/n_student).apply(math.ceil)
        
        assignment_report = pd.concat(pd.DataFrame(get_assignment_report(row, store)) for index, row in assignments.iterrows())
        assignment_report['submission_rate'] = (assignment_report['n_submitted'] * 100 / n_student).apply(math.ceil)
        
        grades.rename(columns={'assignment': 'assignment_id'}, inplace=True)
        assignments['assignment_id'] = assignments['_id']
        store['grades'] = grades.merge(assignments[['assignment_id', 'name']], on='assignment_id')
        
        survey_report = pd.concat(pd.DataFrame(get_survey_report(row)) for index, row in survey_subs.iterrows())
        
        store['attendance_report'] = attendance_report
        store['assignment_report'] = assignment_report
        store['survey_report'] = survey_report
        store['submission_rate'] = math.ceil(100*assignment_report[assignment_report['n_submitted']>0]['submission_rate'].mean())/100
        store['attendance_rate'] = math.ceil(100*attendance_report['attendance_rate'].mean())/100
        store['engagement_score'] = math.ceil(np.array([store['submission_rate'], store['attendance_rate']]).mean()*100)/100
        store['performance_score'] = math.ceil(100*assignment_report[assignment_report['n_submitted']>0]['avg_score'].mean())/100
        store['happiness_score'] = math.ceil(100*survey_report['avg_score'].mean())/10

    def build_overview_scores(data):
        engagement_score = data['engagement_score']
        performance_score = data['performance_score']
        happiness_score = data['happiness_score']
        n_student = data['n_student']
        n_staff = data['n_staff']
        n_session = data['n_session']
        quality_score = (0.4*engagement_score + 0.4*performance_score + 0.2*happiness_score) / (0.4*bool(engagement_score) + 0.4*bool(performance_score) + 0.2*bool(happiness_score))
        happiness_score = happiness_score if happiness_score else '-'
        
        df = pd.DataFrame({
            "Student": [n_student],
            "Staff": [n_staff],
            "Session": [n_session],
        })
        
        quality_score_display = dbc.Card(
            children=[
                dbc.CardHeader(
                    "Class Quality Score",
                    style={
                        "text-align": "center",
                        "color": "white",
                        "backgroundColor": "black",
                        "border-radius": "1px",
                        "border-width": "5px",
                        "border-top": "1px solid rgb(216, 216, 216)",
                    },
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            daq.Gauge(
                                id="active-power-information-gauge",
                                min=0,
                                max=100,  # This one should be the theoretical maximum
                                value=quality_score,
                                showCurrentValue=True,
                                color="#fec036",
                                style={
                                    "align": "center",
                                    "display": "flex",
                                    "marginTop": "5%",
                                    "marginBottom": "-10%",
                                },
                            ),
                            className="m-auto",
                            style={
                                "display": "flex",
                                "backgroundColor": "black",
                                "border-radius": "1px",
                                "border-width": "5px",
                            },
                        )
                    ],
                    className="d-flex",
                    style={
                        "backgroundColor": "black",
                        "border-radius": "1px",
                        "border-width": "5px",
                        "border-top": "1px solid rgb(216, 216, 216)",
                    },
                ),
            ],
        )
        
        # Scorecards        
        engagement_card = dbc.Card([
            dbc.CardBody([
                html.H2(f'{engagement_score}', className='card_title'),
                html.P("Engagement Score", className='card-text'),
                html.I(
                    className="fas fa-bolt position-absolute",
                    style={
                        'top': '1.5rem',
                        'right': '2rem',
                        'font-size': '3rem',
                        'opacity': '0.5',
                    }
                )
            ], className="position-relative p-3 pl-4")
        ], color="success", inverse=True)

        performance_card = dbc.Card([
            dbc.CardBody([
                html.H2(f'{performance_score}', className='card_title'),
                html.P("Performance Score", className='card-text'),
                html.I(
                    className="fas fa-chart-line position-absolute",
                    style={
                        'top': '1.5rem',
                        'right': '2rem',
                        'font-size': '3rem',
                        'opacity': '0.5',
                    }
                )
            ], className="position-relative p-3 pl-4")
        ], color="warning", inverse=True)

        happiness_card = dbc.Card([
            dbc.CardBody([
                html.H2(f'{happiness_score}', className='card_title'),
                html.P("Happiness Score", className='card-text'),
                html.I(
                    className="fas fa-heart position-absolute",
                    style={
                        'top': '1.5rem',
                        'right': '2rem',
                        'font-size': '3rem',
                        'opacity': '0.5',
                    }
                )
            ], className="position-relative p-3 pl-4")
        ], color="primary", inverse=True)
        score_cards = dbc.Row([
            dbc.Col([
                engagement_card,
                performance_card,
                happiness_card
            ], className='d-flex flex-column justify-content-between')
        ], className='h-100')
        
        layout = [
            dbc.Row(dbc.Col(dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True))),
            dbc.Row([
                # dbc.Col(dcc.Graph(figure=fig), className='col-8'),
                dbc.Col(quality_score_display, className='col-8'),
                dbc.Col(score_cards, className='col-4'),
            ])
        ]

        return layout

    def build_engagement_charts(data):
        engagement_score = data['engagement_score']
        submission_rate = data['submission_rate']
        attendance_rate = data['attendance_rate']
        n_session = data['n_session']
        n_assignment = data['n_assignment']
        attendance_report = data['attendance_report']
        assignment_report = data['assignment_report']
        
        df = pd.DataFrame({
            "Engagement Score": [engagement_score],
            "Submission Rate (%)": [submission_rate],
            "Attendance Rate (%)": [attendance_rate],
            "# Assignment": [n_assignment],
            "# Session": [n_session],
        })
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Attendance', 'Submission'))
        fig.add_trace(
            go.Bar(x=attendance_report['session'], y=attendance_report['attendance_rate'], marker_color='#2980b9', name='% Attendance'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=attendance_report['session'], y=(100-attendance_report['attendance_rate']), marker_color='indianred', name='% Missing'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=assignment_report['name'], y=assignment_report['submission_rate'], marker_color='#2980b9', name='% Submitted'),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=assignment_report['name'], y=(100-assignment_report['submission_rate']), marker_color='indianred', name='% Missing'),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='Submission & Attendance Rate (%)',
            barmode='group', xaxis_tickangle=-45,
            showlegend=False
        )
        
        layout = [
            dbc.Row(dbc.Col(dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True))),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig)),
            ])
        ]

        return layout

    def build_performance_charts(data):
        performance_score = data['performance_score']
        n_assignment = data['n_assignment']
        grades = data['grades']
        
        df = pd.DataFrame({
            "Performance Score": [performance_score],
            "# Assignment": [n_assignment],
        })
        
        fig = px.box(
            grades, x="name", y="totalScore", points="all",
            # notched=True, 
        )
        
        layout = [
            dbc.Row(dbc.Col(dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True))),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig)),
            ])
        ]

        return layout

    def build_happiness_charts(data):
        happiness_score = data['happiness_score']
        survey_report = data['survey_report']
        n_student = data['n_student']
        
        df = pd.DataFrame({
            "Happiness Score": [happiness_score],
            "# Feedback": [survey_report.shape[0]],
            "% Feedback": [math.ceil(100*survey_report.shape[0]/n_student)]
        })
        
        num_graph = len(survey_questions)
        num_col = 2
        num_row = math.ceil(num_graph / num_col)
        questions = list(survey_questions.values())

        fig = make_subplots(rows=num_row, cols=num_col, subplot_titles=questions)
        for i, question in enumerate(questions):
            fig.add_trace(
                go.Histogram(
                    x=survey_report[question],
                    # xbins=dict(
                    #     start= 1,
                    #     end= 10,
                    #     size=1
                    # ),
                    bingroup=1,
                ),
                row=(i//num_col) + 1, col=(i % num_col)+1
            )
            fig.update_xaxes(title_text=f'Average: {math.ceil(survey_report[question].mean()*100)/100}', row=(i//num_col) + 1, col=(i % num_col)+1)

        fig.update_xaxes(
            range=[1,11],  # sets the range of xaxis
            constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        )
        fig.update_layout(
            title_text=f'Survey Responses', # title of plot
            yaxis_title_text='Count', # yaxis label
            bargap=0.2, # gap between bars of adjacent location coordinates
            showlegend=False
        )
        
        layout = [
            dbc.Row(dbc.Col(dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True))),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig)),
            ])
        ]

        return layout

    # LAYOUT
    load_data(store)
    filter_data(store)
    preprocess_data(store)
    # Navbar
    navbar = dbc.Navbar([
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src="https://i.imgur.com/dpd20EG.png", height="30px")),
                    dbc.Col(dbc.NavbarBrand(f"{cohort.name}", className="ml-2")),

                ],
                align='center',
                no_gutters=True
            ),
            href="#"
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            [
                dbc.Nav([
                    # dcc.Dropdown(
                    #     id='groups-dropdown',
                    #     options=[
                    #         {'label': group['name'], 'value': group['name']}
                    #         for i, group in cohort_groups.sort_values('name').iterrows()
                    #     ] if n_group else [],
                    #     value='',
                    #     placeholder='Select a group',
                    #     style={'width': '180px', 'color': 'black'}
                    # )
                ]),
                dbc.Button('Refresh Data', id='btn-refresh', color="primary", className="mr-1 ml-auto"),
            ], 
            id="navbar-collapse", navbar=True, is_open=False
        ),
    ], color="dark", dark=True)

    # overview
    overview_scores = html.Div(id='overview-scores', className='my-4', children=build_overview_scores(store))

    # engagement
    engagement_charts = html.Div(id='engagement-charts', className='my-4', children=build_engagement_charts(store))

    # performance
    performance_charts = html.Div(id='performance-charts', className='my-4', children=build_performance_charts(store))

    # happiness
    happiness_charts = html.Div(id='happiness-charts', className='my-4', children=build_happiness_charts(store))

    app.layout = dbc.Container([
        navbar,
        html.H4('Overview'),
        overview_scores,
        html.Hr(className='bg-primary'),
        html.H4('Engagement Score'),
        engagement_charts,
        html.Hr(className='bg-primary'),
        html.H4('Performance Score'),
        performance_charts,
        html.Hr(className='bg-primary'),
        html.H4('Happiness Score'),
        happiness_charts
    ])
    app.run_server(mode='inline', port=port, debug=True)