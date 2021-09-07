# '''Test progress unit'''
# import cspyclient as cs
# from cspyclient import ProgressScore


# def test_base():
#     #get progress score information
#     val1 = cs.ProgressScore.find_one()
#     assert type(val1) == cs.ProgressScore
#     #get 1000 progress score
#     val2 = cs.ProgressScore.find()
#     #add a progress score
#     cs.ProgressScore.create({'name':'yolo!','_id':'123456'})
#     #find that progress score
#     assert cs.ProgressScore.find_by_id('123456') == '123456'
#     #remove a progress score by id'
#     cs.ProgressScore.remove_by_id('123456')
#     #add a progress score without name
#     cs.ProgressScore.create({})
#     #add duplicated progress score
#     cs.ProgressScore.create({'name':'yolo!','_id':'123456'})
#     #add with wrong format
#     cs.ProgressScore.create([1,2,3])
#     #remove wrong id
#     cs.ProgressScore.remove_by_id('6435435234532462346')

# def test_progress():
#     # Creating a progress score without cohortMemberId
#     data = {'activity':'Attendance', 'notes':'On time', 'score': 1}
#     progress_score = ProgressScore.create(data)
#     assert getattr(progress_score, '_id', '') == '' 
#     # Create a new progress_score
#     data['cohortMemberId'] = student_members[0]._id
#     progress_score = ProgressScore.create(data)
#     print(progress_score.to_json())
#     student_members[0] = CohortMember.find_by_id(student_members[0]._id)
#     assert progress_score.cohort_member == student_members[0]._id and progress_score._id and student_members[0].progress_score == 101
#     # Update progress score
#     progress_score.score = 2
#     progress_score.save()
#     student_members[0] = CohortMember.find_by_id(student_members[0]._id)
#     assert progress_score._id and progress_score.score == 2 and student_members[0].progress_score == 102
#     # Get progress_score by id
#     assert ProgressScore.find_by_id(progress_score._id).cohort_member == student_members[0]._id
#     # Get list of progress_score
#     progress_scores = ProgressScore.find(output='object')
#     assert progress_score._id in [c._id for c in progress_scores]
#     # Remove the progress_score
#     ProgressScore.remove_by_id(progress_score._id) 
#     assert getattr(ProgressScore.find_by_id(progress_score._id), '_id', '') == ''
#     student_members[0] = CohortMember.find_by_id(db, student_members[0]._id)
#     assert student_members[0].progress_score == 100