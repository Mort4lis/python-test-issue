from typing import Optional

from aiohttp import web
from aiohttp_tokenauth import token_auth_middleware

from dao import SqlAlchemyUserDAO
from db import close_pg, init_pg
from exceptions import DAOException
from middlewares import transaction_middleware
from routes import setup_routes
from settings import config
from storage import User


async def init() -> web.Application:
    """
    Инициализация aiohttp-приложения.

    :return: экземпляр aiohttp-приложения
    """
    async def user_loader(token: str) -> Optional[User]:
        """
        Проверить валидность переданного токена.

        :param token: Токен из HTTP заголовка "Authorization"
        :return: если токен найден в БД - вернет экземпляр класса `User`,
                 в противном случае - None
        """
        async with app['db'].acquire() as conn:
            user_dao = SqlAlchemyUserDAO(conn)
            try:
                user = await user_dao.get_by_token(token)
            except DAOException:
                user = None
            return user

    app = web.Application(middlewares=[
        transaction_middleware,
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
