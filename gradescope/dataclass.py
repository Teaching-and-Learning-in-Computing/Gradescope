# dataclass.py

from dataclasses import dataclass
from urllib.parse import urljoin
from .constants import BASE_URL, Role


@dataclass
class Course:
    course_id: int
    url: str
    role: Role
    term: str
    short_name: str
    full_name: str

    def get_url(self) -> str:
        return urljoin(BASE_URL, self.url)


@dataclass
class Assignment:
    assignment_id: int
    assignment_type: str
    url: str
    title: str
    container_id: str
    versioned: bool
    version_index: str
    version_name: str
    total_points: str
    student_submission: str
    created_at: str
    release_date: str
    due_date: str
    hard_due_date: str
    time_limit: str
    active_submissions: int
    grading_progress: int
    published: bool
    regrade_requests_open: bool
    regrade_requests_possible: bool
    regrade_request_count: int
    due_or_created_at_date: str

    # Not included:
    # edit_url
    # edit_actions_url
    # has_section_overrides
    # regrade_request_url

    def get_url(self) -> str:
        return urljoin(BASE_URL, self.url)

    def get_grades_url(self) -> str:
        return urljoin(BASE_URL, self.url + '/scores.csv')


@dataclass
class Member:
    member_id: int
    full_name: str
    first_name: str
    last_name: str
    role: int
    sid: str
    email: str


@dataclass
class Submission:
    course_id: int
    assignment_id: int
    member_id: int
    submission_id: int
    created_at: str
    score: int
    url: str

    def get_url(self) -> str:
        return urljoin(BASE_URL, self.url)
