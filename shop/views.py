import json

from aiohttp.web import Response, View, json_response
from aiohttp_validate import validate

from .exceptions import OrderNotFoundException, ProductNotEnoughException, ProductNotFoundException
from .mixins import (AccessTokenServiceViewMixin, AuthServiceViewMixin,
                     OrderServiceViewMixin, ProductServiceViewMixin)
from .schemas import AUTH_SCHEMA, ORDER_PRODUCT_SCHEMA, PRODUCT_SCHEMA
from .storage import Product
from .utils import JsonEncoder


class LoginView(AuthServiceViewMixin, AccessTokenServiceViewMixin, View):
    """View аутентификации."""

    @validate(request_schema=AUTH_SCHEMA)
    async def post(self, *args) -> Response:
        """
        Аутентификация пользователя.

        :return: ответ 200 (OK), содержащий тело токена в случае успешной аутентификации;
                 ответ 400 (Bad Request), если были переданы некорректные аутентификационные данные
        """
        credentials = await self.request.json()
        if await self.auth_service.check_credentials(**credentials):
            token = await self.token_service.get_by_login(login=credentials['login'])
            return json_response(status=200, data={'token': token})

        return json_response(status=400, data={'error': 'Bad credentials'})


class ProductListCreateView(ProductServiceViewMixin, View):
    """View создания и получения списка продуктов."""

    async def get(self) -> Response:
        """
        Endpoint вывода всех продуктов.

        :return: ответ 200 (OK), содержащий коллекцию json-представлений продуктов
        """
        products = await self.product_service.get_all()
        body = json.dumps([dict(product) for product in products], cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    @validate(request_schema=PRODUCT_SCHEMA)
    async def post(self, *args) -> Response:
        """
        Endpoint создания продуктов.

        :return: ответ 201 (Created), содержащий json-представление продукта в случае успеха;
                 ответ 400 (Bad Request), если данный продукт уже существует или были переданы некорректные данные
        """
        data = await self.request.json()
        product = Product(**data)
        if await self.product_service.exists_by_slug(slug=product.slug):
            return json_response(status=400,
                                 data={'error': 'Product with this slug is already exists'})

        created = await self.product_service.create(product=product)
        body = json.dumps(dict(created), cls=JsonEncoder)
        return Response(status=201, text=body, content_type='application/json')


class ProductRetrieveUpdateDeleteView(ProductServiceViewMixin, View):
    """View получения/обновления/удаления конкретного продукта."""

    async def get(self) -> Response:
        """
        Endpoint, возвращающий представление конкретного продукта по slug.

        :return: ответ 200 (OK), содержащий json-представление продукта;
                 ответ 404 (Not Found), если продукт не был найден
        """
        try:
            product = await self.product_service.get_by_slug(
                slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        body = json.dumps(dict(product), cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    @validate(request_schema=PRODUCT_SCHEMA)
    async def put(self, *args) -> Response:
        """
        Endpoint, возвращающий обновленное представление продукта по slug.

        Принимает тело запроса и обновляет выбранный продукт.

        :return: ответ 200 (OK), содержащий json-представление обновленного продукта;
                 ответ 404 (Not Found), если продукт не был найден
        """
        data = await self.request.json()
        try:
            product = await self.product_service.get_by_slug(
                slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        for prop, value in data.items():
            setattr(product, prop, value)

        product = await self.product_service.update(product)
        body = json.dumps(dict(product), cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')

    async def delete(self) -> Response:
        """
        Endpoint, удаляющий продукт по его slug.

        :return: ответ 204 (No Content) в случае успешного удаления продукта;
                 ответ 404 (Not Found) если продукт не был найден
        """
        try:
            product = await self.product_service.get_by_slug(
                slug=self.request.match_info['slug'])
        except ProductNotFoundException:
            return json_response(status=404, data={'error': 'Product not found'})

        await self.product_service.delete(product)
        return Response(status=204)


class OrderListCreateView(ProductServiceViewMixin, OrderServiceViewMixin, View):
    """View создания и получения списка заказов."""

    @validate(request_schema=ORDER_PRODUCT_SCHEMA)
    async def post(self, *args):
        """
        Endpoint создания заказа.

        :return: ответ 201 (Created), в случае успешного создания заказа;
                 ответ 404 (Not Found), в случае, если запрашиваемый продукт не был найден;
                 ответ 400 (Bad Request), в случае, если клиент пытается заказать товара больше, чем есть на складе
        """
        products = []
        data = await self.request.json()
        for item in data:
            try:
                product = await self.product_service.get_by_slug(slug=item['product'])
                products.append((product, item['quantity']))
            except ProductNotFoundException:
                error_message = 'Product with "{slug}" slug do not exists'.format(slug=item['product'])
                return json_response(status=404, data={'error': error_message})

        try:
            order, order_products = await self.order_service.create(
                user=self.request['user'], products=products)
        except ProductNotEnoughException as e:
            await self.request['trans'].rollback()
            error_message = 'Not enough product with slug "{slug}" in stock.'.format(slug=e.product.slug)
            return json_response(status=400, data={'error': error_message})

        order_dict = dict(order)
        order_dict['products'] = [dict(product) for product in order_products]
        body = json.dumps(order_dict, cls=JsonEncoder)
        return Response(status=201, text=body, content_type='application/json')


class OrderRetrieveUpdateDeleteView(OrderServiceViewMixin, View):
    """View получения/обновления/удаления конкретного заказа."""

    async def get(self):
        """
        Endpoint получения конкретного заказа.

        :return: ответ 200 (OK), содержащий json-представление заказа и его продуктов;
                 ответ 404 (Not Found), в случае, если заказ не был найден, либо принадлежит другому пользователю
        """
        order_number = int(self.request.match_info['number'])
        try:
            order, order_products = await self.order_service.get_by_number(
                user=self.request['user'], number=order_number)
        except OrderNotFoundException:
            return json_response(status=404, data={'error': 'Order not found'})

        order_dict = dict(order)
        order_dict['products'] = [dict(product) for product in order_products]
        body = json.dumps(order_dict, cls=JsonEncoder)
        return Response(status=200, text=body, content_type='application/json')
