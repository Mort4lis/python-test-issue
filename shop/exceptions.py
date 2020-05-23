class DAOException(Exception):
    """Базовый класс исключений DAO-слоя."""

    pass


class UserNotFoundException(DAOException):
    """Исключение, выбрасываемое из DAO-слоя в случае, если объект пользователя (User) не найден."""

    pass


class TokenNotFoundException(DAOException):
    """Исключение, выбрасываемое из DAO-слоя в случае, если объект токена (AccessToken) не найден."""

    pass


class ProductNotFoundException(DAOException):
    """Исключение, выбрасываемое из DAO-слоя в случае, если объект продукта (Product) не найден."""

    pass
