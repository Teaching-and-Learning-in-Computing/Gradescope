# gradescope.py

import io
import re
import json
import requests
import pandas as pd
import logging as log
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from .dataclass import Course, Assignment, StudentAssignment, Member, Submission
from .errors import LoginError, NotLoggedInError, ResponseError
from .constants import BASE_URL, LOGIN_URL, GRADEBOOK, PAST_SUBMISSIONS, ROLE_MAP, Role


class Gradescope:
    '''
    A Python wrapper for Gradescope to easily retrieve data from your Gradescope Courses.
    '''
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        auto_login: bool = True,
        verbose: bool = False
    ) -> None:
        '''
        Initializes a Gradescope object.

        Args:
            username (str | None): The username for logging into Gradescope. Defaults to None.
            password (str | None): The password for logging into Gradescope. Defaults to None.
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
        Log into Gradescope with the provided username and password.

        Args:
            username (str | None): The username for logging into Gradescope. Defaults to None.
            password (str | None): The password for logging into Gradescope. Defaults to None.

        Returns:
            bool: True if login is successful, False otherwise.

        Raises:
            TypeError: If the username or password is None.
            LoginError: If the return URL after login is unknown.
        '''
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if self.username is None or self.password is None:
            raise TypeError('The username or password cannot be None.')

        response = self.session.get(BASE_URL)
        self._response_check(response)
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
        self._response_check(response)

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
            raise LoginError('Unknown return URL.')

    def get_courses(self, role: Role) -> list[Course]:
        '''
        Retrieves the list of courses for the specified role.

        Args:
            role (Role): The role for which to retrieve the courses.

        Returns:
            list[Course]: The list of courses for the specified role.

        Raises:
            NotLoggedInError: If not logged in.
            ResponseError: If the heading for the specified role is not found.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(BASE_URL)
        self._response_check(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        courses = list()

        rmap = ROLE_MAP[role.value]
        for _ in rmap:
            current_heading = soup.find('h1', string=ROLE_MAP[role.value])
            if current_heading:
                break

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
        else:
            log.warning(f'Cannot find heading for Role: {role}')
            # raise ResponseError(f'Cannot find heading for Role: {role}')
        return courses

    def get_assignments(self, course: Course) -> list[Assignment]:
        '''
        Retrieves the list of assignments for the specified course.

        Args:
            course (Course): The course for which to retrieve the assignments.

        Returns:
            list[Assignment]: The list of assignments for the specified course.

        Raises:
            NotLoggedInError: If not logged in.
            ResponseError: If the assignments table is empty or not found for the specified course.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(course.get_url() + '/assignments')
        self._response_check(response)
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
                raise ResponseError(f'Assignments Table is empty for course ID: {course.course_id}')
        raise ResponseError(f'Assignments Table not found for course ID: {course.course_id}')

    def get_assignments_as_student(self, course: Course) -> list[StudentAssignment]:
        '''
        Retrieves the list of assignments visible to a student for the specified course.

        This method parses the student-facing assignment table on Gradescope to extract information such as
        assignment title, submission status, scores, due dates, and template download links.

        Args:
            course (Course): The course for which to retrieve the assignments.

        Returns:
            list[StudentAssignment]: A list of StudentAssignment objects with assignment details.

        Raises:
            NotLoggedInError: If the user is not logged in.
            ResponseError: If the assignments table cannot be found for the specified course.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(course.get_url())
        self._response_check(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        assignments_table = soup.find('table', {'id': 'assignments-student-table'})
        if not assignments_table:
            raise ResponseError(f'Student assignments table not found for course ID: {course.course_id}')

        assignments = []
        rows = assignments_table.find('tbody').find_all('tr')

        for row in rows:
            title_cell = row.find('th', class_='table--primaryLink')
            if not title_cell:
                continue

            title_button = title_cell.find('button')
            title = title_button.get_text(strip=True) if title_button else title_cell.get_text(strip=True)
            assignment_id = int(title_button['data-assignment-id']) if title_button and 'data-assignment-id' in title_button.attrs else None
            submission_url = title_button['data-post-url'] if title_button and 'data-post-url' in title_button.attrs else None
            template_url = title_button.get('data-template-url') if title_button and 'data-template-url' in title_button.attrs else None

            status_cell = row.find('td', class_='submissionStatus')
            submitted = 'submissionStatus-complete' in status_cell.get('class', []) if status_cell else False
            score_div = status_cell.find('div', class_='submissionStatus--score') if status_cell else None
            score = score_div.get_text(strip=True) if score_div else None

            release_time = row.find('time', class_='submissionTimeChart--releaseDate')
            due_time = row.find('time', class_='submissionTimeChart--dueDate')

            # Some rows have two due time elements (for late due date)
            all_due_times = row.find_all('time', class_='submissionTimeChart--dueDate')
            late_due_time = all_due_times[1]['datetime'] if len(all_due_times) > 1 else None

            assignments.append(StudentAssignment(
                assignment_id=assignment_id,
                title=title,
                submission_url=submission_url,
                template_url=template_url,
                submitted=submitted,
                score=score,
                release_date=release_time['datetime'] if release_time else None,
                due_date=due_time['datetime'] if due_time else None,
                late_due_date=late_due_time
            ))

        return assignments

    def get_members(self, course: Course) -> list[Member]:
        '''
        Retrieves the list of members for the specified course.

        Args:
            course (Course): The course for which to retrieve the members.

        Returns:
            list[Member]: The list of members for the specified course.

        Raises:
            NotLoggedInError: If not logged in.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(course.get_url() + '/memberships')
        self._response_check(response)
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

    # Returns None when the member does not exist in the course or assignment
    def get_past_submissions(self, course: Course, assignment: Assignment, member: Member) -> list[Submission]:
        '''
        Retrieves the list of past submissions for the specified course, assignment, and member.

        Args:
            course (Course): The course for which to retrieve the past submissions.
            assignment (Assignment): The assignment for which to retrieve the past submissions.
            member (Member): The member for which to retrieve the past submissions.

        Returns:
            list[Submission]: The list of past submissions for the specified course, assignment, and member.

        Raises:
            NotLoggedInError: If not logged in.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        gradebook = self.get_gradebook(course, member)
        url = None
        for item in gradebook:
            item_data = item.get('assignment')
            if item_data.get('id') == assignment.assignment_id:
                url = item_data.get('submission').get('url')
                break

        if url is None:
            return None

        response = self.session.get(urljoin(BASE_URL, url + PAST_SUBMISSIONS))
        self._response_check(response)
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
                    score=float(data.get('score')) if data.get('score') else None,
                    url=data.get('show_path')
                )
            )
        return submissions

    def get_gradebook(self, course: Course, member: Member) -> dict:
        '''
        Retrieves the gradebook for a specific course and member.

        Args:
            course (Course): The course object.
            member (Member): The member object.

        Returns:
            dict: The gradebook data as a dictionary.

        Raises:
            NotLoggedInError: If the user is not logged in.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        url = GRADEBOOK.format(
            course_id=course.course_id,
            member_id=member.member_id
        )
        response = self.session.get(url)
        self._response_check(response)
        return json.loads(response.text)

    def get_assignment_grades(self, assignment: Assignment) -> pd.DataFrame:
        '''
        Retrieves the grades for a specific assignment.

        Args:
            assignment (Assignment): The assignment object.

        Returns:
            pd.DataFrame: The assignment grades as a pandas DataFrame.

        Raises:
            NotLoggedInError: If the user is not logged in.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(assignment.get_grades_url())
        self._response_check(response)
        return pd.read_csv(io.StringIO(response.content.decode('utf-8')), skiprows=2)

    def download_file(self, path: str, url: str) -> None:
        '''
        Downloads a file from a given URL and saves it to the specified path.

        Args:
            path (str): The path where the file should be saved.
            url (str): The URL of the file to be downloaded.

        Raises:
            NotLoggedInError: If the user is not logged in.
        '''
        if not self.logged_in:
            raise NotLoggedInError

        response = self.session.get(url)
        self._response_check(response)
        with open(path, 'wb') as file:
            file.write(response.content)

    def _response_check(self, response: requests.Response) -> bool:
        '''
        Checks the response status code and raises an error if it's not 200.

        Args:
            response (requests.Response): The response object.

        Returns:
            bool: True if the status code is 200.

        Raises:
            ResponseError: If the status code is not 200.
        '''
        if response.status_code == 200:
            return True
        else:
            raise ResponseError(f'Failed to fetch the webpage. Status code: {response.status_code}. URL: {response.url}')

    def _parse_int(self, text: str) -> int:
        '''
        Parses an integer from a given text.

        Args:
            text (str): The text containing the integer.

        Returns:
            int: The parsed integer.
        '''
        return int(''.join(re.findall(r'\d', text)))

    def _to_datetime(self, text: str) -> datetime:
        '''
        Converts a string to a datetime object.

        Args:
            text (str): The string to be converted.

        Returns:
            datetime: The converted datetime object.
        '''
        return datetime.strptime(text, "%Y-%m-%dT%H:%M")
