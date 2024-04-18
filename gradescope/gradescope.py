# gradescope.py

import json
import requests
import logging as log
from bs4 import BeautifulSoup
from .dataclass import Course, Assignment
from .constants import BASE_URL, LOGIN_URL, ROLE_MAP, Role


class Gradescope:
    '''
    A Python wrapper for Gradescope.

    Args:
        username (str | None): The username for Gradescope. Defaults to None.
        password (str | None): The password for Gradescope. Defaults to None.
        auto_login (bool): Whether to automatically login upon object initialization. Defaults to True.
        verbose (bool): Whether to enable verbose logging. Defaults to False.

    Attributes:
        session (requests.Session): The session object for making HTTP requests.
        username (str | None): The username for Gradescope.
        password (str | None): The password for Gradescope.
        verbose (bool): Whether verbose logging is enabled.
        logged_in (bool): Whether the user is logged in to Gradescope.
    '''

    def __init__(
            self,
            username: str | None = None,
            password: str | None = None,
            auto_login: bool = True,
            verbose: bool = False
        ) -> None:
        '''
        Initializes a new instance of the Gradescope class.

        Args:
            username (str | None): The username for Gradescope. Defaults to None.
            password (str | None): The password for Gradescope. Defaults to None.
            auto_login (bool): Whether to automatically login upon object initialization. Defaults to True.
            verbose (bool): Whether to enable verbose logging. Defaults to False.
        '''
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
        '''
        Logs in to the Gradescope website.

        Args:
            username (str | None): The username for Gradescope. Defaults to None.
            password (str | None): The password for Gradescope. Defaults to None.

        Returns:
            bool: True if login is successful, False otherwise.

        Raises:
            TypeError: If the username or password is None.
            ValueError: If the login return URL is unknown.
        '''
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
        '''
        Retrieves a list of courses based on the specified role.

        Args:
            role (Role): The role for which to retrieve the courses.

        Returns:
            list: A list of Course objects representing the courses.
        '''
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
                                    course_id=course.get('href', '').split('/')[-1],
                                    url=course.get('href', None),
                                    role=role.value,
                                    term=term_name,
                                    short_name=course.find(class_='courseBox--shortname').get_text(strip=True),
                                    full_name=course.find(class_='courseBox--name').get_text(strip=True)
                                ))

        return courses

    def get_course_assignments(self, course: Course) -> list[Assignment]:
        '''
        Retrieves the assignments for a specific course.

        Args:
            course_id (str): The course ID for the course.
        
        Returns:
            list | None: A list of assignment IDs. 
                         Returns None if the assignments table is empty.
        '''
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
                            assignment_id=data.get('id'),
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
                print('Assignments Table is empty for course ID:', course.course_id)
                return None
        
        print('Assignments Table not found for course ID:', course.course_id)
        return None
    
    def get_latest_submissions(self, course_id, assignment_id):
        '''
        Retrieves the students who have submitted the assignment.

        Args:
            course_id (str): The course ID for the course.
            assignment_id (str): The assignment ID for the assignment.

        Returns:
            list: A list of student IDs. (This ID is not the same as the student's university ID. It is a unique ID for Gradescope)
        '''
        response = self.session.get(BASE_URL+'/courses/'+course_id+'/assignments/'+assignment_id+'/review_grades')
        soup = BeautifulSoup(response.text, 'html.parser')
        submissions = []
        for student in soup.find_all(class_='link-gray'):
            submissions.append(student.get('href').split('/')[-1])
        return submissions
    
    def _response_check(self, response: requests.Response) -> bool:
        '''
        Checks if the HTTP response is successful.

        Args:
            response (requests.Response): The HTTP response object.

        Returns:
            bool: True if the response is successful, False otherwise.

        Raises:
            ValueError: If the response status code is not 200.
        '''
        if response.status_code == 200:
            return True
        else:
            raise ValueError(f'Failed to fetch the webpage. Status code: {response.status_code}')
