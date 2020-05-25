from storage import Product


class BaseShopException(Exception):
    """Базовый класс приложения."""

    pass


class DAOException(BaseShopException):
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


class OrderNotFoundException(DAOException):
    """Исключение, выбрасываемое из DAO-слоя в случае, если объект заказа (Order) не найден."""

    pass


class ProductNotEnoughException(BaseShopException):
    """Исключение, выбрасываемое в случае, если продукта недостаточно на складе."""

    def __init__(self, product: Product, *args) -> None:
        """
        Конструктор инициализации исключения.

        :param product: экземпляр продукта
        :param args: кортеж дополнительных аргументов
        """
        super().__init__(*args)
        self.product = product
