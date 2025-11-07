import json
from gradescope import *

with open('./login.key', 'r') as f:
    login_info = json.load(f)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)

courses = gs.get_courses(role=Role.INSTRUCTOR)
save_json('./courses.data', courses, encoder=EnhancedJSONEncoder)

course = courses[1]
print(course)

assignments = gs.get_assignments(course)
save_json('./assignments.data', assignments, encoder=EnhancedJSONEncoder)

# members = gs.get_members(course)
# save_json('./members.data', members, encoder=EnhancedJSONEncoder)

assignment = assignments[0]
print(assignment)
assignment.release_date="2025-11-03T14:50"

testing = gs.set_assignment_date(assignment)

# member = members[2]
# print(member)

# gradebook = gs.get_gradebook(course, member)
# save_json('./gradebook.data', gradebook, encoder=EnhancedJSONEncoder)

# past_submission = gs.get_past_submissions(course, assignment, member)
# save_json('./past_submission.data', past_submission, encoder=EnhancedJSONEncoder)

# grades_csv = gs.get_assignment_grades(assignment)
# save_csv('./assignment_grades_csv.data', grades_csv)

# print('Downloading...', past_submission[-1])
# gs.download_file('./submission.zip', past_submission[-1].get_file_url())
