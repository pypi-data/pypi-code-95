# from cspyclient import CohortMember
# import cspyclient

# def test_template():
#     print('TESTING COHORT MEMBER ------------------------------')
#     # Creating a cohort_member without cohortId
#     #data = {'memberType': 'User', 'memberId': db.current_user._id}
#     #cohort_member = CohortMember.create(db, data)
#     #assert getattr(cohort_member, '_id', '') == '' 
#     # Create a new cohort_member
#     # Create a new cohort
#     course_name = 'Test Course 1'
#     cohort_name = 'Test Cohort'
#     course = cspyclient.Course.create({'name': course_name})
#     data = {'name': cohort_name}
#     data['courseId'] = course._id
#     cohort = cspyclient.Cohort.create(data)
#     cohort_member = CohortMember.create(data)
#     print(cohort_member.to_json())
#     assert cohort_member.cohort == cohort._id and cohort_member._id
#     # Update cohort_member & get cohort_member by ID
#     cohort_member_status = 'Alumni'
#     cohort_member.status = cohort_member_status
#     cohort_member.save()
#     assert CohortMember.find_by_id(cohort_member._id).status == cohort_member_status
#     # Get list of cohort_member
#     cohort_members = CohortMember.find(output='object')
#     assert cohort_member._id in [c._id for c in cohort_members]
#     # Create the same cohort_member
#     same_cohort_member = CohortMember.create(data)
#     assert getattr(same_cohort_member, '_id', '') == ''
#     # Remove the cohort_member
#     CohortMember.remove_by_id(cohort_member._id)
#     assert getattr(CohortMember.get_cohort_member_by_id(cohort_member._id), '_id', '') == ''
#     # Add student member to group
#     student_members = CohortMember.get_cohort_members(output='object', filter={'cohort': cohort._id, 'memberType':'Student', 'EXACT': True})
#     assert [s.member for s in student_members].sort() == [s._id for s in cohort_students].sort()
#     added_students = []
#     #for index, group in enumerate(cohort_groups):
#     #    group.add_members_to_group(db, [student_members[index]])
#     #    added_students += group.get_student_list(db, output='object')
#     #assert [s._id for s in added_students].sort() == [s._id for s in cohort_students].sort()
#     print('-------------------------------------------------')