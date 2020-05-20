from aiohttp.web import middleware

from shop.dao import SqlAlchemyTokenDAO, SqlAlchemyUserDAO


@middleware
async def dao_middleware(request, handler):
    async with request.app['db'].acquire() as conn:
        dao_instances = {
            'user': SqlAlchemyUserDAO(conn),
            'token': SqlAlchemyTokenDAO(conn),
            # others dao ...
        }
        request.app['dao'] = dao_instances
        return await handler(request)
