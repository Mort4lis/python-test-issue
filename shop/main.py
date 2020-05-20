from aiohttp import web

from shop.db import close_pg, init_pg
from shop.routes import setup_routes
from shop.settings import config

app = web.Application()
app['config'] = config

app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

setup_routes(app)
web.run_app(app)
