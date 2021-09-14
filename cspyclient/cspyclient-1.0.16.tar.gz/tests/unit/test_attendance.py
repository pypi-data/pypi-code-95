# import cspyclient as cs
# from cspyclient import Attendance


# def testing_attendance():
#     # get attendance information
#     val1 = Attendance.find_one()
#     assert type(val1) == Attendance
#     # get 1000 assginments
#     val2 = Assignment.find()
#     # test with local assignment
#     fake_name = 'yolo!'
#     testing_val = Attendance({'name': 'yolo!', 'cohort_id': '420'})
#     assert fake_name == testing_val.name
#     # add an assignment
#     attendance_name = 'Test Attendance'
#     data = {
#         "cohortId": attendance_name,
#         "name": "string",
#         "assignmentType": "string",
#         "maxProgressScore": '',
#         "questions": [
#             {
#                 "question": "string",
#                 "score": 0,
#                 "solution": "string",
#                 "preCode": "string",
#                 "testCases": [
#                     "string"
#                 ],
#                 "resultType": "FUNCTION"
#             }
#         ]
#     }
#     Attendance.create(data)
#     # find that assignmnet
#     recent_assignment = Attendance.find_one_by_name(data['name'])
#     assert recent_assignment.name == data['name']
#     recent_id = recent_assignment('yolo!')._id
#     # remove an assginment by id
#     Attendance.remove_by_id(recent_id)
#     # add an assignment without name
#     Attendance.create({})
#     # add duplicated assginment
#     Attendance.create({'name': 'yolo!', '_id': '123456'})
#     Attendance.create({'name': 'yolo!', '_id': '123456'})
#     # add with wrong fromat
#     Attendance.create([1, 2, 3])
#     # remove wrong id
#     Attendance.remove_by_id('6435435234532462346')
