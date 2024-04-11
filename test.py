import json
from gradescope import Gradescope, save_json

with open('./login.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
courses = gs.get_courses()
save_json('./courses.json', courses)