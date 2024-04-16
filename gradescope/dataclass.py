from dataclasses import dataclass
from .constants import Role


@dataclass
class Course:
    course_id: str
    url: str
    role: Role
    term: str
    short_name: str
    full_name: str
