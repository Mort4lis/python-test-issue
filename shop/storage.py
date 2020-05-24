from enum import Enum
from typing import Generator, Optional
from uuid import UUID


class Entity:
    """Базовый класс сущностей, используемых в проекте."""

    def __iter__(self) -> Generator:
        """
        Реализация интерфейса итератора в виде генератора.

        Данная реализация необходима для того, чтобы получить представление объекта
        в виде словаря (dict), при этом не включая в данное представление атрибуты объекта,
        значения которых равны None.
        """
        for key, value in self.__dict__.items():
            if value is None:
                continue
            yield key, value


class User(Entity):
    """Класс пользователей."""

    def __init__(self,
                 id: UUID,
                 login: str,
                 password: str,
                 first_name: str,
                 surname: str,
                 middle_name: str,
                 sex: Enum,
                 age: int) -> None:
        """
        Конструктор инициализации экземпляра класса Пользователь.

        :param id: идентификатор пользователя
        :param login: логин пользователя
        :param password: пароль пользователя
        :param first_name: имя пользователя
        :param surname: фамилия пользователя
        :param middle_name: отчество пользователя
        :param sex: пол пользователя
        :param age: возраст пользователя
        """
        self.id = id
        self.login = login
        self.password = password
        self.first_name = first_name
        self.surname = surname
        self.middle_name = middle_name
        self.sex = sex
        self.age = age

    @property
    def full_name(self) -> str:
        """Вернуть полное имя пользователя."""
        return ' '.join([self.surname, self.first_name, self.middle_name])


class AccessToken(Entity):
    """Класс токенов доступа."""

    def __init__(self, id: UUID, token: str, user_id: UUID) -> None:
        """
        Конструктор инициализации экземпляра класса Токен.

        :param id: идентификатор токена
        :param token: последовательность символов (токен)
        :param user_id: идентификатор пользователя
        """
        self.id = id
        self.token = token
        self.user_id = user_id


class Product(Entity):
    """Класс продуктов."""

    def __init__(self,
                 name: str,
                 description: str,
                 price: float,
                 left_in_stock: int,
                 *,
                 id: Optional[UUID] = None,
                 slug: Optional[str] = None) -> None:
        """
        Конструктор инициализации экземпляра класса Продукт.

        :param name: наименование продукта
        :param description: описание продукта
        :param price: цена продукта
        :param left_in_stock: количество оставшихся продуктов данного типа на складе
        :param id: идентификатор продукта
        :param slug: короткое наименование продукта
        """
        self.id = id
        self.name = name
        self.description = description
        self.slug = slug
        self.price = price
        self.left_in_stock = left_in_stock

        if not slug:
            self.slug = '-'.join(name.split(' ')).lower()

    def is_enough_in_stock(self, quantity: int) -> bool:
        """
        Проверить на достаточное наличие товара.

        :param quantity: количество товара
        :return: логический результат проверки
        """
        return self.left_in_stock >= quantity


class Order(Entity):
    """Класс заказов."""

    def __init__(self, id: UUID, number: int) -> None:
        """
        Конструктор инициализации заказа.

        :param id: идентификатор заказа
        :param number: номер заказа
        """
        self.id = id
        self.number = number


class OrderProduct(Entity):
    """Класс связности заказов и продуктов."""

    def __init__(self, order_id: UUID, product_id: UUID, quantity: int) -> None:
        """
        Конструктор иницилизации объекта.

        :param order_id: идентификатор заказа
        :param product_id: идентификатор продукта
        :param quantity: количество продукта
        """
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity


class UserOrder(Entity):
    """Класс связности пользователей и продуктов."""

    def __init__(self, user_id: UUID, order_id: UUID) -> None:
        """
        Конструктор иницилизации объекта.

        :param user_id: идентификатор пользователя
        :param order_id: идентификатор заказа
        """
        self.user_id = user_id
        self.order_id = order_id
