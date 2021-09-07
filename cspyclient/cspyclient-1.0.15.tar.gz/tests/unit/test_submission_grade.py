# '''Test Submission unit'''
# import cspyclient as cs
# from cspyclient import SubmissionGrade


# def test_base():
#     #get submission grade information
#     val1 = cs.SubmissionGrade.find_one()
#     assert type(val1) == cs.SubmissionGrade
#     #get 1000 submission grades
#     val2 = cs.SubmissionGrade.find()
#     #add a submission grade 
#     cs.SubmissionGrade.create({'name':'yolo!','_id':'123456'})
#     #find that submission grade
#     assert cs.SubmissionGrade.find_by_id('123456') == '123456'
#     #remove a submission grade by id'
#     cs.SubmissionGrade.remove_by_id('123456')
#     #add a submission grade without name
#     cs.SubmissionGrade.create({})
#     #add duplicated submission grade
#     cs.SubmissionGrade.create({'name':'yolo!','_id':'123456'})
#     #add with wrong format
#     cs.SubmissionGrade.create([1,2,3])
#     #remove wrong id
#     cs.SubmissionGrade.remove_by_id('6435435234532462346')

# def test_submission_grade():
#     # Creating an assignment without SubmissionId
#     data = {'totalScore': 0, 'notes': 'On Time', 'status':'Online'}
#     submissiongrade = SubmissionGrade.create(data)
#     assert getattr(submissiongrade, '_id', '') == ''   
#     # Create a new submission grade with cohortMemberId
#     data['cohortMemberId'] = student_members[1]._id
#     submissiongrade = SubmissionGrade.create(data)
#     print(submissiongrade.to_json())
#     assert submissiongrade.cohort_member == student_members[1]._id and submissiongrade._id 
#     # Get list of submission grade
#     submissiongrades = SubmissionGrade.find(output='object')
#     assert submissiongrade._id in [c._id for c in submissiongrades]
#     #Remove the submission grade
#     SubmissionGrade.remove_by_id(submissiongrade._id)
#     assert getattr(SubmissionGrade.find_by_id(submissiongrade._id), '_id', '') == ''