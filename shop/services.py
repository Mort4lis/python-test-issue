from typing import Iterable

from .dao import ProductDAO
from .storage import Product


class ProductService:
    def __init__(self, dao: ProductDAO) -> None:
        self.dao = dao

    async def get_all(self) -> Iterable[Product]:
        return await self.dao.get_all()

    async def create(self, product: Product) -> Product:
        return await self.dao.create(product=product)
