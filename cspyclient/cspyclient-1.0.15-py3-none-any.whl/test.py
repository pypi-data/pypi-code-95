from DBService import db
from User import User
from Utils import Utils

user = User({'email':'csplatformservice@coderschool.vn', 'password':'cs123'})
db.auth(user=user)
'''

class Attendance():
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'cohort_member', 'cohort_member_id', 'session', 'status', 'notes', 
                           'created_by', 'updated_by', 'created_at', 'updated_at']
        self.set_attributes(data)
                
    def set_attributes(self, data):
        if (not data):
            return
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if (snake_key in self.ATTRIBUTES):
                setattr(self, snake_key, data[key])

    def __repr__(self):
        cohort_member = getattr(self, 'cohort_member', '')
        session = getattr(self, 'session', '')
        status = getattr(self, 'status', '')
        return f'Attendance: Cohort Member {cohort_member} - Session {session} - Status {status}'

    def to_json(self):
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES if getattr(self, key, None)}
    
    def save(self, db_service):
        if (not getattr(self, '_id', '')):
            new_attendance = db_service.post('/attendances', self.to_json())
            if (new_attendance and '_id' in new_attendance):
                self.set_attributes(new_attendance)
        else:
            updated_attendance = db_service.put(f'/attendances/{self._id}', self.to_json())

    @classmethod
    def create(cls, db_service, data):
        new_attendance = cls(data)
        new_attendance.save(db_service)
        return new_attendance

    @classmethod
    def get_attendances(cls, db_service, output='DataFrame', filter={}):
        filter_params = Utils.build_filter_params(filter)
        attendances = db_service.get(f'/attendances?page=1&limit=1{filter_params}')['attendances']
        return Utils.output_form(cls, attendances, output)

    @classmethod
    def get_attendance_by_id(cls, db_service, attendance_id):
        attendance = db_service.get(f'/attendances/{attendance_id}')
        return Attendance(attendance)

    @classmethod
    def remove_attendance_by_id(cls, db_service, attendance_id):
        return db_service.delete(f'/attendances/{attendance_id}')
print(Attendance.get_attendances(db))

'''
from Assignment import Assignment
print(Assignment.findOne(db))
from Attendance import Attendance
#print(Attendance.findOne(db))
from Cohort import Cohort
print(Cohort.findOne(db))
from CohortGroup import CohortGroup
print(CohortGroup.findOne(db))
from CohortMember import CohortMember
print(CohortMember.findOne(db))
from Course import Course
print(Course.findOne(db))
from Lead import Lead
print(Lead.findOne(db))
from ProgressScore import ProgressScore
print(ProgressScore.findOne(db))
from Student import Student
print(Student.findOne(db))
from Submission import Submission
print(Submission.findOne(db))
from SubmissionGrade import SubmissionGrade
print(SubmissionGrade.findOne(db))




