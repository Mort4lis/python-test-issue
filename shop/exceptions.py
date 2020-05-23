class DAOException(Exception):
    pass


class UserNotFoundException(DAOException):
    pass


class TokenNotFoundException(DAOException):
    pass


class ProductNotFoundException(DAOException):
    pass
