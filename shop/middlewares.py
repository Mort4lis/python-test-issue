from aiohttp.web import middleware

from shop.dao import SqlAlchemyProductDAO, SqlAlchemyTokenDAO, SqlAlchemyUserDAO


@middleware
async def dao_middleware(request, handler):
    """Middleware (посредник), открывающий соединение с БД и создающий DAO-экземпляры."""
    async with request.app['db'].acquire() as conn:
        dao_instances = {
            'user': SqlAlchemyUserDAO(conn),
            'token': SqlAlchemyTokenDAO(conn),
            'product': SqlAlchemyProductDAO(conn)
            # others dao ...
        }
        request.app['dao'] = dao_instances
        return await handler(request)
