class TelloException(Exception):
    """Base class for all Tello exceptions"""


class TelloInvalidResponse(TelloException):
    pass
