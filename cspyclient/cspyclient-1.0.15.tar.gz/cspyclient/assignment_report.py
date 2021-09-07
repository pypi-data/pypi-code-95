import json
from .cohort_group import CohortGroup
from .cohort import Cohort
from .assignment import Assignment
from .submission import Submission
import pandas as pd
import numpy as np

def assignment_report(assignment_name, subs_filter={}, port=8050):
    '''Generate a real-time Dash app that shows the assignment report

    Parameters:
        - assignment_name: name of the assignment
    '''
    try:
        import dash
        from jupyter_dash import JupyterDash
        import dash_core_components as dcc
        import dash_html_components as html
        import dash_bootstrap_components as dbc
        from dash.dependencies import Input, Output, State
        import dash_table
        import plotly.express as px
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
    except:
        print('Installation required: jupyter-dash and dash-bootstrap-components (use pip install)')
        return

    app = JupyterDash(__name__, external_stylesheets=[dbc.themes.SUPERHERO],
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1.0'}]
                    )

    # Data
    assignment = Assignment.find_one_by_name(assignment_name)
    if not getattr(assignment, '_id', None) or not assignment._id:
        print("ERROR: Assignment not found")
        return

    cohort = Cohort.find_by_id(assignment.cohort_id)
    if not getattr(cohort, '_id', None) or not cohort._id:
        print("ERROR: Cohort not found")
        return

    cohort_groups, n_group = CohortGroup.find({'cohortId': cohort._id})

    n_question = len(assignment.questions)
    q_columns = [f'Q{i+1}' for i in range(n_question)]
    initial_state = {
        'students': pd.DataFrame(columns=['name', 'email','currentScore', 'entries', 'time', 'cohortGroupName']),
        'n_student': 0,
        'question_summary': pd.DataFrame(columns=['Questions', 'Struggling', 'Not started yet', 'Finished']),
        'submissions': pd.DataFrame(),
        'n_submission': 0,
        'student_scores': pd.DataFrame(),
        'n_submitted': 0,
        'avg_score': 0,
        'plot_progress_data': pd.DataFrame(columns=['time', 'currentScore', 'email'])
    }
    filters = {'include_staffs': False}
    

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

        subs_columns = ['_id', 'cohortMember', 'assignment', 'name', 'email', 'currentScore', 'answers', 'createdAt']
        submissions, n_submission = Submission.find_all({**subs_filter, 'assignmentId': assignment._id})
        if n_submission > 0:
            submissions = submissions[subs_columns]
        else:
            submissions = pd.DataFrame(subs_columns)

        # Save data in store
        store['df_student'] = df_student
        store['df_staff'] = df_staff
        store['submissions_raw'] = submissions

    def filter_data(store):
        df_staff = store['df_staff']

        students = store['df_student'].copy()
        if ('include_staffs' in filters) and (filters['include_staffs']) and (df_staff.shape[0] > 0):
            # include staff in student list
            students = pd.concat([students, df_staff], axis=0)
        
        if ('group_name' in filters) and (filters['group_name']):
            students = students[students['cohortGroupName'] == filters['group_name']]
        
        std_emails = students['email'].unique()
        store['submissions'] = store['submissions_raw'][store['submissions_raw']['email'].isin(std_emails)].copy()
        
        store['students'] = students
        store['n_student'] = store['students'].shape[0]
        store['n_submission'] = store['submissions'].shape[0]

    def preprocess_data(store):
        submissions = store['submissions']
        n_submission = store['n_submission']
        students = store['students']

        if not n_submission:
            students['entries'] = 0
            students['currentScore'] = -1
            students['time'] = 0
            for q in q_columns:
                students[q] = -1
            store['students'] = students[['name', 'email', 'currentScore', 'entries', 'time', *q_columns]]
            q_result = students[q_columns]
            question_summary = pd.DataFrame({'Questions': q_columns})
            question_summary['Finished'] = q_result[q_result == 1].count().values
            question_summary['Struggling'] = q_result[(q_result >= 0) & (q_result < 1)].count().values
            question_summary['Not started yet'] = q_result[q_result < 0].count().values
            store['question_summary'] = question_summary
            store['n_submitted'] = 0
            store['avg_score'] = 0
            store['plot_progress_data'] = pd.DataFrame(columns=['time', 'currentScore', 'email'])
            return

        submissions['createdAt'] = pd.to_datetime(submissions['createdAt'])
        submissions['assignmentName'] = assignment.name

        # Current score table
        for q_index, question in enumerate(assignment.questions):
            submissions[f'Q{q_index+1}'] = submissions['answers'].apply(
                lambda answers: int(100*answers[q_index]['clientCheck']/question['score'])/100.0 if answers[q_index]['clientCheck'] >= 0 else -1
            )
        student_scores = pd.pivot_table(submissions[['email', 'currentScore', *q_columns]], 
                                    values=['currentScore', *q_columns ], index='email', 
                                    aggfunc=np.max)

        students['entries'] = students.apply(lambda row: len(submissions[submissions['email']==row['email']]), axis=1)
        students = students.merge(student_scores, on='email', how='left').fillna(-1)
        store['student_scores'] = student_scores
        store['n_submitted'] = student_scores.shape[0]
        store['avg_score'] = int(student_scores['currentScore'].mean())

        # question result distribution
        q_result = students[q_columns]
        question_summary = pd.DataFrame({'Questions': q_columns})
        question_summary['Finished'] = q_result[q_result == 1].count().values
        question_summary['Struggling'] = q_result[(q_result >= 0) & (q_result < 1)].count().values
        question_summary['Not started yet'] = q_result[q_result < 0].count().values
        store['question_summary'] = question_summary

        # Compute duration
        first_created = submissions.groupby('email')['createdAt'].min().reset_index().rename(columns={'createdAt': 'firstCreated'})
        plot_progress_data = pd.merge(submissions, first_created, on='email')
        plot_progress_data['time'] = (plot_progress_data['createdAt'] - plot_progress_data['firstCreated']) / pd.to_timedelta(1, 'm')
        plot_progress_data['time'] = plot_progress_data['time'].apply(int)
        store['plot_progress_data'] = plot_progress_data

        students = students.merge(plot_progress_data.groupby('email')[['time']].max(), on='email', how='left').fillna(-1)
        students = students[['name', 'email','currentScore', 'entries', 'time', *q_columns]]
        store['students'] = students

    def build_score_cards(data):
        n_student = data['n_student']
        n_submission = data['n_submission']
        n_submitted = data['n_submitted']
        avg_score = data['avg_score']
        
        # Scorecards        
        num_student_card = dbc.Card([
            dbc.CardBody([
                html.H3(f'{n_submitted} / {n_student}', className='card_title'),
                html.P("Students submitted", className='card-text')
            ])
        ], color="primary", inverse=True)

        num_submission_card = dbc.Card([
            dbc.CardBody([
                html.H3(f'{n_submission}', className='card_title'),
                html.P("Submissions", className='card-text')
            ])
        ], color="secondary", inverse=True)

        avg_score_card = dbc.Card([
            dbc.CardBody([
                html.H3(f'{avg_score} / {assignment.total_score}', className='card_title'),
                html.P("Average score / Total score", className='card-text')
            ])
        ], color="info", inverse=True)
        new_score_cards = [
            dbc.Row([
                dbc.Col(num_student_card),
                dbc.Col(num_submission_card),
                dbc.Col(avg_score_card),
            ], className='my-4')
        ]
        return new_score_cards

    def build_student_table(data):
        students = data['students']
        # Student table
        std_table = dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i} for i in students.columns
            ],
            data=students.to_dict('records'),

            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},

            filter_action="native",
            # row_selectable="multi",
            sort_action="native",
            sort_mode="multi",
            # selected_rows=[],

            style_header={ 
                'border': '1px solid #2c3e50',
                'color': 'white',
                'backgroundColor': '#34495e'
            },
            style_cell={
                # 'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'black',
                'textAlign': 'left',
                'border': '1px solid #2c3e50',
                'font-family': 'Helvetica Neue'
            },
            style_data_conditional=[                
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "inherit !important",
                    "border": "inherit !important",
                }   
            ]
        )
        return std_table

    def build_histogram(data):
        students = data['students']
        # Histogram
        fig_hist = make_subplots(rows=1, cols=2, subplot_titles=('currentScore', 'Time'))
        fig_hist.add_trace(
            go.Histogram(
                x=students['currentScore'],
                nbinsx=10, 
                marker_color='slateblue', 
                name='Time',
                hovertemplate=
                '<i>Range</i>: %{x}'+
                '<br><i>Count</i>: %{y}'
            ),
            row=1, 
            col=1
        )
        fig_hist.add_trace(
            go.Histogram(
                x=students['time'], 
                nbinsx=10, 
                marker_color='salmon', 
                name='Time',
                hovertemplate=
                '<i>Range</i>: %{x}'+
                '<br><i>Count</i>: %{y}'
            ),
            row=1, 
            col=2
        )
        fig_hist.update_layout(
            title_text='Score and Time Distribution',
            template="plotly_white", 
            showlegend=False)
        return fig_hist

    def build_progress_gragh(data):
        plot_progress_data = data['plot_progress_data']
        # Progress graph
        if plot_progress_data.shape[0] > 0:
            fig_progress = px.line(plot_progress_data, 
                                  x="time", 
                                  y="currentScore", 
                                  color="email",
                                  hover_name="email",
                                  template="plotly_white")
            fig_progress.update_traces(mode="markers+lines")
            fig_progress.update_layout(title_text='Student Progresses')
        else:
            fig_progress = {}
        return fig_progress

    def build_question_dist(data):
        question_summary = data['question_summary']
        n_student = store['n_student']

        labels = question_summary['Questions']
        widths = np.array([100/len(labels) for _ in range(len(labels))])
        data = { key: question_summary[key].values for key in ['Struggling', 'Not started yet', 'Finished']}
        data_percentage = { key: (100*question_summary[key]/n_student).values for key in ['Not started yet', 'Struggling', 'Finished']}

        fig = go.Figure()
        for key in data_percentage:
            fig.add_trace(go.Bar(
                name=key,
                y=data_percentage[key],
                x=np.cumsum(widths)-widths,
                width=widths,
                offset=0,
                customdata=data[key],
                texttemplate="%{customdata}",
                textposition="inside",
                textangle=0,
                textfont_color="white",
                hovertemplate="<br>".join([
                    "label: %{key}",
                    "height: %{customdata}",
                ])
            ))

        fig.update_xaxes(
            tickvals=np.cumsum(widths)-widths/2,
            ticktext= [f"{l}" for l in labels]
        )

        fig.update_xaxes(range=[0,100])
        fig.update_yaxes(range=[0,100])

        fig.update_layout(
            title_text="Question Result Distribution",
            barmode="stack",
        )
        return fig

    # LAYOUT
    store = initial_state
    # load_data(store)
    # filter_data(store)
    # preprocess_data(store)
    # Navbar
    navbar = dbc.Navbar([
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src="https://i.imgur.com/dpd20EG.png", height="30px")),
                    dbc.Col(dbc.NavbarBrand(f"{assignment.name}", className="ml-2")),
                    
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
                    dcc.Dropdown(
                        id='groups-dropdown',
                        options=[
                            {'label': group['name'], 'value': group['name']}
                            for i, group in cohort_groups.sort_values('name').iterrows()
                        ] if n_group else [],
                        value='',
                        placeholder='Select a group',
                        style={'width': '180px', 'color': 'black'}
                    ),
                    dbc.Checklist(
                        id='check-include-staffs',
                        options=[
                            {'label': 'Including staffs', 'value': 'staff'},
                        ],
                        value=[],
                        labelStyle={'display': 'inline-block'},
                        className='align-self-center ml-1 mt-1'
                    ),
                ]),
                dbc.Button('Refresh Data', id='btn-refresh', color="primary", className="mr-1 ml-auto"),
            ], 
            id="navbar-collapse", navbar=True, is_open=False
        ),
    ], color="dark", dark=True)

    # Score cards
    score_cards = html.Div(id='score-cards', children=build_score_cards(store))

    # Student table
    student_table = dbc.Row([
        dbc.Col(id='student-table', children=build_student_table(store)),
    ])

    # Histogram
    histograms = html.Div([
        dcc.Graph(id='score_histogram', figure=build_histogram(store)),
    ], className='my-4')

    # Progress graph
    progress_graph = html.Div([
        dcc.Graph(id='progress-graph', figure=build_progress_gragh(store)),
    ], className='my-4')

    # Histogram
    question_dist = html.Div([
        dcc.Graph(id='question-dist', figure=build_question_dist(store)),
    ], className='my-4')

    # Debug
    debug = html.Div(id='debugging')

    # App layout
    app.layout = dbc.Container([
        navbar,
        score_cards,
        # debug,
        student_table,
        question_dist,
        progress_graph,
        histograms,

        # Real-time update
        # dcc.Interval(
        #     id='interval-component',
        #     interval=10*1000, # in milliseconds
        #     n_intervals=0
        # ),
        
        # dcc.Store inside the app that stores the intermediate value
        # dcc.Store(id='intermediate-value')
    ])

    def update_layout(store):
        filter_data(store)
        preprocess_data(store)
        new_score_cards = build_score_cards(store)
        std_table = build_student_table(store)
        fig_hist = build_histogram(store)
        fig_progress = build_progress_gragh(store)
        question_dist = build_question_dist(store)
        return new_score_cards, std_table, fig_hist, fig_progress, question_dist

    @app.callback(
        Output('score-cards', 'children'),
        Output('student-table', 'children'),
        Output('score_histogram', 'figure'),
        Output('progress-graph', 'figure'),
        Output('question-dist', 'figure'),
        # Output('debugging', 'children'),
        [
            Input('btn-refresh','n_clicks'), 
            Input('check-include-staffs', 'value'),
            Input('groups-dropdown', 'value'),
        ])
    def refresh_data(n_clicks, include_staffs_value, select_group_value):
        ctx = dash.callback_context

        # Debug
        # ctx_msg = json.dumps({
        #     'states': ctx.states,
        #     'triggered': ctx.triggered,
        #     'inputs': ctx.inputs
        # }, indent=2)

        if not ctx.triggered:
            load_data(store)
        else:
            if ctx.triggered[0]['prop_id'] == 'btn-refresh.n_clicks':
                load_data(store)

            if ctx.triggered[0]['prop_id'] == 'check-include-staffs.value':
                if 'staff' in include_staffs_value:
                    filters['include_staffs'] = True
                else:
                    filters['include_staffs'] = False

            if ctx.triggered[0]['prop_id'] == 'groups-dropdown.value':
                filters['group_name'] = select_group_value

        return update_layout(store)
        
        # Debug
        # return (*update_layout(store), html.Pre(ctx_msg))

    app.run_server(mode='inline', port=port, debug=True)