class DooverException(Exception):
    pass


class HTTPException(DooverException):
    pass


class NotFound(DooverException):
    pass


class Forbidden(DooverException):
    pass
