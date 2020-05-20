from abc import ABC, abstractmethod
from typing import Iterable
from uuid import UUID

import sqlalchemy as sa
from aiopg.sa.connection import SAConnection

from .db import token_table, user_table
from .storage import AccessToken, User


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

        return User(**row)


class AccessTokenDAO(ABC):
    @abstractmethod
    async def get_by_login(self, user_id: UUID) -> AccessToken:
        """
        Получить токен по идентификатору пользователя.

        :param user_id: идентификатор пользователя
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

        return AccessToken(**row)
