# gradescope.py

import requests
import logging as log
from bs4 import BeautifulSoup


BASE_URL = 'https://www.gradescope.com'
LOGIN_URL = f'{BASE_URL}/login'


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
