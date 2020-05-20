from typing import Optional

from aiohttp import web
from aiohttp_tokenauth import token_auth_middleware

from shop.db import close_pg, init_pg
from shop.exceptions import DAOException
from shop.middlewares import dao_middleware
from shop.routes import setup_routes
from shop.settings import config
from shop.storage import User


async def init():
    async def user_loader(token: str) -> Optional[User]:
        """
        Проверить валидность переданного токена.

        В случае, если токен найден в БД - вернет экземпляр класса `shop.storage.User`.
        В противном случае - None.

        :param token: Токен из HTTP заголовка "Authorization"
        """
        user_dao = app['dao']['user']
        try:
            user = await user_dao.get_by_token(token)
        except DAOException:
            user = None
        return user

    app = web.Application(middlewares=[
        dao_middleware,
        token_auth_middleware(
            user_loader=user_loader,
            exclude_routes=('/login',)
        )
    ])
    app['config'] = config

    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    setup_routes(app)
    return app


if __name__ == '__main__':
    web.run_app(init())
