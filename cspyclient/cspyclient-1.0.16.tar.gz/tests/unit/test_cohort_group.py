# from cspyclient import CohortGroup
# import cspyclient

# def testing_template():
#     print('TESTING COHORT GROUP ------------------------------')
#     # Creating a cohort_group without cohortId
#     cohort_group_name = 'Test CohortGroup'
#     data = {'name': cohort_group_name}
#     cohort_group = CohortGroup.create(data)
#     assert getattr(cohort_group, '_id', '') == '' 
#     # Create a new cohort_group
#     cohort_group = CohortGroup.create({'name': cohort_group_name, 'cohortId':cohort._id})
#     print(cohort_group.to_json())
#     assert cohort_group.name == cohort_group_name and cohort_group._id and cohort_group.cohort == cohort._id
#     # Update cohort_group & get cohort_group by ID
#     cohort_group_name = 'Test CohortGroup 0'
#     cohort_group.name = cohort_group_name
#     cohort_group.save()
#     assert CohortGroup.find_by_id(cohort_group._id).name == cohort_group_name
#     # Get list of cohort_group
#     cohort_groups = CohortGroup.find(output='object')
#     assert cohort_group._id in [c._id for c in cohort_groups]
#     #cohort_groups_by_name = CohortGroup.get_cohort_groups_by_name(db, 'Test', output='object')
#     #assert [c._id for c in cohort_groups].sort() == [c._id for c in cohort_groups_by_name].sort()
#     # Create the same cohort_group
#     data['name'] = cohort_group_name
#     same_cohort_group = CohortGroup.create({'name': cohort_group_name, 'cohortId':cohort._id})
#     assert getattr(same_cohort_group, '_id', '') == ''
#     # Remove the cohort_group
#     CohortGroup.remove_by_id(cohort_group._id)
#     assert getattr(CohortGroup.find_by_id(cohort_group._id), '_id', '') == ''
#     # Add bulk
#     names = ['Group 1', 'Group 2', 'Group 3']
#     # Create a new cohort
#     course_name = 'Test Course 1'
#     course = cspyclient.Course.create({'name': course_name})
#     data['courseId'] = course._id
#     cohort = cspyclient.Cohort.create(data)
#     cohort_groups = CohortGroup.create_groups_by_names(names, cohort._id)
#     assert [c._id for c in cohort_groups].sort() == [c._id for c in CohortGroup.get_cohort_groups(db, output='object')].sort()
#     print('-------------------------------------------------')