# errors.py

class GradescopeError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class LoginError(GradescopeError):
    def __init__(self, msg: str = 'Login failed, please check username and password.'):
        super().__init__(msg)


class NotLoggedInError(GradescopeError):
    def __init__(self, msg: str = 'Not logged in.'):
        super().__init__(msg)


class ResponseError(GradescopeError):
    def __init__(self, msg: str):
        super().__init__(msg)
