from datetime import datetime, timedelta
import cspyclient as cs

mock_user = {
    'name': 'User',
    'email': 'user@coderschool.vn',
    'password': '123',
    'roles': ['STAFF'],
}

n_sample = 3
mock_students = [
    {
    'name': f'Student {i}',
    'email': f'student_{i}@gmail.com',
    'password': '123',
    } for i in range(n_sample)
]
mock_cohort_members = [
    {
        'cohortId': '',
        'memberType': 'Student',
        'memberId': '',
        'status': 'PARTICIPANT'
    } for _ in range(n_sample)
]

mock_course = {
    'name': 'Testing Course'
}

mock_cohort = {
    'name': 'Testing Cohort'
}

mock_sessions = [
    {
        'cohortId': '',
        'sessionType': 'LECTURE',
        'location': 'Ohyay',
        'startTime': datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        'endTime': (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    } for _ in range(n_sample)
]

mock_attendances = [
    {
        'cohortMemberId': '',
        'sessionId': '',
        'status': status,
        'notes': 'xx',
    } for status in ['ABSENT', 'PRESENT', 'EXCUSED']
]

mock_assignment = {
    "cohortId": '',
    "name": 'Basic Javascript',
    "assignmentType": 'EXAM',
    "questions": [
        {
            "question": 'What is Python?',
            "score": 20,
            "solution": 'C',
            "resultType": 'VALUE',
        },
        {
            "question": 'What is Javascript?',
            "score": 20,
            "solution": 'B',
            "resultType": 'VALUE',
        }
    ],
}

mock_submissions = [
    {
        "assignmentId": '',
        "email": mock_students[i]['email'],
        "name": mock_students[i]['name'],
        "answers": [
            {
            "question": 'What is Python?',
            "answer": 'A',
            },
            {
            "question": 'What is Javascript?',
            "answer": 'A',
            },
        ],
    } for i in range(n_sample)
]

mock_submission_grades = [
    {
        "assignmentId": '',
        "cohortMemberId": '',
        "graderId": '',
        "totalScore": 10,
        "notes": f'Student {i}'
    } for i in range(n_sample)
]

mock_progress_scores = [
    {
        "cohortMemberId": '',
        "activity": f'Quiz {i}',
        "score": 1,
        "notes": f'week {i}',
    } for i in range(n_sample)
]

admin = cs.User({'email':'csplatformservice@coderschool.vn', 'password':'123'})
cs.Base.db_service.auth(user=admin)

def create_if_not_exists(data, class_model, filter_=None):
    '''Should create a new instance if not exists. Return the instance otherwise'''
    temp = class_model.find_one(filter_) if filter_ else None
    if (not temp):
        temp = class_model.create(data)
    assert getattr(temp, '_id', '') and temp._id
    return temp

course = create_if_not_exists(mock_course, cs.Course, {'name': mock_course['name']})
mock_course['_id'] = course._id

mock_cohort['courseId'] = course._id
cohort = create_if_not_exists(mock_cohort, cs.Cohort, {'name': mock_cohort['name']})
mock_cohort['_id'] = cohort._id

for i, mock_student in enumerate(mock_students):
    student = create_if_not_exists(mock_student, cs.Student, {'email': mock_student['email']})
    mock_students[i]['_id'] = student._id

    mock_cohort_members[i]['cohortId'] = mock_cohort['_id']
    mock_cohort_members[i]['memberId'] = mock_students[i]['_id']
    cohort_member = create_if_not_exists(mock_cohort_members[i], cs.Student, 
                        {'memberId': mock_cohort_members[i]['memberId'], 'cohortId': mock_cohort_members[i]['cohortId']})
    mock_cohort_members[i]['_id'] = cohort_member._id


sessions, _ = cs.Session.find(limit=n_sample, filter_={'cohortId': cohort._id}, output='object')
if (not sessions):
    sessions = []
    for mock_session in mock_sessions:
        mock_session['cohortId'] = cohort._id
        session = cs.Session.create(mock_session)
        mock_session['_id'] = session._id
        sessions.append(session)

for i, mock_attendance in enumerate(mock_attendances):
    mock_attendance['sessionId'] = sessions[0]._id
    mock_attendance['cohortMemberId'] = mock_cohort_members[i]['_id']
    attendance = create_if_not_exists(mock_attendance, cs.Student, 
                    {'sessionId': mock_attendance['sessionId'], 'cohortMemberId': mock_attendance['cohortMemberId']})
    mock_attendance['_id'] = attendance._id

mock_assignment['cohortId'] = mock_cohort['_id']
assignment = create_if_not_exists(mock_assignment, cs.Assignment, {'name': mock_assignment['name']})
mock_assignment['_id'] = assignment._id

for i, mock_submission in enumerate(mock_submissions):
    mock_submission['assignmentId'] = mock_assignment['_id']
    submission = create_if_not_exists(mock_submission, cs.Student, {'email': mock_submission['email'], 'assignmentId': mock_assignment['_id']})
    mock_submissions[i]['_id'] = submission._id

for i, mock_submission_grade in enumerate(mock_submission_grades):
    mock_submission_grade['assignmentId'] = mock_assignment['_id']
    mock_submission_grade['cohortMemberId'] = mock_cohort_members[i]['_id']
    submission_grade = create_if_not_exists(mock_submission_grade, cs.Student, 
                            {'cohortMemberId': mock_submission_grade['cohortMemberId'], 'assignmentId': mock_assignment['_id']})
    mock_submission_grades[i]['_id'] = submission_grade._id

for i, mock_progress_score in enumerate(mock_progress_scores):
    mock_progress_score['cohortMemberId'] = mock_cohort_members[i]['_id']
    progress_score = create_if_not_exists(mock_progress_score, cs.Student, {'cohortMemberId': mock_progress_score['cohortMemberId']})
    mock_progress_scores[i]['_id'] = progress_score._id