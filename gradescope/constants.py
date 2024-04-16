from enum import StrEnum


ROLE_MAP = {
    'student': 'Student Courses',
    'instructor': 'Instructor Courses'
}


class Role(StrEnum):
    STUDENT     = 'student'
    INSTRUCTOR  = 'instructor'
