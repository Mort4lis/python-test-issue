from typing import Iterable

from .dao import ProductDAO
from .storage import Product


class ProductService:
    """Сервис, инкапсулирующий бизнес-логику продуктов."""

    def __init__(self, dao: ProductDAO) -> None:
        """
        Инициализация экземпляра класса сервиса.

        :param dao: продуктовый DAO-объект
        """
        self.dao = dao

    async def get_all(self) -> Iterable[Product]:
        """
        Вернуть коллекцию всех продуктов.

        :return: коллекция экземпляров класса `Product`
        """
        return await self.dao.get_all()

    async def create(self, product: Product) -> Product:
        """
        Создание продукта.

        :param product: экземпляр продукта, который необходимо создать
        :return: созданный экземпляр продукта
        """
        return await self.dao.create(product=product)
