# gradescope.py

import re
import json
import requests
import logging as log
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from .dataclass import Course, Assignment, Member, Submission
from .constants import BASE_URL, LOGIN_URL, GRADEBOOK, PAST_SUBMISSIONS, ROLE_MAP, Role


class Gradescope:
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        auto_login: bool = True,
        verbose: bool = False
    ) -> None:
        self.session = requests.session()
        self.username = username
        self.password = password
        self.verbose = verbose
        self.logged_in = False

        if self.verbose:
            log.basicConfig(level=log.INFO)
        else:
            log.basicConfig(level=log.WARNING)

        if auto_login and (not (username is None and password is None)):
            self.login()

    def login(self, username: str | None = None, password: str | None = None) -> bool:
        if username is not None: self.username = username
        if password is not None: self.password = password
        if self.username is None or self.password is None:
            raise TypeError('The username or password cannot be None.')

        response = self.session.get(BASE_URL)
        if self._response_check(response):
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', attrs={'name': 'authenticity_token'})

            if token_input:
                authenticity_token = token_input.get('value')
                log.info(f'[Login] Authenticity Token: {authenticity_token}')
            else:
                log.warning('[Login] Authenticity token not found.')

        data = {
            'authenticity_token': authenticity_token,
            'session[email]': self.username,
            'session[password]': self.password,
            'session[remember_me]': 0,
            'commit': 'Log In',
            'session[remember_me_sso]': 0,
        }
        response = self.session.post(LOGIN_URL, data=data)

        if self._response_check(response):
            log.info(f'[Login] Current URL: {response.url}')
            if 'account' in response.url:
                log.info('[Login] Login Successful.')
                self.logged_in = True
                return True
            elif 'login' in response.url:
                log.warning('[Login] Login Failed.')
                self.logged_in = False
                return False
            else:
                self.logged_in = False
                raise ValueError('Unknown return URL.')
        return False

    def get_courses(self, role: Role) -> list[Course]:
        response = self.session.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        courses = list()
        current_heading = soup.find('h1', string=ROLE_MAP[role.value])
        if current_heading:
            course_lists = current_heading.find_next_sibling('div', class_='courseList')
            for term in course_lists.find_all(class_='courseList--term'):
                term_name = term.get_text(strip=True)
                courses_container = term.find_next_sibling(class_='courseList--coursesForTerm')
                if courses_container:
                    for course in courses_container.find_all(class_='courseBox'):
                        if course.name == 'a':
                            courses.append(
                                Course(
                                    course_id=self._parse_int(course.get('href', '').split('/')[-1]),
                                    url=course.get('href', None),
                                    role=role.value,
                                    term=term_name,
                                    short_name=course.find(class_='courseBox--shortname').get_text(strip=True),
                                    full_name=course.find(class_='courseBox--name').get_text(strip=True)
                                )
                            )
        return courses

    def get_assignments(self, course: Course) -> list[Assignment]:
        response = self.session.get(course.get_url())
        soup = BeautifulSoup(response.text, 'html.parser')
        assignments_data = soup.find('div', {'data-react-class': 'AssignmentsTable'})

        assignments = list()
        if assignments_data:
            assignments_data = json.loads(assignments_data.get('data-react-props'))
            if 'table_data' in assignments_data:
                for data in assignments_data['table_data']:
                    assignments.append(
                        Assignment(
                            assignment_id=self._parse_int(data.get('id')),
                            assignment_type=data.get('type'),
                            url=data.get('url'),
                            title=data.get('title'),
                            container_id=data.get('container_id'),
                            versioned=data.get('is_versioned_assignment'),
                            version_index=data.get('version_index'),
                            version_name=data.get('version_name'),
                            total_points=data.get('total_points'),
                            student_submission=data.get('student_submission'),
                            created_at=data.get('created_at'),
                            release_date=data.get('submission_window', {}).get('release_date'),
                            due_date=data.get('submission_window', {}).get('due_date'),
                            hard_due_date=data.get('submission_window', {}).get('hard_due_date'),
                            time_limit=data.get('submission_window', {}).get('time_limit'),
                            active_submissions=data.get('num_active_submissions'),
                            grading_progress=data.get('grading_progress'),
                            published=data.get('is_published'),
                            regrade_requests_open=data.get('regrade_requests_open'),
                            regrade_requests_possible=data.get('regrade_requests_possible'),
                            regrade_request_count=data.get('open_regrade_request_count'),
                            due_or_created_at_date=data.get('due_or_created_at_date')
                        )
                    )
                return assignments
            else:
                raise ValueError(f'Assignments Table is empty for course ID: {course.course_id}')
        raise ValueError(f'Assignments Table not found for course ID: {course.course_id}')

    def get_members(self, course: Course) -> list[Member]:
        response = self.session.get(urljoin(BASE_URL, course.get_url()+'/memberships'))
        soup = BeautifulSoup(response.text, 'html.parser')

        members = list()
        for entry in soup.findAll('table')[0].findAll('tr'):
            id_button = entry.find('button', class_='js-rosterName')
            if id_button:
                parsed_params = parse_qs(urlparse(id_button['data-url']).query)
                user_id = parsed_params.get('user_id')[0]

                other_info_button = entry.find('button', class_='rosterCell--editIcon')
                data_cm = json.loads(other_info_button['data-cm'])

                role = other_info_button.get('data-role')
                email = other_info_button.get('data-email')

                member = Member(
                    member_id=user_id,
                    full_name=data_cm.get('full_name'),
                    first_name=data_cm.get('first_name'),
                    last_name=data_cm.get('last_name'),
                    role=role,
                    sid=data_cm.get('sid'),
                    email=email
                )
                members.append(member)
        return members

    def get_gradebook(self, course: Course, member: Member) -> dict:
        url = GRADEBOOK.format(
            course_id=course.course_id,
            member_id=member.member_id
        )
        response = self.session.get(url)
        return json.loads(response.text)
    
    # Returns None when the member does not exist in the course or assignment
    def get_past_submissions(self, course: Course, assignment: Assignment, member: Member) -> list[Submission]:
        gradebook = self.get_gradebook(course, member)
        url = None
        for item in gradebook:
            item_data = item.get('assignment')
            if item_data.get('id') == assignment.assignment_id:
                url = item_data.get('submission').get('url')
                break

        if url == None:
            return None

        response = self.session.get(urljoin(BASE_URL, url + PAST_SUBMISSIONS))
        json_data = json.loads(response.text)['past_submissions']

        submissions = list()
        for data in json_data:
            submissions.append(
                Submission(
                    course_id=course.course_id,
                    assignment_id=assignment.assignment_id,
                    member_id=member.member_id,
                    submission_id=data.get('id'),
                    created_at=data.get('created_at'),
                    score=float(data.get('score')),
                    url=data.get('show_path')
                )
            )
        return submissions

    def _response_check(self, response: requests.Response) -> bool:
        if response.status_code == 200:
            return True
        else:
            raise ValueError(f'Failed to fetch the webpage. Status code: {response.status_code}')

    def _parse_int(self, text: str) -> int:
        return int(''.join(re.findall(r'\d', text)))

    def _to_datetime(self, text: str) -> datetime:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M")
