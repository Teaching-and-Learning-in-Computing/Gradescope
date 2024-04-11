import json
from gradescope import Gradescope, save_json
import requests

with open('./login.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
courses = gs.get_courses()
save_json('./courses.json', courses)
courseid = courses['Instructor Courses'][0]['course_id']
BASE_URL = 'https://www.gradescope.com'
LOGIN_URL = f'{BASE_URL}/login'
assignemnts = gs.get_course_assignments(courseid)
print(assignemnts)
save_json('./assignments.json', assignemnts)

# print(len(ids))
# students = gs.get_students_from_assignment(courseid, ids[0])
# print(students)