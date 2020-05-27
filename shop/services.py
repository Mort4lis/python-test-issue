from typing import Iterable, Tuple

from passlib.hash import sha256_crypt

from dao import (AccessTokenDAO, OrderDAO, OrderProductDAO, ProductDAO, SqlAlchemyOrderDAO, SqlAlchemyOrderProductDAO,
                 SqlAlchemyProductDAO, SqlAlchemyTokenDAO, SqlAlchemyUserDAO, SqlAlchemyUserOrderDAO, UserDAO,
                 UserOrderDAO)
from exceptions import (OrderNotFoundException, ProductNotEnoughException, ProductNotFoundException,
                        UserNotFoundException)
from storage import Order, OrderProduct, Product, User, UserOrder


class AuthService:
    """Сервис, инкапсулирующий логику аутентификации."""

    def __init__(self, dao: UserDAO) -> None:
        """
        Инициализация экземпляра класса сервиса.

        :param dao: DAO-объект для работы с сущностью Пользователь (User)
        """
        self.dao = dao

    async def check_credentials(self, login: str, password: str) -> bool:
        """
        Проверить аутентификационные данные пользователя.

        :param login: логин пользователя
        :param password: пароль пользователя
        :return: булево значение в зависимости от результата проверки
        """
        try:
            user = await self.dao.get_by_login(login=login)
        except UserNotFoundException:
            return False
        return sha256_crypt.verify(password, user.password)


class AccessTokenService:
    """Сервис, инкапсулирующий логику работы с токенами."""

    def __init__(self, dao: AccessTokenDAO) -> None:
        """
        Инициализация экземпляра класса сервиса.

        :param dao: DAO-объект для работы с сущностью Токен (AccessToken)
        """
        self.dao = dao

    async def get_by_login(self, login: str) -> str:
        """
        Вернуть токен пользователя.

        :param login: логин пользователя
        :return: токен пользователя
        :raise TokenNotFoundException: выбрасывается, если токен не был найден
        """
        access_token = await self.dao.get_by_login(login=login)
        return access_token.token


class ProductService:
    """Сервис, инкапсулирующий бизнес-логику продуктов."""

    def __init__(self, dao: ProductDAO) -> None:
        """
        Инициализация экземпляра класса сервиса.

        :param dao: продуктовый DAO-объект
        """
        self.dao = dao

    async def get_by_slug(self, slug: str) -> Product:
        """
        Поиск продукта по короткому имени slug.

        :param slug: короткое наименование продукта
        :return: найденый экземпляр продукта
        :raise ProductNotFoundException: выбрасывается, если продукт не был найден
        """
        return await self.dao.get_by_slug(slug)

    async def exists_by_slug(self, slug: str) -> bool:
        """
        Проверка на существование продукта в БД по его короткому имени slug.

        :param slug: короткое наименование продукта
        :return: булево значение, обозначающее существование или отстутствие продукта
        """
        try:
            await self.get_by_slug(slug)
        except ProductNotFoundException:
            return False
        else:
            return True

    async def get_all(self) -> Iterable[Product]:
        """
        Вернуть коллекцию всех продуктов.

        :return: коллекция экземпляров класса `Product`
        """
        return await self.dao.get_all()

    async def create(self, product: Product) -> Product:
        """
        Создать продукт.

        :param product: экземпляр продукта, который необходимо создать
        :return: созданный экземпляр продукта
        """
        return await self.dao.create(product=product)

    async def update(self, product: Product) -> Product:
        """
        Обновить продукт.

        :param product: экземпляр продукта с данными, которые необходимо обновить
        :return: обновленный экземпляр продукта
        """
        return await self.dao.update(product=product)

    async def delete(self, product: Product) -> Product:
        """
        Удалить продукт.

        :param product: экземпляр продукта, который необходимо удалить
        :return: удаленный экземпляр продукта
        """
        return await self.dao.delete(product=product)


class OrderService:
    """Сервис, инкапсулирующий бизнес-логику заказов."""

    def __init__(self,
                 order_dao: OrderDAO,
                 product_dao: ProductDAO,
                 order_product_dao: OrderProductDAO,
                 user_order_dao: UserOrderDAO) -> None:
        """
        Инициализация экземпляра класса сервиса.

        :param order_dao: DAO-объект заказа
        :param product_dao:
        :param order_product_dao:
        :param user_order_dao:
        """
        self.order_dao = order_dao
        self.product_dao = product_dao
        self.order_product_dao = order_product_dao
        self.user_order_dao = user_order_dao

    async def get_by_number(self, user: User, number: int) -> Tuple[Order, Iterable[OrderProduct]]:
        """
        Получить заказ по его номеру.

        :param user:
        :param number: номер заказа
        :return: кортеж вида (заказ, список продуктов для заказа)
        :raise OrderNotFoundException: выбрасывается в случае, если заказ не был найден,
            либо он принадлежит другому пользователю
        """
        order = await self.order_dao.get_by_number(number)
        user_order = UserOrder(user_id=user.id, order_id=order.id)
        if not await self.user_order_dao.exists(user_order):
            raise OrderNotFoundException
        order_products = await self.order_product_dao.get_all(order_id=order.id)
        return order, order_products

    async def create(self,
                     user: User,
                     products: Iterable[Tuple[Product, int]]) -> Tuple[Order, Iterable[OrderProduct]]:
        """
        Создать заказ.

        :param user: экземпляр пользователя, которому необходимо привязать созданный заказ
        :param products: коллекция кортежей вида (продукт, количество)
        :return: кортеж вида (заказ, список продуктов для заказа)
        :raise ProductNotEnoughException: выбрасывается в случае, если количество товара на складе недостаточно
        """
        order = await self.order_dao.create()

        order_products = []
        for product, quantity in products:
            if not product.is_enough_in_stock(quantity):
                raise ProductNotEnoughException(product=product)

            product.left_in_stock -= quantity
            order_product = OrderProduct(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity)
            await self.product_dao.update(product)
            await self.order_product_dao.create(order_product)
            order_products.append(order_product)

        user_order = UserOrder(user_id=user.id, order_id=order.id)
        await self.user_order_dao.create(user_order)
        return order, order_products


class ServiceFactory:
    """Фабрика создания объектов-сервисов."""

    def __init__(self, conn) -> None:
        """
        Инициализация фабрики.

        :param conn: объект подключения к БД
        """
        self.conn = conn

    def create_auth_service(self) -> AuthService:
        """
        Создать объект-сервис для работы с аутентификацией.

        :return: объект-сервис для работы с аутентификацией
        """
        return AuthService(dao=SqlAlchemyUserDAO(self.conn))

    def create_access_token_service(self) -> AccessTokenService:
        """
        Создать объект-сервис для работы с токенами.

        :return: объект-сервис для работы с токенами
        """
        return AccessTokenService(dao=SqlAlchemyTokenDAO(self.conn))

    def create_product_service(self) -> ProductService:
        """
        Создать объект-сервис для работы с продуктами.

        :return: объект-сервис для работы с продуктами
        """
        return ProductService(dao=SqlAlchemyProductDAO(self.conn))

    def create_order_service(self) -> OrderService:
        """
        Создать объект-сервис для работы с заказами.

        :return: объект-сервис для работы с заказами
        """
        return OrderService(
            order_dao=SqlAlchemyOrderDAO(self.conn),
            product_dao=SqlAlchemyProductDAO(self.conn),
            order_product_dao=SqlAlchemyOrderProductDAO(self.conn),
            user_order_dao=SqlAlchemyUserOrderDAO(self.conn)
        )
