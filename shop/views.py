import json

from aiohttp.web import Response, View, json_response
from aiohttp_validate import validate

from .auth import check_credentials, get_access_token
from .services import ProductService
from .storage import Product
from .utils import JsonEncoder


class LoginView(View):
    """View аутентификации."""

    @validate(request_schema={
        'type': 'object',
        'properties': {
            'login': {'type': 'string'},
            'password': {'type': 'string'}
        },
        'required': ['login', 'password']
    })
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

    @validate(request_schema={
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 255},
            'description': {'type': 'string', 'minLength': 5},
            'price': {'type': 'number', 'minimum': 0.1},
            'left_in_stock': {'type': 'integer', 'minimum': 1}
        },
        'required': ['name', 'description', 'price', 'left_in_stock']
    })
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
    async def get(self):
        return json_response(data={'get': self.request.match_info['uuid']})

    async def put(self):
        return json_response(data={'put': self.request.match_info['uuid']})

    async def delete(self):
        return json_response(data={'delete': self.request.match_info['uuid']})


async def index(request):
    return json_response(data={'message': 'Hello, world!'})
