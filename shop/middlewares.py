from typing import Callable

from aiohttp import web

from shop.dao import (SqlAlchemyOrderDAO, SqlAlchemyOrderProductDAO, SqlAlchemyProductDAO,
                      SqlAlchemyTokenDAO, SqlAlchemyUserDAO, SqlAlchemyUserOrderDAO)


@web.middleware
async def transaction_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    Middleware (посредник), открывающий соединение с БД и создающий транзакцию.

    Проставляет в экземпляр запроса экземпляр соединения с БД и экземпляр текущей транзакции.

    :param request: экземпляр запроса
    :param handler: обработчик запроса (controller)
    :return: экземпляр ответа
    """
    async with request.app['db'].acquire() as conn:
        trans = await conn.begin()
        request['conn'] = conn
        request['trans'] = trans
        try:
            response = await handler(request)
        except Exception as e:
            await trans.rollback()
            raise e

        if trans.is_active:
            await trans.commit()
        return response


@web.middleware
async def dao_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    Middleware (посредник), создающий DAO-экземпляры.

    Создает DAO-экземпляры и проставляет их в объект запроса.

    :param request: экземпляр запроса
    :param handler: обработчик запроса (controller)
    :return: экземпляр ответа
    """
    conn = request['conn']
    dao_instances = {
        'user': SqlAlchemyUserDAO(conn),
        'token': SqlAlchemyTokenDAO(conn),
        'product': SqlAlchemyProductDAO(conn),
        'order': SqlAlchemyOrderDAO(conn),
        'order_product': SqlAlchemyOrderProductDAO(conn),
        'user_order': SqlAlchemyUserOrderDAO(conn)
    }
    request['dao'] = dao_instances
    return await handler(request)
