from .dao import ProductDAO


class ProductService:
    def __init__(self, dao: ProductDAO):
        self.dao = dao

    async def get_all(self):
        products = await self.dao.get_all()
        return products
