class DAOException(Exception):
    pass


class UserNotFoundException(DAOException):
    pass


class TokenNotFoundException(DAOException):
    pass
