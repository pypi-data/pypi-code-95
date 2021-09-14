# '''Test assignment unit'''
# import cspyclient as cs
# from cspyclient import Assignment


# def test_base():
#     #get assignment information
#     val1 = cs.Assignment.find_one()
#     assert type(val1) == cs.Assignment
#     #get 1000 assginments
#     val2 = cs.Assignment.find()
#     #add an assignment
#     cs.Assignment.create({'name':'yolo!','_id':'123456'})
#     #find that assignmnet
#     assert cs.Assignment.find_by_id('123456') == '123456'
#     #remove an assginment by id'
#     cs.Assignment.remove_by_id('123456')
#     #add an assignment without name
#     cs.Assignment.create({})
#     #add duplicated assginment
#     cs.Assignment.create({'name':'yolo!','_id':'123456'})
#     #add with wrong format
#     cs.Assignment.create([1,2,3])
#     #remove wrong id
#     cs.Assignment.remove_by_id('6435435234532462346')

# def test_assignment():
#     # Creating an assignment without cohortId
#     assignment_name = 'Test Assignment'
#     data = {
#         'name': assignment_name, 
#         'questions': [
#             {'question': 'Who am I', 'score': 10, 'solution': 'Minh'},
#             {'question': 'What is the result of 1 + 1?', 'score': 90, 'solution': '2'}
#         ]
#     }
#     assignment = Assignment.create(data)
#     assert getattr(assignment, '_id', '') == '' 
#     # Create a new assignment
#     data['cohortId'] = cohort._id
#     assignment = Assignment.create(data)
#     print(assignment.to_json())
#     assert assignment.name == assignment_name and assignment._id
#     # Update assignment & get assignment by ID
#     assignment_name = 'Test Assignment 0'
#     assignment.name = assignment_name
#     assignment.questions = [
#         {'question': 'Who am I', 'score': 10, 'solution': 'I dont know'},
#         {'question': 'What is the result of 2 * 2?', 'score': 10, 'solution': '4'},
#         {'question': 'What is the result of 1 + 2?', 'score': 90, 'solution': '3'}
#     ]
#     assignment.save()
#     updated_assignment = Assignment.find_by_id(assignment._id)
#     assert updated_assignment.name == assignment_name and updated_assignment.questions[2]['solution'] == '3'
#     # Get list of assignment
#     assignments = Assignment.find(output='object')
#     assert assignment._id in [c._id for c in assignments]
#     assignments_by_name = Assignment.find_one_by_name('Test', output='object')
#     assert [c._id for c in assignments].sort() == [c._id for c in assignments_by_name].sort()
#     # Create the same assignment
#     data['name'] = assignment_name
#     same_assignment = Assignment.create(data)
#     assert getattr(same_assignment, '_id', '') == ''
#     # Remove the assignment
#     Assignment.remove_by_id(assignment._id)
#     assert getattr(Assignment.find_by_id(assignment._id), '_id', '') == ''
#     # Create another one
#     data['name'] = 'Test Assignment 2'
#     assignment = Assignment.create(data)
#     assert assignment.name == data['name'] and assignment._id