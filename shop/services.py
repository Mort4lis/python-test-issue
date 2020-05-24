from typing import Iterable, Tuple

from .dao import OrderDAO, OrderProductDAO, ProductDAO, UserOrderDAO
from .exceptions import ProductNotEnoughException, ProductNotFoundException
from .storage import Order, OrderProduct, Product, User, UserOrder


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
        :raise ProductNotFoundException: исключение в случае неудачного поиска
        :return: найденый экземпляр продукта
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
        Создать продукта.

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
        """
        self.order_dao = order_dao
        self.product_dao = product_dao
        self.order_product_dao = order_product_dao
        self.user_order_dao = user_order_dao

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
