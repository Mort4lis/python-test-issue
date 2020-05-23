from abc import ABC, abstractmethod
from typing import Iterable
from uuid import UUID

import sqlalchemy as sa
from aiopg.sa.connection import SAConnection

from .db import product_table, token_table, user_table
from .exceptions import ProductNotFoundException, TokenNotFoundException, UserNotFoundException
from .storage import AccessToken, Product, User


class UserDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для сущности Пользователь (User)."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Создать пользователя.

        Данный метод принимает на вход экземпляр класса `User`,
        у которого id=None. А возвращает другой экзампляр класса `User`,
        с установленным id (первичным ключом).

        :param user: экземпляр класса `User`, который необходимо создать
        :return: созданный экземпляр класса `User`
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Обновить пользователя.

        :param user: экземпляр класса `User`, который необходимо обновить
        :return: обновленный экземпляр класса `User`
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
        """
        Вернуть колекцию пользователей.

        :return: коллекция экземпляров класса `User`
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User:
        """
        Получить пользователя по уникальному идентификатору.

        :param user_id: идентификатор пользователя
        :return: найденный экземпляр класса `User`
        """
        pass

    @abstractmethod
    async def get_by_login(self, login: str) -> User:
        """
        Получить пользователя по логину.

        :param login: логин пользователя
        :return: найденный экземпляр класса `User`
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> User:
        """
        Получить пользователя по токену доступа.

        :param token: токен доступа
        :return: найденный экземпляр класса `User`
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
        :return: найденный экземпляр класса `AccessToken`
        """
        pass


class SqlAlchemyTokenDAO(AccessTokenDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Токен (AccessToken)."""

    def __init__(self, conn: SAConnection) -> None:
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
    """Абстрактный слой доступа к БД (DAO) для сущности Продукт (Product)."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Product:
        """
        Получить продукт по slug.

        :raise ProductNotFoundException: исключение в случае неудачного поиска
        :return: найденный экземпляр продукта
        """
        pass

    @abstractmethod
    async def get_all(self) -> Iterable[Product]:
        """
        Вернуть коллекцию всех продуктов.

        :return: коллекция объектов класса `Product`
        """
        pass

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """
        Создать продукт.

        Данный метод принимает на вход экземпляр класса `Product`,
        у которого id=None. А возвращает другой экзампляр класса `Product`,
        с установленным id (первичным ключом).

        :param product: экземпляр продукта, который необходимо создать
        :return: созданный экземпляр продукта
        """
        pass

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """
        Обновить продукт.

        :param product: экземпляр продукта с данными, которые необходимо обновить
        :return: обновленный экземпляр продукта
        """
        pass

    @abstractmethod
    async def delete(self, product: Product) -> Product:
        """
        Удалить продукт.

        :param product: экземпляр продукта, который необходимо удалить
        :return: удаленный экземпляр продукта
        """
        pass


class SqlAlchemyProductDAO(ProductDAO):
    def __init__(self, conn: SAConnection) -> None:
        self.conn = conn

    async def get_by_slug(self, slug: str) -> Product:
        query = product_table.select().where(product_table.c.slug == slug)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise ProductNotFoundException

        return Product(**row)

    async def get_all(self) -> Iterable[Product]:
        query = product_table.select()
        result = await self.conn.execute(query)
        rows = await result.fetchall()
        products = [Product(**row) for row in rows]
        return products

    async def create(self, product: Product) -> Product:
        insert = product_table.insert(). \
            values(**dict(product)). \
            returning(product_table.c.id)
        result = await self.conn.execute(insert)
        inserted_primary_key = await result.scalar()
        return Product(id=inserted_primary_key, **dict(product))

    async def update(self, product: Product) -> Product:
        query = product_table.update(). \
            where(product_table.c.id == product.id). \
            values(**dict(product))
        await self.conn.execute(query)
        return product

    async def delete(self, product: Product) -> Product:
        query = product_table.delete().where(product_table.c.id == product.id)
        await self.conn.execute(query)
        return product
