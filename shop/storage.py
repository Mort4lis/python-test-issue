from enum import Enum
from uuid import UUID
from typing import Optional


class User:
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


class AccessToken:
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


class Product:
    """Класс продуктов."""

    def __init__(self,
                 id: Optional[UUID],
                 name: str,
                 description: str,
                 price: float,
                 left_in_stock: int) -> None:
        """
        Конструктор инициализации экземпляра класса Продукт.

        :param id: идентификатор продукта
        :param name: наименование продукта
        :param description: описание продукта
        :param price: цена продукта
        :param left_in_stock: количество оставшихся продуктов данного типа на складе
        """
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.left_in_stock = left_in_stock

    def __iter__(self):
        for key, value in self.__dict__.items():
            if key == 'id' and value is None:
                continue
            yield key, value
