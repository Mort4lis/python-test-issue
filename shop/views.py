from aiohttp.web import Response, View, json_response
from aiohttp_validate import validate

from .auth import check_credentials, get_access_token


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
        db_engine = self.request.app['db']
        credentials = await self.request.json()
        if await check_credentials(db_engine=db_engine, **credentials):
            token = await get_access_token(db_engine=db_engine, login=credentials['login'])
            return json_response(status=200, data={'token': token})

        return json_response(status=400, data={'error': 'Bad credentials'})


async def index(request):
    return json_response(data={'message': 'Hello, world!'})
