import json
from gradescope import Gradescope, save_json
import requests
from gradescope import dataclass, constants, Role

with open('./login2.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
courses = gs.get_courses(role=Role.INSTRUCTOR)
assignments = gs.get_assignments(courses[0])
members = gs.get_members(courses[0])

past_submissions = gs.get_past_submissions(courses[0], assignments[2], members[0])
print(past_submissions)