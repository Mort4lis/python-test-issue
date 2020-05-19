from aiohttp import web

from . import db


async def index(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.user.select())
        users = await cursor.fetchall()

    return web.json_response(data={'message': 'Hello, world!'})
