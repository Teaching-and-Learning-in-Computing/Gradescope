import json
from gradescope import Gradescope

with open('./login.key', 'r') as f:
    login_info = json.load(f)
# print(login_info)

gs = Gradescope(login_info['username'], login_info['password'], verbose=True)
