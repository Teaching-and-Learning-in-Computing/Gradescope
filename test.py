import json
from gradescope import Gradescope, save_json, Role, EnhancedJSONEncoder, Course, Assignment, Member

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
