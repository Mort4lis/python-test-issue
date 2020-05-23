from typing import Iterable

from .dao import ProductDAO
from .storage import Product
from .exceptions import ProductNotFoundException


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
