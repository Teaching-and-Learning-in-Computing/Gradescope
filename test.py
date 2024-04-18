import json
from gradescope import Gradescope, save_json, Role, EnhancedJSONEncoder

with open('./login.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
courses = gs.get_courses(role=Role.INSTRUCTOR)
save_json('./courses.data', courses, encoder=EnhancedJSONEncoder)

assignments = gs.get_course_assignments(courses[0])
save_json('./assignments.data', assignments, encoder=EnhancedJSONEncoder)
