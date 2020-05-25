from abc import ABC, abstractmethod
from typing import Iterable
from uuid import UUID

import sqlalchemy as sa
from aiopg.sa.connection import SAConnection
from overrides import overrides

from db import order_product_table, order_table, product_table, token_table, user_order_table, user_table
from exceptions import (OrderNotFoundException, ProductNotFoundException, TokenNotFoundException,
                        UserNotFoundException)
from storage import AccessToken, Order, OrderProduct, Product, User, UserOrder


class UserDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для сущности Пользователь (User)."""

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


class AccessTokenDAO(ABC):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Токен (AccessToken)."""

    @abstractmethod
    async def get_by_login(self, login: str) -> AccessToken:
        """
        Получить токен по логину пользователя.

        :param login: логин пользователя
        :return: найденный экземпляр класса `AccessToken`
        """
        pass


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


class OrderDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для сущности Заказ (Order)."""

    @abstractmethod
    async def get_by_number(self, number: int) -> Order:
        """
        Получить заказ по его номеру.

        :param number: номер заказа
        :return: найденный экземпляр заказа
        """
        pass

    @abstractmethod
    async def create(self) -> Order:
        """
        Создать заказ.

        :return: созданный экземпляр заказа
        """
        pass


class OrderProductDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для связи Продуктов и Заказов (OrderProduct)."""

    @abstractmethod
    async def get_all(self, order_id: UUID) -> Iterable[OrderProduct]:
        """
        Получить все связи продукта и заказа по идентификатора заказа.

        :param order_id: идентификатор заказа
        :return: коллекция экземпляров связей
        """
        pass

    @abstractmethod
    async def create(self, order_product: OrderProduct) -> OrderProduct:
        """
        Создать связь продукта и заказа.

        :param order_product: экземпляр связи, которую необходимо создать
        :return: созданный экземпляр связи
        """
        pass


class UserOrderDAO(ABC):
    """Абстрактный слой доступа к БД (DAO) для связи Пользователей и Заказов (UserOrder)."""

    @abstractmethod
    async def exists(self, user_order: UserOrder) -> bool:
        """
        Проверка на существование связи пользователя и продукта.

        :param user_order: проверяемый экземпляр свзи
        :return: булево значение в зависимости от результата
        """
        pass

    @abstractmethod
    async def create(self, user_order: UserOrder) -> UserOrder:
        """
        Создать связь пользователя и продукта.

        :param user_order: экземпляр связи, которую необходимо создать
        :return: созданный экземпляр связи
        """
        pass


class BaseSqlAlchemyDAO(ABC):
    """Базовый DAO-класс, инкапсулирующий в себе конструктор, принимающий подключение к БД."""

    def __init__(self, conn: SAConnection) -> None:
        """
        Инициализация DAO-экземпляра.

        :param conn: экземпляр подключения к БД
        """
        self.conn = conn


class SqlAlchemyUserDAO(BaseSqlAlchemyDAO, UserDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Пользователь (User)."""

    @overrides
    async def get_by_login(self, login: str) -> User:
        query = user_table.select().where(user_table.c.login == login)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise UserNotFoundException

        return User(**row)

    @overrides
    async def get_by_token(self, token: str) -> User:
        join = sa.join(user_table, token_table, user_table.c.id == token_table.c.user_id)
        query = user_table.select().select_from(join).where(token_table.c.token == token)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise UserNotFoundException

        return User(**row)


class SqlAlchemyTokenDAO(BaseSqlAlchemyDAO, AccessTokenDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Токен (AccessToken)."""

    @overrides
    async def get_by_login(self, login: str) -> AccessToken:
        join = sa.join(user_table, token_table, user_table.c.id == token_table.c.user_id)
        query = token_table.select().select_from(join).where(user_table.c.login == login)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise TokenNotFoundException

        return AccessToken(**row)


class SqlAlchemyProductDAO(BaseSqlAlchemyDAO, ProductDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Продукт (Product)."""

    @overrides
    async def get_by_slug(self, slug: str) -> Product:
        query = product_table.select().where(product_table.c.slug == slug)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise ProductNotFoundException

        return Product(**row)

    @overrides
    async def get_all(self) -> Iterable[Product]:
        query = product_table.select()
        result = await self.conn.execute(query)
        rows = await result.fetchall()
        products = [Product(**row) for row in rows]
        return products

    @overrides
    async def create(self, product: Product) -> Product:
        insert = product_table.insert(). \
            values(**dict(product)). \
            returning(product_table.c.id)
        result = await self.conn.execute(insert)
        inserted_primary_key = await result.scalar()
        return Product(id=inserted_primary_key, **dict(product))

    @overrides
    async def update(self, product: Product) -> Product:
        query = product_table.update(). \
            where(product_table.c.id == product.id). \
            values(**dict(product))
        await self.conn.execute(query)
        return product

    @overrides
    async def delete(self, product: Product) -> Product:
        query = product_table.delete().where(product_table.c.id == product.id)
        await self.conn.execute(query)
        return product


class SqlAlchemyOrderDAO(BaseSqlAlchemyDAO, OrderDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для сущности Заказ (Order)."""

    @overrides
    async def get_by_number(self, number: int) -> Order:
        query = order_table.select(). \
            where(order_table.c.number == number)
        result = await self.conn.execute(query)
        row = await result.fetchone()

        if row is None:
            raise OrderNotFoundException

        return Order(**row)

    @overrides
    async def create(self) -> Order:
        query = order_table.insert(). \
            values(). \
            returning(order_table.c.id, order_table.c.number)
        result = await self.conn.execute(query)
        fields = await result.fetchone()
        return Order(id=fields.id, number=fields.number)


class SqlAlchemyOrderProductDAO(BaseSqlAlchemyDAO, OrderProductDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для связи Продуктов и Заказов (OrderProduct)."""

    @overrides
    async def get_all(self, order_id: UUID) -> Iterable[OrderProduct]:
        query = order_product_table.select(). \
            where(order_product_table.c.order_id == order_id)
        result = await self.conn.execute(query)
        rows = await result.fetchall()
        return [OrderProduct(**row) for row in rows]

    @overrides
    async def create(self, order_product: OrderProduct) -> OrderProduct:
        query = order_product_table.insert().values(**dict(order_product))
        await self.conn.execute(query)
        return order_product


class SqlAlchemyUserOrderDAO(BaseSqlAlchemyDAO, UserOrderDAO):
    """Реализация абстрактного слоя доступа к БД (DAO) для связи Пользователей и Заказов (UserOrder)."""

    @overrides
    async def exists(self, user_order: UserOrder) -> bool:
        query = sa.exists().where(
            sa.and_(
                user_order_table.c.user_id == user_order.user_id,
                user_order_table.c.order_id == user_order.order_id
            )
        ).select()
        result = await self.conn.execute(query)
        return await result.scalar()

    @overrides
    async def create(self, user_order: UserOrder) -> UserOrder:
        query = user_order_table.insert().values(**dict(user_order))
        await self.conn.execute(query)
        return user_order
