from enum import Enum


BASE_URL = 'https://www.gradescope.com'
LOGIN_URL = f'{BASE_URL}/login'
GRADEBOOK = 'https://www.gradescope.com/courses/{course_id}/gradebook.json?user_id={member_id}'
PAST_SUBMISSIONS = '.json?content=react&only_keys%5B%5D=past_submissions'


ROLE_MAP = {
    'student': ['Your Courses', 'Student Courses'],
    'instructor': ['Instructor Courses']
}


class Role(Enum):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
