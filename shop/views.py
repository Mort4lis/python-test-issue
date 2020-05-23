import json

from aiohttp.web import Response, View, json_response
from aiohttp_validate import validate

from .auth import check_credentials, get_access_token
from .exceptions import ProductNotFoundException
from .schemas import AUTH_SCHEMA, PRODUCT_SCHEMA
from .services import ProductService
from .storage import Product
from .utils import JsonEncoder


class LoginView(View):
    """View аутентификации."""

    @validate(request_schema=AUTH_SCHEMA)
    async def post(self, *args) -> Response:
        """
        Аутентификация пользователя.

        Возвращает ответ с телом токена в случае успешной аутентификации.
        """
        dao_instances = self.request.app['dao']
        credentials = await self.request.json()
        if await check_credentials(user_dao=dao_instances['user'], **credentials):
            token = await get_access_token(token_dao=dao_instances['token'], login=credentials['login'])
            return json_response(status=200, data={'token': token})

        return json_response(status=400, data={'error': 'Bad credentials'})


class ProductListCreateView(View):
    async def get(self) -> Response:
        """Endpoint вывода всех продуктов."""
        dao = self.request.app['dao']['product']
        service = ProductService(dao=dao)
        products = await service.get_all()
        body = json.dumps([product.__dict__ for product in products], cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    @validate(request_schema=PRODUCT_SCHEMA)
    async def post(self, *args) -> Response:
        """Endpoint создания продуктов."""
        data = await self.request.json()
        service = ProductService(dao=self.request.app['dao']['product'])

        product = Product(**data)
        if await service.exists_by_slug(slug=product.slug):
            return json_response(status=400,
                                 data={'error': 'Product with this slug is already exists'})

        created = await service.create(product=product)
        body = json.dumps(created.__dict__, cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')


class ProductRetrieveUpdateDeleteView(View):
    async def get(self) -> Response:
        """
        Endpoint, возвращающий представление конкретного продукта по slug.

        :return: ответ, содержащий json-представление продукта или 404 статус
        """
        service = ProductService(dao=self.request.app['dao']['product'])
        try:
            product = await service.get_by_slug(slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        body = json.dumps(product.__dict__, cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    @validate(request_schema=PRODUCT_SCHEMA)
    async def put(self, *args) -> Response:
        """
        Endpoint, возвращающий обновленное представление продукта по slug.

        Принимает тело запроса и обновляет выбранный продукт.

        :return: ответ, содержащий json-представление обновленного продукта или 404 статус
        """
        data = await self.request.json()
        service = ProductService(dao=self.request.app['dao']['product'])
        try:
            product = await service.get_by_slug(slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        for prop, value in data.items():
            setattr(product, prop, value)

        product = await service.update(product)
        body = json.dumps(product.__dict__, cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    async def delete(self) -> Response:
        """
        Endpoint, удаляющий продукт по его slug.

        :return: ответ (204-No Content) в случае успеха или 404 статус
        """
        service = ProductService(dao=self.request.app['dao']['product'])
        try:
            product = await service.get_by_slug(slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        await service.delete(product)
        return Response(status=204)


async def index(request):
    return json_response(data={'message': 'Hello, world!'})
