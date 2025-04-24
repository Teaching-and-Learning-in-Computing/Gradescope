# dataclass.py

from dataclasses import dataclass
from urllib.parse import urljoin
from .constants import BASE_URL, Role


@dataclass
class Course:
    '''Represents a course in Gradescope.'''
    course_id: int
    url: str
    role: Role
    term: str
    short_name: str
    full_name: str

    def get_url(self) -> str:
        '''Returns the full URL of the course.'''
        return urljoin(BASE_URL, self.url)


@dataclass
class Assignment:
    '''Represents an assignment in Gradescope.'''
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
        '''Returns the full URL of the assignment.'''
        return urljoin(BASE_URL, self.url)

    def get_grades_url(self) -> str:
        '''Returns the URL to download the grades for the assignment.'''
        return urljoin(BASE_URL, self.url + '/scores.csv')


@dataclass
class StudentAssignment:
    assignment_id: int
    title: str
    submission_url: str
    template_url: str | None
    submitted: bool
    score: str | None
    release_date: str
    due_date: str
    late_due_date: str | None


@dataclass
class Member:
    '''Represents a member (student or instructor) in Gradescope.'''
    member_id: int
    full_name: str
    first_name: str
    last_name: str
    role: int
    sid: str
    email: str


@dataclass
class Submission:
    '''Represents a submission in Gradescope.'''
    course_id: int
    assignment_id: int
    member_id: int
    submission_id: int
    created_at: str
    score: int
    url: str

    def get_url(self) -> str:
        '''Returns the full URL of the submission.'''
        return urljoin(BASE_URL, self.url)

    def get_file_url(self) -> str:
        '''Returns the URL to download the submission file.'''
        return urljoin(BASE_URL, self.url + '.zip')
