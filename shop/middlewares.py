from typing import Callable

from aiohttp import web


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
