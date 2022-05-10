class TelloException(Exception):
    """Base class for all Tello exceptions"""


class TelloInvalidResponse(TelloException):
    pass


class TelloNoConnection(TelloException):
    pass


class TelloNoState(TelloException):
    pass
