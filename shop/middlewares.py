from aiohttp.web import middleware

from shop.dao import SqlAlchemyProductDAO, SqlAlchemyTokenDAO, SqlAlchemyUserDAO


@middleware
async def transaction_middleware(request, handler):
    """
    Middleware (посредник), открывающий соединение с БД и создающий транзакцию.

    Проставляет в экземпляр запроса экземпляр соединения с БД.

    :param request: экземпляр запроса
    :param handler: обработчик запроса (controller)
    :return: http-ответ
    """
    async with request.app['db'].acquire() as conn:
        request['conn'] = conn
        trans = await conn.begin()
        try:
            response = await handler(request)
        except Exception as e:
            await trans.rollback()
            raise e

        await trans.commit()
        return response


@middleware
async def dao_middleware(request, handler):
    """
    Middleware (посредник), создающий DAO-экземпляры.

    :param request: экземпляр запроса
    :param handler: обработчик запроса (controller)
    :return: http-ответ
    """
    conn = request['conn']
    dao_instances = {
        'user': SqlAlchemyUserDAO(conn),
        'token': SqlAlchemyTokenDAO(conn),
        'product': SqlAlchemyProductDAO(conn)
    }
    request.app['dao'] = dao_instances
    return await handler(request)
