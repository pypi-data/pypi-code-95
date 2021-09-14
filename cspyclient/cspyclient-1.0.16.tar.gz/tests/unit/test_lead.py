# from cspyclient import Lead


# def tésting_lead():
#     # get attendance information
#     val1 = Lead.find_one()
#     assert type(val1) == Lead
#     # get 1000 assginments
#     val2 = Lead.find()
#     # test with local assignment
#     fake_name = 'yolo!'
#     testing_val = Lead({'name': 'yolo!', 'cohort_id': '420'})
#     assert fake_name == testing_val.name
#     # add an assignment
#     lead_name = 'Test Lead'
#     data = {
#         "assignmentId": lead_name,
#         "email": "string",
#         "name": 0,
#         "cohortName": "string",
#         "assignmentName": "string"
#     }

#     Lead.create(data)
#     # find that lead
#     recent_lead = Lead.find_one_by_name(data['name'])
#     assert recent_lead.name == data['name']
#     recent_id = recent_lead('yolo!')._id
#     # remove an assginment by id
#     Lead.remove_by_id(recent_id)
#     # add an assignment without name
#     Lead.create({})
#     # add duplicated assginment
#     Lead.create({'name': 'yolo!', '_id': '123456'})
#     Lead.create({'name': 'yolo!', '_id': '123456'})
#     # add with wrong fromat
#     Lead.create([1, 2, 3])
#     # remove wrong id
#     Lead.remove_by_id('6435435234532462346')
