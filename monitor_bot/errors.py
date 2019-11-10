import enum


def parse_pywin_error(e):
    if e.winerror == PyWinErrorCode.ACCESS_DENIED:
        return PermissionException()
    elif e.winerror == PyWinErrorCode.WINDOW_NOT_FOUND:
        return ProcessNotFoundException()

    return UnknownPyWinException(e)


class ProcessNotFoundException(Exception):
    pass


class PermissionException(Exception):
    def __init__(self):
        super().__init__(
            "Administrative access is required to execute win32api"
        )


class UnknownPyWinException(Exception):
    def __init__(self, pywin_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pywin_error = pywin_error


class PyWinErrorCode(enum.Enum):
    ACCESS_DENIED = 5
    WINDOW_NOT_FOUND = 1400

    def __eq__(self, other):
        if type(other) is float or type(other) is int:
            return self.value == other

        if self.__class__ is other.__class__:
            return self.value == other.value

        return NotImplemented
