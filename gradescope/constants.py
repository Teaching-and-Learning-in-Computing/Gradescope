from enum import StrEnum


BASE_URL = 'https://www.gradescope.com'
LOGIN_URL = f'{BASE_URL}/login'


ROLE_MAP = {
    'student': 'Student Courses',
    'instructor': 'Instructor Courses'
}


class Role(StrEnum):
    STUDENT     = 'student'
    INSTRUCTOR  = 'instructor'
