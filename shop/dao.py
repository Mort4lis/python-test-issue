from abc import ABC, abstractmethod
from typing import Iterable
from uuid import UUID

import sqlalchemy as sa
from aiopg.sa.connection import SAConnection

from .db import product_table, token_table, user_table
from .exceptions import TokenNotFoundException, UserNotFoundException
from .storage import AccessToken, Product, User


class UserDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для сущности Пользователь (User)."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Создать пользователя.

        :param user: экземпляр класса `User`
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Обновить пользователя.

        :param user: экземпляр класса `User`
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """
        Удалить пользователя.

        :param user_id: идентификатор пользователя
        """
        pass

    @abstractmethod
    async def get_all(self) -> Iterable[User]:
        """Вернуть колекцию пользователей."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User:
        """
        Получить пользователя по уникальному идентификатору.

        :param user_id: идентификатор пользователя
        """
        pass

    @abstractmethod
    async def get_by_login(self, login: str) -> User:
        """
        Получить пользователя по логину.

        :param login: логин пользователя
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> User:
        """
        Получить пользователя по токену доступа.

        :param token: токен доступа
        """
        pass


class SqlAlchemyUserDAO(UserDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Пользователь (User)."""

    def __init__(self, conn: SAConnection) -> None:
        self.conn = conn

    async def create(self, user: User) -> User:
        pass

    async def update(self, user: User) -> User:
        pass

    async def delete(self, user_id: UUID) -> None:
        pass

    async def get_all(self) -> Iterable[User]:
        pass

    async def get_by_id(self, user_id: UUID) -> User:
        pass

    async def get_by_login(self, login: str) -> User:
        query = user_table.select().where(user_table.c.login == login)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise UserNotFoundException

        return User(**row)

    async def get_by_token(self, token: str) -> User:
        join = sa.join(user_table, token_table, user_table.c.id == token_table.c.user_id)
        query = user_table.select().select_from(join).where(token_table.c.token == token)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise UserNotFoundException

        return User(**row)


class AccessTokenDAO(ABC):
    @abstractmethod
    async def get_by_login(self, login: str) -> AccessToken:
        """
        Получить токен по логину пользователя.

        :param login: логин пользователя
        """
        pass


class SqlAlchemyTokenDAO(AccessTokenDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Токен (AccessToken)."""

    def __init__(self, conn: SAConnection):
        self.conn = conn

    async def get_by_login(self, login: str) -> AccessToken:
        join = sa.join(user_table, token_table, user_table.c.id == token_table.c.user_id)
        query = token_table.select().select_from(join).where(user_table.c.login == login)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise TokenNotFoundException

        return AccessToken(**row)


class ProductDAO(ABC):
    @abstractmethod
    async def get_all(self) -> Iterable[Product]:
        pass


class SqlAlchemyProductDAO(ProductDAO):
    def __init__(self, conn: SAConnection):
        self.conn = conn

    async def get_all(self) -> Iterable[Product]:
        query = product_table.select()
        result = await self.conn.execute(query)
        rows = await result.fetchall()
        products = [Product(**row) for row in rows]
        return products
