# '''Test Submission unit'''
# import cspyclient as cs
# from cspyclient import Submission


# def test_base():
#     #get submission information
#     val1 = cs.Submission.find_one()
#     assert type(val1) == cs.Submission
#     #get 1000 submissions
#     val2 = cs.Submission.find()
#     #add a submission
#     cs.Submission.create({'name':'yolo!','_id':'123456'})
#     #find that submission
#     assert cs.Submission.find_by_id('123456') == '123456'
#     #remove a submission by id'
#     cs.Submission.remove_by_id('123456')
#     #add a submission without name
#     cs.Submission.create({})
#     #add duplicated submission
#     cs.Submission.create({'name':'yolo!','_id':'123456'})
#     #add with wrong format
#     cs.Submission.create([1,2,3])
#     #remove wrong id
#     cs.Submission.remove_by_id('6435435234532462346')

# def test_submission():
#     # Creating a submission without assignmentId
#     data = {'email': students[0].email, 'answers': []}
#     submission = Submission.create(data)
#     assert getattr(submission, '_id', '') == '' 
#     # Create a new submission with wrong email
#     data['assignmentId'] = assignment._id
#     data['email'] = 'unknown@email.com'
#     submission = Submission.create(data)
#     assert getattr(submission, '_id', '') == ''
#     # Create a new submission with unenrolled student
#     unenrolled_student = Student.create({'name': 'Unenroll Student', 'email': 'unenroll@coderschool.vn'})
#     data['email'] = unenrolled_student.email
#     submission = Submission.create(data)
#     assert getattr(submission, '_id', '') == ''
#     # Create a new submission with cohortMemberId
#     del data['email']
#     data['cohortMemberId'] = student_members[1]._id
#     submission = Submission.create(data)
#     print(submission.to_json())
#     assert submission.cohort_member == student_members[1]._id and submission._id
#     # Create a new submission with enrolled student
#     del data['cohortMemberId']
#     data['email'] = students[1].email
#     submission = Submission.create(data)
#     print(submission.to_json())
#     assert submission.cohort_member == student_members[1]._id and submission._id
#     # Get list of submission
#     submissions = Submission.find(output='object')
#     assert submission._id in [c._id for c in submissions]
#     #Remove the submission
#     Submission.remove_by_id(submission._id)
#     assert getattr(Submission.find_by_id(submission._id), '_id', '') == ''