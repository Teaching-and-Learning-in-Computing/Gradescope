import json
from gradescope import *

with open('./login.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
courses = gs.get_courses(role=Role.INSTRUCTOR)
save_json('./courses.data', courses, encoder=EnhancedJSONEncoder)

assignments = gs.get_assignments(courses[0])
print(courses[0])
save_json('./assignments.data', assignments, encoder=EnhancedJSONEncoder)

member = Member(12345, '', '', '', 0, '', '')
gradebook = gs.get_gradebook(courses[0], member)
save_json('./gradebook.data', gradebook, encoder=EnhancedJSONEncoder)

past_submission = gs.get_past_submissions(courses[0], assignments[-1], member)
save_json('./past_submission.data', past_submission, encoder=EnhancedJSONEncoder)

grades_csv = gs.get_assignment_grades(assignments[0])
save_csv('./assignment_grades_csv.data', grades_csv)

print('Downloading...', past_submission[-1])
gs.download_file('./submission.zip', past_submission[-1].get_file_url())
